\# BTS Ingestion Design



\## MVP Scope



The first version ingests a locally downloaded BTS ZIP file.

Automated HTTP downloading will be added after the core ingestion

logic is validated.



\## Inputs



\- Source ZIP file

\- Year

\- Month



\## Raw Output



data/raw/bts/reporting\_carrier\_on\_time/

&#x20; year=YYYY/

&#x20;   month=MM/

&#x20;     bts\_reporting\_carrier\_on\_time\_YYYY\_MM.zip



\## Core Requirements



\- Preserve the complete source ZIP.

\- Validate year and month.

\- Calculate a SHA-256 checksum.

\- Never silently overwrite raw data.

\- Skip when an identical file already exists.

\- Stop and flag a possible source revision when checksums differ.

\- Use a temporary file before moving data into the final partition.



\## Idempotency Behavior



\- Missing destination: save the file.

\- Same checksum: skip successfully.

\- Different checksum: fail and report a source revision.



\## Future Extension



Add automated BTS HTTP downloading with retry, timeout, and

network error handling.

