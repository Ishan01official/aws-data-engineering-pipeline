# 02 · Monitoring the Storage Layer

Storage "just works" — until data stops arriving, small files explode, or the bill doubles. Monitoring a lake means watching four things: **arrival, growth, access, and cost.**

## 1. Did the data arrive? (freshness — the one that pages people)

The most important lake alarm has nothing to do with S3 health and everything to do with *your* data contract:

- **Object-count / row-count metric per entity per day.** After each load (or on a schedule), publish a custom CloudWatch metric like `RetailLake/SilverOrdersRowCount` with an `IngestionDate` dimension; alarm when it's 0 or below a floor.
- **Event-driven heartbeat:** an EventBridge rule on `Object Created` for the expected prefix feeding a "last arrival" timestamp; a scheduled check alarms if no file arrived by the SLA time (e.g. 06:00 UTC).
- This repo's [`scripts/validate_s3_layout.py`](../scripts/validate_s3_layout.py) is the same check in CLI form — it exits non-zero when expected objects are missing, so a scheduler can alert on it.

## 2. Is the lake growing sanely? (structure)

- **S3 Storage Lens** — free default dashboard across all buckets: total bytes, object counts, growth trends, non-current version bytes. The advanced tier adds prefix-level detail. This is where you notice "the raw bucket doubled this month" or "40% of our storage is old versions."
- **S3 Inventory** — daily/weekly manifest of every object (key, size, storage class, encryption), delivered as Parquet and queryable in Athena. The tool for small-file audits:

```sql
-- Athena over an S3 Inventory table: find partitions full of tiny files
SELECT substr(key, 1, 60) AS prefix,
       count(*) AS objects,
       avg(size) / 1048576.0 AS avg_mb
FROM lake_inventory
WHERE key LIKE 'silver/%'
GROUP BY 1
HAVING count(*) > 100 AND avg(size) < 16 * 1048576
ORDER BY objects DESC;
```

- **CloudWatch S3 metrics** — free daily `BucketSizeBytes` and `NumberOfObjects` per bucket; request metrics (per-prefix, paid opt-in) when you need request-rate visibility.

## 3. Who is touching it? (access)

- **S3 server access logs** → a logging bucket, for cheap traffic analysis (top keys, top callers, 4xx patterns).
- **CloudTrail data events** on sensitive prefixes for compliance-grade "who read what" ([Module 01 · cloudwatch.md](../01-aws-core-services/cloudwatch.md)) — scoped, because lake-wide data events cost real money.
- **EventBridge rule on `PutBucketPolicy` / ACL changes** → immediate alert. Nobody should be editing lake bucket policies by hand.

## 4. What does it cost? (spend)

- **Budget alarm** on the account (non-negotiable before any lab).
- **Cost Explorer grouped by the `zone` tag** — the stack tags every bucket, so raw/silver/gold spend is separable.
- Watch two sneaky lines: `TimedStorage-*` for non-current versions (fix: lifecycle) and request charges (fix: small files, misbehaving pollers).

## The minimum alarm set for this repo's lake

| Alarm | Signal | Why |
|---|---|---|
| `orders-freshness` | Expected daily object missing by SLA time | Source outage / broken ingestion |
| `silver-rowcount-floor` | Custom row-count metric < floor | "Succeeded but empty" runs |
| `bucket-policy-changed` | CloudTrail event via EventBridge | Security drift |
| `noncurrent-bytes-growth` | Storage Lens / Inventory trend review (weekly, human) | Version bloat |
| Budget alarm | Account spend > threshold | Everything else |

## Runbook links

Missing data → [Athena cannot find data / S3 upload failed runbooks](../TROUBLESHOOTING-RUNBOOK.md). Small files → same runbook. Access anomaly → [SECURITY-GOVERNANCE](../SECURITY-GOVERNANCE.md).

---
*Deep dive on the observability services themselves: [Module 01 · cloudwatch.md](../01-aws-core-services/cloudwatch.md). Pipeline-level (job) monitoring: Module 11.*
