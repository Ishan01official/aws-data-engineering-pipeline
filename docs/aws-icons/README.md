# AWS Architecture Icons

This repo does **not** bundle AWS's official icon assets, because they're distributed under AWS's own terms and shouldn't be redistributed in a third-party repo. Instead, here's how to get and use them correctly.

## Get the official icons
1. Download the latest **AWS Architecture Icons** toolkit from the official page: https://aws.amazon.com/architecture/icons/
2. Review the usage terms on that page before using the assets — they govern how AWS icons may be used.
3. Unzip locally. The toolkit includes PNG/SVG icons and the official drawing guidelines.

## How we use diagrams in this repo
- **For GitHub rendering:** we use **Mermaid** diagrams inline in Markdown — they render natively on GitHub with no assets to manage. Every module has them.
- **For polished architecture diagrams:** use **draw.io / diagrams.net**, which has a built-in AWS icon shape library (or import the official toolkit). Save `.drawio` source in [`../diagrams/`](../diagrams/) plus a PNG/SVG export for embedding.

## Convention
- Keep Mermaid as the source of truth for flow logic (versionable, diffable).
- Use draw.io + AWS icons for the "hero" architecture image in a project README.
- Do not commit the downloaded AWS icon toolkit into this repo; reference it locally.
