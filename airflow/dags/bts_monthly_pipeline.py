from __future__ import annotations

import logging
import os
import subprocess
from dataclasses import asdict
from datetime import timedelta
from pathlib import Path

import pendulum
from airflow.sdk import Param, dag, get_current_context, task

from airline_ops.ingestion.paths import build_raw_partition_path
from airline_ops.ingestion.validation import validate_raw_zip
from airline_ops.quality.service import get_monthly_quality_summary
from airline_ops.staging.paths import build_staging_partition_path
from airline_ops.staging.service import stage_raw_zip
from airline_ops.warehouse.config import WarehouseConfig
from airline_ops.warehouse.service import load_parquet_to_warehouse

PROJECT_DIR = Path("/opt/airflow/project")
RAW_BASE_DIR = PROJECT_DIR / "data" / "raw"
STAGING_BASE_DIR = PROJECT_DIR / "data" / "interim"
LOGGER = logging.getLogger(__name__)


def _reporting_period() -> tuple[int, int]:
    params = get_current_context()["params"]
    return int(params["year"]), int(params["month"])


@dag(
    dag_id="bts_monthly_pipeline",
    description="Validate, stage, load, and model one BTS reporting month.",
    schedule=None,
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    catchup=False,
    max_active_runs=1,
    default_args={"owner": "data-engineering", "retries": 2, "retry_delay": timedelta(minutes=2)},
    params={
        "year": Param(2026, type="integer", minimum=1987),
        "month": Param(1, type="integer", minimum=1, maximum=12),
    },
    tags=["bts", "monthly", "airline-ops"],
)
def bts_monthly_pipeline():
    @task
    def validate_raw() -> dict[str, object]:
        year, month = _reporting_period()
        raw_path = build_raw_partition_path(RAW_BASE_DIR, year, month)
        result = validate_raw_zip(raw_path, year, month)
        return {**asdict(result), "zip_path": str(raw_path)}

    @task
    def build_typed_staging(_: dict[str, object]) -> dict[str, object]:
        year, month = _reporting_period()
        raw_path = build_raw_partition_path(RAW_BASE_DIR, year, month)
        result = stage_raw_zip(raw_path, STAGING_BASE_DIR, year, month)
        return {
            "decision": result.decision.value,
            "parquet_path": str(result.destination_path),
            "row_count": result.row_count,
            "source_checksum": result.source_checksum,
        }

    @task
    def load_warehouse(_: dict[str, object]) -> dict[str, object]:
        year, month = _reporting_period()
        parquet_path = build_staging_partition_path(STAGING_BASE_DIR, year, month)
        result = load_parquet_to_warehouse(
            parquet_path,
            WarehouseConfig.from_env(),
            year,
            month,
        )
        return {
            "decision": result.decision.value,
            "row_count": result.row_count,
            "source_checksum": result.source_checksum,
        }

    @task
    def build_analytics(_: dict[str, object]) -> None:
        env = os.environ.copy()
        subprocess.run(
            [
                "dbt",
                "build",
                "--project-dir",
                str(PROJECT_DIR),
                "--profiles-dir",
                str(PROJECT_DIR / "dbt"),
            ],
            cwd=PROJECT_DIR,
            env=env,
            check=True,
        )

    @task
    def report_quality_metrics(_: None) -> dict[str, object]:
        year, month = _reporting_period()
        summary = get_monthly_quality_summary(
            WarehouseConfig.from_env(),
            year,
            month,
        )
        metrics = asdict(summary)
        LOGGER.info("Monthly quality summary: %s", metrics)
        return metrics

    validation = validate_raw()
    staged = build_typed_staging(validation)
    loaded = load_warehouse(staged)
    analytics = build_analytics(loaded)
    report_quality_metrics(analytics)


bts_monthly_pipeline()
