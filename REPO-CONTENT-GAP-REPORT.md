# Repo Content Gap Report

Audited inventory of what is real vs scaffolded, with each gap classified **Critical / High / Medium / Low**. Severity reflects impact on a learner's path to job-readiness and the acceptance criteria, not raw file count.

Last audit: this pass. Method: scanned all `.md`/`.py` for gap markers (`TODO`, `SKELETON`, `scaffold`, `example-only`, `pending`) and reviewed non-marker files for depth.

## Scorecard

| Area | Complete | Scaffolded | Severity of remaining |
|---|---|---|---|
| Root docs | 11/11 | 0 | — |
| Module 00 Foundations | Yes | — | — |
| Module 02 S3 Lake | Yes (9 files) | topical extras | Low |
| Modules 01, 03–12 | — | ~180 files | **Critical/High** |
| Labs | 01 done | 02–13 | **High** |
| Projects | — | 01–07 (+08–11 not yet created) | Medium |
| CDK stacks | S3 only | ~15 stacks | **High** |
| Code (src) | scripts + 1 Lambda | glue/streaming/quality/utils/sql | **Critical** |
| Tests | unit (16 passing) | integration/dq/architecture | Medium |
| Papers (docs/papers) | — | 10 papers | Medium |
| Service encyclopedia | — | ~40 services | **Critical** |

## Complete and verified (no gaps)

Root: `README`, `ROADMAP`, `LEARNING-PATH`, `CERTIFICATION-MAPPING`, `COST-OPTIMIZATION`, `TROUBLESHOOTING-RUNBOOK`, `SECURITY-GOVERNANCE`, `INDUSTRY-USE-CASES`, `LATEST-AWS-UPDATES`, `GLOSSARY`, `SERVICE-DECISION-FRAMEWORK`.
Module 00 (README, architect-notes, glossary). Module 02 (all 9 core files, real content + diagrams).
Lab 01 (runnable: deployable CDK S3 stack, 4 scripts, sample data, 16 passing tests, cleanup).
`infra/cdk/` S3 data lake stack (synth-verified). `scripts/` (all run). `tests/unit/` (16 pass).

## Gaps by severity

### Critical (blocks the core job-ready path)
- **`src/utils/` shared code layer** — missing. Everything else (Lambdas, Glue jobs, quality checks) should import logging/config/s3/errors from here. Built this pass.
- **`src/quality/` data-quality checks** — missing. Schema, null, duplicate, freshness, reconciliation. Partially built this pass.
- **`src/glue_jobs/` transforms** — missing. raw→bronze→silver→gold PySpark. Started this pass.
- **Modules 01 (IAM/core) and 03–04 (ingestion/Glue) concept+code** — the spine of Domain 1. Scaffolded.
- **Service encyclopedia** — no per-service pages following the 16-section template yet.

### High (needed for practitioner + production competence)
- **Labs 02–13** — scaffolds only. Lab 02 built this pass.
- **CDK stacks** — IAM, Lambda, Glue (db/crawler/job), EventBridge, Step Functions, SNS, SQS DLQ, Kinesis, Firehose, Athena, CloudWatch alarms, OIDC. Only S3 exists.
- **Modules 05–08** (streaming, orchestration, Redshift, governance) topical files.

### Medium (depth, breadth, senior polish)
- **Projects 01–11** — 01–07 scaffolded; 08–11 (finance, healthcare, IoT, SaaS) not created.
- **`docs/papers/`** — 10 architecture papers not created.
- **Modules 09, 11, 12** (patterns, production eng, architect playbook) topical files.
- **Integration / data-quality / architecture tests.**

### Low (nice-to-have, non-blocking)
- Module 02 topical extras (industry-use-cases, monitoring, service-decision, certification-notes, mistakes-to-avoid) — the 9 core files are done; these 5 remain scaffolded.
- Notebooks.

## README honesty check
Root README now carries a **Content status** section and links this report. Lab map marks Lab 01 as the only fully-runnable lab. No current overpromise; this pass keeps it honest by updating status as content lands.

## How progress is tracked
Each pass shrinks the "Scaffolded" column and moves items out of Critical/High. The [build roadmap](./REPO-BUILD-ROADMAP.md) sequences the work into phases.
