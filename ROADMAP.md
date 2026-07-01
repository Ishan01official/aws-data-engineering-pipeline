# Roadmap

The progression from "I know some Python" to "I can design an enterprise data platform." Each level lists what to learn, the repo modules that teach it, and the signal that you're ready to move up.

## Beginner — get oriented and land your first data in a lake
- Cloud basics: regions, AZs, the account model, the console vs CLI vs IaC.
- Data engineering basics: the lifecycle (ingest→store→transform→serve), batch vs streaming, lake vs warehouse.
- Core services hands-on: S3, IAM, Lambda, Glue basics, Athena.
- **Modules:** 00, 01, 02 · **Labs:** 01, 02, 04, 05
- **Ready to advance when:** you can drop a file in S3, crawl it into the Glue Catalog, and query it in Athena — and explain why each step exists.

## Intermediate — build real batch pipelines
- S3 lake layout: bronze/silver/gold, partitioning, Parquet, lifecycle policies.
- Glue ETL with PySpark, crawlers, job bookmarks for incremental loads.
- Orchestration: Step Functions, EventBridge scheduling.
- Operations: data quality checks, CloudWatch monitoring, SNS alerts.
- **Modules:** 02, 03, 04, 06 · **Labs:** 03, 06, 07, 11
- **Ready to advance when:** you can build a scheduled, monitored, multi-stage Glue pipeline that fails safely and alerts you.

## Advanced — streaming, warehousing, and tuning
- Streaming: Kinesis, MSK, Managed Flink, exactly-once vs at-least-once, late data, replay.
- Redshift: dimensional modeling, distribution & sort keys, Spectrum, COPY, materialized views.
- EMR / EMR Serverless and Spark performance tuning.
- Governance: Lake Formation, DMS CDC.
- **Modules:** 05, 07, 08 + 04 (EMR) · **Labs:** 08, 09, 10
- **Ready to advance when:** you can choose correctly between streaming and batch for a given SLA, and model a star schema in Redshift with sensible keys.

## Architect — design platforms, not pipelines
- Multi-account design, dev/UAT/prod separation, environment config.
- Governance at scale, cost optimization as a design constraint, failure recovery (RTO/RPO).
- Service selection frameworks and trade-off reasoning.
- Enterprise platform design end to end.
- **Modules:** 09, 11, 12 · **Project:** 07 (capstone)
- **You're here when:** given a vague business requirement, you can produce a defensible architecture with explicit trade-offs, a cost model, and a failure plan.
