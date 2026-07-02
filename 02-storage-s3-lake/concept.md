# 02 · Concept — First Principles

## What S3 is

Amazon S3 (Simple Storage Service) is an **object store**: you put and get whole objects (files) identified by a key (a string that looks like a path), inside a bucket. It is not a filesystem and not a database. Objects are immutable in place — you replace an object by overwriting the whole thing. S3 is designed for extreme durability (many nines) and effectively unlimited scale, and it's cheap: roughly **$0.023 per GB-month** for standard storage.

That combination — cheap, durable, unlimited, decoupled from compute — is *why* S3 is the foundation of AWS data lakes.

## Why S3 is the foundation of AWS data lakes

The central economic fact of modern data architecture: **storage is cheap, compute is expensive, and they should be decoupled.** Old data warehouses bundled storage and compute, so storing more data forced you to pay for more compute. S3 breaks that coupling — you keep one cheap copy of all your data in S3 and point whatever compute you need at it (Athena, Glue, EMR, Redshift Spectrum), scaling compute independently and paying only when you run it.

Everything else in this module is discipline layered on top of that idea, to keep the cheap storage from becoming an unusable swamp.

## Object vs file vs block storage

| | **Object (S3)** | **File (EFS/NFS)** | **Block (EBS)** |
|---|---|---|---|
| Unit | Whole object + metadata, by key | Files in a directory tree | Raw blocks on a volume |
| Access | HTTP API (get/put whole object) | POSIX filesystem | Attached to one instance as a disk |
| Scale | Effectively unlimited | High | Volume-sized |
| Best for | Data lakes, backups, big analytics data | Shared app filesystems | Databases, OS disks |
| Update in place | No (replace object) | Yes | Yes |

Data lakes use **object storage** because analytics reads large objects in bulk, scales horizontally, and doesn't need POSIX semantics or per-block updates. The lack of in-place update is a feature here: it pushes you toward immutable raw data and versioned, replayable pipelines.

## Data lake zones: raw / bronze / silver / gold

The **medallion architecture** layers the lake so each zone has one job:

- **Raw / Bronze** — data exactly as received, immutable. The source of truth. If a downstream job has a bug, you re-run from raw. Never edit it.
- **Silver** — cleaned, validated, deduplicated, typed. Stored as partitioned Parquet. This is what most analytics actually reads.
- **Gold** — business-ready aggregates and marts (e.g. daily sales by region). What BI tools and Redshift consume.

Why layer instead of one bucket? Separation of concerns (each zone optimized for its purpose), replayability (raw is untouched), and cost/format optimization (raw can be cheap cold CSV; silver is query-optimized Parquet).

> In simple lakes, **raw and bronze are the same thing**. Splitting them (raw = literal received bytes; bronze = lightly typed/cleaned) is a choice you make when sources are messy enough to want a clean replay boundary.

## Partitioning

Partitioning physically organizes data into folders by a key so query engines can **skip** irrelevant data. Using Hive-style `key=value` folders:

```
silver/entity=orders/order_date=2026-07-01/part-0001.parquet
silver/entity=orders/order_date=2026-07-02/part-0001.parquet
```

A query `WHERE order_date = '2026-07-01'` reads only the first folder — **partition pruning**. Since Athena bills per byte scanned, this is the single biggest lever on lake query cost and speed.

Rules of thumb:
- Partition on **low-cardinality keys you filter on** — dates are the canonical choice.
- Don't partition on high-cardinality keys (like `order_id`) — see the small-files problem.

## The small-files problem

Query engines have per-file overhead (open, read metadata, close). Thousands of tiny files are dramatically slower and more expensive to scan than a few right-sized ones, even for the same total bytes. You get tiny files by **over-partitioning** (too granular a partition key) or by streaming many small writes without compaction.

Fixes: partition coarsely enough that each partition holds reasonably sized files (target ~128 MB–1 GB per file for analytics); compact small files periodically; in streaming, buffer before writing (Firehose does this).

## File formats: CSV, JSON, Parquet, Iceberg

| Format | Kind | Use for | Avoid for |
|---|---|---|---|
| **CSV** | Row, text | Ingestion, interchange, human-readable | Analytics at scale (slow, no schema) |
| **JSON** | Row, nested text | APIs, semi-structured/nested data | Large-scale scans (slow to parse) |
| **Parquet** | Columnar, binary | Analytics — scan few columns, great compression | Row-by-row/OLTP access |
| **Iceberg** | Table format over Parquet | Lake tables needing ACID, schema evolution, time-travel, upserts | Trivial append-only data with no update needs |

The progression of a mature lake: land **CSV/JSON** in raw → convert to **Parquet** in silver (columnar + compressed slashes scan cost) → optionally manage silver/gold as **Iceberg** tables when you need safe `MERGE`/upserts, schema evolution, and time-travel. Iceberg isn't a competitor to Parquet — it's a metadata layer *over* Parquet files that turns a pile of files into a real table.

## S3 lifecycle policies

Rules that automatically transition or expire objects by age: e.g. move raw data to Infrequent Access after 30 days, Glacier after 90, and expire Athena query results after 14. This matches storage cost to access patterns without manual work. → [cost.md](./cost.md)

## S3 versioning

Keeps previous versions of an object when overwritten or deleted, so you can recover from bad writes or accidental deletes. Essential for the raw source-of-truth bucket. Trade-off: old versions accumulate storage cost, so pair versioning with a lifecycle rule that expires non-current versions.

