import zipfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from tempfile import NamedTemporaryFile

import pyarrow as pa
import pyarrow.csv as arrow_csv
import pyarrow.parquet as pq

from airline_ops.ingestion.idempotency import IngestionDecision, calculate_sha256
from airline_ops.ingestion.validation import RawZipValidationError
from airline_ops.staging.paths import build_staging_partition_path
from airline_ops.staging.schema import SOURCE_COLUMNS, SOURCE_TYPES, staging_schema


class StagingRevisionError(RuntimeError):
    """Raised when an existing Parquet file came from a different raw source."""


@dataclass(frozen=True)
class StagingResult:
    decision: IngestionDecision
    source_path: Path
    destination_path: Path
    source_checksum: str
    row_count: int
    column_count: int
    minimum_flight_date: date
    maximum_flight_date: date


def stage_raw_zip(
    source_path: Path,
    staging_base_dir: Path,
    year: int,
    month: int,
) -> StagingResult:
    """Convert one immutable BTS raw ZIP into a typed monthly Parquet file."""

    if not source_path.is_file():
        raise FileNotFoundError(source_path)
    if not zipfile.is_zipfile(source_path):
        raise RawZipValidationError(f"not a valid ZIP archive: {source_path}")

    destination_path = build_staging_partition_path(staging_base_dir, year, month)
    source_checksum = calculate_sha256(source_path)
    existing_result = _existing_result(
        source_path, destination_path, source_checksum, year, month
    )
    if existing_result is not None:
        return existing_result

    destination_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = _temporary_path(destination_path)
    try:
        result = _write_parquet(
            source_path,
            temporary_path,
            destination_path,
            source_checksum,
            year,
            month,
        )
        temporary_path.replace(destination_path)
        return result
    finally:
        temporary_path.unlink(missing_ok=True)


def _write_parquet(
    source_path: Path,
    temporary_path: Path,
    destination_path: Path,
    source_checksum: str,
    year: int,
    month: int,
) -> StagingResult:
    csv_member = _single_csv_member(source_path)
    metadata = {
        b"source_sha256": source_checksum.encode(),
        b"source_file": source_path.name.encode(),
        b"source_csv_member": csv_member.encode(),
        b"reporting_year": str(year).encode(),
        b"reporting_month": str(month).encode(),
    }
    schema = staging_schema(metadata)
    row_count = 0
    minimum_date: date | None = None
    maximum_date: date | None = None

    with zipfile.ZipFile(source_path) as archive, archive.open(csv_member) as csv_file:
        reader = arrow_csv.open_csv(
            csv_file,
            read_options=arrow_csv.ReadOptions(block_size=8 * 1024 * 1024),
            convert_options=arrow_csv.ConvertOptions(
                include_columns=list(SOURCE_COLUMNS),
                column_types=SOURCE_TYPES,
                strings_can_be_null=True,
            ),
        )
        with pq.ParquetWriter(temporary_path, schema, compression="snappy") as writer:
            for source_batch in reader:
                batch = pa.RecordBatch.from_arrays(source_batch.columns, schema=schema)
                batch_minimum, batch_maximum = _validate_batch_period(batch, year, month)
                writer.write_batch(batch)
                row_count += batch.num_rows
                minimum_date = min(minimum_date, batch_minimum) if minimum_date else batch_minimum
                maximum_date = max(maximum_date, batch_maximum) if maximum_date else batch_maximum

    if row_count == 0 or minimum_date is None or maximum_date is None:
        raise RawZipValidationError("CSV contains no data rows")

    return StagingResult(
        IngestionDecision.SAVE,
        source_path,
        destination_path,
        source_checksum,
        row_count,
        len(schema),
        minimum_date,
        maximum_date,
    )


def _validate_batch_period(batch: pa.RecordBatch, year: int, month: int) -> tuple[date, date]:
    dates = batch.column(batch.schema.get_field_index("flight_date")).to_pylist()
    if not dates or any(value is None for value in dates):
        raise RawZipValidationError("flight_date contains null values")

    minimum_date = min(dates)
    maximum_date = max(dates)
    if (
        minimum_date.year != year
        or minimum_date.month != month
        or maximum_date.year != year
        or maximum_date.month != month
    ):
        raise RawZipValidationError(
            f"flight_date outside requested period: {minimum_date} through {maximum_date}"
        )
    return minimum_date, maximum_date


def _existing_result(
    source_path: Path,
    destination_path: Path,
    source_checksum: str,
    year: int,
    month: int,
) -> StagingResult | None:
    if not destination_path.exists():
        return None

    parquet_file = pq.ParquetFile(destination_path)
    metadata = parquet_file.schema_arrow.metadata or {}
    stored_checksum = metadata.get(b"source_sha256", b"").decode()
    if stored_checksum != source_checksum:
        raise StagingRevisionError(
            f"staging revision detected for {year}-{month:02d}: {destination_path}"
        )

    flight_date_index = parquet_file.schema_arrow.get_field_index("flight_date")
    statistics = [
        parquet_file.metadata.row_group(index).column(flight_date_index).statistics
        for index in range(parquet_file.metadata.num_row_groups)
    ]
    minimum_date = min(item.min for item in statistics if item is not None)
    maximum_date = max(item.max for item in statistics if item is not None)
    return StagingResult(
        IngestionDecision.SKIP,
        source_path,
        destination_path,
        source_checksum,
        parquet_file.metadata.num_rows,
        len(parquet_file.schema_arrow),
        minimum_date,
        maximum_date,
    )


def _single_csv_member(source_path: Path) -> str:
    with zipfile.ZipFile(source_path) as archive:
        members = [
            name
            for name in archive.namelist()
            if not name.endswith("/") and name.lower().endswith(".csv")
        ]
    if len(members) != 1:
        raise RawZipValidationError(
            f"expected exactly one CSV member, found {len(members)}"
        )
    return members[0]


def _temporary_path(destination_path: Path) -> Path:
    with NamedTemporaryFile(
        dir=destination_path.parent,
        prefix=f".{destination_path.name}.",
        suffix=".tmp",
        delete=False,
    ) as temporary_file:
        return Path(temporary_file.name)
