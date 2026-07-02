#!/usr/bin/env python3
"""
Upload the local retail sample CSVs to the raw zone of an S3 data lake.

Purpose:
    Place each entity's CSV at the correct Hive-partitioned raw-zone key so a
    Glue crawler / Athena can later discover partitions automatically.

Inputs (CLI):
    --bucket          Target raw/bronze bucket name (REQUIRED).
    --data-dir        Local dir holding sample data (default: data/sample/retail).
    --ingestion-date  Partition date YYYY-MM-DD (default: today).
    --profile         AWS CLI profile to use (optional).
    --dry-run         Print what would be uploaded without calling AWS.

Outputs:
    Objects at:
      s3://<bucket>/raw/source=retail/entity=orders/ingestion_date=<date>/orders_<date>.csv
      ...customers... , ...products...

Run locally (dry run, no AWS needed):
    python scripts/upload_sample_data.py --bucket my-raw-bucket --dry-run

Deploy / real upload (COSTS: negligible S3 PUT + storage):
    python scripts/upload_sample_data.py --bucket my-raw-bucket

Common errors:
    - NoCredentialsError: run `aws configure` or pass --profile.
    - NoSuchBucket / AccessDenied: create the bucket first (CDK stack) and ensure
      your identity has s3:PutObject on it.
    - FileNotFoundError: --data-dir doesn't contain the expected CSVs.

Cost warning:
    Uploads a handful of tiny objects. Cost is effectively zero, but this DOES
    create real S3 objects. Run the Lab 01 cleanup to remove them.
"""
from __future__ import annotations

import argparse
import logging

from pathlib import Path

log = logging.getLogger("upload_sample_data")

# Support both "python scripts/x.py" and "python -m scripts.x"
try:
    from lake_layout import ENTITIES, default_filename, raw_key, today_iso, _DATE_RE
except ImportError:  # pragma: no cover
    from scripts.lake_layout import ENTITIES, default_filename, raw_key, today_iso, _DATE_RE


def find_local_csv(data_dir: Path, entity: str) -> Path:
    """Locate the local CSV for an entity under data_dir/<entity>/."""
    entity_dir = data_dir / entity
    matches = sorted(entity_dir.glob(f"{entity}_*.csv"))
    if not matches:
        raise FileNotFoundError(
            f"no CSV like {entity}_*.csv found in {entity_dir}. "
            f"Check --data-dir (expected data/sample/retail)."
        )
    return matches[-1]  # newest by name


def upload(bucket: str, data_dir: Path, ingestion_date: str,
           profile: str | None, dry_run: bool, region: str | None = None) -> int:
    plan = []
    for entity in ENTITIES:
        local = find_local_csv(data_dir, entity)
        key = raw_key(entity, ingestion_date, default_filename(entity, ingestion_date))
        plan.append((local, key))

    for local, key in plan:
        print(f"{'DRY-RUN ' if dry_run else ''}upload {local} -> s3://{bucket}/{key}")

    if dry_run:
        print("Dry run complete. No AWS calls made.")
        return 0

    try:
        import boto3
        from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError
    except ImportError:
        log.error("boto3 not installed. `pip install boto3`")
        return 2

    session = boto3.Session(profile_name=profile) if profile else boto3.Session()
    s3 = session.client("s3", region_name=region) if region else session.client("s3")
    try:
        for local, key in plan:
            s3.upload_file(str(local), bucket, key)
            print(f"uploaded s3://{bucket}/{key}")
    except NoCredentialsError:
        log.error("no AWS credentials. Run `aws configure` or pass --profile.")
        return 2
    except (ClientError, BotoCoreError) as e:
        log.error("upload to s3://%s failed: %s", bucket, e)
        return 1
    print(f"Done. Uploaded {len(plan)} objects to s3://{bucket}/raw/...")
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Upload retail sample CSVs to the S3 raw zone.")
    p.add_argument("--bucket", required=True, help="Target raw/bronze S3 bucket name.")
    p.add_argument("--data-dir", default="data/sample/retail",
                   help="Local sample data dir (default: data/sample/retail).")
    p.add_argument("--ingestion-date", default=today_iso(),
                   help="Partition date YYYY-MM-DD (default: today).")
    p.add_argument("--profile", default=None, help="AWS CLI profile (optional).")
    p.add_argument("--region", default=None,
                   help="AWS region override (optional; defaults to your CLI config).")
    p.add_argument("--dry-run", action="store_true",
                   help="Print planned uploads without calling AWS.")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    args = parse_args(argv)
    if not _DATE_RE.match(args.ingestion_date):
        log.error("--ingestion-date must be YYYY-MM-DD, got %r", args.ingestion_date)
        return 2
    data_dir = Path(args.data_dir).expanduser().resolve()
    if not data_dir.exists():
        log.error("--data-dir not found: %s", data_dir)
        return 2
    try:
        return upload(args.bucket, data_dir, args.ingestion_date, args.profile,
                      args.dry_run, region=args.region)
    except FileNotFoundError as e:
        log.error("%s", e)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
