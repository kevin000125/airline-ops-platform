import hashlib
from pathlib import Path

import pytest

from airline_ops.ingestion.idempotency import (
    IngestionDecision,
    calculate_sha256,
    decide_ingestion,
)


def test_calculate_sha256(tmp_path: Path) -> None:
    file_path = tmp_path / "source.zip"
    content = b"monthly airline data"
    file_path.write_bytes(content)

    assert calculate_sha256(file_path) == hashlib.sha256(content).hexdigest()


def test_decide_ingestion_saves_new_file(tmp_path: Path) -> None:
    source_path = tmp_path / "source.zip"
    source_path.write_bytes(b"new data")

    decision = decide_ingestion(source_path, tmp_path / "raw.zip")

    assert decision is IngestionDecision.SAVE


def test_decide_ingestion_skips_identical_file(tmp_path: Path) -> None:
    source_path = tmp_path / "source.zip"
    destination_path = tmp_path / "raw.zip"
    source_path.write_bytes(b"same data")
    destination_path.write_bytes(b"same data")

    decision = decide_ingestion(source_path, destination_path)

    assert decision is IngestionDecision.SKIP


def test_decide_ingestion_flags_source_revision(tmp_path: Path) -> None:
    source_path = tmp_path / "source.zip"
    destination_path = tmp_path / "raw.zip"
    source_path.write_bytes(b"revised data")
    destination_path.write_bytes(b"original data")

    decision = decide_ingestion(source_path, destination_path)

    assert decision is IngestionDecision.SOURCE_REVISION


def test_decide_ingestion_rejects_missing_source(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="source file does not exist"):
        decide_ingestion(tmp_path / "missing.zip", tmp_path / "raw.zip")
