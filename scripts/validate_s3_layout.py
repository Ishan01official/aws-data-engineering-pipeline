#!/usr/bin/env python3
"""
Validate that the expected raw-zone objects exist in an S3 data-lake bucket.

Purpose:
    After uploading, confirm each retail entity landed at its correct
    Hive-partitioned key. Use it as the Lab 01 validation step and as a
    lightweight pipeline health check.

Inputs (CLI):
    --bucket          Bucket to check (REQUIRED).
    --ingestion-date  Partition date YYYY-MM-DD (default: today).
    --profile         AWS CLI profile (optional).

Outputs:
    Prints PASS/FAIL per entity and exits non-zero if any expected object is
    missing (so it can gate a pipeline or CI step).

Run:
    python scripts/validate_s3_layout.py --bucket my-raw-bucket --ingestion-date 2026-07-01

Common errors:
    - AccessDenied: your identity needs s3:ListBucket / s3:GetObject on the bucket.
    - NoSuchBucket: check the name / region.

Cost warning:
    Read-only (HEAD/LIST). Effectively free. Creates nothing.
"""
from __future__ import annotations

import argparse
import logging

from pathlib import Path

log = logging.getLogger("validate_s3_layout")

try:
    from lake_layout import ENTITIES, default_filename, raw_key, today_iso, _DATE_RE
except ImportError:  # pragma: no cover
    from scripts.lake_layout import ENTITIES, default_filename, raw_key, today_iso, _DATE_RE


def object_exists(s3, bucket: str, key: str) -> bool:
    from botocore.exceptions import ClientError
    try:
        s3.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] in ("404", "NoSuchKey", "NotFound"):
            return False
        raise


def validate(bucket: str, ingestion_date: str, profile: str | None,
             region: str | None = None) -> int:
    try:
        import boto3
        from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError
    except ImportError:
        log.error("boto3 not installed. `pip install boto3`")
        return 2

    session = boto3.Session(profile_name=profile) if profile else boto3.Session()
    s3 = session.client("s3", region_name=region) if region else session.client("s3")

    expected = {
        entity: raw_key(entity, ingestion_date, default_filename(entity, ingestion_date))
        for entity in ENTITIES
    }

    all_ok = True
    try:
        for entity, key in expected.items():
            ok = object_exists(s3, bucket, key)
            status = "PASS" if ok else "FAIL"
            print(f"[{status}] {entity:9s} s3://{bucket}/{key}")
            all_ok = all_ok and ok
    except NoCredentialsError:
        log.error("no AWS credentials. Run `aws configure` or pass --profile.")
        return 2
    except (ClientError, BotoCoreError) as e:
        log.error("checking s3://%s failed: %s", bucket, e)
        return 1

    if all_ok:
        print(f"\nAll {len(expected)} expected objects present for {ingestion_date}.")
        return 0
    log.error("One or more expected objects are MISSING. Did upload run for this date?")
    return 1


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Validate raw-zone S3 layout for retail entities.")
    p.add_argument("--bucket", required=True, help="Bucket to validate.")
    p.add_argument("--ingestion-date", default=today_iso(),
                   help="Partition date YYYY-MM-DD (default: today).")
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
    return validate(args.bucket, args.ingestion_date, args.profile, region=args.region)


if __name__ == "__main__":
    raise SystemExit(main())
