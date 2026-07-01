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
import sys
from pathlib import Path

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


def validate(bucket: str, ingestion_date: str, profile: str | None) -> int:
    try:
        import boto3
        from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError
    except ImportError:
        print("ERROR: boto3 not installed. `pip install boto3`", file=sys.stderr)
        return 2

    session = boto3.Session(profile_name=profile) if profile else boto3.Session()
    s3 = session.client("s3")

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
        print("ERROR: no AWS credentials. Run `aws configure` or pass --profile.",
              file=sys.stderr)
        return 2
    except (ClientError, BotoCoreError) as e:
        print(f"ERROR checking s3://{bucket}: {e}", file=sys.stderr)
        return 1

    if all_ok:
        print(f"\nAll {len(expected)} expected objects present for {ingestion_date}.")
        return 0
    print("\nOne or more expected objects are MISSING. Did upload run for this date?",
          file=sys.stderr)
    return 1


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Validate raw-zone S3 layout for retail entities.")
    p.add_argument("--bucket", required=True, help="Bucket to validate.")
    p.add_argument("--ingestion-date", default=today_iso(),
                   help="Partition date YYYY-MM-DD (default: today).")
    p.add_argument("--profile", default=None, help="AWS CLI profile (optional).")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not _DATE_RE.match(args.ingestion_date):
        print(f"ERROR: --ingestion-date must be YYYY-MM-DD, got {args.ingestion_date!r}",
              file=sys.stderr)
        return 2
    return validate(args.bucket, args.ingestion_date, args.profile)


if __name__ == "__main__":
    raise SystemExit(main())
