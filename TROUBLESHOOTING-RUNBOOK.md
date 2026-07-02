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

---

# S3 data lake runbooks

Storage-layer incidents, in the format an on-call engineer needs: symptom → likely causes → checks → fix → prevention → senior note. These assume the repo's lake layout (`raw/source=.../entity=.../ingestion_date=.../`).

## S3 upload failed

- **Symptom:** `upload_sample_data.py` (or any producer) exits non-zero; objects missing from raw.
- **Likely causes:** no/expired credentials; wrong bucket name or region; no `s3:PutObject` on the prefix; bucket policy denying non-TLS or wrong KMS key; local file missing.
- **Checks:** `aws sts get-caller-identity` (who am I?); `aws s3api head-bucket --bucket <b>` (exists? accessible?); re-run with the exact error visible; confirm `--region`/`--profile` flags.
- **Fix:** match the failure: `NoCredentialsError` → `aws configure`/`--profile`; `NoSuchBucket` → check stack outputs for the real name; `AccessDenied` → grant `s3:PutObject` on `raw/*` to the caller; KMS deny → grant `kms:GenerateDataKey` on the bucket key.
- **Prevention:** producers read bucket names from stack outputs/Parameter Store, never hardcode; CI smoke-test uploads with `--dry-run` plus one canary object.
- **Senior note:** an upload that "fails" by writing to the *wrong* bucket (stale env var) is worse than one that errors. Validate after upload (`validate_s3_layout.py`) — never trust the writer's exit code alone.

## AccessDenied on S3

- **Symptom:** any principal gets 403 `AccessDenied` on Get/Put/List.
- **Likely causes:** identity policy missing the action; missing `s3:ListBucket` specifically (bucket-level, not `/*`); bucket policy explicit deny (TLS, VPC endpoint, or source conditions); SSE-KMS object without `kms:Decrypt`; Lake Formation governing the location; SCP at the org level.
- **Checks:** read the error — it names principal/action/resource; `head-object` to see `x-amz-server-side-encryption` (KMS?); `aws iam simulate-principal-policy` for the exact action/ARN; check the bucket policy's `Deny` statements.
- **Fix:** add the *specific* missing action/resource; for KMS add `kms:Decrypt` in both IAM and the key policy; for LF-governed tables grant in Lake Formation.
- **Prevention:** standard per-zone role templates (raw-reader, silver-writer…) so policies are never hand-rolled; test new roles with the simulator in CI.
- **Senior note:** 90% of lake AccessDenied incidents are one of exactly three things: `ListBucket`, `kms:Decrypt`, or an `aws:SecureTransport`/VPC-endpoint deny condition. Check those before reading another line of policy.

## Wrong partition path

- **Symptom:** data landed at `raw/orders/2026-07-01/` or `raw/source=retail/entity=orders/2026-07-01/` — not the contract layout; queries/crawlers miss it.
- **Likely causes:** a producer built keys by hand instead of using the shared layout function; date formatted wrong (`2026_07_01` as the partition value); typo'd entity name creating a phantom partition.
- **Checks:** `aws s3 ls s3://<raw>/raw/ --recursive | head -50` and eyeball against `scripts/build_s3_prefix.py --entity orders --ingestion-date <d>` output.
- **Fix:** copy objects to the correct key (`aws s3 cp` old→new), verify with `validate_s3_layout.py`, then remove the wrong-path copies *after* downstream reprocesses. Update the producer to import `lake_layout`.
- **Prevention:** one key-building function (`scripts/lake_layout.py`), unit-tested; validation gate after every load; reject unknown entities at write time (the helper already does).
- **Senior note:** treat key layout as an API with a contract test. The cost of a wrong path isn't the copy-fix — it's every downstream consumer that silently read incomplete data meanwhile. Announce the correction with the affected date range.

## Athena cannot find data

- **Symptom:** the objects are visibly in S3, but `SELECT` returns zero rows (or the new day is missing).
- **Likely causes:** partition exists in S3 but not the Glue Catalog; table `LOCATION` points elsewhere; partition values mismatch (hyphens vs underscores); data written *outside* the partition scheme; wrong database/workgroup.
- **Checks:** `SHOW PARTITIONS <table>`; `DESCRIBE FORMATTED <table>` for LOCATION; `SELECT "$path" FROM <table> LIMIT 5` to see which files Athena actually reads.
- **Fix:** `MSCK REPAIR TABLE <table>` (or `ALTER TABLE ... ADD PARTITION`), or re-run the crawler; longer-term enable **partition projection** so date partitions never need registration.
- **Prevention:** pipeline adds partitions as part of the load step (post-write `ADD PARTITION` or projection); freshness check queries the *table*, not the bucket — so it catches catalog gaps too.
- **Senior note:** "data in S3 but not in the catalog" is the single most common lake incident. Partition projection eliminates the whole class for date-shaped partitions; adopt it once layouts stabilize.

