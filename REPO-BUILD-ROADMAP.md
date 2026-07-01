# Repo Build Roadmap

The plan to take this repo from strong-skeleton to complete field guide + codebase, in deliberate phases. Each phase ships complete, verified content — no shallow passes. Progress is tracked against [`REPO-CONTENT-GAP-REPORT.md`](./REPO-CONTENT-GAP-REPORT.md).

## Principle
Build **vertically** (one complete path end-to-end) before **horizontally** (breadth). A learner can follow a finished S3→Glue→Athena path and actually build something; they can't use forty half-written service pages. So we complete the core batch path first, then widen.

---

## Phase 0 — Audit & content standards ✅
- Gap report with severity classification.
- This roadmap.
- Content standard: the 16-section service template (in [CONTRIBUTING](./CONTRIBUTING.md)) and the lab template (Objective → … → Architect extension).
- README honesty pass.

## Phase 1 — AWS core service encyclopedia (in progress)
The substrate: IAM, STS, VPC/SG/NACL, KMS, Secrets Manager, SSM, CloudWatch, CloudTrail, SNS, SQS, EventBridge, Lambda, Step Functions. Each as a page following the 16-section template. Lands in Module 01 + referenced from modules that use them.

## Phase 2 — Data engineering concepts & patterns
The pattern library (batch/stream/CDC ingestion, ETL/ELT, medallion, lakehouse, Lambda/Kappa, SCD, incremental/backfill/replay, idempotency, dedup, late data, small files, partitioning/compaction, lineage, DR, multi-account). Each: problem → diagram → services → example → failure modes → trade-offs → interview + architect answer. Lands in Modules 09/11/12 + `docs/papers/`.

## Phase 3 — Service-specific modules
Fill Modules 01, 03–08 topical files (concept, architecture, code-walkthrough, deployment, monitoring, troubleshooting, cost, security, interview, cert) to Module 02's depth, each with diagrams and runnable code.

## Phase 4 — Hands-on labs
Complete Labs 02–13 to Lab 01's bar: real supporting code, CDK, tests, sample data, validation, cleanup. One lab fully, then the next. **Order:** 02 (Glue crawler) → 03 (Glue ETL) → 04 (Athena) → 05 (Lambda) → 06 (EventBridge) → 07 (Step Functions) → 08 (Redshift) → 09 (Kinesis) → 10 (Lake Formation) → 11 (CloudWatch) → 12 (e2e) → 13 (architect).

## Phase 5 — Production-grade projects
Projects 01–11, each a realistic business scenario with code, CDK, tests, monitoring, security, cost, failure cases, cleanup, extensions. Capstone (07) is fully production-style.

## Phase 6 — Architecture & senior playbook
`docs/papers/` (10 original architecture papers), Module 12 senior playbook (multi-account, DR, cost-aware, governance at scale), `docs/decision-records/` ADRs.

## Phase 7 — Certification & interview prep
Deepen CERTIFICATION-MAPPING per domain with practice scenarios and hands-on tasks; per-module interview questions; `docs/interview-prep/` cross-cutting sets.

## Phase 8 — Final quality review
Every acceptance criterion checked: services explained, code runs, diagrams present, labs have cleanup, tests pass, no fake README claims, no empty pages. Mermaid validation + link check green.

---

## Current position
Phase 0 done. Phase 1 underway (shared code layer + first service pages). Phase 4 Lab 02 completed this pass alongside the code it depends on. This interleaving is deliberate: labs prove the code, code powers the labs.

## Per-pass reporting
Every pass prints: files created, files changed, what's now complete, what's still missing, commands to run, tests to run, cleanup commands. See the end of each pass summary.
