import argparse
from collections.abc import Sequence
from pathlib import Path

from airline_ops.ingestion.service import SourceRevisionError, ingest_local_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Ingest one local BTS ZIP into partitioned raw storage."
    )
    parser.add_argument(
        "--source",
        required=True,
        type=Path,
        help="Path to the locally downloaded BTS ZIP file.",
    )
    parser.add_argument("--year", required=True, type=int)
    parser.add_argument("--month", required=True, type=int)
    parser.add_argument(
        "--raw-base-dir",
        type=Path,
        default=Path("data/raw"),
        help="Raw storage root (default: data/raw).",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        result = ingest_local_file(
            source_path=args.source,
            raw_base_dir=args.raw_base_dir,
            year=args.year,
            month=args.month,
        )
    except (FileNotFoundError, SourceRevisionError, ValueError) as error:
        parser.exit(status=1, message=f"error: {error}\n")

    print(f"Decision: {result.decision.value.upper()}")
    print(f"Destination: {result.destination_path}")
    print(f"SHA-256: {result.checksum}")
    print(f"CSV member: {result.validation.csv_member}")
    print(f"Rows: {result.validation.row_count}")
    print(f"Columns: {result.validation.column_count}")
    print(
        "Flight dates: "
        f"{result.validation.minimum_flight_date} "
        f"through {result.validation.maximum_flight_date}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
