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
import sys
from pathlib import Path

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
           profile: str | None, dry_run: bool) -> int:
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
        print("ERROR: boto3 not installed. `pip install boto3`", file=sys.stderr)
        return 2

    session = boto3.Session(profile_name=profile) if profile else boto3.Session()
    s3 = session.client("s3")
    try:
        for local, key in plan:
            s3.upload_file(str(local), bucket, key)
            print(f"uploaded s3://{bucket}/{key}")
    except NoCredentialsError:
        print("ERROR: no AWS credentials. Run `aws configure` or pass --profile.",
              file=sys.stderr)
        return 2
    except (ClientError, BotoCoreError) as e:
        print(f"ERROR uploading to s3://{bucket}: {e}", file=sys.stderr)
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
    p.add_argument("--dry-run", action="store_true",
                   help="Print planned uploads without calling AWS.")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not _DATE_RE.match(args.ingestion_date):
        print(f"ERROR: --ingestion-date must be YYYY-MM-DD, got {args.ingestion_date!r}",
              file=sys.stderr)
        return 2
    data_dir = Path(args.data_dir).expanduser().resolve()
    if not data_dir.exists():
        print(f"ERROR: --data-dir not found: {data_dir}", file=sys.stderr)
        return 2
    try:
        return upload(args.bucket, data_dir, args.ingestion_date, args.profile, args.dry_run)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
