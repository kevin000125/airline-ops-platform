from pathlib import Path

import pytest

from airline_ops.ingestion.paths import build_raw_partition_path


def test_build_raw_partition_path() -> None:
    result = build_raw_partition_path(Path("data/raw"), 2026, 1)

    assert result == Path(
        "data/raw/bts/reporting_carrier_on_time/"
        "year=2026/month=01/"
        "bts_reporting_carrier_on_time_2026_01.zip"
    )


@pytest.mark.parametrize("month", [0, 13])
def test_build_raw_partition_path_rejects_invalid_month(month: int) -> None:
    with pytest.raises(ValueError, match="month must be between 1 and 12"):
        build_raw_partition_path(Path("data/raw"), 2026, month)


def test_build_raw_partition_path_rejects_year_before_dataset() -> None:
    with pytest.raises(ValueError, match="year must be 1987 or later"):
        build_raw_partition_path(Path("data/raw"), 1986, 12)
