# Contributing & Conventions

This is a structured reference system. Consistency is what keeps it navigable as it grows.

## File conventions
- **Modules** use the standard 15-file structure (README + concept, architecture, service-decision, industry-use-cases, code-walkthrough, deployment, monitoring, troubleshooting, cost, security, interview-questions, certification-notes, mistakes-to-avoid, hands-on-lab).
- **Labs** use the standard template: Objective · Architecture · Prerequisites · 💰 Cost warning · Steps · Code · Validation · Cleanup · Interview questions · Production notes.
- One concept per file. READMEs explain; `architect`/`service-decision` files cover trade-offs; code runs.

## Teaching pattern (every service)
Simple explanation → why it exists → where it fits → real industry use (e-commerce / finance / IoT) → how it works internally → hands-on code → deployment → triggering → monitoring → security → cost → troubleshooting → architect decision.

## Quality rules
- Every explanation is practical, not theory-only, and connects to pipeline design.
- Every code sample should run, or is clearly marked **example only**.
- Cost is first-class: any architectural claim involving money gets a `💰` note.
- **Every AWS lab has a mandatory cleanup step.** Never leave paid resources running without warning.
- Use placeholders (`REPLACE_ACCOUNT_ID`, `REPLACE_REGION`, `REPLACE_BUCKET`, role ARNs). Never commit secrets, credentials, or real account details.
- Least-privilege IAM in all examples; config via env vars / config files.
- Diagrams: Mermaid inline (renders on GitHub); draw.io + AWS icons for hero diagrams (see `docs/aws-icons/`).
- Don't copy copyrighted book content — original explanations, link to sources.
- Mark unfinished content clearly as **TODO**; no silent empty placeholders.

## Markdown
Verify diagrams and links render on GitHub before committing. The `lint-docs` workflow checks links.
