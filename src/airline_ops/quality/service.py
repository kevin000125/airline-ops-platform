from dataclasses import dataclass
from datetime import date
from decimal import Decimal

import psycopg

from airline_ops.warehouse.config import WarehouseConfig


@dataclass(frozen=True)
class MonthlyQualitySummary:
    reporting_month: date
    total_flights: int
    operated_flights: int
    cancelled_flights: int
    diverted_flights: int
    delayed_arrivals: int
    cancellation_rate_pct: float
    arrival_delay_rate_pct: float


def get_monthly_quality_summary(
    config: WarehouseConfig,
    year: int,
    month: int,
) -> MonthlyQualitySummary:
    """Read the dbt-built observability metrics for one reporting month."""

    with psycopg.connect(
        host=config.host,
        port=config.port,
        dbname=config.database,
        user=config.user,
        password=config.password,
        connect_timeout=10,
    ) as connection:
        row = connection.execute(
            """
            SELECT
                reporting_month,
                total_flights,
                operated_flights,
                cancelled_flights,
                diverted_flights,
                delayed_arrivals,
                cancellation_rate_pct,
                arrival_delay_rate_pct
            FROM analytics.ops_monthly_quality
            WHERE reporting_month = make_date(%s, %s, 1)
            """,
            (year, month),
        ).fetchone()

    if row is None:
        raise ValueError(f"quality summary not found for {year}-{month:02d}")
    return _summary_from_row(row)


def _summary_from_row(row: tuple[object, ...]) -> MonthlyQualitySummary:
    return MonthlyQualitySummary(
        reporting_month=row[0],
        total_flights=int(row[1]),
        operated_flights=int(row[2]),
        cancelled_flights=int(row[3]),
        diverted_flights=int(row[4]),
        delayed_arrivals=int(row[5]),
        cancellation_rate_pct=_to_float(row[6]),
        arrival_delay_rate_pct=_to_float(row[7]),
    )


def _to_float(value: object) -> float:
    if not isinstance(value, (int, float, Decimal)):
        raise TypeError(f"expected numeric quality metric, got {type(value).__name__}")
    return float(value)
