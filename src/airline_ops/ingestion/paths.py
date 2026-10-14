from pathlib import Path

DATASET_NAME = "reporting_carrier_on_time"
EARLIEST_DATA_YEAR = 1987


def build_raw_partition_path(
    base_dir: Path,
    year: int,
    month: int,
) -> Path:
    """Return the raw ZIP destination for one BTS reporting month."""

    if year < EARLIEST_DATA_YEAR:
        raise ValueError(
            f"year must be {EARLIEST_DATA_YEAR} or later"
        )

    if not 1 <= month <= 12:
        raise ValueError("month must be between 1 and 12")

    month_text = f"{month:02d}"
    file_name = f"bts_{DATASET_NAME}_{year}_{month_text}.zip"

    return (
        base_dir
        / "bts"
        / DATASET_NAME
        / f"year={year}"
        / f"month={month_text}"
        / file_name
    )
