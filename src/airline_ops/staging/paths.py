from pathlib import Path

from airline_ops.ingestion.paths import DATASET_NAME, EARLIEST_DATA_YEAR


def build_staging_partition_path(base_dir: Path, year: int, month: int) -> Path:
    """Return the typed Parquet destination for one reporting month."""

    if year < EARLIEST_DATA_YEAR:
        raise ValueError(f"year must be {EARLIEST_DATA_YEAR} or later")
    if not 1 <= month <= 12:
        raise ValueError("month must be between 1 and 12")

    month_text = f"{month:02d}"
    return (
        base_dir
        / "bts"
        / DATASET_NAME
        / f"year={year}"
        / f"month={month_text}"
        / f"bts_{DATASET_NAME}_{year}_{month_text}.parquet"
    )
