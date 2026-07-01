# Service Decision Framework

The hardest part of AWS data engineering isn't using a service — it's *choosing* the right one when three could technically do the job. This is the reference for those decisions. Each comparison gives you a **Best for / Avoid when / Cost / Complexity / Latency / Ops burden**, plus the short answer you'd give in an **interview** and the deeper one an **architect** would give in a design review.

Read the [Foundations five-axis framework](./00-foundations/) first — every decision below is an application of latency / volume / structure / cost-model / ops-burden.

> Rule of thumb that resolves ~70% of these: **default to the most managed (serverless) option, and move toward provisioned/self-managed only when a concrete requirement forces it.** "We might need control later" is not a requirement.

---

## 1. Glue vs EMR vs Lambda vs Redshift SQL (where do I transform data?)

| | **Glue ETL** | **EMR / EMR Serverless** | **Lambda** | **Redshift SQL (ELT)** |
|---|---|---|---|---|
| Best for | Default serverless Spark batch ETL | Heavy, tuned, long-running Spark/Hive; custom runtimes | Light per-event/per-file transforms | Transforming data already in the warehouse |
| Avoid when | You need fine Spark tuning or non-Spark engines | You don't want to manage clusters/versions | Job >15 min, big shuffles, heavy memory | Data isn't (and shouldn't be) in Redshift |
| Cost | Per DPU-hour, no idle cost | Cheapest per-unit at high steady use; cluster cost | Per-ms; near-zero idle | Coupled to cluster/serverless RPU |
| Complexity | Low | High | Lowest | Low (if you know SQL) |
| Latency | Minutes (job startup) | Minutes; low once warm | Milliseconds | Seconds |
| Ops burden | Low | High | Lowest | Low–medium |

**Interview answer:** "Glue for default batch ETL, EMR when I need heavy Spark tuning or a long-running cluster, Lambda for lightweight event-driven transforms under 15 minutes, and Redshift SQL when the data's already in the warehouse and ELT is cheaper than moving it out."

**Architect answer:** The real decision is *where the data already is* and *how much it costs to move it*. Pushing transformation to where the data lives (ELT in Redshift, query-in-place with Athena) often beats pulling it into a separate compute layer. Glue vs EMR is a utilization-and-control question: below ~60–70% sustained utilization Glue's zero-idle model wins; above it, and when you need specific Spark versions or tuning, EMR earns its operational cost. Lambda's 15-minute ceiling and memory limits make it a router and light-transformer, not an ETL engine — using it for big joins is the classic "wrong tool" smell.

---

## 2. Step Functions vs MWAA vs Glue Workflows vs EventBridge (how do I orchestrate?)

| | **Step Functions** | **MWAA (Airflow)** | **Glue Workflows** | **EventBridge** |
|---|---|---|---|---|
| Best for | Serverless coordination of AWS services with branching/retries | Complex, Python-defined DAGs across many systems | Orchestrating Glue-only crawler+job chains | Event routing & cron triggering |
| Avoid when | DAG logic is very complex/dynamic | You want zero infra and low cost | Non-Glue steps are involved | You need stateful multi-step workflows |
| Cost | Per state transition; cheap | Always-on environment cost (notable) | Included with Glue | Near-free |
| Complexity | Medium | High | Low | Low |
| Latency | Low | Low | Low | Low |
| Ops burden | Very low (serverless) | High (managed but you own DAGs/env) | Very low | Very low |

**Interview answer:** "Step Functions for serverless AWS-service orchestration, MWAA when I need rich Airflow DAGs and a big operator ecosystem, Glue Workflows for simple Glue-only chains, and EventBridge as the trigger layer that kicks any of them off."

**Architect answer:** MWAA's always-on cost and operational weight mean you should justify it — it's right when you have many DAGs, cross-system operators, and a team that knows Airflow. For most AWS-native pipelines, Step Functions + EventBridge is cheaper, lower-ops, and integrates natively with retries and error handling. Glue Workflows is fine until you need a single non-Glue step, at which point you'll wish you'd started with Step Functions. A common pattern: EventBridge (schedule/event) → Step Functions (orchestration) → Glue/Lambda (work).

---

## 3. Kinesis Data Streams vs Firehose vs MSK (how do I move streaming data?)

| | **Kinesis Data Streams** | **Kinesis Firehose** | **Amazon MSK (Kafka)** |
|---|---|---|---|
| Best for | Real-time ingest you process with custom consumers; replay | "Just land my stream in S3/Redshift" with zero code | Kafka ecosystem, multi-consumer, high throughput, portability |
| Avoid when | You only need delivery to S3 (use Firehose) | You need custom per-record processing or replay | You don't want to manage Kafka concepts |
| Cost | Per shard-hour + payload | Per GB ingested; no infra | Per broker-hour; highest baseline |
| Complexity | Medium | Lowest | High |
| Latency | ~ sub-second | Buffered (60s+ / size-based) | sub-second |
| Ops burden | Low | Lowest | Medium–high |

**Interview answer:** "Firehose when I just need buffered delivery to S3/Redshift with no code, Data Streams when I need real-time custom processing and replay, and MSK when I specifically need Kafka — its ecosystem, multiple independent consumers, or portability across clouds."

**Architect answer:** The Streams-vs-Firehose line is *delivery vs processing*: Firehose is a managed sink with buffering and basic transforms; Streams is a durable, replayable log you build consumers on. MSK is the answer when "we need Kafka" is a real requirement — existing Kafka apps, the connector ecosystem, fan-out to many consumer groups, or multi-cloud portability — and you accept the operational tax. Watch the cost shapes: Firehose scales to zero, Streams bills per provisioned shard (or on-demand), MSK carries an always-on broker cost that makes it expensive for low volumes.

---

## 4. Athena vs Redshift vs OpenSearch (where do users query?)

| | **Athena** | **Redshift** | **OpenSearch** |
|---|---|---|---|
| Best for | Ad-hoc SQL over S3, no loading, infrequent/varied | Fast, repeated BI on structured data at scale | Search, log analytics, text/observability |
| Avoid when | High-concurrency, low-latency dashboards | Truly ad-hoc exploration of raw lake data | Relational analytics / joins-heavy SQL |
| Cost | Per TB scanned (partitioning is everything) | Cluster/serverless compute | Cluster cost |
| Complexity | Low | Medium | Medium |
| Latency | Seconds | Sub-second once modeled | Sub-second search |
| Ops burden | Very low | Medium | Medium |

**Interview answer:** "Athena for serverless ad-hoc querying of the lake, Redshift for fast repeated BI on modeled data, OpenSearch for search and log analytics. Athena cost is driven by data scanned, so partitioning and columnar formats matter enormously."

**Architect answer:** Athena and Redshift are not rivals so much as different points on a frequency/latency curve. Infrequent, varied queries over a huge lake → Athena, paying only per scan. The same dashboard hit thousands of times a day → model it into Redshift, where you amortize the load cost across fast repeated reads. Redshift Spectrum and Athena both query S3, so the lake stays the source of truth either way. OpenSearch is a different shape entirely — reach for it for full-text search and log/observability use cases, not relational analytics.

---

## 5. S3 Data Lake vs Redshift Warehouse vs Lakehouse

| | **S3 Lake** | **Redshift Warehouse** | **Lakehouse (S3 + Iceberg)** |
|---|---|---|---|
| Best for | Cheap storage of raw/varied data, ML, exploration | Fast structured BI, complex joins, concurrency | Both: lake economics + warehouse reliability (ACID) |
| Avoid when | You need fast complex joins & strict schema | Data is huge, raw, or schema-flexible | Team can't absorb extra tooling/maturity |
| Cost | Lowest (storage) | Higher (coupled compute) | Low storage, flexible compute |
| Complexity | Low storage, high to govern | Medium | Highest (newest moving parts) |
| Ops burden | Low–medium | Medium | Medium–high |

**Architect answer:** This is the central architecture decision of the modern stack, and it's driven by the price gap between S3 storage (~$0.023/GB-mo) and warehouse storage. Keep the bulk of data in S3; bring compute to it. The lakehouse (Iceberg on S3) exists to give the lake the ACID transactions, schema evolution, and time-travel that warehouses always had — letting you keep one cheap copy of data that's both lake and warehouse-queryable. Pure Redshift is still right when you have heavy, concurrent, latency-sensitive BI on well-modeled data. Most mature platforms run *both*: lakehouse as source of truth, Redshift as a fast serving layer for the hottest marts.

---

## 6. Glue Data Catalog vs Hive Metastore

| | **Glue Data Catalog** | **Self-managed Hive Metastore** |
|---|---|---|
| Best for | AWS-native metadata, serverless, integrates with Athena/Redshift/EMR | Existing Hive investments, multi-cloud, specific Hive features |
| Avoid when | You have a hard multi-cloud/portability need | You don't want to run a metastore DB |
| Cost | Per-object + request; cheap | EC2/RDS for the metastore |
| Ops burden | Near-zero | You own it |

**Architect answer:** On AWS, the Glue Data Catalog is the default — it's the metadata layer Athena, Redshift Spectrum, EMR, and Glue all read, with no server to run. Self-managed Hive Metastore is justified mainly by portability or an existing Hive ecosystem you're migrating. The catalog *is* the contract between storage and every query engine; treat its schema definitions as a first-class, version-controlled asset.

---

## 7. Lake Formation vs IAM-only access

| | **Lake Formation** | **IAM-only** |
|---|---|---|
| Best for | Fine-grained (column/row/cell) access, many users, tag-based governance | Simple, coarse bucket/prefix-level access, few principals |
| Avoid when | Access truly is coarse (overkill) | You need column/row-level control or central grants |
| Complexity | Medium | Low |

**Architect answer:** IAM controls access at the resource/prefix level — fine for "team A reads this bucket." The moment you need *column-level* ("analysts can't see the PII columns") or *row-level* ("regional managers see only their region") security, or central tag-based grants across many tables, that's Lake Formation. The cost is added complexity and a permission model that layers on top of IAM, so don't reach for it until coarse access genuinely fails the requirement.

---

## 8. Batch vs Streaming

| | **Batch** | **Streaming** |
|---|---|---|
| Best for | Periodic processing, large volumes, lower cost | Low-latency reactions, continuous data |
| Avoid when | Decisions need fresh-by-the-second data | Hourly/daily freshness is fine (wasted cost/complexity) |
| Cost | Lower | Higher |
| Complexity | Lower | Higher |

**Architect answer:** Streaming is the most over-specified requirement in data engineering. "Real-time" usually means "within a few minutes," which micro-batch satisfies at a fraction of the cost and complexity. Interrogate the *decision* the data drives: a fraud block needs milliseconds; a "live" exec dashboard refreshed hourly is fine. Choose the slowest pattern that meets the actual SLA.

---

## 9. ETL vs ELT

| | **ETL** (transform before load) | **ELT** (load then transform) |
|---|---|---|
| Best for | Heavy cleansing before storage; sensitive data minimization | Modern warehouses/lakes with cheap compute; flexibility |
| Avoid when | Target compute is cheap and you want raw retained | You can't land raw data (compliance/PII) |

**Architect answer:** ELT became dominant because warehouse/lake compute got cheap and elastic — land raw data first (preserving the source of truth), transform in place, and re-transform freely as needs change. ETL still wins when you must minimize sensitive data before it lands, or when the target can't transform efficiently. The medallion architecture (bronze→silver→gold) is ELT in practice: raw lands first, transformations are versioned layers on top.

---

## 10. Star schema vs wide table

| | **Star schema** | **One big wide table** |
|---|---|---|
| Best for | Reusable dimensions, many query patterns, governed BI | Single denormalized query pattern, max read speed |
| Avoid when | Read performance is paramount and patterns are fixed | Dimensions change/reused; storage and update cost matter |

**Architect answer:** Columnar engines made wide tables viable by killing the storage/scan penalty of denormalization, and they're often faster for a fixed dashboard. But star schemas remain the governance and reuse winner — conformed dimensions are reused across marts and changes are localized. Many teams model in star schema and materialize wide tables for the hottest dashboards.

---

## 11. Parquet vs CSV vs JSON vs Iceberg

| | **Parquet** | **CSV** | **JSON** | **Iceberg** (table format over Parquet) |
|---|---|---|---|---|
| Best for | Analytics — columnar, compressed | Interchange, tiny data, human-readable | Nested/semi-structured, APIs | Lake tables needing ACID, schema evolution, time-travel |
| Avoid when | Row-by-row OLTP access | Any analytics at scale | Analytics at scale (slow to scan) | Simple append-only with no update needs |

**Architect answer:** Parquet is the default storage format for analytics — columnar layout means you scan only the columns you need, and compression slashes both storage and Athena scan cost. CSV/JSON are for ingestion and interchange, not analytics. Iceberg is not a competitor to Parquet — it's a *table format* layered over Parquet files that adds ACID transactions, safe schema evolution, hidden partitioning, and time-travel. It's what turns a pile of Parquet into a real table you can `MERGE` into safely. → Mod 02, Mod 09.

---

## 12. Partitioning vs bucketing

| | **Partitioning** | **Bucketing** |
|---|---|---|
| Best for | Pruning by a low-cardinality key (usually date) | Optimizing joins/aggregations on a high-cardinality key |
| Avoid when | High-cardinality key (→ tiny-file explosion) | You only filter, not join, on the key |

**Architect answer:** Partitioning is the single biggest lever on lake query cost — it lets the engine skip whole folders of data. But over-partitioning on a high-cardinality column creates millions of tiny files, which destroys performance (the small-files problem). Partition on date-like keys; bucket on high-cardinality join keys. Getting this layout right at the start saves you a painful re-write later. → Mod 02.

---

## 13. Serverless vs provisioned

| | **Serverless** | **Provisioned** |
|---|---|---|
| Best for | Spiky/unpredictable load, low ops, fast start | Steady high utilization, predictable cost at scale |
| Avoid when | Sustained near-full utilization (premium adds up) | Bursty/idle workloads (you pay for idle) |

**Architect answer:** The crossover is utilization. Serverless bills per-use with a per-unit premium and scales to zero; provisioned bills flat regardless of use. Below ~60–70% sustained utilization, serverless usually wins once you price in the engineer-hours you're *not* spending managing infrastructure. Above it, provisioned's lower per-unit cost wins. Model both with real numbers before committing a steady high-volume workload to serverless. → [Foundations architect-notes](./00-foundations/architect-notes.md).
