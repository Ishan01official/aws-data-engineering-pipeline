# 02 · Code Walkthrough

The real code that builds and populates the lake. All of it runs; the tests and the `cdk synth` are verified.

## The CDK stack — `infra/cdk/stacks/s3_data_lake_stack.py`

The stack creates four buckets via one private helper, `_make_bucket`, so every bucket gets the same production-safe defaults. Key decisions in the code:

- **`encryption=S3_MANAGED`** — SSE-S3 at rest on every object. For regulated data you'd switch to `KMS` with a customer-managed key (Module 08).
- **`versioned=True`** (except Athena results) — recover from bad overwrites; the raw source-of-truth especially needs this.
- **`block_public_access=BLOCK_ALL`** — a data lake is never public. This is non-negotiable and set explicitly.
- **`enforce_ssl=True`** — adds a bucket policy denying non-TLS requests.
- **Lifecycle rules** — the raw bucket tiers to Infrequent Access at 30 days and Glacier at 90; Athena results expire at 14 days; versioned buckets expire non-current versions so old versions don't accumulate cost.
- **Name suffix** `f"{Aws.ACCOUNT_ID}-{Aws.REGION}"` — globally unique names resolved at deploy time, so no account ID is hardcoded in source.
- **`removal_policy=DESTROY` + `auto_delete_objects=True`** — *lab convenience only*, so cleanup fully removes buckets. Production uses `RETAIN`.
- **Tags** — `project`, `zone`, `managed-by` on every bucket, for cost allocation and governance.
- **`CfnOutput`** for each bucket name, so scripts and later stacks can read them.

Verify it compiles to the right CloudFormation without deploying:
```bash
cd infra/cdk && CDK_DEFAULT_ACCOUNT=111122223333 CDK_DEFAULT_REGION=us-east-1 cdk synth
```

## The layout helper — `scripts/lake_layout.py`

One source of truth for raw-zone keys, imported by both scripts and the tests so they can't drift. `raw_prefix()` builds `raw/source=retail/entity=<e>/ingestion_date=<date>/`; `raw_key()` appends the filename; both validate their inputs (known entity, `YYYY-MM-DD` date, bare filename) and raise `ValueError` on bad input.

## The scripts — `scripts/`

- **`create_local_lake_layout.py`** — makes `raw/bronze/silver/gold` folders locally with a describing README each. Pure local, free. `--base` sets where.
- **`upload_sample_data.py`** — finds each entity's CSV under `data/sample/retail/<entity>/`, computes the partitioned key via the helper, and uploads. Has `--dry-run` (prints the exact keys, no AWS calls), `--profile`, and `--ingestion-date`. Handles missing creds, missing files, and S3 errors with clear messages and non-zero exit codes.
- **`validate_s3_layout.py`** — HEADs each expected object and prints PASS/FAIL, exiting non-zero if any is missing (so it can gate CI or a pipeline).

Run the dry run to see the layout without touching AWS:
```bash
python scripts/upload_sample_data.py --bucket demo --ingestion-date 2026-07-01 --dry-run
```

## The tests — `tests/unit/`

- **`test_s3_key_layout.py`** — asserts the exact prefix/key shapes and that bad entities/dates/filenames raise. No AWS needed.
- **`test_sample_data_schema.py`** — asserts the sample CSVs have the expected headers, no blank/duplicate IDs, and that every order references a real customer and product (referential integrity). This catches sample-data rot.

```bash
pytest tests/unit -q   # all pass, no AWS credentials required
```
