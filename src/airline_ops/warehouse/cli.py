import argparse
from collections.abc import Sequence
from pathlib import Path

import psycopg

from airline_ops.staging.paths import build_staging_partition_path
from airline_ops.warehouse.config import WarehouseConfig
from airline_ops.warehouse.service import (
    WarehouseRevisionError,
    WarehouseStateError,
    load_parquet_to_warehouse,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Load one monthly typed Parquet file into PostgreSQL."
    )
    parser.add_argument("--year", required=True, type=int)
    parser.add_argument("--month", required=True, type=int)
    parser.add_argument("--staging-base-dir", type=Path, default=Path("data/interim"))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    parquet_path = build_staging_partition_path(
        args.staging_base_dir, args.year, args.month
    )

    try:
        result = load_parquet_to_warehouse(
            parquet_path,
            WarehouseConfig.from_env(),
            args.year,
            args.month,
        )
    except (
        FileNotFoundError,
        WarehouseRevisionError,
        WarehouseStateError,
        ValueError,
        psycopg.Error,
    ) as error:
        parser.exit(status=1, message=f"error: {error}\n")

    print(f"Decision: {result.decision.value.upper()}")
    print(f"Source: {result.source_path}")
    print(f"Source SHA-256: {result.source_checksum}")
    print(f"Rows: {result.row_count}")
    print("Destination: PostgreSQL staging.bts_flights")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
