# AWS Architecture Icons

This repo does **not** bundle AWS's official icon assets, because they're distributed under AWS's own terms and shouldn't be redistributed in a third-party repo. Instead, here's how to get and use them correctly.

## Get the official icons
1. Download the latest **AWS Architecture Icons** toolkit from the official page: https://aws.amazon.com/architecture/icons/
2. Review the usage terms on that page before using the assets — they govern how AWS icons may be used.
3. Unzip locally. The toolkit includes PNG/SVG icons and the official drawing guidelines.

## How we use diagrams in this repo
- **For GitHub rendering:** we use **Mermaid** diagrams inline in Markdown — they render natively on GitHub with no assets to manage. Every module has them.
- **For polished architecture diagrams:** use **draw.io / diagrams.net**, which has a built-in AWS icon shape library (or import the official toolkit). Save `.drawio` source in [`../diagrams/`](../diagrams/) plus a PNG/SVG export for embedding.

## Convention
- Keep Mermaid as the source of truth for flow logic (versionable, diffable).
- Use draw.io + AWS icons for the "hero" architecture image in a project README.
- Do not commit the downloaded AWS icon toolkit into this repo; reference it locally.

## Suggested diagrams to create with the official icons

When you want polished, portfolio-grade versions of this repo's Mermaid diagrams, recreate these in draw.io/diagrams.net with the AWS shape library (source `.drawio` + exported PNG go in [`../diagrams/`](../diagrams/)):

1. **Medallion data lake** — five S3 buckets (raw/bronze/silver/gold/results) with the Glue Catalog, Athena, and Redshift consumers. Source: [Module 02 · architecture.md](../../02-storage-s3-lake/architecture.md).
2. **Lab 01 flow** — local CSVs → upload script → raw zone → (future) Glue/Athena. Source: [Lab 01 README](../../labs/lab-01-s3-data-lake/README.md).
3. **Event-driven ingestion** — S3 event → EventBridge → Lambda/Step Functions with SNS/SQS fan-out and DLQs. Source: [Module 01 · eventbridge.md](../../01-aws-core-services/eventbridge.md) and [sqs-sns.md](../../01-aws-core-services/sqs-sns.md).
4. **Pipeline orchestration** — EventBridge → Step Functions → Glue → quality gate → SNS, with retry/catch paths. Source: [Module 01 · step-functions.md](../../01-aws-core-services/step-functions.md).
5. **The capstone platform** — the full enterprise architecture from the root README, once the later modules are built.

Drawing conventions from the official AWS guidelines: service icons at consistent size, group boxes for VPC/account/zone boundaries, arrows labeled with the *action* (not just "→"), and a legend when you use more than ~8 services.
