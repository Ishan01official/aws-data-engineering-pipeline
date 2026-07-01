# Security & Governance

The cross-cutting reference for keeping data safe and legal. Module 08 goes deep; this is the platform-wide view. Maps to **DEA-C01 Domain 4**.

## The layered model
Security on AWS data platforms is layered — each layer assumes the others might fail.

1. **Identity (authentication):** who are you? IAM users/roles, federation, MFA. Pipelines authenticate as **roles**, never long-lived keys.
2. **Authorization (access):** what can you do? IAM policies for coarse access; **Lake Formation** for fine-grained (column/row/tag-based) access to lake data; Redshift grants for warehouse access.
3. **Encryption:** at rest (KMS — SSE-S3 or SSE-KMS) and in transit (TLS everywhere). Customer-managed KMS keys when you need control/audit over key usage.
4. **Secrets:** never in code. **Secrets Manager** for credentials (with rotation), **SSM Parameter Store** for config.
5. **Audit:** **CloudTrail** records who did what (control plane); CloudWatch covers operational metrics. Logs are prepared for audit and retained per policy.
6. **Privacy:** **Macie** identifies PII in S3; Lake Formation enforces who can see it; masking/tokenization for sensitive columns.

## Least-privilege in practice
- One role per job/function, scoped to exactly the buckets/prefixes/tables it touches.
- No `*` resources in production policies. Name the ARNs (use placeholders in this repo: `arn:aws:s3:::REPLACE_BUCKET/*`).
- Separate read and write roles where the blast radius justifies it.
- Use **OIDC** for CI/CD (GitHub Actions assumes a role) instead of storing AWS keys in the CI system. → Module 11.

## Fine-grained access: when IAM isn't enough
IAM grants access at the bucket/prefix level. When you need:
- **Column-level** ("analysts can't see SSN") → Lake Formation column permissions.
- **Row-level** ("regional managers see only their region") → Lake Formation row filters.
- **Tag-based central governance** across many tables → LF-Tags.

…that's Lake Formation, layered on top of IAM. → Module 08.

## PII handling checklist
- [ ] Identify PII (Macie scan of S3).
- [ ] Classify and tag data (LF-Tags / data classification).
- [ ] Restrict access (Lake Formation column/row permissions).
- [ ] Encrypt (KMS at rest, TLS in transit).
- [ ] Mask/tokenize where full values aren't needed.
- [ ] Audit access (CloudTrail) and retain logs.
- [ ] Prevent unauthorized copies/replication of sensitive data.

## Governance beyond access
- **Catalog as contract:** the Glue Data Catalog is the shared schema contract; version and review changes to it.
- **Lineage:** know where data came from and what transformed it (for trust and debugging).
- **Data quality gates:** bad data is a governance problem — quarantine, alert, don't promote. → Module 11.
- **DataZone / SageMaker Unified Studio:** AWS's higher-level data governance and cataloging surface for organization-wide data sharing and discovery (overview in Module 08).

> Align with the AWS **Well-Architected Framework Security Pillar** and **Data Analytics Lens**. Verify service capabilities against current AWS docs — governance services evolve quickly.
