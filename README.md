# Airline Operations Data Platform

Portfolio-oriented data engineering project for exploring U.S. airline operations, delay patterns, cancellations, congestion, and reliability.

## Current Stage

Stage 8: Continuous Integration Baseline

Raw monthly BTS archives are validated, converted to typed Parquet, and loaded
atomically into PostgreSQL. dbt then builds a tested analytics layer containing
flight facts and airline and airport dimensions. Airflow coordinates these
steps as an observable monthly DAG with retries and task-level logs. Focused
dbt contracts stop bad data, while monthly quality metrics summarize each run.
GitHub Actions now runs Python linting and unit tests for every change to `main`
without requiring local data, Docker, or database credentials.

## Learning Goals

- Inspect the source schema and understand what one row represents.
- Identify candidate business keys and the dataset grain.
- Explore scheduled times, actual times, delays, cancellations, diversions, and delay causes.
- Look for nulls, duplicates, anomalies, and future data-quality checks.
- Capture observations before making architecture or modeling decisions.

## Repository Structure

```text
.
├── data/
│   ├── raw/              # Source files kept close to their downloaded form
│   │   └── bts/          # BTS on-time performance extracts
│   ├── interim/          # Typed monthly Parquet staging outputs
│   └── processed/        # Curated local outputs, if needed later
├── docs/
│   └── data_discovery/   # Notes from schema, grain, null, and anomaly analysis
├── notebooks/            # Local exploratory notebooks
├── scripts/              # Small helper scripts, not pipelines yet
├── src/
│   └── airline_ops/      # Future reusable Python package code
└── tests/                # Future tests
```

## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the project dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Copy the environment template:

```powershell
Copy-Item .env.example .env
```

## Verify The Environment

Run:

```powershell
python -c "import pandas, pyarrow, dotenv; print('environment ok')"
pytest
```

Run all automated checks with:

```powershell
ruff check src tests
pytest
```

GitHub Actions runs the same checks on pushes and pull requests to `main`. See
`docs/ci_cd.md` for the workflow scope and current integration-test boundary.

## Run The Local Pipeline

Start the local PostgreSQL warehouse:

```cmd
docker compose up -d postgres
docker compose ps
```

Open a PostgreSQL command-line session inside the container:

```cmd
docker compose exec postgres psql -U airline_user -d airline_ops
```

Stop PostgreSQL without deleting its data:

```cmd
docker compose stop postgres
```

Ingest a downloaded monthly ZIP into immutable raw storage:

```cmd
python -m airline_ops.ingestion.cli --source "C:\path\to\source.zip" --year 2026 --month 1
```

Convert the stored raw month into typed Parquet staging data:

```cmd
python -m airline_ops.staging.cli --year 2026 --month 1
```

Load the typed month into PostgreSQL:

```cmd
python -m airline_ops.warehouse.cli --year 2026 --month 1
```

Build and test the dbt analytics models:

```cmd
python -m dotenv run -- dbt build --profiles-dir dbt
```

Build, initialize, and start Airflow:

```cmd
docker compose build airflow-init
docker compose up airflow-init
docker compose up -d airflow-api-server airflow-scheduler airflow-dag-processor
```

Open `http://localhost:8080`, select `bts_monthly_pipeline`, and trigger it with
the desired `year` and `month`. See `docs/orchestration.md` for the architecture.

## First Data Discovery Task

Download one month of BTS Reporting Carrier On-Time Performance data and place the CSV or ZIP file under:

```text
data/raw/bts/
```

Then create a short note in:

```text
docs/data_discovery/
```

Start by answering only these questions:

1. What does one row appear to represent?
2. Which columns look like candidate identifiers for a flight record?
3. Which columns represent scheduled times, actual times, cancellations, diversions, and delays?

Do not design the final schema yet. The goal is observation, not architecture.
