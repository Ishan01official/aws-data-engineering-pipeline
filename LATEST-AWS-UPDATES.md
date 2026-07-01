# Latest AWS Updates

> ⚠️ **This file goes stale by design.** AWS ships changes constantly. **Always verify with the official AWS docs, the AWS Big Data Blog, and AWS What's New** before relying on anything here. This file is a *starting pointer and a process*, not a source of truth.

Last reviewed: see git history. If that's old, treat everything below as "verify."

## How to keep this current (repeatable process)
1. Check the [official AWS documentation](https://docs.aws.amazon.com/) for the service.
2. Check the [AWS Big Data Blog](https://aws.amazon.com/blogs/big-data/).
3. Check [AWS What's New](https://aws.amazon.com/new/).
4. Update this changelog with date + one-line summary + link.
5. Update the affected module(s).
6. Add or update an example if the change affects how you'd build.

## Areas to track

### AWS Glue
Watch for: new Glue version / Spark runtime, Glue Data Quality enhancements, Glue for Ray, streaming improvements, and Catalog/Iceberg integration changes.

### Amazon EMR
Watch for: EMR Serverless capabilities, new application versions (Spark/Hive/Trino), Graviton support, and cost/performance features.

### Amazon Redshift
Watch for: Redshift Serverless features, zero-ETL integrations (e.g. from operational DBs), data sharing, materialized view improvements, and Spectrum/Iceberg querying.

### Lake Formation / DataZone / Governance
Watch for: fine-grained access enhancements, LF-Tags, and the evolution of DataZone / SageMaker Unified Studio as the org-wide governance and data-sharing surface.

### Apache Iceberg on AWS
Watch for: deeper Iceberg support across Glue, Athena, EMR, and Redshift; this is the most actively evolving area in the AWS lakehouse story — verify current support per engine.

### Serverless analytics
Watch for: Athena engine versions, Glue/EMR Serverless, Redshift Serverless, and zero-ETL patterns that reduce pipeline glue code.

### Spark version updates
Watch for: the Spark version bundled in current Glue and EMR releases — APIs and performance characteristics shift between versions.

### Certification (DEA-C01)
Watch for: exam guide revisions (published at least one month before they take effect). Re-check the [official exam guide](https://docs.aws.amazon.com/aws-certification/latest/examguides/data-engineer-associate-01.html) and update [CERTIFICATION-MAPPING.md](./CERTIFICATION-MAPPING.md).

## Changelog
| Date | Area | Change | Link |
|---|---|---|---|
| _add entries as you review_ | | | |
