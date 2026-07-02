# Industry Use Cases

The same AWS building blocks, arranged differently per industry. For each: data sources, the pipeline pattern, key services, batch/streaming balance, security concerns, cost concerns, and a sketch architecture. Use these to ground abstract services in real problems.

## Retail / E-commerce
- **Sources:** POS/sales (CSV/DB), product & inventory (RDS), clickstream (events), SaaS marketing (AppFlow).
- **Pattern:** medallion lakehouse — raw → cleaned → marts — feeding BI and recommendations.
- **Services:** S3, DMS, Kinesis Firehose, Glue, Athena, Redshift, Lake Formation.
- **Batch/streaming:** mostly batch (daily/hourly sales marts) with streaming clickstream for near-real-time behavior.
- **Security:** customer PII (Lake Formation column access, Macie). **Cost:** clickstream volume — partition aggressively, Parquet.
- This is the repo's **capstone** ([project 07](./projects/project-07-enterprise-data-platform/)).

## Banking / Finance
- **Sources:** transactions (CDC from core banking), market data feeds, customer data.
- **Pattern:** CDC ingestion + strict governance; often a regulated warehouse layer.
- **Services:** DMS, Kinesis/MSK, Glue, Redshift, Lake Formation, KMS (customer-managed keys), CloudTrail.
- **Batch/streaming:** streaming for fraud detection (millisecond decisions); batch for regulatory reporting.
- **Security:** the dominant concern — encryption everywhere, row/column security, immutable audit, data residency. **Cost:** secondary to compliance.

## Healthcare
- **Sources:** EHR systems, device telemetry, claims.
- **Pattern:** highly governed lake with strict PII/PHI controls; lineage and audit are first-class.
- **Services:** S3, Glue, Lake Formation, Macie, KMS, CloudTrail.
- **Batch/streaming:** batch for claims/analytics; streaming for device/patient monitoring.
- **Security:** PHI handling, HIPAA alignment, minimum-necessary access, encryption and masking. **Cost:** retention of large imaging/telemetry → lifecycle tiering.

## Manufacturing / IoT
- **Sources:** sensor/telemetry streams, MES/ERP, maintenance logs.
- **Pattern:** high-volume streaming ingest → time-series storage → anomaly detection.
- **Services:** IoT Core/Kinesis/MSK, Managed Flink, S3, Timestream/Redshift.
- **Batch/streaming:** streaming-heavy (real-time equipment monitoring) plus batch trend analysis.
- **Security:** device identity, network isolation. **Cost:** raw telemetry volume — aggregate early, tier aggressively.

## SaaS / Product Analytics
- **Sources:** app events, billing, support, third-party SaaS.
- **Pattern:** event pipeline → warehouse → product/usage analytics; often ELT.
- **Services:** Kinesis/Firehose, S3, Glue, Redshift/Athena, AppFlow.
- **Batch/streaming:** event streaming to S3, batch transforms to marts.
- **Security:** tenant isolation, customer data segregation. **Cost:** event volume and warehouse compute — model the hot marts.

## Media / Entertainment
- **Sources:** playback/streaming events, content metadata, ad telemetry.
- **Pattern:** massive clickstream → real-time engagement + batch content analytics.
- **Services:** Kinesis, Flink, S3, Redshift, OpenSearch (search/recommendations).
- **Batch/streaming:** streaming engagement metrics, batch content performance.
- **Security:** content rights, viewer privacy. **Cost:** enormous event volume — this is where partitioning/columnar discipline pays most.

## Finance Analytics (buy/sell-side)
- **Sources:** market data, positions, risk feeds.
- **Pattern:** low-latency ingest + heavy compute (risk/analytics) + governed warehouse.
- **Services:** MSK/Kinesis, EMR (heavy Spark), Redshift, Lake Formation.
- **Batch/streaming:** both — streaming market data, batch overnight risk.
- **Security:** strict access and audit. **Cost:** EMR compute — right-size and use Spot/Serverless.

> The lesson across all of these: the *services* are a small, stable toolkit. The *arrangement* — driven by latency needs, data volume, and regulatory weight — is the engineering. That's what the [Service Decision Framework](./SERVICE-DECISION-FRAMEWORK.md) trains.

---

# S3 data lake deep dives

