from collections.abc import Callable
from pathlib import Path

import pyarrow.parquet as pq
import pytest

from airline_ops.ingestion.idempotency import IngestionDecision
from airline_ops.staging.schema import TARGET_COLUMNS
from airline_ops.staging.service import StagingRevisionError, stage_raw_zip


def test_stage_raw_zip_writes_typed_parquet(
    tmp_path: Path,
    staging_zip_factory: Callable[[Path, str], Path],
) -> None:
    source_path = staging_zip_factory(tmp_path / "raw.zip")

    result = stage_raw_zip(source_path, tmp_path / "interim", 2026, 1)

    table = pq.read_table(result.destination_path)
    assert result.decision is IngestionDecision.SAVE
    assert result.row_count == 1
    assert result.column_count == 39
    assert result.minimum_flight_date.isoformat() == "2026-01-01"
    assert table.column_names == list(TARGET_COLUMNS)
    assert table.column("flight_date")[0].as_py().isoformat() == "2026-01-01"
    assert table.schema.metadata[b"source_sha256"].decode() == result.source_checksum


def test_stage_raw_zip_skips_same_source(
    tmp_path: Path,
    staging_zip_factory: Callable[[Path, str], Path],
) -> None:
    source_path = staging_zip_factory(tmp_path / "raw.zip")
    stage_raw_zip(source_path, tmp_path / "interim", 2026, 1)

    result = stage_raw_zip(source_path, tmp_path / "interim", 2026, 1)

    assert result.decision is IngestionDecision.SKIP
    assert result.row_count == 1


def test_stage_raw_zip_rejects_changed_source(
    tmp_path: Path,
    staging_zip_factory: Callable[[Path, str], Path],
) -> None:
    source_path = staging_zip_factory(tmp_path / "raw.zip")
    stage_raw_zip(source_path, tmp_path / "interim", 2026, 1)
    staging_zip_factory(source_path, airline="DL")

    with pytest.raises(StagingRevisionError, match="staging revision detected"):
        stage_raw_zip(source_path, tmp_path / "interim", 2026, 1)