## Glue crawler does not detect the table

- **Symptom:** crawler runs green but creates no table, wrong columns, or one giant table instead of per-entity tables.
- **Likely causes:** crawler pointed at the wrong prefix depth; mixed formats/schemas under one prefix (crawler merges or gives up); files with no extension/unsupported compression; exclusions filtering everything; crawler role can't read the objects (KMS!).
- **Checks:** crawler's CloudWatch log (it says what it classified and why); the S3 path configured vs where data actually is; sample a file's format; role permissions incl. KMS.
- **Fix:** point the crawler at the *entity* level (`.../entity=orders/`) or set proper table-level configuration; one format per prefix; grant the crawler role read+decrypt; for stable schemas, skip the crawler and define the table in IaC.
- **Prevention:** layout discipline (this is what the `source=/entity=` levels are for); crawler per source with explicit include paths; schema changes reviewed, not discovered.
- **Senior note:** crawlers are for *discovery*, not for production schema management. Mature pipelines crawl once during onboarding, then own the schema in code — the crawler surprising you is a smell that schema governance is missing.

## Too many small files

- **Symptom:** queries slow despite pruning; request costs climbing; Spark jobs with thousands of tiny tasks.
- **Likely causes:** over-partitioning; streaming/event-driven writers writing per-event; too many parallel writers each flushing small parts; daily loads of naturally tiny extracts.
- **Checks:** S3 Inventory query for object count and average size per prefix (see [Module 02 · monitoring.md](./02-storage-s3-lake/monitoring.md)); Athena `SELECT count(*), avg(length("$path"))`-style sampling; job task counts.
- **Fix:** compaction job (read partition → coalesce/repartition → rewrite, target 128 MB–1 GB); increase Firehose buffer size/interval; drop needless partition levels; Iceberg users: run compaction/`rewrite_data_files`.
- **Prevention:** buffer before writing (Firehose exists for this); partition-cardinality review at design time; a scheduled compaction pass over hot tables; alert on avg-object-size floors from Inventory.
- **Senior note:** small files are the lake's technical debt — invisible day one, compounding daily. Put "average file size per partition" on the platform dashboard, not just in an annual audit.

## Duplicate files uploaded

