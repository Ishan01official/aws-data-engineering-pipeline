# Repo Content Gap Report

The audited inventory of what is real versus scaffolded. Every gap is classified **Critical / High / Medium / Low** by its impact on a learner's path to job-readiness. This report is the single source of truth for repo status; the [build roadmap](./REPO-BUILD-ROADMAP.md) sequences the work.

**Last audit:** 2026-07-02 (Phase 3 pass). Method: full-tree scan for gap markers (`TODO`, `scaffold`, `skeleton`, `planned`, `placeholder`, `example-only`, `pending`, `coming soon`, `not implemented`, `TBD`) plus manual depth review of non-marker files, plus execution of tests (69 passing) and `cdk synth` on both stacks.

---

## 1. Current repo status summary

| Area | Status |
|---|---|
| Root docs (README, roadmaps, framework, runbook, use-cases, cert map, glossary, etc.) | ✅ Real content, expanded this pass |
| CLAUDE.md / CONTENT-STANDARD.md | ✅ Written |
| Module 00 Foundations | ⚠️ README + architect-notes + glossary real; **14 topical files are stubs** |
| **Module 01 AWS Core Services** | ✅ **Complete this pass** — 9 real pages (IAM/STS, VPC/SG/NACL, KMS/Secrets/SSM, CloudWatch/CloudTrail, SQS/SNS, EventBridge, Lambda, Step Functions) |
| **Module 02 S3 Lake** | ✅ **Complete** — all 15 files real, incl. naming/compression/inventory/anti-patterns and 6 diagrams |
| Modules 03–12 | ❌ ~150 stub files (self-marked scaffolds) |
| **Lab 01** | ✅ **Complete and runnable** — CDK 5-bucket stack (synth-verified), 5 scripts, tracked sample data, 47 passing tests, validation, cleanup |
| Lab 02 | ⚠️ **Code-complete, synth-verified only** — per-entity crawler targets, CSV header classifier, least-privilege role, 15 automated tests (template assertions + validation logic), full deploy/run/validate/cleanup commands, and a manual verification checklist in the lab README (§12). Needs one live-account run to remove the banner |
| Labs 03–13 | ❌ Scaffold READMEs (~144 words each) |
| Projects 01–06 | ❌ Scaffold READMEs |
| Project 07 (capstone) | ⚠️ Outline only |
| CDK | ✅ DataLakeStack + GlueCatalogStack synth-verified **and covered by template assertion tests** (`tests/infra/`); all other stacks not written |
| `src/` code | ✅ Lambda handler, glue transform (unit-tested core), utils, quality checks exist with tests; ⚠️ 2 tracked TODOs in `src/lambda/handler.py` (quarantine copy + SNS publish wiring, planned for Lab 05) |
| Tests | ✅ 69 passing (`pytest tests/`) — layout, schema, scripts, transform, utils, quality, catalog-validation logic, CDK template assertions |
| Sample data | ✅ Tracked in git (gitignore fixed this pass), matches documented schema, referentially consistent |

## 2. What is already good

- **Lab 01 is genuinely end-to-end:** deployable CDK (5 buckets with encryption/versioning/BPA/TLS/lifecycle/tags, no hardcoded account IDs), scripts with argparse/logging/`--region`/`--profile`/`--dry-run`, deterministic key layout shared via `scripts/lake_layout.py`, validation with non-zero exit on failure, cleanup, and tests.
- **Modules 01 and 02** meet the [CONTENT-STANDARD](./CONTENT-STANDARD.md): beginner-first, internals, runnable snippets, security/cost/troubleshooting/architect/interview/cert sections, Mermaid diagrams.
- **Root reference docs** are deep: 18-comparison decision framework (incl. 5 S3 design decisions with the full 9-field format), 25+ runbooks (incl. 11 S3-lake runbooks in symptom/causes/checks/fix/prevention/senior format), industry deep dives, and a per-service DEA-C01 map with original scenario questions.
- **Honesty machinery:** stubs self-identify, the README status section matches reality, and this report is regenerated per pass.

## 3. What is missing (by severity)

### Critical — blocks the core learn-by-building path
- **Modules 04 (Glue/batch) and 03 (ingestion) real content** — the spine of exam Domain 1 and of the pipeline itself. All stubs.
- **Labs 03 (Glue ETL) and 04 (Athena)** — without them the lake built in Lab 01 is never transformed or queried. Scaffolds only.
- **Lab 02 live-account run** — the code, commands, tests, and cleanup are complete (Phase 3 pass fixed a real mixed-schema design flaw via entity-level crawler targets, added a CSV header classifier for the all-strings header bug, and shipped `scripts/validate_glue_catalog.py` + 15 tests). This machine has no AWS CLI/credentials, so the lab is honestly marked **synth-verified only** with an 8-step manual checklist in its README (§12). One sandbox run closes this item.

