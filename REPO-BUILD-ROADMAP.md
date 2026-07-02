# Repo Build Roadmap

The plan that takes this repo from a strong foundation to a complete field guide + production codebase, in **depth-first phases**: each phase ships complete, verified content before the next begins. Progress is tracked in [REPO-CONTENT-GAP-REPORT.md](./REPO-CONTENT-GAP-REPORT.md); rules in [CLAUDE.md](./CLAUDE.md); page structure in [CONTENT-STANDARD.md](./CONTENT-STANDARD.md).

**Principle:** build vertically (one complete S3→Glue→Athena→orchestrated path a learner can actually run) before horizontally (forty half-written service pages help nobody).

**Definition of done, globally:** content follows the standard; code runs; commands verified; tests pass; diagrams present; cost warning + cleanup exist; no untracked TODO/scaffold markers; gap report and README status updated.

---

## Phase 0 — Audit and content standards ✅ (done)

- **Goal:** honest inventory, permanent rules, and templates before building.
- **Files:** REPO-CONTENT-GAP-REPORT.md, this roadmap, CLAUDE.md, CONTENT-STANDARD.md, README honesty pass.
- **Code/tests/diagrams:** none (process phase).
- **Done when:** every scaffold is tracked, README matches reality, standards written. ✅

## Phase 1 — AWS core services foundation ✅ (done)

- **Goal:** the substrate every pipeline stands on, taught properly.
- **Files:** `01-aws-core-services/` — README + iam, vpc, kms, cloudwatch, sqs-sns, eventbridge, lambda, step-functions (all real).
- **Code:** CLI/boto3/ASL snippets per page; handler pattern referencing `src/lambda/handler.py`.
- **Tests:** covered by existing unit suite where code is shared.
- **Diagrams:** one Mermaid per page + module map.
- **Done when:** all 9 pages meet CONTENT-STANDARD. ✅

## Phase 2 — S3 data lake and Lab 01 ✅ (done)

- **Goal:** a real, deployable, tested data lake and the book-quality module behind it.
- **Files:** `02-storage-s3-lake/` (15 files), `labs/lab-01-s3-data-lake/README.md`, `infra/cdk/` (DataLakeStack), `scripts/` (5), `data/sample/retail/` (3 CSVs), `tests/unit/` (4 files).
- **Code:** 5-bucket CDK stack; upload/validate/layout/prefix scripts with logging + `--region`/`--profile`/`--dry-run`.
- **Tests:** 47 passing (layout, schema, scripts, transform, utils, quality).
- **Diagrams:** zones, ingestion flow, pruning, raw→gold, event trigger, failure/cleanup.
- **Done when:** `pytest` green, `cdk synth` clean, lab runnable with cleanup. ✅

## Phase 3 — Glue Catalog and Lab 02 (in progress)

- **Goal:** the metadata layer — crawler, catalog, partitions — verified end-to-end.
- **Files to update:** Lab 02 README (written), `04-batch-processing/` catalog pages, `infra/cdk/stacks/glue_catalog_stack.py` (written, synth-verified).
- **Code to add:** none major; possible crawler config hardening after the live run.
- **Tests to add:** CDK assertion test for the Glue stack; post-crawl validation script (table + partition count check).
- **Diagrams to add:** crawler flow, catalog-as-contract.
- **Definition of done:** Lab 02 executed against a real account (crawl → table visible → partitions correct → cleanup), README claim unqualified, gap report updated.

## Phase 4 — Glue ETL PySpark and Lab 03

- **Goal:** raw→silver transformation for all three entities — the pipeline's first real compute.
- **Files to update:** Lab 03 README; `04-batch-processing/` ETL/bookmarks/data-quality pages; `src/glue_jobs/` (orders exists; add customers, products, silver→gold orders).
- **Code to add:** GlueJobStack (job + least-privilege role); job scripts with pure-function cores.
- **Tests to add:** unit tests per transform core; schema contract tests.
- **Diagrams to add:** job anatomy, bookmark incremental flow, quarantine path.
- **Definition of done:** deployed job converts Lab 01 data to partitioned Parquet, validated by row counts and Athena-readable output; cleanup verified.

## Phase 5 — Athena and Lab 04

- **Goal:** query the lake; *see* partition pruning and scan-cost mechanics.
- **Files to update:** Lab 04 README; Athena pages in Module 04; `src/sql/` query set.
- **Code to add:** AthenaStack (workgroup + results location); example CTAS.
- **Tests to add:** scripted query with bytes-scanned assertion (pruned vs unpruned).
- **Diagrams to add:** query path (catalog → S3), CTAS materialization.
- **Definition of done:** documented queries run with measured scan sizes; costs explained; cleanup verified.

## Phase 6 — Lambda S3 trigger and Lab 05

- **Goal:** event-driven validation on file arrival, production-shaped.
- **Files to update:** Lab 05 README; `03-ingestion/` event-ingestion pages; finish `src/lambda/handler.py` TODOs (quarantine copy, SNS publish).
- **Code to add:** LambdaStack (function, trigger, DLQ, alarm); SNS topic.
- **Tests to add:** handler unit tests incl. malformed events and idempotency; CDK assertions.
- **Diagrams to add:** S3→Lambda→quarantine/alert flow.
- **Definition of done:** a bad file demonstrably quarantines + alerts; a good file passes; DLQ wired; cleanup verified.

## Phase 7 — EventBridge scheduling and Lab 06

