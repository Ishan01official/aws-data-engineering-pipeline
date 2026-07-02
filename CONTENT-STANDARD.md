# Content Standard

Every **service page** in this repo follows the same 16-section structure. This is the contract that keeps content deep, consistent, and useful for three audiences at once: beginners, practitioners, and architects. Module 01's pages (e.g. [iam.md](./01-aws-core-services/iam.md)) are the reference implementations.

A page may merge closely-related sections when it reads better (e.g. troubleshooting tables that include fixes), but every section's *content* must exist. Pages that cover several sibling services (e.g. sqs-sns.md) apply the structure to each.

---

# Service Name

## 1. Simple explanation

Explain the service in beginner language. No prior AWS knowledge assumed. One analogy is allowed if it's accurate.

## 2. Why this service exists

The real engineering problem it solves. What did people do before it, and why did that fail?

## 3. Where it fits in data engineering

Which layer: storage, ingestion, processing, orchestration, warehouse, streaming, governance, monitoring, security, or DevOps. Include a Mermaid diagram showing the service in a pipeline context.

## 4. Real industry use cases

Ground it in at least a few of: retail, banking/finance, healthcare, manufacturing/IoT, SaaS, media/advertising, product analytics. One sentence each is fine — specificity beats volume.

## 5. How it works internally

Main components, scaling model, hard limits, and failure modes. This is what separates a page from marketing copy.

## 6. Hands-on code

Runnable code (Python/boto3, CLI, or CDK) wherever possible. If something can't be made runnable yet, say so explicitly and track it in [REPO-CONTENT-GAP-REPORT.md](./REPO-CONTENT-GAP-REPORT.md).

## 7. Code walkthrough

Explain the code's inputs, outputs, IAM needs, configuration, error handling, logging, retry behavior, and idempotency. Idempotency is discussed on every page that processes events.

## 8. Deployment

How it's deployed for real: AWS CLI, AWS CDK, or GitHub Actions. Exact commands.

## 9. Triggering

How it runs: manual, schedule, event, S3, SNS, SQS, EventBridge, Step Functions, API Gateway, or CI/CD.

## 10. Monitoring

CloudWatch logs, the metrics that matter, the alarms to set, dashboards, and a link to the relevant runbook.

## 11. Security

IAM (least privilege), encryption/KMS, secrets handling, networking, public-access prevention, PII considerations, and audit.

## 12. Cost

Pricing drivers, the cost traps specific to this service, optimization levers, and when the service is the *wrong* (too expensive) choice.

## 13. Troubleshooting

Common failures with symptom → check → fix. Written to be scannable during an incident.

## 14. Architect-level decisions

When to choose this service, when to avoid it, and what it competes with. Link the relevant [SERVICE-DECISION-FRAMEWORK](./SERVICE-DECISION-FRAMEWORK.md) comparison.

## 15. Interview questions

Beginner, intermediate, senior, and scenario-based — with what a strong answer contains, not just the question.

## 16. Certification notes

Map to the DEA-C01 domains: what the exam tests about this service and the trap answers.

---

## Lab standard

Every lab README follows the 18-item checklist in [CLAUDE.md](./CLAUDE.md#every-lab-must-include) — from Objective through Architect-level extension. Labs are only marked **runnable** when code, deployment commands, validation, tests, and cleanup all exist and have been executed successfully. [Lab 01](./labs/lab-01-s3-data-lake/) is the reference implementation.

## Writing rules

- Simple professional English. Short sentences. No filler.
- Original writing only. Reference official AWS docs by link; never reproduce book or documentation text.
- Beginner explanation first, architect trade-offs last — every page serves both.
- Mermaid for diagrams (renders on GitHub). Polished AWS-icon diagrams follow [docs/aws-icons](./docs/aws-icons/).
- Prices and limits change: state them as approximate and date-sensitive, and point readers at official pricing pages.
- Every claim of "runnable" must be backed by commands, validation, tests, and cleanup — no exceptions.