## S3 encryption

At rest: **SSE-S3** (S3-managed keys, simplest) or **SSE-KMS** (KMS keys, adds audit and access control over the key). In transit: TLS (enforce with `enforce_ssl`). Regulated data uses SSE-KMS with customer-managed keys. → [security.md](./security.md), Module 08.

## S3 event notifications

S3 can emit an event when an object is created/deleted, delivered to Lambda, SNS, SQS, or EventBridge. This is the trigger mechanism for event-driven pipelines — e.g. "when a file lands in raw, invoke a validation Lambda." → Module 03.

## Data lake cost design

The levers, in order of impact: (1) columnar + partitioned format to cut scan cost, (2) lifecycle tiering to cut storage cost, (3) expiring old versions and query results, (4) avoiding the small-files tax. → [cost.md](./cost.md)

## Production mistakes

Treating raw as mutable; over-partitioning into tiny files; leaving data as CSV and paying scan cost forever; unpartitioned Athena `SELECT *`; forgetting to expire non-current versions on a versioned bucket; making a bucket public. → [troubleshooting.md](./troubleshooting.md), [mistakes-to-avoid.md](./mistakes-to-avoid.md)

## Architect-level decisions

- **Zone count and whether bronze ≠ raw** — governed by source messiness and replay needs.
- **Partition granularity** — daily vs hourly, trading query latency against file count.
- **One bucket with `source=`/`entity=` prefixes vs many buckets** — simplicity vs blast-radius isolation.
- **Plain Parquet lake vs Iceberg lakehouse** — reach for Iceberg when you need ACID upserts, schema evolution, or time-travel; the cost is added tooling maturity. → Module 09.

## File naming strategy

Objects inside a partition should follow a deterministic, sortable convention:

```
<entity>_<YYYY_MM_DD>[_<part-number>][_<run-id>].<ext>
orders_2026_07_01.csv                      # single daily extract
orders_2026_07_01_part-0003.parquet        # one of N parts
```

Rules that pay off later:
- **Deterministic names for deterministic data.** A re-run of the same day produces the same key and *overwrites* — that is what makes re-runs idempotent instead of duplicating data.
- **Embed the date in the filename too**, not just the prefix. Files get downloaded, moved, and attached to tickets; a file named `data.csv` is anonymous the moment it leaves S3.
- **No spaces, no uppercase surprises, no special characters.** Keys are case-sensitive; URL-encoding bites tools.
- **Never encode secrets or PII in keys.** Keys appear in logs, inventories, and access logs everywhere.
- Streaming writers (Firehose) add timestamps/IDs automatically — that's fine, because streaming data is append-only; determinism matters for *re-runnable batch* writes.

## Compression

Compression cuts storage cost *and* scan cost (Athena bills on compressed bytes read).

| Codec | Traits | Use |
|---|---|---|
| **Snappy** | Fast, moderate ratio, splittable inside Parquet | Default inside Parquet/ORC |
| **gzip** | Better ratio, slower, **not splittable** as a bare .csv.gz | Raw text file transfer; small files |
| **zstd** | Better ratio than gzip at near-Snappy speed | Modern default where supported |
| none | — | Only tiny files or already-compressed media |

The trap: one giant `.csv.gz` file cannot be split, so one Spark task decompresses it alone — a 10 GB gzip file serializes your whole cluster. Parquet avoids this: compression is applied per column chunk internally, so files stay splittable. Practical rule: **raw zone = whatever the source sends (often gzip CSV); silver/gold = Parquet with Snappy or zstd.**

## S3 inventory and access logs

Two built-in features that answer questions a lake operator asks constantly:

- **S3 Inventory** — a scheduled (daily/weekly) manifest of every object in a bucket: key, size, storage class, encryption status, version info — delivered as Parquet/CSV to a bucket you choose, queryable with Athena. Use it for: finding small-file explosions, auditing encryption coverage, reconciling object counts against expectations, and lifecycle planning. Listing a billion-object bucket with `ListObjects` is slow and costs per request; Inventory is the scalable answer.
- **S3 server access logs** (or CloudTrail data events) — per-request logs: who requested which key, when, from where, with what result. Access logs are cheap and delivered to a bucket (best-effort); CloudTrail data events are structured and integrate with EventBridge but cost per event. Use access logs for traffic analysis, CloudTrail for compliance-grade audit.

## Data lake anti-patterns

The failure modes that turn a lake into a swamp — each is expanded in [mistakes-to-avoid.md](./mistakes-to-avoid.md):

1. **The dumping ground** — data lands with no zones, no naming convention, no catalog entry, no owner. Six months later nobody can say what's trustworthy.
2. **The mutable raw zone** — jobs "fix" raw data in place; replays now produce different answers than the original run and lineage is fiction.
3. **CSV forever** — analytics runs on raw CSV for years because conversion "never made the sprint." Every query pays full scan cost.
4. **Partition-by-everything** — five levels of partitioning to make queries "fast," producing millions of empty/tiny partitions that make everything slow.
5. **The single god-bucket with `s3:*` roles** — no blast-radius isolation; any job can destroy anything.
6. **Catalog drift** — tables exist in S3 but not the catalog, or catalog schemas no longer match files. The catalog must be the enforced contract, not a suggestion.
7. **No lifecycle discipline** — versioned buckets accumulating years of non-current versions and Athena results nobody expires.
