# Industry Use Cases

The same AWS building blocks, arranged differently per industry. For each: data sources, the pipeline pattern, key services, batch/streaming balance, security concerns, cost concerns, and a sketch architecture. Use these to ground abstract services in real problems.

## Retail / E-commerce
- **Sources:** POS/sales (CSV/DB), product & inventory (RDS), clickstream (events), SaaS marketing (AppFlow).
- **Pattern:** medallion lakehouse — raw → cleaned → marts — feeding BI and recommendations.
- **Services:** S3, DMS, Kinesis Firehose, Glue, Athena, Redshift, Lake Formation.
- **Batch/streaming:** mostly batch (daily/hourly sales marts) with streaming clickstream for near-real-time behavior.
- **Security:** customer PII (Lake Formation column access, Macie). **Cost:** clickstream volume — partition aggressively, Parquet.
- This is the repo's **capstone** ([project 07](./projects/project-07-enterprise-data-platform/)).

## Banking / Finance
- **Sources:** transactions (CDC from core banking), market data feeds, customer data.
- **Pattern:** CDC ingestion + strict governance; often a regulated warehouse layer.
- **Services:** DMS, Kinesis/MSK, Glue, Redshift, Lake Formation, KMS (customer-managed keys), CloudTrail.
- **Batch/streaming:** streaming for fraud detection (millisecond decisions); batch for regulatory reporting.
- **Security:** the dominant concern — encryption everywhere, row/column security, immutable audit, data residency. **Cost:** secondary to compliance.

## Healthcare
- **Sources:** EHR systems, device telemetry, claims.
- **Pattern:** highly governed lake with strict PII/PHI controls; lineage and audit are first-class.
- **Services:** S3, Glue, Lake Formation, Macie, KMS, CloudTrail.
- **Batch/streaming:** batch for claims/analytics; streaming for device/patient monitoring.
- **Security:** PHI handling, HIPAA alignment, minimum-necessary access, encryption and masking. **Cost:** retention of large imaging/telemetry → lifecycle tiering.

## Manufacturing / IoT
- **Sources:** sensor/telemetry streams, MES/ERP, maintenance logs.
- **Pattern:** high-volume streaming ingest → time-series storage → anomaly detection.
- **Services:** IoT Core/Kinesis/MSK, Managed Flink, S3, Timestream/Redshift.
- **Batch/streaming:** streaming-heavy (real-time equipment monitoring) plus batch trend analysis.
- **Security:** device identity, network isolation. **Cost:** raw telemetry volume — aggregate early, tier aggressively.

## SaaS / Product Analytics
- **Sources:** app events, billing, support, third-party SaaS.
- **Pattern:** event pipeline → warehouse → product/usage analytics; often ELT.
- **Services:** Kinesis/Firehose, S3, Glue, Redshift/Athena, AppFlow.
- **Batch/streaming:** event streaming to S3, batch transforms to marts.
- **Security:** tenant isolation, customer data segregation. **Cost:** event volume and warehouse compute — model the hot marts.

## Media / Entertainment
- **Sources:** playback/streaming events, content metadata, ad telemetry.
- **Pattern:** massive clickstream → real-time engagement + batch content analytics.
- **Services:** Kinesis, Flink, S3, Redshift, OpenSearch (search/recommendations).
- **Batch/streaming:** streaming engagement metrics, batch content performance.
- **Security:** content rights, viewer privacy. **Cost:** enormous event volume — this is where partitioning/columnar discipline pays most.

## Finance Analytics (buy/sell-side)
- **Sources:** market data, positions, risk feeds.
- **Pattern:** low-latency ingest + heavy compute (risk/analytics) + governed warehouse.
- **Services:** MSK/Kinesis, EMR (heavy Spark), Redshift, Lake Formation.
- **Batch/streaming:** both — streaming market data, batch overnight risk.
- **Security:** strict access and audit. **Cost:** EMR compute — right-size and use Spot/Serverless.

> The lesson across all of these: the *services* are a small, stable toolkit. The *arrangement* — driven by latency needs, data volume, and regulatory weight — is the engineering. That's what the [Service Decision Framework](./SERVICE-DECISION-FRAMEWORK.md) trains.
