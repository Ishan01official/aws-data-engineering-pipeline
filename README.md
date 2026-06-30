# AWS Data Engineering — From Fundamentals to Architect

A structured, build-as-you-learn reference for becoming effective at data engineering on AWS. It is designed to do three things at once, layered so you can read at whatever depth you need:

1. **Certification track** — everything mapped to the AWS Certified Data Engineer – Associate (DEA-C01) exam domains, so the same material that makes you competent also makes you certified.
2. **Practitioner track** — runnable code, realistic pipelines, and the operational details (logging, idempotency, cost) that separate a demo from a system someone has to keep alive at 3am.
3. **Architect track** — the *why*: service trade-offs, decision frameworks, failure modes, and the patterns that recur across real data platforms.

Each module carries all three layers. A `📘 Cert`, `🔧 Practitioner`, and `🏛 Architect` marker tells you which lens a section is written through, so you can skim or go deep deliberately.

---

## How to use this repo

This is not a tutorial you read front-to-back in one sitting and forget. It is a reference system you work *through* and come *back* to. The recommended path:

- Read a module's `README.md` for the mental model and the diagram.
- Do the lab in `labs/` for that module — the concepts only stick once you've broken something and fixed it.
- Skim the `architect-notes.md` after the lab, when the trade-offs will actually mean something to you.

If you are studying for the cert specifically, `10-cert-prep/` has the domain-by-domain mapping and a "what they actually test" guide that points back into the modules.

---

## Module map

| # | Module | Core question it answers | Cert domain |
|---|--------|--------------------------|-------------|
| 00 | [Foundations](./00-foundations/) | What *is* data engineering, and what problem is each AWS service actually solving? | All |
| 01 | [AWS Core Services](./01-aws-core-services/) | IAM, VPC, the account model — the substrate everything else sits on. | 4 |
| 02 | [Storage & the S3 Data Lake](./02-storage-s3-lake/) | Where does data live, and how do you lay it out so it stays cheap and queryable? | 2 |
| 03 | [Ingestion](./03-ingestion/) | How does data get *in* — batch, CDC, streaming, file drops? | 1 |
| 04 | [Batch Processing](./04-batch-processing/) | Glue, EMR, Spark — transforming data at rest, at scale. | 1, 2 |
| 05 | [Streaming](./05-streaming/) | Kinesis, MSK, Flink — transforming data in motion. | 1 |
| 06 | [Orchestration](./06-orchestration/) | Step Functions, MWAA, EventBridge — making pipelines run reliably and in order. | 1, 3 |
| 07 | [Data Warehouse (Redshift)](./07-data-warehouse-redshift/) | Serving analytics — modeling, distribution, performance. | 2, 3 |
| 08 | [Governance & Security](./08-governance-security/) | Lake Formation, encryption, lineage, PII — keeping data safe and legal. | 4 |
| 09 | [Architecture Patterns](./09-architecture-patterns/) | How do you assemble the pieces? Lambda vs Kappa, medallion, lakehouse. | All |
| 10 | [Certification Prep](./10-cert-prep/) | Domain mapping, exam strategy, practice scenarios. | All |

---

## Conventions used throughout

- **Diagrams** are authored in [Mermaid](https://mermaid.js.org/) (renders directly in GitHub) with `draw.io` (`.drawio`) exports in [`docs/diagrams/`](./docs/diagrams/) for the ones complex enough to deserve a real canvas.
- **Code** is Python-first (boto3, PySpark, AWS SDK) because that is what the field runs on. Each snippet is meant to run, not just illustrate.
- **Cost callouts** appear as `> 💰` blocks. On AWS, an architecture you can't afford is a wrong architecture, so cost is treated as a first-class design constraint, not an afterthought.
- **Trade-off tables** appear wherever a decision has more than one defensible answer. The goal is to teach you to *choose*, not to memorize one blessed path.

---

## Source material & honest scope

This curriculum is original writing. It is informed by the standard canon of the field — Reis & Housley's *Fundamentals of Data Engineering*, the *Data Engineering with AWS* titles, and the official DEA-C01 exam guide — but it does not reproduce them. Where a concept maps cleanly to AWS's own documentation, the doc is linked rather than copied, because AWS docs change and you should learn to read the current source.

If something here ever conflicts with the [official exam guide](https://aws.amazon.com/certification/certified-data-engineer-associate/) or current AWS docs, trust those. This repo is a teacher, not an authority.

---

## Status

Built module-by-module. See each module's README for completeness. Foundations (00) is the reference depth target — if a later module feels thinner, it's still in progress.
