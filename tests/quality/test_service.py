from datetime import date
from decimal import Decimal

import pytest

from airline_ops.quality.service import _summary_from_row


def test_summary_from_row_normalizes_database_values() -> None:
    summary = _summary_from_row(
        (
            date(2026, 1, 1),
            544_003,
            517_222,
            25_635,
            1_146,
            92_000,
            Decimal("4.71"),
            Decimal("17.79"),
        )
    )

    assert summary.total_flights == 544_003
    assert summary.cancellation_rate_pct == 4.71
    assert summary.arrival_delay_rate_pct == 17.79


def test_summary_from_row_rejects_non_numeric_rate() -> None:
    with pytest.raises(TypeError, match="expected numeric quality metric"):
        _summary_from_row(
            (date(2026, 1, 1), 1, 1, 0, 0, 0, "invalid", Decimal("0"))
        )
