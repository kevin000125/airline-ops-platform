# Data Quality and Observability

The project keeps the first quality layer intentionally small. The selected
checks cover different failure modes without turning the portfolio project into
a long checklist.

## Blocking Checks

`dbt build` fails when any of these contracts is violated:

1. Business keys and dimension keys remain unique and non-null.
2. Staging `year` and `month` agree with `flight_date`.
3. The fact table row count matches the warehouse staging view.
4. `flight_status` is one of `operated`, `cancelled`, or `diverted`.

Because Airflow runs `dbt build`, a failed dbt test makes the
`build_analytics` task fail and prevents quality metrics from being published.

## Monthly Metrics

`analytics.ops_monthly_quality` contains one row per reporting month with:

- total, operated, cancelled, and diverted flight counts;
- delayed arrival count;
- cancellation rate;
- arrival delay rate among operated flights.

The final Airflow task, `report_quality_metrics`, reads this row and records it
in the task log. This gives operators a concise monthly summary without needing
to inspect all flight records.
