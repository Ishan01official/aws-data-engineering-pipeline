# Glossary

Plain-language definitions for the whole repo. Module 00 has a focused foundations glossary; this is the superset. Return here whenever a term bites.

**ACID** — Atomicity, Consistency, Isolation, Durability: transaction guarantees. Lakes historically lacked these; Iceberg adds them back.

**At-least-once / exactly-once** — Delivery guarantees. At-least-once may deliver duplicates (handle with idempotency); exactly-once guarantees no dupes (costlier, needs framework support). → Mod 05.

**Bronze / Silver / Gold (medallion)** — Lake layering: raw → cleaned/validated → business-ready/aggregated.

**CDC (Change Data Capture)** — Capturing row-level DB changes as they happen, vs re-copying tables. AWS: DMS. → Mod 03.

**Columnar format** — Storing by column (Parquet/ORC) not row (CSV). Analytics scans few columns over many rows → far cheaper/faster. → Mod 02.

**CTAS** — `CREATE TABLE AS SELECT`: materialize query results as a new table; in Athena, a common way to convert/partition data. → Mod 04.

**DAG** — Directed Acyclic Graph of tasks with dependencies; how pipelines are modeled (Airflow/MWAA). → Mod 06.

**Distribution key / Sort key** — Redshift table design: distribution key controls how rows spread across nodes (affects join colocation); sort key controls on-disk order (affects scan pruning). → Mod 07.

**DPU** — Data Processing Unit: Glue's unit of compute capacity you're billed for.

**Glue Data Catalog** — Central metadata registry (schemas, locations, partitions) that Athena, Redshift Spectrum, EMR, and Glue all read. → Mod 04.

**Idempotency** — Re-running an operation yields the same result as running it once. Precondition for safe retries/backfills. → Mod 00, 11.

**Iceberg** — Open table format over Parquet adding ACID, schema evolution, hidden partitioning, time-travel. → Mod 02, 09.

**Job bookmark** — Glue's mechanism to track already-processed data so jobs run incrementally. → Mod 04.

**Lakehouse** — Lake storage economics + warehouse reliability (ACID), via table formats like Iceberg. → Mod 09.

**Lake Formation** — Fine-grained (column/row/tag) access control over lake data, on top of IAM. → Mod 08.

**LF-Tags** — Lake Formation tags enabling scalable, attribute-based grants across many tables. → Mod 08.

**MPP** — Massively Parallel Processing: split a query across nodes, each on a data slice. Redshift. → Mod 07.

**OIDC (in CI/CD)** — Lets GitHub Actions assume an AWS role without storing static AWS keys. → Mod 11.

**Partitioning** — Organizing data into folders by a key (usually date) so engines skip irrelevant data. Biggest lake cost/speed lever. → Mod 02.

**RTO / RPO** — Recovery Time Objective (how fast you recover) / Recovery Point Objective (how much data you can lose). Failure-recovery design. → Mod 12.

**Replay** — Reprocessing past events from a durable stream (Kinesis/MSK) after a bug or new requirement. → Mod 05.

**Schema-on-read / -on-write** — Impose structure at query time (lakes, flexible) vs at write time (warehouses, validated). → Mod 00.

**Schema drift** — Upstream schema changing over time; must be detected and handled. → Mod 04, runbook.

**Serverless** — Pay-per-use, auto-scaled, no servers to manage (Lambda, Glue, Athena, Firehose). Cheaper when spiky. → Mod 00.

**SLA / SLO** — Service Level Agreement (the promise) / Objective (the internal target). → Mod 11.

**Spectrum** — Redshift Spectrum: query S3 data directly from Redshift without loading it. → Mod 07.

**Upsert / MERGE** — Insert-or-update by key; the idempotent alternative to blind insert. → Mod 07.

**Watermark** — In streaming, a marker of event-time progress used to decide when a window can close, handling late data. → Mod 05.
