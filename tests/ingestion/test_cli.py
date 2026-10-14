from collections.abc import Callable
from pathlib import Path

from airline_ops.ingestion.cli import main


def test_cli_ingests_local_file(
    tmp_path: Path,
    capsys,
    bts_zip_factory: Callable[[Path, str], Path],
) -> None:
    source_path = bts_zip_factory(tmp_path / "download.zip")
    raw_base_dir = tmp_path / "raw"

    exit_code = main(
        [
            "--source",
            str(source_path),
            "--year",
            "2026",
            "--month",
            "1",
            "--raw-base-dir",
            str(raw_base_dir),
        ]
    )

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Decision: SAVE" in output
    assert "year=2026" in output
    assert "month=01" in output
    assert "SHA-256:" in output
    assert "Rows: 1" in output
    assert "Columns: 109" in output
    assert "Flight dates: 2026-01-01 through 2026-01-01" in output
