# 02 · Certification Notes — DEA-C01 Domain 2 (Data Store Management)

Domain 2 is ~26% of the exam, and S3-lake design is its core. This page maps the module to what the exam actually probes. Practice questions for this material: [CERTIFICATION-MAPPING](../CERTIFICATION-MAPPING.md#domain-2--data-store-management-26).

## Facts the exam expects you to know cold

- **Athena bills per byte scanned** → partitioning + columnar formats are the cost/performance answer to almost every "queries are slow/expensive" scenario.
- **Hive-style `key=value` prefixes** are how Glue crawlers and Athena auto-discover partition columns.
- **Partition pruning** requires filtering on the partition column; `WHERE date_col = X` on a non-partition column prunes nothing.
- **Small-files problem:** many tiny files degrade scans; fixes are coarser partitioning, compaction, and buffered streaming writes (Firehose buffering exists precisely for this).
- **Storage classes:** Standard → Standard-IA (30d min) → Glacier tiers; Intelligent-Tiering when access patterns are unknown; lifecycle rules automate transitions and expirations.
- **Versioning** protects against overwrite/delete; non-current versions cost storage until expired by lifecycle.
- **Encryption:** SSE-S3 vs SSE-KMS (audit + separate `kms:Decrypt` permission) vs client-side; bucket keys cut KMS request cost.
- **`MSCK REPAIR TABLE` / `ALTER TABLE ADD PARTITION` / partition projection** — the three answers to "data is in S3 but Athena can't see the new partition."
- **Parquet vs ORC vs CSV/JSON**: columnar for analytics; **Iceberg** adds ACID/`MERGE`/schema evolution/time-travel on top.

## Scenario patterns that recur

| Scenario smell | Expected answer |
|---|---|
| "Costs too much to query, always filters by date" | Convert to Parquet, partition by date |
| "New data not visible in Athena" | Add/repair partitions or partition projection |
| "Millions of small JSON files from a stream" | Firehose buffering / compaction job |
| "Must recover from accidental overwrite" | Versioning (+ lifecycle for cost) |
| "Reduce storage cost for rarely-read data" | Lifecycle to IA/Glacier; Intelligent-Tiering if unknown |
| "Need upserts/row-level updates on the lake" | Iceberg table format |
| "Unknown access pattern, avoid retrieval fees" | S3 Intelligent-Tiering |

## Traps

- Choosing **Glacier** for data with a compliance *query* requirement (retrieval latency).
- Partitioning on high-cardinality keys because "more partitions = faster."
- Confusing **bucketing** (join optimization on high-cardinality keys) with **partitioning** (pruning on low-cardinality keys).
- Assuming versioning is free.
- SSE-KMS scenarios where the missing piece is `kms:Decrypt`, not an S3 permission.

## Hands-on the exam assumes you've done

Exactly what [Lab 01](../labs/lab-01-s3-data-lake/) does: create zoned buckets with lifecycle/versioning/encryption, land Hive-partitioned data, and validate it — then Labs 02–04 (crawl, transform to Parquet, query and watch bytes-scanned drop). If you've run those, this domain is earned rather than memorized.
