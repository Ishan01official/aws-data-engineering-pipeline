# 02 · Security

How the lake is secured, and what the stack sets by default. Maps to DEA-C01 Domain 4.

## What the stack enforces
- **Encryption at rest:** SSE-S3 (`BucketEncryption.S3_MANAGED`) on every object. Upgrade to SSE-KMS with a customer-managed key when you need audit/control over the key itself (regulated data).
- **Encryption in transit:** `enforce_ssl=True` adds a policy denying non-HTTPS requests.
- **Block public access:** `BLOCK_ALL` on every bucket. A data lake is never public; this is set explicitly, not left to defaults.
- **Versioning:** on for raw/silver/gold, so a bad write or delete is recoverable.

## Least privilege
- Give each job/function a role scoped to exactly the buckets/prefixes it needs. A Glue job that reads raw and writes silver gets `s3:GetObject` on `raw/*` and `s3:PutObject` on `silver/*` — not `s3:*` on everything.
- Separate read and write roles where the blast radius justifies it.
- Never use the root account or long-lived keys for pipelines; use roles.

## Encryption choices
| Option | Key managed by | When |
|---|---|---|
| SSE-S3 | AWS | Default; simplest; fine for most internal data |
| SSE-KMS | You (KMS) | Need audit trail of key use, cross-account control, compliance |
| SSE-KMS + CMK | You (customer-managed) | Strict regulatory requirements |

## Fine-grained access
IAM controls access at the bucket/prefix level. For **column-level** or **row-level** access to lake tables (e.g. analysts can't see PII columns), that's **Lake Formation**, layered on top — Module 08.

## Auditing
Enable CloudTrail data events on sensitive buckets to record object-level access (who read what). CloudTrail answers "who did what"; CloudWatch covers operational metrics.

## Checklist
- [ ] Encryption at rest on (SSE-S3 or KMS)
- [ ] TLS enforced
- [ ] Public access blocked
- [ ] Versioning on for source-of-truth buckets
- [ ] Roles scoped least-privilege, no `s3:*`
- [ ] CloudTrail data events on sensitive prefixes
- [ ] KMS + Lake Formation for regulated/PII data (Module 08)
