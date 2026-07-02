# 02 · Mistakes to Avoid

The storage-layer mistakes that show up in real platforms, why they happen, and what to do instead. Each one is cheap to prevent and expensive to unwind.

## 1. Treating the raw zone as mutable

**What happens:** a job finds bad rows in raw and "fixes" them in place, or an engineer deletes "obviously wrong" files.
**Why it's fatal:** raw is the replay boundary. Once raw is edited, re-running the pipeline gives different answers than the original run, lineage stops being trustworthy, and debugging "what did we actually receive?" becomes impossible.
**Instead:** raw is append-only. Fixes happen in bronze/silver transforms. Enforce it with IAM — no pipeline role gets `s3:DeleteObject` on raw ([Module 01 · iam.md](../01-aws-core-services/iam.md)).

## 2. Partitioning on a high-cardinality key

**What happens:** someone partitions by `order_id` or `customer_id` "so lookups are fast."
**Why it's fatal:** millions of folders each holding one tiny file — the small-files problem. Scans slow to a crawl; the catalog balloons; list operations cost real money.
**Instead:** partition on low-cardinality columns you filter by (dates, source, entity). Target ~128 MB–1 GB per file. High-cardinality lookup needs are a sign the data belongs (also) in a database, or should be bucketed, not partitioned.

## 3. Leaving analytics data as CSV/JSON

**What happens:** "we'll convert to Parquet later" — and later never comes because queries *work*, just slowly.
**Why it costs:** Athena bills per byte scanned. Row formats scan every column of every row. Teams routinely cut 90%+ of query cost with one conversion job.
**Instead:** the first transform out of raw writes partitioned, compressed Parquet. Make it part of the pipeline's definition of done, not a backlog item.

## 4. Ignoring versioning's storage bill

**What happens:** versioning is enabled (correctly!) on source-of-truth buckets, and every overwrite quietly keeps the old version forever.
**Instead:** pair versioning with a lifecycle rule expiring non-current versions (the Lab 01 stack does 30–90 days). Check with S3 Storage Lens or Inventory — non-current bytes are invisible in a casual `aws s3 ls`.

## 5. One god-bucket, one god-role

**What happens:** everything lands in one bucket, and every job uses a shared role with `s3:*`.
**Why it's fatal:** any bug can destroy anything; audits can't attribute access; you can't give one dataset stricter treatment (KMS key, retention) than another.
**Instead:** zone-per-bucket (this repo's layout) or at minimum prefix-scoped roles; one role per job; sensitive datasets get their own bucket/key when compliance asks.

## 6. Uploading without a key contract

**What happens:** each ingestion script invents its own path: `data/orders-final-v2/july/`.
**Why it's fatal:** crawlers can't infer partitions, Athena can't prune, nobody can find anything, and "where does entity X land for date Y" requires reading source code.
**Instead:** one shared key-building function used by every producer — in this repo that's [`scripts/lake_layout.py`](../scripts/lake_layout.py), enforced by tests. The layout is an API; treat it like one.

## 7. Skipping the empty/zero-row check

**What happens:** the daily extract arrives *empty* (source outage), the pipeline "succeeds," dashboards silently show zeros.
**Instead:** validation on arrival (file size > 0, row count within expected band) and a freshness/volume metric with a floor alarm ([Module 01 · cloudwatch.md](../01-aws-core-services/cloudwatch.md)).

## 8. Testing lifecycle rules in production

**What happens:** a lifecycle rule written as "expire after 1 day" (meant: transition), or applied to the wrong prefix, deletes current data.
**Instead:** lifecycle rules go through IaC review like code; prefer transitions over expirations on source-of-truth buckets; test on a scratch bucket; remember versioned buckets soft-delete (delete markers) — recovery is possible *if* you notice before non-current expiry.

## 9. Making "just this one bucket" public

There is no data-lake reason for a public bucket. The stack sets `BLOCK_ALL` and every account should set account-level Block Public Access too. Sharing data externally has proper answers: presigned URLs, cross-account roles, S3 Access Points.

## 10. No catalog discipline

**What happens:** data exists that no Glue table describes, or the table schema is three versions behind the files.
**Instead:** every dataset that matters has a catalog entry, created by crawler or (better, for stable schemas) defined in IaC; schema changes are deliberate events, not surprises discovered by broken queries (Module 04, Lab 02).

---
*The compact version of this list lives in [concept.md → Data lake anti-patterns](./concept.md#data-lake-anti-patterns); runbooks for when you hit them anyway: [TROUBLESHOOTING-RUNBOOK](../TROUBLESHOOTING-RUNBOOK.md).*
