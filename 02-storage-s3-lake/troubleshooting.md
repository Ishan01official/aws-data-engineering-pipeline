# 02 · Troubleshooting

Storage-layer failures and fixes. See also the repo-wide [TROUBLESHOOTING-RUNBOOK](../TROUBLESHOOTING-RUNBOOK.md).

## Partition not showing in Athena
- **Cause:** the partition exists in S3 but not in the Glue Catalog.
- **Fix:** `MSCK REPAIR TABLE <table>` or `ALTER TABLE ... ADD PARTITION`, enable partition projection, or re-run the crawler.

## Athena query too slow / too expensive
- **Cause:** scanning unpartitioned or CSV data (billed per byte scanned).
- **Fix:** convert to partitioned Parquet; filter on partition columns; select only needed columns; check bytes-scanned in query stats; use CTAS to materialize hot subsets.

## Small-files problem (slow scans, high request cost)
- **Cause:** over-partitioning or many tiny streaming writes.
- **Fix:** coarser partition key; compact files (target ~128 MB–1 GB); buffer streaming (Firehose) before writing.

## Crawler infers wrong / inconsistent schema
- **Cause:** mixed formats in one prefix, or schemas differ across files.
- **Fix:** one format per prefix; consistent schemas; lay out partitions as `key=value`; consider defining the table manually.

## Schema drift breaks downstream
- **Cause:** upstream added/changed/removed a column.
- **Fix:** detect via crawler/Glue Data Quality; use Iceberg schema evolution or a schema registry; fail loudly on breaking changes rather than dropping data silently.

## `cdk destroy` won't remove a bucket
- **Cause:** bucket not empty (often old versions on a versioned bucket).
- **Fix:** `aws s3 rm s3://<bucket> --recursive`, then retry. (The lab stack sets `auto_delete_objects` to handle this.)

## AccessDenied writing to the lake
- **Cause:** role missing `s3:PutObject`, or a bucket/KMS policy blocking.
- **Fix:** grant the specific action on the specific prefix; check bucket policy and KMS key policy; if the table is Lake Formation-governed, grant LF permissions too.
