# 02 · Hands-on — Build the Lake

The hands-on for this module is **[Lab 01 — Build an S3 Data Lake with Bronze, Silver, and Gold Zones](../labs/lab-01-s3-data-lake/)**. It is fully runnable: deployable CDK stack, working scripts, sample data, validation, tests, and cleanup. This page is the quick-reference command sequence; the lab README explains every step, cost, and trade-off — read it first.

> 💰 Creates real S3 buckets. Cost with lab data: a few cents. Cleanup is mandatory.

## Zero-cost dry run (no AWS account touched)

```bash
# mirror the zone layout locally and inspect it
python scripts/create_local_lake_layout.py --base ./local-lake

# build and print the exact S3 keys the pipeline uses
python scripts/build_s3_prefix.py --entity orders --ingestion-date 2026-07-01 \
  --filename orders_2026_07_01.csv

# see the full upload plan without any AWS call
python scripts/upload_sample_data.py --bucket any-name --ingestion-date 2026-07-01 --dry-run

# verify the layout logic and sample-data quality offline
python -m pytest tests/unit -q
```

## The real thing (billable)

```bash
# 1. deploy the five zone buckets
cd infra/cdk && pip install -r requirements.txt
cdk bootstrap && cdk synth && cdk deploy DataLakeStack
cd ../..

# 2. grab the raw bucket name from stack outputs
RAW_BUCKET=$(aws cloudformation describe-stacks --stack-name DataLakeStack \
  --query "Stacks[0].Outputs[?OutputKey=='RawBucketName'].OutputValue" --output text)

# 3. land the partitioned retail data
python scripts/upload_sample_data.py --bucket "$RAW_BUCKET" --ingestion-date 2026-07-01

# 4. validate — exits non-zero if anything is missing
python scripts/validate_s3_layout.py --bucket "$RAW_BUCKET" --ingestion-date 2026-07-01
```

## Cleanup (mandatory)

```bash
aws s3 rm "s3://$RAW_BUCKET" --recursive
cd infra/cdk && cdk destroy DataLakeStack
aws s3 ls | grep ade-retail-lake        # must print nothing
```

## What to make sure you *understood*, not just ran

1. Why the key is `raw/source=retail/entity=orders/ingestion_date=2026-07-01/...` and what each `key=value` segment buys you (crawler auto-discovery, partition pruning, multi-source layout).
2. Why re-running the upload for the same date is safe (deterministic keys → overwrite, not duplicate).
3. Why the buckets are versioned, encrypted, TLS-only, and public-blocked — and which of those settings you'd change in production (`removal_policy`, `auto_delete_objects`).
4. What `validate_s3_layout.py` proves and where that same check would sit in a production pipeline (post-load gate, scheduled freshness check).

Next: [Lab 02](../labs/lab-02-glue-crawler-catalog/) crawls this data into the Glue Catalog so Athena can query it.
