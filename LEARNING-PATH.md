# Learning Path

A concrete order to work through the repo. The [ROADMAP](./ROADMAP.md) is the "what/why" by level; this is the "do this, then this."

## How to study each module
1. Read `README.md` — the mental model and diagram.
2. Read `concept.md` for first-principles depth.
3. Do the linked lab (`hands-on-lab.md` → `labs/`).
4. Read `service-decision.md` and `architecture.md` once you've built something.
5. Skim `mistakes-to-avoid.md` and `interview-questions.md`.
6. Check `certification-notes.md` against the [cert mapping](./CERTIFICATION-MAPPING.md).

## Suggested 9-week order
| Week | Focus | Modules | Labs |
|---|---|---|---|
| 1 | Foundations + account safety | 00, 01 | account setup, 01 |
| 2 | S3 lake + catalog + query | 02 | 01, 02, 04 |
| 3 | Ingestion patterns | 03 | 05 |
| 4 | Glue ETL + data quality | 04 | 03 |
| 5 | Orchestration + monitoring | 06 | 06, 07, 11 |
| 6 | Redshift + modeling | 07 | 08 |
| 7 | Streaming | 05 | 09 |
| 8 | Security + governance | 08 | 10 |
| 9 | Patterns + capstone + cert review | 09, 10, 11, 12 | 12, 13 |

## If you only have time for the essentials (job-ready core)
Modules 00, 02, 03, 04, 06 and Labs 01–07. That's the spine: lake, ingest, transform, orchestrate, monitor. Everything else deepens it.
