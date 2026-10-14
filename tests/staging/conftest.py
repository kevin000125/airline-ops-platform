import csv
import io
import zipfile
from collections.abc import Callable
from pathlib import Path

import pyarrow as pa
import pytest

from airline_ops.staging.schema import COLUMNS


@pytest.fixture
def staging_zip_factory() -> Callable[[Path, str], Path]:
    def write_zip(zip_path: Path, airline: str = "AA") -> Path:
        values: dict[str, str] = {}
        for column in COLUMNS:
            values[column.source_name] = (
                "text" if pa.types.is_string(column.data_type) else "0"
            )

        values.update(
            {
                "Year": "2026",
                "Month": "1",
                "DayofMonth": "1",
                "DayOfWeek": "4",
                "FlightDate": "2026-01-01",
                "Reporting_Airline": airline,
                "Tail_Number": "N100AA",
                "Origin": "PHX",
                "Dest": "LAX",
                "CRSDepTime": "900",
                "CRSArrTime": "1030",
            }
        )

        csv_buffer = io.StringIO(newline="")
        writer = csv.DictWriter(csv_buffer, fieldnames=[item.source_name for item in COLUMNS])
        writer.writeheader()
        writer.writerow(values)

        with zipfile.ZipFile(zip_path, "w") as archive:
            archive.writestr("monthly.csv", csv_buffer.getvalue())
        return zip_path

    return write_zip
