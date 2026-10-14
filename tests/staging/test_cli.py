from collections.abc import Callable
from pathlib import Path

from airline_ops.ingestion.paths import build_raw_partition_path
from airline_ops.staging.cli import main


def test_staging_cli(
    tmp_path: Path,
    capsys,
    staging_zip_factory: Callable[[Path, str], Path],
) -> None:
    raw_base_dir = tmp_path / "raw"
    source_path = build_raw_partition_path(raw_base_dir, 2026, 1)
    source_path.parent.mkdir(parents=True)
    staging_zip_factory(source_path)

    exit_code = main(
        [
            "--year",
            "2026",
            "--month",
            "1",
            "--raw-base-dir",
            str(raw_base_dir),
            "--staging-base-dir",
            str(tmp_path / "interim"),
        ]
    )

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Decision: SAVE" in output
    assert "Rows: 1" in output
    assert "Columns: 39" in output
