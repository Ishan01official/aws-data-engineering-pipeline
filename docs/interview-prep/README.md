# Interview Prep

Interview questions organized by level and type. Each module also has its own `interview-questions.md` scoped to that service; this folder holds the cross-cutting sets.

## Categories (built out per module + here)
- **Beginner** — definitions and "what is X for" (lake vs warehouse, batch vs streaming).
- **Scenario** — "design a pipeline for…", service-selection under constraints.
- **Production incident** — "the nightly job failed / costs spiked / data is duplicated — what do you do?"
- **Architecture** — trade-offs, multi-account, governance, cost.
- **Certification** — DEA-C01-style scenario reasoning ([mapping](../../CERTIFICATION-MAPPING.md)).
- **Senior engineer** — idempotency, schema evolution, reconciliation, SLAs.

## Sample scenario (architecture)
> *"Design ingestion for a system that needs both a real-time fraud signal and accurate end-of-day reporting from the same transaction stream."*
> **What they're testing:** can you serve two latency needs from one source without over-building? A strong answer: durable stream (Kinesis/MSK) → real-time consumer (Flink/Lambda) for fraud, *and* the same stream landed to S3 (Firehose) for batch end-of-day marts. One source of truth, two read paths, each matched to its actual SLA.
