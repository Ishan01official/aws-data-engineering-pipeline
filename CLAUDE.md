# AWS Data Engineering Pipeline Repo Rules

This repo teaches AWS Data Engineering from beginner to senior architect level.

Do not create empty placeholders.
Do not leave TODO unless tracked in REPO-CONTENT-GAP-REPORT.md.
Do not claim code is runnable unless code, commands, validation, tests, and cleanup exist.
Build depth-first, not breadth-first.
Use simple professional English.
Every module must explain beginner concepts first, then senior architect trade-offs.
Every lab must have a cost warning and cleanup commands.
Every infrastructure file must avoid hardcoded AWS account IDs.
Never include secrets or real credentials.
Use least-privilege IAM where possible.
Use Mermaid diagrams for GitHub rendering.
Use AWS icon diagram instructions (docs/aws-icons/) instead of redistributing icons.
Follow CONTENT-STANDARD.md for every service page.

## Priority order

1. S3 + IAM + Lab 01
2. Glue Catalog + Lab 02
3. Glue ETL + Lab 03
4. Athena + Lab 04
5. Lambda S3 Trigger + Lab 05
6. EventBridge + Lab 06
7. Step Functions + Lab 07
8. Redshift + Lab 08
9. Kinesis + Lab 09
10. Lake Formation + Lab 10
11. CloudWatch + Lab 11
12. End-to-end production pipeline
13. Complex architect project

## Every lab must include

- Objective
- Business scenario
- Architecture diagram
- AWS services used
- Prerequisites
- Estimated cost
- Safety warning
- Step-by-step setup
- Code explanation
- Deployment commands
- Trigger commands
- Validation steps
- Expected output
- Troubleshooting
- Cleanup
- Interview questions
- Production notes
- Architect-level extension

## Verification before claiming anything works

- `python -m pytest tests/unit` must pass (use `.venv` — system Python has no pytest).
- `cdk synth` must succeed from `infra/cdk` (use `npx aws-cdk@2 synth` if the CLI is not installed globally).
- New markdown must contain no untracked TODO/scaffold/placeholder markers.
- Update REPO-CONTENT-GAP-REPORT.md and the README status section whenever content moves between scaffolded and complete.

## Repo conventions

- Sample data lives in `data/sample/` (tracked in git; tiny and fake only). Never commit real data, PII, or large files.
- S3 key layout logic lives only in `scripts/lake_layout.py`; every producer/validator imports it.
- Bucket names are never hardcoded; CDK derives them with an account+region suffix.
- Scripts use argparse, type hints, docstrings, logging, `--region`/`--profile`/`--dry-run` where meaningful, and non-zero exit codes on failure.
