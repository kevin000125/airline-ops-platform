# PostgreSQL Warehouse Loading

## Purpose

Load one typed monthly Parquet partition into PostgreSQL so SQL and dbt can
build reusable analytics models.

## Database Schemas

- `staging.bts_flights`: typed flight records loaded from Parquet.
- `control.pipeline_loads`: source checksum, period, row count, path, and load time.

## Load Guarantees

- Uses PostgreSQL `COPY` for bulk loading.
- Loads one month inside a single transaction.
- Rolls back the entire month if any step fails.
- Verifies the PostgreSQL row count against Parquet metadata.
- Returns `SKIP` when the same source checksum was already loaded.
- Stops on source revision or untracked rows instead of silently overwriting data.

## Command

```cmd
python -m airline_ops.warehouse.cli --year 2026 --month 1
```

## Verification

```cmd
docker compose exec postgres psql -U airline_user -d airline_ops
```

```sql
SELECT count(*), min(flight_date), max(flight_date)
FROM staging.bts_flights;
```