- **Symptom:** double-counted rows downstream; two near-identical objects for the same entity/date (e.g. `orders_2026_07_01.csv` and `orders_2026_07_01 (1).csv` or re-timestamped names).
- **Likely causes:** producer retries with non-deterministic keys; two schedules/two environments writing the same partition; manual re-upload "to be safe."
- **Checks:** `aws s3 ls` the partition prefix — more objects than the contract expects?; compare ETags/sizes; check producer logs for retries.
- **Fix:** remove the extras (after confirming they're true duplicates), reprocess the partition, and — the real fix — make the producer write **deterministic keys** so retries overwrite instead of duplicate.
- **Prevention:** deterministic naming (this repo's `default_filename()`); one writer per partition by design; downstream dedupe on business keys as defense-in-depth ([`src/glue_jobs/bronze_to_silver_orders.py`](./src/glue_jobs/bronze_to_silver_orders.py) dedupes on `order_id`).
- **Senior note:** at-least-once delivery is the default physics of distributed systems; idempotent writes are non-negotiable. If a re-run can create a duplicate, the bug is in the writer's key scheme, not in the retry.

## Data landed in the wrong zone

- **Symptom:** cleaned Parquet in raw, or raw CSVs in silver; consumers reading data at the wrong quality level.
- **Likely causes:** copy-pasted job config (wrong bucket variable); environment mix-up (dev job with prod outputs or vice versa); a human `aws s3 cp` to the wrong console tab.
- **Checks:** object metadata/tags and key style tell you what it is; CloudTrail data events (if enabled) or access logs tell you who wrote it.
- **Fix:** move the data to the correct zone; reprocess anything that consumed the wrong-zone data; rotate the credentials/config that made it possible.
- **Prevention:** IAM makes wrong-zone writes *impossible*, not just unlikely: the silver-writer role has no `PutObject` on raw, and vice versa. Zone bucket names come from stack outputs, not hand-typed strings.
- **Senior note:** if a job *could* write to the wrong zone, the IAM design is wrong. Least privilege isn't only a security posture — it's a correctness mechanism.

## Public access risk

- **Symptom:** Security Hub/Trusted Advisor/console badge flags a lake bucket as public or "objects can be public"; or an EventBridge alert fired on `PutBucketPolicy`.
- **Likely causes:** someone loosened a bucket policy/ACL to share data quickly; Block Public Access disabled at bucket or account level; a policy with a broad `Principal: "*"` without conditions.
- **Checks:** `aws s3api get-public-access-block --bucket <b>` (and `aws s3control get-public-access-block --account-id <id>`); `get-bucket-policy` and read every `Principal`/`Condition`; S3 console "Access" column; CloudTrail for who changed what, when.
- **Fix:** re-enable Block Public Access (bucket *and* account level) immediately; remove/repair the policy; assess exposure via access logs/CloudTrail for the open window; rotate anything sensitive that was exposed.
- **Prevention:** account-level Block Public Access on; SCP denying `s3:PutBucketPublicAccessBlock`/public ACLs; EventBridge alert on bucket-policy changes; the *legitimate* sharing paths documented (presigned URLs, cross-account roles, Access Points) so nobody "needs" a public bucket.
- **Senior note:** treat any public-exposure finding as an incident with a timeline (when opened, what was read), not a config fix. The postmortem question is "why did someone need to bypass the sharing paths?" — answer that, or it recurs.

## KMS permission issue

- **Symptom:** `AccessDenied`/`KMS.NotFoundException` on reads or writes to an encrypted zone; Glue/Athena/Firehose failing with KMS errors while S3 permissions look perfect.
- **Likely causes:** role missing `kms:Decrypt` (read) or `kms:GenerateDataKey` (write); the **key policy** not allowing the role even though IAM does; key in another account/region; key disabled or pending deletion.
- **Checks:** `head-object` for the KMS key ARN in use; `aws kms describe-key` (enabled? right region?); does the key policy allow the account to delegate via IAM (the default root statement)?
- **Fix:** grant the missing KMS action in IAM *and* verify the key policy; cross-account: grant on the key policy for the consumer account; re-enable/cancel deletion if the key is disabled.
- **Prevention:** per-zone key ARNs documented next to the buckets; role templates include the KMS statements matching each zone; alarms on `kms:DisableKey`/`ScheduleKeyDeletion` CloudTrail events.
- **Senior note:** KMS denials mask themselves as S3 errors, and key-policy-vs-IAM is the least understood interaction in AWS access control ([Module 01 · kms.md](./01-aws-core-services/kms.md)). Also: a scheduled key deletion is a data-loss countdown for everything the key encrypts — alarm on it.

## Lifecycle deleted data earlier than expected

- **Symptom:** objects (or old versions you were counting on) are gone; consumers hit missing files; storage dropped suddenly.
- **Likely causes:** an `Expiration` rule written where a `Transition` was intended; rule scoped to a broader prefix than planned; non-current version expiry shorter than your real recovery window; someone confused days-since-creation with days-since-transition.
- **Checks:** `aws s3api get-bucket-lifecycle-configuration --bucket <b>` and read every rule's filter+action; CloudTrail won't show lifecycle deletions per-object, but S3 access logs record them (`S3.EXPIRE.OBJECT`); versioned bucket? Look for delete markers — data may be recoverable.
- **Fix:** if versioned and non-current copies survive: restore by deleting the delete markers / copying old versions forward. Otherwise: re-ingest from source (this is why raw's upstream matters) or restore from replication/backups. Fix the rule immediately.
- **Prevention:** lifecycle only via IaC with review; on source-of-truth buckets prefer transitions and set expirations only with the data owner's sign-off; test rules on a scratch bucket; keep non-current retention ≥ your realistic incident-detection window (30d minimum).
- **Senior note:** lifecycle rules are the only "code" in your platform that *deletes data silently on a timer* — review them with the same fear you'd review a `DROP TABLE` migration. And know your last line of defense before you need it: versioning, replication, or source re-extract.