Five industries, the same S3 machinery from [Module 02](./02-storage-s3-lake/), arranged around each industry's dominant constraint. Each dive covers: sources, the four zones, partition strategy, the security and cost concerns that dominate, a realistic failure, and the architect's note.

## Retail sales (this repo's running scenario)

- **Data sources:** nightly order/customer/product extracts from the e-commerce platform and store POS systems; clickstream events via Firehose; marketing SaaS exports.
- **Raw zone:** files exactly as received at `raw/source=<system>/entity=<entity>/ingestion_date=<d>/`. POS CSVs, clickstream JSON batches. Immutable; versioned; tiers to IA/Glacier.
- **Bronze zone:** typed copies — headers normalized, columns cast, obviously corrupt rows tagged (not dropped). Still row-per-source-record.
- **Silver zone:** deduplicated (order retries happen), validated (quantity > 0, referential checks against customers/products), Parquet partitioned by `order_date`. The zone analysts query.
- **Gold zone:** daily sales by category/country/segment marts; customer-lifetime aggregates. Loaded to Redshift for dashboards.
- **Partition strategy:** `source=/entity=/ingestion_date=` in raw (reprocessing unit = source-day); `order_date=` in silver/gold (query unit = business day).
- **Security concern:** customer PII (emails) — restrict silver customer columns via Lake Formation; marketing gets segments, not emails.
- **Cost concern:** clickstream volume dwarfs transactional data; Firehose buffering to ≥64 MB files and aggressive raw tiering keep it sane.
- **Failure example:** the POS vendor re-sent a whole week of files after "an incident" — with the same filenames. Deterministic keys meant overwrites, versioning kept the originals, and a diff of versions showed 3 changed files; only those partitions were reprocessed. Without deterministic naming this becomes a week of double-counted revenue.
- **Architect note:** retail's dominant constraint is *trustworthy daily numbers* — invest in the silver quality gates and reconciliation against the source-of-truth financial system, not in shaving latency nobody asked for.

## Banking transactions

- **Data sources:** CDC stream from the core banking DB (DMS), card-network settlement files, market data feeds, KYC systems.
- **Raw zone:** CDC change files and settlement files as received, `raw/source=corebank/entity=transactions/ingestion_date=`; **Object Lock/immutability** where regulation demands WORM retention.
- **Bronze zone:** CDC events resolved to typed change records (insert/update/delete with ordering metadata).
- **Silver zone:** current-state account/transaction tables built by applying CDC (Iceberg `MERGE` is the natural fit), partitioned by `txn_date`; full change history preserved separately for audit.
- **Gold zone:** regulatory reports, risk aggregates, fraud-feature tables — each with a documented owner and SLA.
- **Partition strategy:** `txn_date=` innermost; `source_system=` above it (banks always have multiple core systems mid-migration).
- **Security concern:** the dominant axis — SSE-KMS with customer-managed keys per sensitivity class, CloudTrail data events on everything, Lake Formation row/column controls, and a provable "who could and who did read X" answer at all times.
- **Cost concern:** secondary to compliance, but 7–10 year retention makes Glacier Deep Archive for aged raw a large saving.
- **Failure example:** an out-of-order CDC apply (updates processed before the insert arrived) produced negative balances in silver. Fix: order by LSN/commit timestamp within the merge, and a reconciliation check (sum of silver balances vs source ledger) that blocks gold publication on mismatch.
- **Architect note:** in banking the lake is evidence. Design for the auditor as a first-class consumer: immutable raw, replayable transforms, lineage, and reconciliation — the analytics are almost the easy part.

## Healthcare claims

