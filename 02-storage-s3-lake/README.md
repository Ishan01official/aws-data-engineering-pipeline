# 02 · Storage & the S3 Data Lake

> **Status:** planned — scaffolded, full build pending. Module 00 (Foundations) is the depth target this module will match.

## What this module covers

S3 deeply: storage classes, partitioning, Parquet vs CSV/JSON, the medallion layout, Athena query-in-place, and Iceberg table format.

**Cert domain:** 2 (Data Store Management)

## Planned contents

- `README.md` — the mental model, Mermaid architecture diagram, and the core trade-offs (cert / practitioner / architect layers).
- `architect-notes.md` — service-selection decision frameworks and failure modes specific to this stage.
- Runnable code (boto3 / PySpark / SQL as appropriate), each snippet meant to actually run.
- A hands-on lab under [`../labs/`](../labs/).

## Where it sits in the pipeline

This module is one stage of the end-to-end pipeline mapped in [Module 00](../00-foundations/). Read Foundations first if you haven't.
