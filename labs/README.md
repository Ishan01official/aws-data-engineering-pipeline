# Labs

Thirteen hands-on labs. Each is self-contained and follows the same template: **Objective · Architecture · Prerequisites · 💰 Cost warning · Steps · Code · Validation · Cleanup · Interview questions · Production notes.**

> 💰 **Every lab creates real, billable AWS resources.** Set a budget alarm first, and **always run the cleanup step.** Cleanup is mandatory, not optional.

| # | Lab | Module(s) | Builds |
|---|---|---|---|
| 01 | s3-data-lake | 02 | Bronze/silver/gold buckets, partitioned layout |
| 02 | glue-crawler-catalog | 02, 04 | Crawl raw data into the Glue Catalog |
| 03 | glue-etl-pyspark | 04 | PySpark clean/transform raw→silver |
| 04 | athena-query | 02 | Query the lake, see partition pruning in action |
| 05 | lambda-s3-trigger | 03 | Event-driven validation on file arrival |
| 06 | eventbridge-schedule | 06 | Scheduled pipeline triggering |
| 07 | step-functions-orchestration | 06 | Orchestrate crawler→ETL→quality with retries |
| 08 | redshift-serverless | 07 | Load dimensional marts, COPY, modeling |
| 09 | kinesis-streaming | 05 | Stream events → S3, handle replay |
| 10 | lake-formation-governance | 08 | Column/row-level access control |
| 11 | cloudwatch-monitoring | 11 | Metrics, alarms, SNS alerts on failure |
| 12 | end-to-end-production-pipeline | all | Wire the pieces into one pipeline |
| 13 | complex-architect-project | 09, 12 | Design + build an architect-level platform |

## Honest status

| Lab | Status |
|---|---|
| **01 — S3 data lake** | ✅ Complete and runnable: deployable CDK, working scripts, 47 passing tests, validation, cleanup |
| **02 — Glue crawler** | ⚠️ Code-complete: per-entity crawler, CSV classifier, validation script, 15 automated tests, full commands + cleanup. **Synth-verified only** — one live-account run pending (checklist in the lab README §12) |
| 03–13 | ❌ Scaffold READMEs only — not runnable yet; tracked in [REPO-CONTENT-GAP-REPORT](../REPO-CONTENT-GAP-REPORT.md) |

Labs are built depth-first in the priority order defined in [CLAUDE.md](../CLAUDE.md). A lab is only marked runnable when its code, deployment commands, validation, tests, and cleanup all exist and have been executed.
