#!/usr/bin/env python3
"""
Shared helpers for the retail data-lake S3 key layout.

Purpose:
    One source of truth for how raw-zone S3 keys are constructed, so the upload
    script, the validation script, and the unit tests can never drift apart.

Prefix design (raw zone):
    raw/source=retail/entity=<entity>/ingestion_date=<YYYY-MM-DD>/<filename>

Why Hive-style key=value partitions:
    Crawlers (Glue) and query engines (Athena, Spectrum) recognize the
    `key=value` folder convention and automatically expose `source`, `entity`,
    and `ingestion_date` as partition columns — enabling partition pruning at
    query time without extra configuration.
"""
from __future__ import annotations

import re
from datetime import date

ENTITIES = ("orders", "customers", "products")
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def raw_prefix(entity: str, ingestion_date: str, source: str = "retail") -> str:
    """Return the raw-zone prefix (no filename) for an entity + date.

    >>> raw_prefix("orders", "2026-07-01")
    'raw/source=retail/entity=orders/ingestion_date=2026-07-01/'
    """
    if entity not in ENTITIES:
        raise ValueError(f"unknown entity {entity!r}; expected one of {ENTITIES}")
    if not _DATE_RE.match(ingestion_date):
        raise ValueError(f"ingestion_date must be YYYY-MM-DD, got {ingestion_date!r}")
    return f"raw/source={source}/entity={entity}/ingestion_date={ingestion_date}/"


def raw_key(entity: str, ingestion_date: str, filename: str, source: str = "retail") -> str:
    """Return the full raw-zone S3 key including filename."""
    if not filename or "/" in filename:
        raise ValueError(f"filename must be a bare file name, got {filename!r}")
    return raw_prefix(entity, ingestion_date, source) + filename


def default_filename(entity: str, ingestion_date: str) -> str:
    """Conventional filename, e.g. orders_2026_07_01.csv."""
    return f"{entity}_{ingestion_date.replace('-', '_')}.csv"


def today_iso() -> str:
    return date.today().isoformat()
