import csv
import io
import zipfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path

EXPECTED_COLUMN_COUNT = 109
REQUIRED_COLUMNS = (
    "Year",
    "Month",
    "FlightDate",
    "Reporting_Airline",
    "Flight_Number_Reporting_Airline",
    "Origin",
    "Dest",
    "CRSDepTime",
    "Cancelled",
    "Diverted",
    "ArrDelayMinutes",
)


class RawZipValidationError(ValueError):
    """Raised when a BTS raw archive violates the expected source contract."""


@dataclass(frozen=True)
class RawZipValidationResult:
    """Summary of a validated monthly BTS raw archive."""

    csv_member: str
    row_count: int
    column_count: int
    minimum_flight_date: date
    maximum_flight_date: date


def validate_raw_zip(
    zip_path: Path,
    year: int,
    month: int,
) -> RawZipValidationResult:
    """Validate the archive, source schema, and requested reporting month."""

    if not zipfile.is_zipfile(zip_path):
        raise RawZipValidationError(f"not a valid ZIP archive: {zip_path}")

    with zipfile.ZipFile(zip_path) as archive:
        csv_members = [
            member
            for member in archive.namelist()
            if not member.endswith("/") and member.lower().endswith(".csv")
        ]
        if len(csv_members) != 1:
            raise RawZipValidationError(
                f"expected exactly one CSV member, found {len(csv_members)}"
            )

        csv_member = csv_members[0]
        with archive.open(csv_member) as binary_file:
            text_file = io.TextIOWrapper(binary_file, encoding="utf-8-sig", newline="")
            reader = csv.DictReader(text_file)
            headers = tuple(header for header in (reader.fieldnames or ()) if header)
            _validate_schema(headers)
            row_count, minimum_date, maximum_date = _validate_rows(
                reader,
                year,
                month,
            )

    return RawZipValidationResult(
        csv_member=csv_member,
        row_count=row_count,
        column_count=len(headers),
        minimum_flight_date=minimum_date,
        maximum_flight_date=maximum_date,
    )


def _validate_schema(headers: tuple[str, ...]) -> None:
    if len(headers) != EXPECTED_COLUMN_COUNT:
        raise RawZipValidationError(
            f"expected {EXPECTED_COLUMN_COUNT} columns, found {len(headers)}"
        )

    missing_columns = sorted(set(REQUIRED_COLUMNS) - set(headers))
    if missing_columns:
        raise RawZipValidationError(
            f"missing required columns: {', '.join(missing_columns)}"
        )


def _validate_rows(
    reader: csv.DictReader,
    year: int,
    month: int,
) -> tuple[int, date, date]:
    row_count = 0
    minimum_date: date | None = None
    maximum_date: date | None = None

    for row_number, row in enumerate(reader, start=2):
        try:
            flight_date = date.fromisoformat(row["FlightDate"])
        except (KeyError, TypeError, ValueError) as error:
            raise RawZipValidationError(
                f"invalid FlightDate at CSV row {row_number}"
            ) from error

        if flight_date.year != year or flight_date.month != month:
            raise RawZipValidationError(
                f"FlightDate outside requested period at CSV row {row_number}: "
                f"{flight_date}"
            )

        row_count += 1
        minimum_date = min(minimum_date, flight_date) if minimum_date else flight_date
        maximum_date = max(maximum_date, flight_date) if maximum_date else flight_date

    if row_count == 0 or minimum_date is None or maximum_date is None:
        raise RawZipValidationError("CSV contains no data rows")

    return row_count, minimum_date, maximum_date
