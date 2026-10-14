import csv
import io
import zipfile
from pathlib import Path

import pytest

from airline_ops.ingestion.validation import (
    EXPECTED_COLUMN_COUNT,
    REQUIRED_COLUMNS,
    RawZipValidationError,
    validate_raw_zip,
)


def test_validate_raw_zip_returns_source_profile(tmp_path: Path) -> None:
    zip_path = _write_test_archive(tmp_path, ["2026-01-01", "2026-01-31"])

    result = validate_raw_zip(zip_path, 2026, 1)

    assert result.csv_member == "monthly.csv"
    assert result.row_count == 2
    assert result.column_count == EXPECTED_COLUMN_COUNT
    assert result.minimum_flight_date.isoformat() == "2026-01-01"
    assert result.maximum_flight_date.isoformat() == "2026-01-31"


def test_validate_raw_zip_rejects_invalid_archive(tmp_path: Path) -> None:
    zip_path = tmp_path / "invalid.zip"
    zip_path.write_text("not a zip archive", encoding="utf-8")

    with pytest.raises(RawZipValidationError, match="not a valid ZIP archive"):
        validate_raw_zip(zip_path, 2026, 1)


def test_validate_raw_zip_requires_one_csv(tmp_path: Path) -> None:
    zip_path = tmp_path / "no-csv.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("readme.html", "documentation")

    with pytest.raises(RawZipValidationError, match="exactly one CSV"):
        validate_raw_zip(zip_path, 2026, 1)


def test_validate_raw_zip_rejects_date_outside_requested_month(
    tmp_path: Path,
) -> None:
    zip_path = _write_test_archive(tmp_path, ["2026-02-01"])

    with pytest.raises(RawZipValidationError, match="outside requested period"):
        validate_raw_zip(zip_path, 2026, 1)


def _write_test_archive(tmp_path: Path, flight_dates: list[str]) -> Path:
    headers = list(REQUIRED_COLUMNS)
    headers.extend(
        f"AdditionalColumn{index}"
        for index in range(EXPECTED_COLUMN_COUNT - len(headers))
    )

    csv_buffer = io.StringIO(newline="")
    writer = csv.DictWriter(csv_buffer, fieldnames=headers)
    writer.writeheader()
    for flight_date in flight_dates:
        writer.writerow(
            {
                "Year": flight_date[:4],
                "Month": str(int(flight_date[5:7])),
                "FlightDate": flight_date,
                "Reporting_Airline": "AA",
                "Flight_Number_Reporting_Airline": "100",
                "Origin": "PHX",
                "Dest": "LAX",
                "CRSDepTime": "900",
                "Cancelled": "0",
                "Diverted": "0",
                "ArrDelayMinutes": "0",
            }
        )

    zip_path = tmp_path / "monthly.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("monthly.csv", csv_buffer.getvalue())
        archive.writestr("readme.html", "documentation")
    return zip_path
