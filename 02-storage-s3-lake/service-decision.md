# 02 · Service & Design Decisions for the Storage Layer

The storage layer forces a handful of decisions that are hard to change later. This page gives the short answers; the full nine-field comparisons (cost / performance / operations / security / architect / interview) live in the repo-wide [SERVICE-DECISION-FRAMEWORK](../SERVICE-DECISION-FRAMEWORK.md#s3-data-lake-design-decisions).

## The decisions, in the order you'll face them

### 1. S3 data lake vs Redshift warehouse (or both)
**Short answer:** default the source of truth to S3; add Redshift when repeated, concurrent, low-latency BI justifies a serving layer. Storage in S3 is ~10× cheaper than warehouse-coupled storage; compute comes to the data (Athena/Glue/Spectrum). → [full comparison](../SERVICE-DECISION-FRAMEWORK.md#5-s3-data-lake-vs-redshift-warehouse-vs-lakehouse)

### 2. CSV vs JSON vs Parquet vs Iceberg
**Short answer:** land what the source sends (CSV/JSON) in raw; standardize silver/gold on Parquet; adopt Iceberg *on top of* Parquet when you need `MERGE`/upserts, schema evolution, or time-travel. → [full comparison](../SERVICE-DECISION-FRAMEWORK.md#11-parquet-vs-csv-vs-json-vs-iceberg)

### 3. One bucket vs multiple buckets
**Short answer:** this repo uses bucket-per-zone: clear blast-radius, per-zone lifecycle and (later) per-zone keys, simple mental model. Prefix-per-zone in one bucket also works and simplifies name management; split sensitive datasets out regardless. → [full comparison](../SERVICE-DECISION-FRAMEWORK.md#s3-1-one-bucket-vs-multiple-buckets)

### 4. raw/bronze/silver/gold vs raw/trusted/curated (zone naming)
**Short answer:** the names don't matter; the *contracts* do — an immutable landing zone, a cleaned/validated zone, a business-ready zone. Pick one vocabulary, define each zone's contract in writing, and never let a zone serve two purposes. → [full comparison](../SERVICE-DECISION-FRAMEWORK.md#s3-2-rawbronzesilvergold-vs-rawtrustedcurated)

### 5. Partitioning: by date vs entity vs region
**Short answer:** partition by what queries filter on — for this repo, `source=` / `entity=` / `ingestion_date=`. Date is almost always the innermost key; add region/tenant only when queries genuinely slice on it. → [full comparison](../SERVICE-DECISION-FRAMEWORK.md#s3-3-partitioning-by-date-vs-entity-vs-region)

### 6. Event-driven vs scheduled ingestion
**Short answer:** event-driven (S3 event → pipeline) for freshness and pay-per-occurrence; scheduled for predictable batch boundaries and "is everything in?" semantics. Most platforms use both: event-driven landing, scheduled consolidation. → [full comparison](../SERVICE-DECISION-FRAMEWORK.md#s3-4-event-driven-vs-scheduled-ingestion)

### 7. Lifecycle policies vs manual cleanup
**Short answer:** lifecycle, always — declared in IaC, reviewed like code. Manual cleanup does not happen, and when it does happen it deletes the wrong thing. → [full comparison](../SERVICE-DECISION-FRAMEWORK.md#s3-5-lifecycle-policy-vs-manual-cleanup)

## How to argue these in a design review

For any storage decision, walk the same five axes the [Foundations framework](../00-foundations/) established: **latency** (who waits on this data?), **volume** (GB or PB?), **structure** (fixed schema or drifting?), **cost model** (storage vs scan vs request), **ops burden** (who maintains it at 3am?). A decision justified on all five axes survives; a decision justified by "it's what I know" doesn't.
