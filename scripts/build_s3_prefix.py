#!/usr/bin/env python3
"""
Build a raw-zone S3 key (or prefix) from source, entity, date, and filename.

Purpose:
    A small CLI over the shared `lake_layout` helpers, so you can construct and
    inspect the exact Hive-partitioned key the pipeline uses — from the shell,
    from CI, or from another script — without duplicating the layout logic.

Inputs (CLI):
    --source          Source system name (default: retail).
    --entity          One of: orders, customers, products (REQUIRED).
    --ingestion-date  Partition date YYYY-MM-DD (default: today).
    --filename        File name to append. Omit to print only the prefix.
    --bucket          Optional bucket; if given, prints a full s3:// URI.

Outputs:
    Prints the key/prefix (or s3:// URI) to stdout. Exit code 0 on success,
    2 on invalid input.

Run locally (no AWS needed — pure string building):
    python scripts/build_s3_prefix.py --entity orders --ingestion-date 2026-07-01 \
        --filename orders_2026_07_01.csv
    # -> raw/source=retail/entity=orders/ingestion_date=2026-07-01/orders_2026_07_01.csv

Cost warning:
    None. This script makes no AWS calls.
"""
from __future__ import annotations

import argparse
import logging
import sys

try:
    from lake_layout import ENTITIES, raw_key, raw_prefix, today_iso
except ImportError:  # pragma: no cover
    from scripts.lake_layout import ENTITIES, raw_key, raw_prefix, today_iso

log = logging.getLogger("build_s3_prefix")


def build(entity: str, ingestion_date: str, filename: str | None,
          source: str = "retail", bucket: str | None = None) -> str:
    """Return the raw-zone key (with filename) or prefix (without).

    Raises ValueError on invalid entity/date/filename — same rules as
    `lake_layout`. Unit-testable with no AWS.
    """
    if filename:
        key = raw_key(entity, ingestion_date, filename, source=source)
    else:
        key = raw_prefix(entity, ingestion_date, source=source)
    return f"s3://{bucket}/{key}" if bucket else key


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Build the Hive-partitioned raw-zone S3 key for an entity.")
    p.add_argument("--source", default="retail", help="Source system (default: retail).")
    p.add_argument("--entity", required=True, choices=ENTITIES,
                   help="Entity to build the key for.")
    p.add_argument("--ingestion-date", default=today_iso(),
                   help="Partition date YYYY-MM-DD (default: today).")
    p.add_argument("--filename", default=None,
                   help="Filename to append; omit to print only the prefix.")
    p.add_argument("--bucket", default=None,
                   help="If given, print a full s3://<bucket>/<key> URI.")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    args = parse_args(argv)
    try:
        print(build(args.entity, args.ingestion_date, args.filename,
                    source=args.source, bucket=args.bucket))
    except ValueError as e:
        log.error("%s", e)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
