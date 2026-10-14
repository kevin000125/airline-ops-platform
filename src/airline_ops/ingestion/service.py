import shutil
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile

from airline_ops.ingestion.idempotency import (
    IngestionDecision,
    calculate_sha256,
    decide_ingestion,
)
from airline_ops.ingestion.paths import build_raw_partition_path
from airline_ops.ingestion.validation import RawZipValidationResult, validate_raw_zip


class SourceRevisionError(RuntimeError):
    """Raised when a monthly raw file differs from the stored version."""


@dataclass(frozen=True)
class IngestionResult:
    """Summary of a completed local-file ingestion attempt."""

    decision: IngestionDecision
    destination_path: Path
    checksum: str
    validation: RawZipValidationResult


def ingest_local_file(
    source_path: Path,
    raw_base_dir: Path,
    year: int,
    month: int,
) -> IngestionResult:
    """Ingest one local BTS ZIP into immutable partitioned raw storage."""

    validation_result = validate_raw_zip(source_path, year, month)
    destination_path = build_raw_partition_path(raw_base_dir, year, month)
    decision = decide_ingestion(source_path, destination_path)
    source_checksum = calculate_sha256(source_path)

    if decision is IngestionDecision.SKIP:
        return IngestionResult(
            decision,
            destination_path,
            source_checksum,
            validation_result,
        )

    if decision is IngestionDecision.SOURCE_REVISION:
        raise SourceRevisionError(
            f"source revision detected for {year}-{month:02d}: "
            f"{destination_path}"
        )

    destination_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = _copy_to_temporary_file(source_path, destination_path)

    try:
        if calculate_sha256(temporary_path) != source_checksum:
            raise OSError("temporary copy checksum does not match source")

        temporary_path.replace(destination_path)
    finally:
        temporary_path.unlink(missing_ok=True)

    return IngestionResult(
        decision,
        destination_path,
        source_checksum,
        validation_result,
    )


def _copy_to_temporary_file(source_path: Path, destination_path: Path) -> Path:
    with NamedTemporaryFile(
        dir=destination_path.parent,
        prefix=f".{destination_path.name}.",
        suffix=".tmp",
        delete=False,
    ) as temporary_file:
        temporary_path = Path(temporary_file.name)

    shutil.copyfile(source_path, temporary_path)
    return temporary_path
