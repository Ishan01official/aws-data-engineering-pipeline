#!/usr/bin/env python3
"""
Create the local data-lake folder layout (raw/bronze/silver/gold).

Purpose:
    Mirror the S3 medallion zone structure on your local disk so you can stage
    and inspect data before/without uploading to AWS. Useful for Lab 01 dry-runs
    and for understanding the zone layout with zero cost.

Inputs (CLI):
    --base   Base directory to create the lake under (default: ./local-lake)

Outputs:
    Creates <base>/raw, <base>/bronze, <base>/silver, <base>/gold with a small
    .gitkeep-style README in each so the zones are self-describing.

Run locally:
    python scripts/create_local_lake_layout.py --base ./local-lake

Deploy:
    N/A — local only, creates no AWS resources.

Common errors:
    - PermissionError: you don't have write access to --base. Choose a writable path.

Cost warning:
    None. This script is entirely local and free.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ZONES = {
    "raw": "Landing zone. Exactly as received from the source. Immutable, never edited.",
    "bronze": "Raw promoted/typed with minimal cleaning. Often same as raw in simple lakes.",
    "silver": "Cleaned, validated, deduplicated. Parquet, partitioned. Query-ready.",
    "gold": "Business-ready aggregates and marts. What BI and Redshift consume.",
}


def create_layout(base: Path) -> list[Path]:
    """Create the zone folders under base. Returns the list of created dirs."""
    created = []
    for zone, desc in ZONES.items():
        d = base / zone
        d.mkdir(parents=True, exist_ok=True)
        (d / "README.md").write_text(f"# {zone} zone\n\n{desc}\n", encoding="utf-8")
        created.append(d)
    return created


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Create local data-lake zone folders.")
    p.add_argument("--base", default="./local-lake",
                   help="Base directory for the local lake (default: ./local-lake)")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    base = Path(args.base).expanduser().resolve()
    try:
        created = create_layout(base)
    except PermissionError as e:
        print(f"ERROR: cannot write under {base}: {e}", file=sys.stderr)
        return 1
    print(f"Created local lake at: {base}")
    for d in created:
        print(f"  - {d.relative_to(base.parent)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
