# Troubleshooting Runbook

Symptom → likely cause → fix, for the failures you'll actually hit. Each entry is written to be scannable at 3am. Module-specific debugging lives in each module's `troubleshooting.md`.

> General method for any AWS data failure: **(1)** find the authoritative log (CloudWatch log group for the service), **(2)** read the actual error, not the summary, **(3)** check IAM/permissions first — it's the most common root cause, **(4)** reproduce in isolation.

## Glue job failed
- **Check first:** the job's CloudWatch log group (`/aws-glue/jobs/...`) and the error in the Glue console run details.
- **Common causes:** IAM role missing S3/Catalog permissions; schema mismatch vs the Catalog; OOM on a skewed join; bad input data.
- **Fixes:** grant least-privilege S3/Glue permissions to the job role; handle schema drift explicitly; increase DPUs or repartition to fix skew; add input validation upstream.

## Access denied (the universal AWS error)
- **Check first:** which principal, which action, which resource — the error message names all three.
- **Common causes:** missing IAM policy statement; resource policy (bucket policy/KMS key policy) blocking; Lake Formation permissions not granted on top of IAM.
- **Fixes:** add the specific action to the role policy (least privilege); check the resource policy and KMS key policy; if the table is Lake Formation-governed, grant LF permissions too — IAM alone isn't enough.

## S3 event trigger not firing
- **Common causes:** event notification not configured on the bucket; prefix/suffix filter excludes your key; Lambda lacks `s3:` invoke permission / S3 lacks permission to invoke Lambda; event went to a different target (SNS/SQS) than expected.
- **Fixes:** verify the bucket's Event Notifications config and filters; confirm the Lambda resource policy allows S3 to invoke it; check the right region.

## Glue Crawler not detecting schema / wrong schema
- **Common causes:** mixed file formats in one prefix; inconsistent schemas across files; crawler pointed at the wrong path; partition structure not in `key=value` form.
- **Fixes:** separate formats by prefix; use consistent schemas or a schema registry; lay out partitions as `dt=2025-01-01/`; consider defining the table manually instead of crawling.

## Athena query too expensive / too slow
- **Cause:** scanning unpartitioned or non-columnar data (billed per TB scanned).
- **Fixes:** convert to partitioned Parquet/Iceberg; filter on partition columns; `SELECT` only needed columns; use CTAS to materialize hot subsets; check the bytes-scanned in query stats.

## Redshift COPY failed
- **Check first:** the `STL_LOAD_ERRORS` system table — it names the row and reason.
- **Common causes:** column/type mismatch; bad delimiter or encoding; IAM role on the cluster lacks S3 read; malformed input.
- **Fixes:** align the table DDL to the file; specify format options correctly; attach an IAM role with S3 read to the cluster; clean or quarantine bad rows.

## Step Functions execution failed
- **Check first:** the visual execution graph — the failed state is highlighted with its error.
- **Common causes:** a task's IAM permissions; unhandled error in a Lambda/Glue task; timeout; malformed state input/output.
- **Fixes:** add `Retry`/`Catch` blocks; fix the task role; align input/output paths between states; raise timeouts for long Glue jobs.

## Lambda timeout
- **Common causes:** doing heavy processing (Lambda's max is 15 min); waiting on a slow downstream; cold-start plus large work.
- **Fixes:** if the work is genuinely big, move it to Glue/EMR — Lambda is a router, not an ETL engine; increase memory (also raises CPU); make the work incremental; offload waits.

## Kinesis throttling (ProvisionedThroughputExceeded)
- **Common causes:** too few shards for the write/read rate; a hot partition key concentrating traffic on one shard.
- **Fixes:** add shards or use on-demand mode; choose a higher-cardinality partition key to spread load; batch records.

## Data quality check failed
- **Method:** treat it as a feature, not a bug — the check caught bad data. Route the batch to a quarantine prefix, alert via SNS, and don't promote it to silver/gold. Investigate the source.

## Late-arriving data
- **Cause:** events arrive after their time window closed.
- **Fixes:** use event-time (not processing-time) windows with a watermark/grace period; design idempotent upserts so a late record updates rather than duplicates; reprocess the affected partition.

## Duplicate records
- **Cause:** at-least-once delivery, retries, or non-idempotent writes.
- **Fixes:** deduplicate on a natural/business key; use `MERGE`/upsert into Iceberg/Redshift instead of blind insert; deterministic S3 keys so re-runs overwrite.

## Schema drift
- **Cause:** upstream added/changed/removed a field.
- **Fixes:** detect via crawler/Glue Data Quality; use a schema registry or Iceberg's schema evolution; fail loudly on breaking changes rather than silently dropping data.

## Partition not showing in Athena
- **Cause:** new partition exists in S3 but not in the Catalog.
- **Fixes:** run `MSCK REPAIR TABLE` or `ALTER TABLE ADD PARTITION`; enable partition projection; re-run the crawler.

## CloudWatch logs missing
- **Common causes:** the service's execution role lacks `logs:CreateLogGroup/PutLogEvents`; logging not enabled on the service; looking in the wrong log group/region.
- **Fixes:** add logging permissions to the role; enable continuous logging (e.g. Glue); confirm the exact log group name and region.
