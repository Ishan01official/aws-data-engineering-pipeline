# Contributing & Conventions

This is a structured reference system. Consistency is what keeps it navigable as it grows.

## File conventions
- **Modules** use the standard 15-file structure (README + concept, architecture, service-decision, industry-use-cases, code-walkthrough, deployment, monitoring, troubleshooting, cost, security, interview-questions, certification-notes, mistakes-to-avoid, hands-on-lab).
- **Labs** use the standard template: Objective · Architecture · Prerequisites · 💰 Cost warning · Steps · Code · Validation · Cleanup · Interview questions · Production notes.
- One concept per file. READMEs explain; `architect`/`service-decision` files cover trade-offs; code runs.

## Teaching pattern (every service)
Simple explanation → why it exists → where it fits → real industry use (e-commerce / finance / IoT) → how it works internally → hands-on code → deployment → triggering → monitoring → security → cost → troubleshooting → architect decision.

## Quality rules
- Every explanation is practical, not theory-only, and connects to pipeline design.
- Every code sample should run, or is clearly marked **example only**.
- Cost is first-class: any architectural claim involving money gets a `💰` note.
- **Every AWS lab has a mandatory cleanup step.** Never leave paid resources running without warning.
- Use placeholders (`REPLACE_ACCOUNT_ID`, `REPLACE_REGION`, `REPLACE_BUCKET`, role ARNs). Never commit secrets, credentials, or real account details.
- Least-privilege IAM in all examples; config via env vars / config files.
- Diagrams: Mermaid inline (renders on GitHub); draw.io + AWS icons for hero diagrams (see `docs/aws-icons/`).
- Don't copy copyrighted book content — original explanations, link to sources.
- Mark unfinished content clearly as **TODO**; no silent empty placeholders.

## Markdown
Verify diagrams and links render on GitHub before committing. The `lint-docs` workflow checks links.

## The 16-section service template

Every AWS service page follows this structure (the content standard):

1. Simple explanation — beginner language
2. Why this service exists — the real engineering problem
3. Where it fits in data engineering — storage/ingestion/processing/orchestration/warehouse/streaming/governance/monitoring/security/DevOps
4. Real industry use cases — retail, banking/finance, healthcare, manufacturing, SaaS, IoT, media/advertising, product analytics
5. How it works internally — components, data flow, limits, scaling, failure modes
6. Hands-on code — Python/boto3/PySpark/SQL/CDK/CLI, runnable
7. Code walkthrough — inputs, outputs, env vars, IAM, errors, logging, idempotency, retries
8. Deployment — CLI / CDK / GitHub Actions
9. Triggering — S3 event / EventBridge / SNS / SQS / Step Functions / API GW / CLI / CI-CD
10. Monitoring — logs, metrics, alarms, alerts, dashboards, runbooks
11. Security — least-privilege IAM, encryption, KMS, secrets, network, public-access, PII
12. Cost — pricing drivers, traps, optimization, when not to use
13. Troubleshooting — real failures and how to debug
14. Architect-level decisions — when to choose/avoid, vs alternatives
15. Interview questions — beginner/intermediate/senior/scenario
16. Certification notes — DEA-C01 domain mapping

The lab template: Objective → Business scenario → Architecture → Services → Prerequisites → Cost/safety → Setup → Code explanation → Deployment → Trigger → Validation → Expected output → Troubleshooting → Interview questions → Cleanup → Production notes → Architect extension.
