# CI/CD Baseline

The GitHub Actions workflow in `.github/workflows/ci.yml` validates every pull
request to `main` and every push to `main`. It can also be started manually from
the Actions page with `workflow_dispatch`.

## Checks

The `python-quality` job uses Python 3.11 and runs:

```text
python -m ruff check src tests
python -m pytest
```

These checks are intentionally independent of local BTS files, PostgreSQL, and
Docker. Unit tests use small generated fixtures, so the workflow is fast and no
database credentials or production-like data need to be stored in GitHub.

## Current Boundary

This is the continuous integration (CI) baseline. It validates source code but
does not deploy the pipeline, so continuous deployment (CD) is not enabled yet.
Database-backed dbt and Airflow integration checks remain local until their
runtime cost and value justify a separate CI job.

## Local Equivalent

Run the same checks before pushing:

```cmd
python -m ruff check src tests
python -m pytest
```
