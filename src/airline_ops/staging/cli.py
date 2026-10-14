import argparse
from collections.abc import Sequence
from pathlib import Path

from airline_ops.ingestion.paths import build_raw_partition_path
from airline_ops.staging.service import StagingRevisionError, stage_raw_zip


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert one monthly BTS raw ZIP into typed Parquet staging data."
    )
    parser.add_argument("--year", required=True, type=int)
    parser.add_argument("--month", required=True, type=int)
    parser.add_argument("--raw-base-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--staging-base-dir", type=Path, default=Path("data/interim"))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    source_path = build_raw_partition_path(args.raw_base_dir, args.year, args.month)

    try:
        result = stage_raw_zip(
            source_path,
            args.staging_base_dir,
            args.year,
            args.month,
        )
    except (FileNotFoundError, StagingRevisionError, ValueError) as error:
        parser.exit(status=1, message=f"error: {error}\n")

    print(f"Decision: {result.decision.value.upper()}")
    print(f"Source: {result.source_path}")
    print(f"Destination: {result.destination_path}")
    print(f"Source SHA-256: {result.source_checksum}")
    print(f"Rows: {result.row_count}")
    print(f"Columns: {result.column_count}")
    print(
        "Flight dates: "
        f"{result.minimum_flight_date} through {result.maximum_flight_date}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
