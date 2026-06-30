# 00 · Glossary

Plain-language definitions. Where a term is AWS-specific, that's noted. Return here whenever a word bites.

**ACID** — Atomicity, Consistency, Isolation, Durability: the transaction guarantees databases give. Data lakes historically lacked these; table formats like Iceberg add them back.

**Backfill** — Re-running a pipeline over historical data, e.g. after fixing a bug or adding a new field. A good pipeline can backfill without producing duplicates (see *idempotency*).

**Bronze / Silver / Gold** — The "medallion" layering of a lake: raw (bronze), cleaned/validated (silver), business-ready/aggregated (gold). Conventional names, not AWS services.

**CDC (Change Data Capture)** — Capturing row-level changes (insert/update/delete) from a source database as they happen, rather than re-copying the whole table. On AWS, done with DMS. → Mod 03.

**Columnar format** — Storing data column-by-column (Parquet, ORC) instead of row-by-row (CSV). Analytics reads a few columns over many rows, so columnar is dramatically faster and cheaper to scan. → Mod 02.

**Data Catalog** — A central registry of table definitions (schema, location, partitions) that query engines read. AWS's is the *Glue Data Catalog*. → Mod 04.

**Data swamp** — A data lake that grew without governance: nobody knows what's in it, what's trustworthy, or who owns it. The failure mode lakes are prone to.

**DAG (Directed Acyclic Graph)** — A graph of tasks with dependencies and no cycles; the standard way to represent a pipeline's execution order. Airflow/MWAA pipelines are DAGs. → Mod 06.

**Idempotency** — A property where running an operation multiple times has the same effect as running it once. Critical for safe retries and backfills. → Mod 00 architect-notes, Mod 03.

**Lakehouse** — An architecture combining a lake's cheap, flexible storage with a warehouse's reliability (ACID, schema enforcement), via table formats like Iceberg. → Mod 09.

**MPP (Massively Parallel Processing)** — Splitting a query across many nodes that each work on a slice of the data, then combining results. Redshift is an MPP warehouse. → Mod 07.

**Partitioning** — Physically organizing data into folders by a key (usually date), so queries can skip irrelevant data. The single biggest lever for lake query cost and speed. → Mod 02.

**Schema-on-read vs schema-on-write** — On-read: store raw, impose structure when querying (lakes, flexible). On-write: validate/structure on the way in (warehouses, rigid but reliable). → Mod 00.

**Serverless** — A model where you don't provision or manage servers; you pay per use and AWS scales it. Lambda, Glue, Athena, Firehose. Cheaper when spiky, pricier when steady-high. → Mod 00 architect-notes.

**Spark** — The dominant distributed data-processing engine. Runs on Glue (serverless) and EMR (managed clusters). → Mod 04.

**Throughput vs latency** — Throughput: how much data per unit time. Latency: delay for a single item. Batch optimizes throughput; streaming optimizes latency. They trade off.

**Upsert / MERGE** — Insert-or-update: write a row if its key is new, update it if the key exists. The idempotent alternative to blind inserts. → Mod 07.
