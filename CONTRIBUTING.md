# Contributing & Conventions

This repo is a personal reference system, but it follows consistent conventions so it stays navigable as it grows.

- **One concept per file.** READMEs explain; `architect-notes.md` covers trade-offs; code files run.
- **Three-layer marking.** Sections are written through a cert / practitioner / architect lens; keep that explicit so readers can skim by depth.
- **Diagrams in Mermaid** for anything that renders inline; `.drawio` exports in `docs/diagrams/` for complex canvases.
- **Every code sample should run.** No pseudo-code passed off as real. If it needs setup, document the setup.
- **Cost is a first-class citizen.** Any architectural claim gets a `> 💰` callout where money is involved.
- **Link, don't copy.** AWS docs change; link the current source rather than freezing a copy.
