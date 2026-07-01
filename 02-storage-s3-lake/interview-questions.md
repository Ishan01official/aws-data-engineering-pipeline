# 02 · Interview Questions

Beginner → architect, with what a strong answer includes.

## Beginner
1. **What is S3 and why is it the base of a data lake?** Object store; cheap, durable, unlimited, decoupled from compute — so you keep one cheap copy and bring compute to it.
2. **Object vs block vs file storage?** Object = whole files by key via API (lakes); block = raw disk for DBs/OS; file = POSIX shared filesystem.
3. **What are raw/silver/gold zones?** Raw = immutable source of truth; silver = cleaned, partitioned Parquet; gold = business marts.

## Intermediate
4. **What does partitioning do and how do you choose the key?** Lets engines skip data (pruning); partition on low-cardinality columns you filter on (dates), never high-cardinality (order_id).
5. **Parquet vs CSV for analytics?** Columnar + compressed → scan only needed columns, far cheaper/faster; CSV is for ingestion/interchange.
6. **What's the small-files problem?** Many tiny files → per-file overhead dominates, slow and costly; caused by over-partitioning/streaming; fix by compacting and coarser partitions.
7. **Why version the raw bucket, and what's the catch?** Recover from bad writes/deletes; catch is old versions cost storage, so expire non-current versions via lifecycle.

## Advanced / Architect
8. **When does a Parquet lake become an Iceberg lakehouse?** When you need ACID upserts/`MERGE`, schema evolution, or time-travel — Iceberg is a table format over Parquet adding those; cost is tooling maturity.
9. **One bucket with prefixes vs many buckets?** Prefixes = simpler IAM surface, one lifecycle; separate buckets = clearer blast-radius isolation and per-dataset keys/policies. Start with prefixes, split out sensitive datasets.
10. **How do you keep a lake from becoming a swamp?** Governance: a catalog as the schema contract, enforced zones, data quality gates, partitioning discipline, and lineage — the storage layout alone isn't enough.
11. **Design the storage layer for a retailer ingesting batch files and clickstream.** Raw zone with `source=/entity=/ingestion_date=` partitions; batch lands directly, clickstream via Firehose (buffered to avoid small files); convert to partitioned Parquet in silver; aggregate to gold; Glue Catalog as metadata; Athena for ad-hoc, Redshift for hot marts. Justify each with cost/latency.