### High — needed for practitioner/production competence
- Labs 05–07 (Lambda trigger, EventBridge, Step Functions) + their CDK stacks (IamStack, LambdaStack, OrchestrationStack).
- Module 06 (orchestration) and Module 11 (production engineering) content.
- `src/lambda/handler.py` TODOs: quarantine copy + SNS publish (tracked; land with Lab 05).
- Module 00's 14 topical stub files (the module README is strong; the stubs should be filled or removed).

### Medium — depth and breadth
- Modules 05, 07, 08 (streaming, Redshift, governance) + Labs 08–11 + their stacks.
- Projects 01–07 as real builds; docs/papers (10 architecture papers) not started; docs/decision-records empty of ADRs.
- Integration tests and infra assertion tests (CDK `assertions` on the stacks).

### Low — polish
- Modules 09, 10, 12 topical files (root-level equivalents already cover much of this).
- Notebooks directory content; polished draw.io exports in docs/diagrams.

## 4. Files with weak content

- `projects/project-0{1..6}-*/README.md` (~70 words each) and `labs/lab-{03..13}-*/README.md` (~144 words each) — outline-only.
- `00-foundations/{concept,cost,deployment,...}.md` — 14 five-line stubs alongside a strong README.

## 5. Files with TODO/scaffold/skeleton markers (tracked)

- ~150 module stub files across 00, 03–12 (each self-marked `Status: TODO — scaffolded`).
- 11 lab scaffolds + 6 project scaffolds (self-marked).
- `src/lambda/handler.py` — 2 TODOs (quarantine + SNS), scheduled for Lab 05.
- All are **intentional and tracked here**; no untracked markers exist in completed scope (Modules 01–02, Lab 01, scripts, CDK, tests, root docs).

## 6. Missing service explanations

DMS, DataSync, Transfer Family, AppFlow, API Gateway (Module 03); Glue ETL/crawlers/bookmarks/Data Quality, EMR, EMR Serverless, Athena internals (Module 04); Kinesis Data Streams/Firehose, MSK, Managed Flink (Module 05); MWAA, Glue Workflows (Module 06); Redshift (Module 07); Lake Formation, Macie (Module 08); DynamoDB, OpenSearch, QuickSight (referenced, unexplained).

## 7. Missing code

Glue jobs beyond `bronze_to_silver_orders` (silver→gold, customers/products entities); streaming producers/consumers; Redshift SQL/DDL; Lake Formation grants as code; CDK stacks for IAM/Lambda/Glue-job/StepFunctions/EventBridge/SNS/SQS/Kinesis/Athena-workgroup/CloudWatch-alarms/OIDC.

## 8. Missing deployment commands

Labs 03–13 have no verified deploy sequences (Lab 02's exist, pending execution). GitHub Actions deploy workflow exists (`cdk-deploy-dev.yml`) but is not yet documented end-to-end in Module 11.

## 9. Missing tests

Integration tests (deployed-stack smoke tests); data-quality tests beyond the current unit set; contract tests for future Glue jobs. CDK assertion tests were **added this pass** (`tests/infra/`, 14 tests over both stacks) and are no longer a gap.

## 10. Missing diagrams

Modules 03–12 diagrams (arrive with their content); polished AWS-icon exports in `docs/diagrams/` (instructions exist in `docs/aws-icons/`).

## 11. Missing labs

Labs 03–13 (scaffolds). Lab 02 is complete in code/commands/tests/cleanup; only the live-account verification run remains.

## 12. Missing cleanup instructions

Complete for Labs 01–02 and the CDK README. Each future lab must ship cleanup per [CLAUDE.md](./CLAUDE.md); labs 03–13 currently have none (they have no steps yet).

## 13. Missing production notes

Modules 03–12 production sections (arrive with content). Module 11 (CI/CD, idempotency, reconciliation, SLAs) is the concentrated gap.

## 14. README claims that overpromise vs actual content

- ✅ Root README status section is accurate after this pass (states exactly: Modules 01–02 + Lab 01 complete; Lab 02 pending verification; the rest scaffolded).
- ✅ **Lab 02 claim fixed:** its README now opens with an explicit "synth-verified only" banner, states exactly what is and isn't verified, and includes the manual verification checklist. No fake runnable claim remains.
- ✅ `infra/cdk/README.md` outdated "SKELETON" claim — **fixed this pass** (it under-promised: the stack is real and synth-verified).
- No other overpromises found in the scan.

---

## How to read progress

Completed scope only grows: an item leaves this report when its content is real, its commands run, its tests pass, and its cleanup exists. Next per the [roadmap](./REPO-BUILD-ROADMAP.md): one live-account run of Lab 02's checklist (its README §12), then Phase 4 (Glue ETL + Lab 03).
