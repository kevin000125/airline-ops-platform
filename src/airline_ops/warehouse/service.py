from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import psycopg
import pyarrow as pa
import pyarrow.parquet as pq

from airline_ops.ingestion.idempotency import IngestionDecision
from airline_ops.staging.schema import TARGET_COLUMNS
from airline_ops.warehouse.config import WarehouseConfig

DATASET_NAME = "bts_reporting_carrier_on_time"
BOOLEAN_COLUMNS = {"dep_del15", "arr_del15", "cancelled", "diverted"}
CREATE_WAREHOUSE_SQL = Path(__file__).with_name("sql") / "001_create_warehouse.sql"
COPY_SQL = "COPY staging.bts_flights (" + ", ".join(TARGET_COLUMNS) + ") FROM STDIN"


class WarehouseRevisionError(RuntimeError):
    """Raised when a reporting period was loaded from a different source."""


class WarehouseStateError(RuntimeError):
    """Raised when warehouse data and its load manifest disagree."""


@dataclass(frozen=True)
class WarehouseLoadResult:
    decision: IngestionDecision
    source_path: Path
    source_checksum: str
    row_count: int
    year: int
    month: int


def load_parquet_to_warehouse(
    parquet_path: Path,
    config: WarehouseConfig,
    year: int,
    month: int,
) -> WarehouseLoadResult:
    """Atomically load one typed monthly Parquet file into PostgreSQL."""

    parquet_file = _validated_parquet(parquet_path, year, month)
    metadata = parquet_file.schema_arrow.metadata or {}
    source_checksum = metadata[b"source_sha256"].decode()
    source_row_count = parquet_file.metadata.num_rows

    with psycopg.connect(
        host=config.host,
        port=config.port,
        dbname=config.database,
        user=config.user,
        password=config.password,
        connect_timeout=10,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_WAREHOUSE_SQL.read_text(encoding="utf-8"))
            existing_load = cursor.execute(
                """
                SELECT source_sha256, source_row_count
                FROM control.pipeline_loads
                WHERE dataset_name = %s
                  AND reporting_year = %s
                  AND reporting_month = %s
                """,
                (DATASET_NAME, year, month),
            ).fetchone()

            if existing_load is not None:
                if existing_load == (source_checksum, source_row_count):
                    return WarehouseLoadResult(
                        IngestionDecision.SKIP,
                        parquet_path,
                        source_checksum,
                        source_row_count,
                        year,
                        month,
                    )
                raise WarehouseRevisionError(
                    f"warehouse revision detected for {year}-{month:02d}"
                )

            existing_rows = cursor.execute(
                """
                SELECT count(*) FROM staging.bts_flights
                WHERE year = %s AND month = %s
                """,
                (year, month),
            ).fetchone()[0]
            if existing_rows:
                raise WarehouseStateError(
                    f"found {existing_rows} untracked warehouse rows for {year}-{month:02d}"
                )

            with cursor.copy(COPY_SQL) as copy:
                for batch in parquet_file.iter_batches(batch_size=10_000):
                    for row in iter_warehouse_rows(batch):
                        copy.write_row(row)

            loaded_rows = cursor.execute(
                """
                SELECT count(*) FROM staging.bts_flights
                WHERE year = %s AND month = %s
                """,
                (year, month),
            ).fetchone()[0]
            if loaded_rows != source_row_count:
                raise WarehouseStateError(
                    f"row count mismatch: Parquet={source_row_count}, PostgreSQL={loaded_rows}"
                )

            cursor.execute(
                """
                INSERT INTO control.pipeline_loads (
                    dataset_name, reporting_year, reporting_month,
                    source_sha256, source_row_count, source_path
                ) VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    DATASET_NAME,
                    year,
                    month,
                    source_checksum,
                    source_row_count,
                    str(parquet_path),
                ),
            )

    return WarehouseLoadResult(
        IngestionDecision.SAVE,
        parquet_path,
        source_checksum,
        source_row_count,
        year,
        month,
    )


def iter_warehouse_rows(batch: pa.RecordBatch) -> Iterator[tuple[object, ...]]:
    columns = [column.to_pylist() for column in batch.columns]
    for row in zip(*columns, strict=True):
        yield tuple(
            _normalize_value(name, value)
            for name, value in zip(TARGET_COLUMNS, row, strict=True)
        )


def _normalize_value(column_name: str, value: object) -> object:
    if column_name in BOOLEAN_COLUMNS and value is not None:
        return bool(int(value))
    return value


def _validated_parquet(parquet_path: Path, year: int, month: int) -> pq.ParquetFile:
    if not parquet_path.is_file():
        raise FileNotFoundError(parquet_path)

    parquet_file = pq.ParquetFile(parquet_path)
    if tuple(parquet_file.schema_arrow.names) != TARGET_COLUMNS:
        raise ValueError("Parquet schema does not match the 39-column staging contract")

    metadata = parquet_file.schema_arrow.metadata or {}
    if b"source_sha256" not in metadata:
        raise ValueError("Parquet metadata is missing source_sha256")
    if metadata.get(b"reporting_year") != str(year).encode():
        raise ValueError("Parquet reporting_year does not match requested year")
    if metadata.get(b"reporting_month") != str(month).encode():
        raise ValueError("Parquet reporting_month does not match requested month")
    return parquet_file
