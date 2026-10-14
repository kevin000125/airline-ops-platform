import hashlib
from enum import StrEnum
from pathlib import Path


class IngestionDecision(StrEnum):
    """Possible outcomes when a monthly raw file is ingested."""

    SAVE = "save"
    SKIP = "skip"
    SOURCE_REVISION = "source_revision"


def calculate_sha256(file_path: Path) -> str:
    """Return the SHA-256 checksum for a file without loading it all into memory."""

    with file_path.open("rb") as file_handle:
        return hashlib.file_digest(file_handle, "sha256").hexdigest()


def decide_ingestion(
    source_path: Path,
    destination_path: Path,
) -> IngestionDecision:
    """Choose whether a source file should be saved, skipped, or flagged."""

    if not source_path.is_file():
        raise FileNotFoundError(f"source file does not exist: {source_path}")

    if not destination_path.exists():
        return IngestionDecision.SAVE

    if calculate_sha256(source_path) == calculate_sha256(destination_path):
        return IngestionDecision.SKIP

    return IngestionDecision.SOURCE_REVISION