- **Data sources:** claims batches from clearinghouses (X12/837 or CSV extracts), provider/member masters, adjudication system extracts.
- **Raw zone:** claims files as received under `raw/source=clearinghouse/entity=claims/ingestion_date=`; PHI from the first byte, so the raw bucket itself is KMS-encrypted with a PHI key and access is a short allowlist.
- **Bronze zone:** parsed claim records, typed; member identifiers still present.
- **Silver zone:** validated claims joined to member/provider dimensions; **two variants** commonly exist — an identified silver (restricted, for care/fraud teams) and a de-identified silver (broader analytics), produced by masking/tokenizing member fields.
- **Gold zone:** cost-per-condition, utilization, denial-rate marts on de-identified data.
- **Partition strategy:** `service_date=` (what analysts filter on) rather than ingestion date in silver; raw keeps `ingestion_date=` for replay.
- **Security concern:** PHI everywhere — minimum-necessary access, separate KMS keys for identified vs de-identified zones, Macie scans for PHI leaking into the wrong zone, audit-grade logging.
- **Cost concern:** claims history is kept for many years; imaging/attachments (if present) dominate bytes — lifecycle to Deep Archive and keep only pointers hot.
- **Failure example:** a "de-identified" gold table turned out to include a rare-condition + ZIP + age combination that re-identified patients. Prevention is a governance review of *quasi-identifiers*, not just direct identifiers — a policy/architecture failure, not a pipeline bug.
- **Architect note:** healthcare's constraint is confidentiality with *provable process*. The identified/de-identified zone split — with different keys, roles, and audit — is the architecture; get it wrong and no amount of pipeline quality matters.

## IoT sensor events

- **Data sources:** millions of devices publishing telemetry (temperature, vibration, status) via IoT Core/Kinesis; device registry; maintenance logs.
- **Raw zone:** Firehose-delivered batches `raw/source=iot/entity=telemetry/event_date=.../hour=...` — hour partitions are justified here by volume and by queries that genuinely slice by hour.
- **Bronze zone:** decoded/validated readings (unit normalization, dead-sensor flags).
- **Silver zone:** cleaned time-series in Parquet, partitioned `site=/event_date=`; late-arriving data (devices reconnecting after network gaps) upserted by event time.
- **Gold zone:** per-device daily health aggregates, anomaly features, downtime KPIs.
- **Partition strategy:** `site=` (low cardinality, matches both queries and access boundaries) then `event_date=`; **never** `device_id=` (cardinality in the millions — the canonical over-partitioning mistake).
- **Security concern:** device identity/spoofing at ingest; site-level access separation (plant A can't read plant B).
- **Cost concern:** the dominant axis — raw telemetry is enormous and mostly never re-read. Aggregate early, compress hard (zstd), tier raw to Glacier in weeks, expire it when the retention policy allows, and keep only aggregates hot.
- **Failure example:** a firmware bug made 5% of devices re-send 48h of history every hour. Volume tripled, small files exploded, and the bill followed. Caught by an object-count anomaly alarm from S3 Inventory trends; fixed with ingest-side dedupe on (device_id, reading_ts) and a quota per device.
- **Architect note:** IoT lakes live or die on *write-path discipline* — buffering, dedupe, early aggregation. Every byte you don't need but store anyway is multiplied by a million devices and 365 days.

## SaaS product analytics

- **Data sources:** in-app event stream (SDK → Kinesis/Firehose), billing system exports, support-ticket exports, CRM sync.
- **Raw zone:** event batches at `raw/source=app/entity=events/event_date=`; billing/CRM extracts as daily files.
- **Bronze zone:** schema-validated events (the event taxonomy is a *contract* — unknown event names are quarantined, not silently stored).
- **Silver zone:** sessionized, enriched events (user → account join), Parquet by `event_date=`; **tenant_id is a column, not a partition** — cardinality is far too high to partition by.
- **Gold zone:** activation/retention/feature-adoption marts; per-account usage for billing; churn-model features.
- **Partition strategy:** `event_date=` only, plus `entity=` at raw. Tenant isolation is enforced by query/row-level controls, not physical layout — until a contract demands physical isolation (enterprise single-tenant), at which point that tenant gets its own prefix or bucket.
- **Security concern:** tenant data segregation — a leak *between customers* is existential for a SaaS. Row-level security in the serving layer, careful join logic, and tests that assert cross-tenant leakage is impossible.
- **Cost concern:** event volume grows with product success; warehouse compute for marts is the other big line — model the hot marts, query the rest in place with Athena.
- **Failure example:** an SDK release renamed `page_view` to `pageView`. Half the events "disappeared" from dashboards while landing fine in raw. The schema-contract gate in bronze caught it as unknown-event quarantine within an hour; without it, weeks of product decisions run on halved numbers.
- **Architect note:** the event taxonomy is the real asset — version it, validate at the gate, and keep raw replayable so taxonomy mistakes are recoverable. Physical architecture here is mostly standard; the differentiation is contract discipline.
