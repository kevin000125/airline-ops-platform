from collections.abc import Callable
from pathlib import Path

import pytest

from airline_ops.ingestion.idempotency import IngestionDecision, calculate_sha256
from airline_ops.ingestion.service import SourceRevisionError, ingest_local_file


def test_ingest_local_file_saves_new_source(
    tmp_path: Path,
    bts_zip_factory: Callable[[Path, str], Path],
) -> None:
    source_path = bts_zip_factory(tmp_path / "download.zip")
    raw_base_dir = tmp_path / "raw"

    result = ingest_local_file(source_path, raw_base_dir, 2026, 1)

    expected_destination = (
        raw_base_dir
        / "bts"
        / "reporting_carrier_on_time"
        / "year=2026"
        / "month=01"
        / "bts_reporting_carrier_on_time_2026_01.zip"
    )
    assert result.decision is IngestionDecision.SAVE
    assert result.destination_path == expected_destination
    assert result.checksum == calculate_sha256(source_path)
    assert expected_destination.read_bytes() == source_path.read_bytes()
    assert result.validation.row_count == 1
    assert result.validation.column_count == 109


def test_ingest_local_file_skips_identical_source(
    tmp_path: Path,
    bts_zip_factory: Callable[[Path, str], Path],
) -> None:
    source_path = bts_zip_factory(tmp_path / "download.zip")
    raw_base_dir = tmp_path / "raw"

    first_result = ingest_local_file(source_path, raw_base_dir, 2026, 1)
    second_result = ingest_local_file(source_path, raw_base_dir, 2026, 1)

    assert first_result.decision is IngestionDecision.SAVE
    assert second_result.decision is IngestionDecision.SKIP


def test_ingest_local_file_rejects_source_revision(
    tmp_path: Path,
    bts_zip_factory: Callable[[Path, str], Path],
) -> None:
    source_path = bts_zip_factory(tmp_path / "download.zip")
    raw_base_dir = tmp_path / "raw"
    original_result = ingest_local_file(source_path, raw_base_dir, 2026, 1)

    bts_zip_factory(source_path, "revised")

    with pytest.raises(SourceRevisionError, match="source revision detected"):
        ingest_local_file(source_path, raw_base_dir, 2026, 1)

    assert original_result.destination_path.read_bytes() != source_path.read_bytes()
