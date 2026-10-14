from datetime import date

import pyarrow as pa

from airline_ops.staging.schema import staging_schema
from airline_ops.warehouse.service import iter_warehouse_rows


def test_iter_warehouse_rows_normalizes_indicators_to_booleans() -> None:
    schema = staging_schema()
    values: list[object] = []
    for field in schema:
        if field.name == "flight_date":
            values.append(date(2026, 1, 1))
        elif pa.types.is_string(field.type):
            values.append("value")
        else:
            values.append(1)

    batch = pa.RecordBatch.from_pylist(
        [dict(zip(schema.names, values, strict=True))],
        schema=schema,
    )

    row = next(iter_warehouse_rows(batch))
    assert row[schema.get_field_index("dep_del15")] is True
    assert row[schema.get_field_index("arr_del15")] is True
    assert row[schema.get_field_index("cancelled")] is True
    assert row[schema.get_field_index("diverted")] is True
