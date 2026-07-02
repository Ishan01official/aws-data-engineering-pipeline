#!/usr/bin/env python3
"""
Validate the Glue Data Catalog state after the Lab 02 crawler run.

Purpose:
    Prove the crawler did its job: the database exists, one table exists per
    retail entity with the expected columns, each table is partitioned by
    ingestion_date, and the expected partition is registered. Exits non-zero
    on any failure, so it can gate a pipeline or CI step — the catalog
    equivalent of validate_s3_layout.py.

Inputs (CLI):
    --database        Glue database name (default: retail_lake).
    --crawler         Crawler name to check/wait on (default: retail-raw-crawler).
    --ingestion-date  Partition expected to be registered, YYYY-MM-DD (default: today).
    --wait            Poll the crawler until READY before validating (up to --timeout).
    --timeout         Max seconds to wait for the crawler (default: 900).
    --profile         AWS CLI profile (optional).
    --region          AWS region override (optional).

Outputs:
    PASS/FAIL per check on stdout; exit 0 all pass, 1 validation failure,
    2 usage/environment error.

Run:
    python scripts/validate_glue_catalog.py --wait --ingestion-date 2026-07-01

Cost warning:
    Read-only Glue API calls. Effectively free. Creates nothing.
"""
from __future__ import annotations

import argparse
import logging
import time

try:
    from lake_layout import _DATE_RE, today_iso
except ImportError:  # pragma: no cover
    from scripts.lake_layout import _DATE_RE, today_iso

log = logging.getLogger("validate_glue_catalog")

# Expected schema per entity: column names the crawler should have inferred
# from the CSV headers (types are engine-inferred and not asserted here).
EXPECTED_COLUMNS = {
    "orders": ["order_id", "customer_id", "product_id", "order_ts", "quantity",
               "unit_price", "currency", "status"],
    "customers": ["customer_id", "customer_name", "email", "country",
                  "signup_date", "customer_segment"],
    "products": ["product_id", "product_name", "category", "brand",
                 "list_price", "currency"],
}
PARTITION_KEY = "ingestion_date"


def wait_for_crawler(glue, crawler: str, timeout: int) -> tuple[bool, str]:
    """Poll until the crawler is READY. Returns (ok, last_status_message)."""
    deadline = time.time() + timeout
    while True:
        resp = glue.get_crawler(Name=crawler)["Crawler"]
        state = resp["State"]
        if state == "READY":
            last = resp.get("LastCrawl", {})
            status = last.get("Status", "UNKNOWN")
            return status == "SUCCEEDED", f"last crawl status: {status}"
        if time.time() > deadline:
            return False, f"timed out after {timeout}s in state {state}"
        log.info("crawler %s is %s; waiting...", crawler, state)
        time.sleep(15)


def find_entity_table(tables: list[dict], entity: str) -> dict | None:
    """Locate the table for an entity by name substring (crawler-derived
    names like raw_entity_orders vary in prefix/sanitization details)."""
    matches = [t for t in tables if entity in t["Name"]]
    return matches[0] if matches else None


def check_table(table: dict, entity: str) -> list[str]:
    """Return a list of problems (empty = table is as expected)."""
    problems = []
    pkeys = [k["Name"] for k in table.get("PartitionKeys", [])]
    if pkeys != [PARTITION_KEY]:
        problems.append(f"partition keys {pkeys}, expected ['{PARTITION_KEY}']")
    cols = [c["Name"] for c in table.get("StorageDescriptor", {}).get("Columns", [])]
    missing = [c for c in EXPECTED_COLUMNS[entity] if c not in cols]
    if missing:
        problems.append(f"missing columns {missing} (crawler saw: {cols})")
    return problems


def partition_registered(glue, database: str, table_name: str,
                         ingestion_date: str) -> bool:
    resp = glue.get_partitions(
        DatabaseName=database, TableName=table_name,
        Expression=f"{PARTITION_KEY} = '{ingestion_date}'",
    )
    return len(resp.get("Partitions", [])) > 0


def validate(glue, database: str, ingestion_date: str) -> int:
    """Run all catalog checks with the given Glue client. Returns exit code."""
    from botocore.exceptions import ClientError

    try:
        glue.get_database(Name=database)
        print(f"[PASS] database  {database} exists")
    except ClientError as e:
        if e.response["Error"]["Code"] == "EntityNotFoundException":
            print(f"[FAIL] database  {database} not found — was the stack deployed?")
            return 1
        raise

    tables: list[dict] = []
    paginator = glue.get_paginator("get_tables")
    for page in paginator.paginate(DatabaseName=database):
        tables.extend(page["TableList"])

    all_ok = True
    for entity in EXPECTED_COLUMNS:
        table = find_entity_table(tables, entity)
        if table is None:
            print(f"[FAIL] table     no table for '{entity}' "
                  f"(found: {[t['Name'] for t in tables] or 'none'}) — did the crawler run?")
            all_ok = False
            continue
        problems = check_table(table, entity)
        if problems:
            print(f"[FAIL] table     {table['Name']}: {'; '.join(problems)}")
            all_ok = False
        else:
            print(f"[PASS] table     {table['Name']} schema + partition key OK")
            if partition_registered(glue, database, table["Name"], ingestion_date):
                print(f"[PASS] partition {table['Name']} {PARTITION_KEY}={ingestion_date}")
            else:
                print(f"[FAIL] partition {table['Name']} has no "
                      f"{PARTITION_KEY}={ingestion_date} — wrong date, or crawler "
                      f"ran before upload?")
                all_ok = False

    if all_ok:
        print(f"\nCatalog validation passed: {len(EXPECTED_COLUMNS)} entity tables, "
              f"partitioned and registered for {ingestion_date}.")
        return 0
    print("\nCatalog validation FAILED — see [FAIL] lines above and "
          "labs/lab-02-glue-crawler-catalog/README.md troubleshooting.")
    return 1


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Validate the Glue catalog after the Lab 02 crawl.")
    p.add_argument("--database", default="retail_lake", help="Glue database name.")
    p.add_argument("--crawler", default="retail-raw-crawler", help="Crawler name.")
    p.add_argument("--ingestion-date", default=today_iso(),
                   help="Partition date YYYY-MM-DD expected in the catalog (default: today).")
    p.add_argument("--wait", action="store_true",
                   help="Wait for the crawler to reach READY before validating.")
    p.add_argument("--timeout", type=int, default=900,
                   help="Max seconds to wait for the crawler (default: 900).")
    p.add_argument("--profile", default=None, help="AWS CLI profile (optional).")
    p.add_argument("--region", default=None,
                   help="AWS region override (optional; defaults to your CLI config).")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    args = parse_args(argv)
    if not _DATE_RE.match(args.ingestion_date):
        log.error("--ingestion-date must be YYYY-MM-DD, got %r", args.ingestion_date)
        return 2

    try:
        import boto3
        from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError
    except ImportError:
        log.error("boto3 not installed. `pip install boto3`")
        return 2

    session = boto3.Session(profile_name=args.profile) if args.profile else boto3.Session()
    glue = session.client("glue", region_name=args.region) if args.region \
        else session.client("glue")

    try:
        if args.wait:
            ok, msg = wait_for_crawler(glue, args.crawler, args.timeout)
            print(f"[{'PASS' if ok else 'FAIL'}] crawler   {args.crawler} — {msg}")
            if not ok:
                return 1
        return validate(glue, args.database, args.ingestion_date)
    except NoCredentialsError:
        log.error("no AWS credentials. Run `aws configure` or pass --profile.")
        return 2
    except (ClientError, BotoCoreError) as e:
        log.error("Glue API error: %s", e)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
