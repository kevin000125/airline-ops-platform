# Airflow Orchestration

Airflow coordinates the existing monthly pipeline; it does not replace the
Python transformation or loading code.

## DAG

`bts_monthly_pipeline` runs five tasks in order:

1. `validate_raw` validates the immutable BTS ZIP contract and reporting month.
2. `build_typed_staging` converts the source into typed Parquet.
3. `load_warehouse` atomically loads PostgreSQL and records the source checksum.
4. `build_analytics` runs `dbt build` to create and test analytics models.
5. `report_quality_metrics` logs the selected month's operational summary.

The DAG is manual (`schedule=None`) because BTS data does not arrive at a fixed
day and the project does not yet download files automatically. A run accepts
`year` and `month` parameters. Existing idempotency rules remain active, so a
rerun safely returns `SKIP` for unchanged staging and warehouse inputs.

## Runtime Architecture

- `postgres`: project warehouse containing staging and analytics data.
- `airflow-postgres`: Airflow metadata only, such as DAG runs and task states.
- `airflow-api-server`: web UI and Airflow API on port 8080.
- `airflow-scheduler`: schedules tasks and executes them with `LocalExecutor`.
- `airflow-dag-processor`: parses and serializes DAG definitions.
- `airflow-init`: one-time metadata migration and local admin creation.

This is a local learning environment. Production deployments require external
secret management, stronger authentication, remote logs, monitoring, backups,
and a scalable executor or managed Airflow service.

## Commands

Initialize and start Airflow:

```cmd
docker compose build airflow-init
docker compose up airflow-init
docker compose up -d airflow-api-server airflow-scheduler airflow-dag-processor
docker compose ps
```

Open `http://localhost:8080` and sign in with the local credentials from `.env`.

Stop Airflow without deleting its metadata:

```cmd
docker compose stop airflow-api-server airflow-scheduler airflow-dag-processor airflow-postgres
```
