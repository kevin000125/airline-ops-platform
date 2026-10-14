# BTS Typed Staging Design

## Purpose

Convert an immutable monthly BTS raw ZIP into a typed, query-efficient
Parquet file without changing the raw source.

## Input

```text
data/raw/bts/reporting_carrier_on_time/
  year=YYYY/month=MM/bts_reporting_carrier_on_time_YYYY_MM.zip
```

## Output

```text
data/interim/bts/reporting_carrier_on_time/
  year=YYYY/month=MM/bts_reporting_carrier_on_time_YYYY_MM.parquet
```

## Transformation Contract

- Stream the CSV directly from the ZIP instead of extracting a temporary CSV.
- Select the 39 columns confirmed during data discovery.
- Rename source columns to consistent `snake_case` names.
- Apply explicit Arrow data types, including a real `date32` flight date.
- Write Snappy-compressed Parquet in bounded record batches.
- Confirm every flight date belongs to the requested year and month.
- Store source SHA-256 and reporting-period lineage in Parquet metadata.
- Write to a temporary file before publishing the final output.

## Idempotency

- Missing Parquet destination: create it and return `SAVE`.
- Existing Parquet with the same source SHA-256: return `SKIP`.
- Existing Parquet with a different source SHA-256: stop with a staging revision error.

## Command

Run from the repository root with the virtual environment activated:

```cmd
python -m airline_ops.staging.cli --year 2026 --month 1
```
