\# BTS Reporting Carrier Data Discovery



\## Source Profile



\- Source: Bureau of Transportation Statistics (BTS)

\- Dataset: Reporting Carrier On-Time Performance

\- Extract period: January 2026

\- File: T\_ONTIME\_REPORTING.csv

\- Format: CSV

\- File size: 91.13 MiB

\- Rows: 544,003

\- Selected columns: 39

\- Date range: 2026-01-01 through 2026-01-31

\- Invalid flight dates: 0



\## Data Grain



One row represents one scheduled flight leg operated by a carrier

on a specific date.



\## Candidate Business Key



\- FL\_DATE

\- OP\_UNIQUE\_CARRIER

\- OP\_CARRIER\_FL\_NUM

\- ORIGIN

\- DEST



The candidate key produced zero duplicates in the January 2026 extract.



\## Core Data Quality Findings



\- Cancellation codes were consistent with cancellation status.

\- Cancelled flights may contain DEP\_TIME when the aircraft left the

&#x20; gate before cancellation.

\- Delay cause fields were populated only for qualifying delays.

\- Conditional null values are expected and should not automatically

&#x20; be treated as data quality failures.



\## Scope Limitation



This is a selected-field extract containing 39 columns rather than

the complete BTS source schema. Findings have only been validated

against January 2026.

