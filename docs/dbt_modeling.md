# dbt Analytics Modeling

## Purpose

Transform warehouse staging data into documented, reusable analytics models.
Python owns file ingestion and warehouse loading; dbt owns SQL transformations
inside PostgreSQL.

## Lineage

```text
source('warehouse_staging', 'bts_flights')
  -> analytics.stg_bts_flights
       -> analytics.fct_flights
       -> analytics.dim_airlines
       -> analytics.dim_airports
       -> analytics.ops_monthly_quality
```

## Models

- `stg_bts_flights`: typed source view plus deterministic `flight_record_id`.
- `fct_flights`: one row per scheduled flight leg with operational status.
- `dim_airlines`: one row per observed reporting airline.
- `dim_airports`: one row per observed origin or destination airport.
- `ops_monthly_quality`: one monthly row of operational counts and rates.

## Core Tests

- `flight_record_id`: not null and unique.
- `airline_code`: not null and unique.
- `airport_code`: not null and unique.
- staging and fact row counts reconcile.
- partition year/month agree with `flight_date`.
- `flight_status` contains only documented values.

## Commands

Run commands from the repository root with PostgreSQL running:

```cmd
python -m dotenv run -- dbt debug --profiles-dir dbt
python -m dotenv run -- dbt build --profiles-dir dbt
```

The `.env` file supplies local PostgreSQL credentials and is not committed.
