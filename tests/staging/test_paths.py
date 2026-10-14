from pathlib import Path

import pytest

from airline_ops.staging.paths import build_staging_partition_path


def test_build_staging_partition_path() -> None:
    result = build_staging_partition_path(Path("data/interim"), 2026, 1)

    assert result == Path(
        "data/interim/bts/reporting_carrier_on_time/"
        "year=2026/month=01/"
        "bts_reporting_carrier_on_time_2026_01.parquet"
    )


@pytest.mark.parametrize("month", [0, 13])
def test_build_staging_partition_path_rejects_invalid_month(month: int) -> None:
    with pytest.raises(ValueError, match="month must be between 1 and 12"):
        build_staging_partition_path(Path("data/interim"), 2026, month)
