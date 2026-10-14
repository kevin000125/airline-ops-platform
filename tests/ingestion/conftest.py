import csv
import io
import zipfile
from collections.abc import Callable
from pathlib import Path

import pytest

from airline_ops.ingestion.validation import EXPECTED_COLUMN_COUNT, REQUIRED_COLUMNS


@pytest.fixture
def bts_zip_factory() -> Callable[[Path, str], Path]:
    def write_bts_zip(zip_path: Path, marker: str = "original") -> Path:
        headers = list(REQUIRED_COLUMNS)
        headers.extend(
            f"AdditionalColumn{index}"
            for index in range(EXPECTED_COLUMN_COUNT - len(headers))
        )

        row = {
            "Year": "2026",
            "Month": "1",
            "FlightDate": "2026-01-01",
            "Reporting_Airline": "AA",
            "Flight_Number_Reporting_Airline": "100",
            "Origin": "PHX",
            "Dest": "LAX",
            "CRSDepTime": "900",
            "Cancelled": "0",
            "Diverted": "0",
            "ArrDelayMinutes": "0",
            "AdditionalColumn0": marker,
        }

        csv_buffer = io.StringIO(newline="")
        writer = csv.DictWriter(csv_buffer, fieldnames=headers)
        writer.writeheader()
        writer.writerow(row)

        with zipfile.ZipFile(zip_path, "w") as archive:
            archive.writestr("monthly.csv", csv_buffer.getvalue())
            archive.writestr("readme.html", "documentation")
        return zip_path

    return write_bts_zip