- **Goal:** scheduled and event-pattern triggering with replay/DLQ discipline.
- **Files to update:** Lab 06 README; Module 06 trigger pages.
- **Code to add:** EventsStack (Scheduler schedule, failure-event rule → SNS, target DLQs).
- **Tests to add:** `test-event-pattern` fixtures; CDK assertions.
- **Diagrams to add:** bus/rules/targets; hybrid event+schedule design.
- **Definition of done:** schedule fires the pipeline; failure rule alerts; cleanup verified.

## Phase 8 — Step Functions orchestration and Lab 07

- **Goal:** the full crawl→transform→quality→publish workflow with retries and gates.
- **Files to update:** Lab 07 README; Module 06 orchestration pages; state machine ASL/CDK.
- **Code to add:** OrchestrationStack; quality-check Lambda using `src/quality/`.
- **Tests to add:** state-machine definition assertions; quality-gate unit tests.
- **Diagrams to add:** state machine graph, failure paths.
- **Definition of done:** one execution runs the whole batch path end-to-end, incl. a forced-failure demo; cleanup verified.

## Phase 9 — Redshift warehouse and Lab 08

- **Goal:** serving layer — Serverless namespace, COPY from gold, dist/sort key reasoning.
- **Files to update:** Lab 08 README; Module 07 pages; `src/sql/redshift/` DDL + COPY + marts.
- **Code to add:** RedshiftStack (Serverless, scoped IAM for COPY).
- **Tests to add:** row-count reconciliation script lake↔warehouse.
- **Diagrams to add:** lake→warehouse flow; distribution styles.
- **Definition of done:** marts queryable in Redshift, reconciled counts, **cost warning prominent** (priciest lab), cleanup verified.

## Phase 10 — Kinesis streaming and Lab 09

- **Goal:** streaming ingest with replay, buffering, and small-file avoidance.
- **Files to update:** Lab 09 README; Module 05 pages; `src/streaming/` producer + consumer.
- **Code to add:** KinesisStack (stream + Firehose → raw with buffering).
- **Tests to add:** producer unit tests; delivered-object size/naming validation.
- **Diagrams to add:** stream vs delivery; replay flow.
- **Definition of done:** synthetic clickstream lands buffered in the lake; replay demonstrated; cleanup verified.

## Phase 11 — Lake Formation governance and Lab 10

- **Goal:** column/row-level access on the cataloged lake.
- **Files to update:** Lab 10 README; Module 08 pages.
- **Code to add:** governance-as-code grants; two demo principals.
- **Tests to add:** scripted access checks (allowed vs denied queries).
- **Diagrams to add:** LF-over-IAM permission layering.
- **Definition of done:** analyst principal provably cannot read PII columns; cleanup (incl. deregistration) verified.

## Phase 12 — CloudWatch monitoring and Lab 11

- **Goal:** the four-question monitoring posture (running? succeeded? data right? on time?) on the real pipeline.
- **Files to update:** Lab 11 README; Module 11 monitoring pages.
- **Code to add:** ObservabilityStack (alarms, dashboard, freshness custom-metric emitter).
- **Tests to add:** alarm-definition assertions; forced-failure alert demo.
- **Diagrams to add:** monitoring architecture; alert routing.
- **Definition of done:** dashboard live, a forced failure alerts via SNS, cleanup verified.

## Phase 13 — End-to-end production pipeline (Lab 12)

- **Goal:** wire Phases 3–12 into one production-style pipeline: CI/CD (OIDC), idempotent replays, runbooks.
- **Files to update:** Lab 12 README; Module 11 remaining pages; `.github/workflows/` verified end-to-end.
- **Code to add:** integration glue only — the point is composition.
- **Tests to add:** end-to-end smoke test script; replay test (same partition twice, no duplicates).
- **Diagrams to add:** the full platform diagram (matches root README).
- **Definition of done:** one deploy pipeline processes a day end-to-end, is re-runnable, monitored, and torn down cleanly.

## Phase 14 — Complex architect project (Lab 13 + capstone project 07)

- **Goal:** design-first exercise: multi-source, governed, cost-modeled platform with written trade-offs.
- **Files to update:** Lab 13 README; `projects/project-07-*/` full build; `docs/decision-records/` ADRs; `docs/papers/` first papers.
- **Code/tests/diagrams:** the capstone's stacks, tests, and hero architecture diagram.
- **Definition of done:** a senior engineer could run a design review from the docs alone; the build deploys.

## Phase 15 — Certification and interview prep

- **Goal:** DEA-C01 readiness from the completed material.
- **Files to update:** CERTIFICATION-MAPPING per-domain deep sections (Scope-A services done; extend to all), Module 10, `docs/interview-prep/` question sets.
- **Definition of done:** every domain maps to completed modules/labs with original scenarios and hands-on tasks; no exam dumps.

## Phase 16 — Final quality review

- **Goal:** verify every acceptance criterion across the repo.
- **Method:** re-run the Phase-0 audit; execute every lab's validation; `pytest` + `cdk synth` + link check + Mermaid render check; confirm zero untracked markers; final gap-report update.
- **Definition of done:** the gap report's Critical and High sections are empty.

---

## Current position

**Phases 0–2 complete** (verified this pass: 47 tests green, both stacks synth). **Phase 3 is next:** run Lab 02 end-to-end against a real account. Do not start Phase 4 until Lab 02's runnable claim is unqualified.
