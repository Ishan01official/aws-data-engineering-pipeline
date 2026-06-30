# 03 · Ingestion

> **Status:** planned — scaffolded, full build pending. Module 00 (Foundations) is the depth target this module will match.

## What this module covers

Getting data in: batch file drops, DMS change-data-capture, Kinesis Firehose, and the SNS-triggered Lambda routing pattern with idempotent keys and structured logging.

**Cert domain:** 1 (Data Ingestion & Transformation)

## Planned contents

- `README.md` — the mental model, Mermaid architecture diagram, and the core trade-offs (cert / practitioner / architect layers).
- `architect-notes.md` — service-selection decision frameworks and failure modes specific to this stage.
- Runnable code (boto3 / PySpark / SQL as appropriate), each snippet meant to actually run.
- A hands-on lab under [`../labs/`](../labs/).

## Where it sits in the pipeline

This module is one stage of the end-to-end pipeline mapped in [Module 00](../00-foundations/). Read Foundations first if you haven't.
