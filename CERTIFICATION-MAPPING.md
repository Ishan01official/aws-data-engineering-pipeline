# Certification Mapping — AWS Certified Data Engineer – Associate (DEA-C01)

This maps the repo to the official exam so the same work that makes you competent makes you certified. It uses **original, scenario-based practice questions only** — no exam dumps.

> ⚠️ Verify current details against the [official exam guide](https://docs.aws.amazon.com/aws-certification/latest/examguides/data-engineer-associate-01.html) — AWS revises it periodically.

## Exam at a glance (verify before booking)

| Fact | Value |
|---|---|
| Code | DEA-C01 |
| Questions | 65 (50 scored + 15 unscored), multiple choice / multiple response |
| Duration | 130 minutes |
| Scoring | Scaled 100–1000, **pass = 720**, compensatory (no per-domain minimum) |
| Cost | 150 USD |
| Recommended experience | 2–3 yrs data engineering, 1–2 yrs hands-on AWS |

## Domain weights

| Domain | Weight | Repo modules | Labs |
|---|---|---|---|
| 1 · Data Ingestion & Transformation | **34%** | 03, 04, 05, 06 | 02, 03, 05, 06, 07, 09 |
| 2 · Data Store Management | **26%** | 02, 07 | 01, 02, 04, 08 |
| 3 · Data Operations & Support | **22%** | 06, 11 | 06, 07, 11 |
| 4 · Data Security & Governance | **18%** | 01, 08 | 10 |

Domain 1 is the largest single block — prioritize ingestion patterns, Glue ETL, and orchestration.

---

## Domain 1 · Data Ingestion and Transformation (34%)

**What it means:** Get data in (batch and streaming) and transform it, orchestrating pipelines with programming concepts. The official task statements cover performing ingestion, transforming/processing data, orchestrating pipelines, and applying programming concepts (idempotency, retries, CI/CD).

**Key AWS services:** S3, Glue (ETL, crawlers, bookmarks, data quality), EMR/EMR Serverless, Lambda, Kinesis Data Streams & Firehose, MSK, DMS, AppFlow, Step Functions, MWAA, EventBridge, Athena CTAS.

**Where it's taught:** Modules [03](./03-ingestion/), [04](./04-batch-processing/), [05](./05-streaming/), [06](./06-orchestration/).

**Common traps:**
- Confusing Kinesis Data Streams (replayable, custom consumers) with Firehose (managed delivery, buffered). The exam tests this line hard.
- Forgetting Glue **job bookmarks** as the mechanism for incremental processing.
- Choosing streaming when the scenario's actual latency need is satisfiable by batch.
- Idempotency / replayability questions — knowing how to make a re-run safe.

**Scenario practice:**

> *A team ingests clickstream events and must retain the ability to reprocess the last 7 days if a downstream bug is found. Events also feed a real-time dashboard. Which ingestion service?*
> **Answer reasoning:** Replay requirement + custom processing → **Kinesis Data Streams** (durable, replayable log with configurable retention), not Firehose (delivery-only, no replay). Firehose could *additionally* land a copy in S3, but the replay requirement is what forces Data Streams.

> *A nightly Glue job reprocesses the entire table each run, and cost is climbing. What's the fix?*
> **Answer reasoning:** Enable **Glue job bookmarks** to process only new/changed data incrementally, rather than re-scanning everything.

---

## Domain 2 · Data Store Management (26%)

**What it means:** Choose and manage the right data stores — lake and warehouse — including modeling, cataloging, lifecycle, and performance.

**Key AWS services:** S3 (storage classes, lifecycle, partitioning), Glue Data Catalog, Lake Formation, Redshift (dist/sort keys, Spectrum, materialized views), Athena, Iceberg on AWS, DynamoDB.

**Where it's taught:** Modules [02](./02-storage-s3-lake/), [07](./07-data-warehouse-redshift/).

**Common traps:**
- Partitioning strategy — choosing a high-cardinality partition key and creating the small-files problem.
- Redshift distribution key choice (KEY vs EVEN vs ALL) and its effect on data skew and join performance.
- When to use Parquet/Iceberg vs raw formats.
- Athena cost driven by **data scanned** — partitioning and columnar formats are the levers.

**Scenario practice:**

> *Analysts query a 5 TB S3 dataset in Athena, always filtering by event date, and bills are high. What change cuts cost most?*
> **Answer reasoning:** Convert to **partitioned Parquet by date** — partition pruning means Athena scans only the relevant days, and columnar Parquet scans only needed columns. This attacks the per-TB-scanned cost directly.

> *A Redshift fact-to-dimension join is slow due to data redistribution at query time. What design fixes it?*
> **Answer reasoning:** Choose **distribution keys** so joined tables are colocated (or use `DISTSTYLE ALL` for small dimensions), eliminating cross-node redistribution.

---

## Domain 3 · Data Operations and Support (22%)

**What it means:** Automate, analyze, maintain, monitor pipelines, and ensure data quality. Task statements: automate processing, analyze data, maintain/monitor pipelines, ensure data quality.

**Key AWS services:** CloudWatch (logs/metrics/alarms), EventBridge, SNS, Step Functions, Glue Data Quality, Athena, Lambda, X-Ray, dead-letter queues.

**Where it's taught:** Modules [06](./06-orchestration/), [11](./11-production-engineering/).

**Common traps:**
- Knowing which CloudWatch construct does what (metric vs alarm vs log subscription).
- Data quality dimensions (completeness, uniqueness, freshness, validity) and how Glue Data Quality / custom checks enforce them.
- Retry vs DLQ semantics, and idempotency as the precondition for safe retries.

**Scenario practice:**

> *A Glue job occasionally fails on bad upstream data, and you need to be alerted and to not lose the failed records. What's the pattern?*
> **Answer reasoning:** Route failures to an **SNS alert** (notification) and a **dead-letter location/queue** (so records aren't lost and can be reprocessed), with **CloudWatch alarms** on the failure metric.

---

## Domain 4 · Data Security and Governance (18%)

**What it means:** Authentication, authorization, encryption/masking, audit logging, and data privacy/governance. Task statements: apply authentication, apply authorization, encryption & masking, prepare logs for audit, understand privacy & governance.

**Key AWS services:** IAM, Lake Formation (column/row/tag-based access), KMS, Secrets Manager, SSM Parameter Store, CloudTrail, Macie (PII identification), Redshift data sharing.

**Where it's taught:** Modules [01](./01-aws-core-services/), [08](./08-governance-security/).

**Common traps:**
- IAM vs Lake Formation — when coarse IAM suffices vs when fine-grained (column/row) access requires Lake Formation.
- Encryption: at-rest (KMS, SSE-S3/SSE-KMS) vs in-transit (TLS), and key management responsibilities.
- Macie for **PII identification**; Lake Formation for enforcing access to it.
- CloudTrail for audit (who did what) vs CloudWatch for operational metrics.

**Scenario practice:**

> *Analysts must query a customer table but must not see the email and SSN columns, while the data science team can. What enforces this?*
> **Answer reasoning:** **Lake Formation column-level permissions** (or LF-Tags), granting different column sets per principal. IAM alone can't do column-level control.

> *Compliance requires identifying where PII lives across the S3 lake. Which service?*
> **Answer reasoning:** **Amazon Macie** scans S3 and classifies sensitive data / PII; pair it with Lake Formation to then govern access.

---

## A study plan that uses this repo

1. **Weeks 1–2:** Modules 00–02 + Labs 01, 02, 04. Build the lake, catalog, query with Athena.
2. **Weeks 3–4:** Modules 03–04 + Labs 03, 05, 06. Ingestion and Glue ETL — this is Domain 1, the biggest slice.
3. **Week 5:** Module 06 + Lab 07. Orchestration and operations (Domain 3).
4. **Week 6:** Module 07 + Lab 08. Redshift and modeling (Domain 2).
5. **Week 7:** Module 05 + Lab 09. Streaming (Domain 1).
6. **Week 8:** Modules 01, 08 + Lab 10. Security and governance (Domain 4).
7. **Week 9:** Module 10 review, scenario questions, and a full official AWS practice exam on SkillBuilder.

> The repo's labs *are* the hands-on the exam assumes you have. Don't skip cleanup — but don't skip the labs either.
