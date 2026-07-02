# Infrastructure — AWS CDK (Python)

Infrastructure-as-code for the data platform. **Every deploy creates real, billable AWS resources.** Read the cost warning in each stack's docstring before deploying, and always destroy when finished.

## What exists today (honest status)

| Stack | Status | Creates | Used by |
|---|---|---|---|
| `DataLakeStack` | ✅ **Implemented, synth-verified** | 5 S3 buckets: raw, bronze, silver, gold, Athena results — each with SSE encryption, versioning (except results), Block Public Access, TLS-only bucket policy, lifecycle rules, tags | [Lab 01](../../labs/lab-01-s3-data-lake/) |
| `GlueCatalogStack` | ✅ Implemented, synth-verified, template-tested (`tests/infra/`) | Glue database `retail_lake`, CSV header classifier, least-privilege crawler role, crawler with one S3 target per entity | [Lab 02](../../labs/lab-02-glue-crawler-catalog/) — synth-verified only; live run pending |
| IAM / Lambda / Step Functions / Kinesis / Redshift stacks | ❌ Not written yet | — | Later labs — tracked in [REPO-CONTENT-GAP-REPORT](../../REPO-CONTENT-GAP-REPORT.md) |

No AWS account ID or user-specific value is hardcoded anywhere. Bucket names get an `{account}-{region}` suffix resolved at deploy time; account/region can be passed via CDK context (`-c account=... -c region=...`) or fall back to your CLI configuration.

## Prerequisites

- An AWS account **you control** (personal sandbox, not a shared work account), with a **budget alarm** set.
- AWS CLI v2 configured — `aws sts get-caller-identity` must work.
- Node.js 20+ (the CDK CLI runs on Node).
- Python 3.11+.

## Setup

```bash
cd infra/cdk

# 1. Python virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. Python dependencies (aws-cdk-lib + constructs)
pip install -r requirements.txt

# 3. CDK CLI — either install globally...
npm install -g aws-cdk
# ...or skip the install and prefix every cdk command with npx:
#    npx aws-cdk@2 <command>
```

## Deploy

```bash
# One-time per account+region: provisions the CDK staging bucket/roles.
cdk bootstrap

# Render CloudFormation locally. No AWS resources created, no cost.
# Do this first, every time — it catches most errors before you deploy.
cdk synth

# Deploy the data lake (creates 5 real S3 buckets).
cdk deploy DataLakeStack
```

`cdk deploy` prints the bucket names as stack outputs (`RawBucketName`, `BronzeBucketName`, `SilverBucketName`, `GoldBucketName`, `AthenaResultsBucketName`). Fetch one later with:

```bash
aws cloudformation describe-stacks --stack-name DataLakeStack \
  --query "Stacks[0].Outputs[?OutputKey=='RawBucketName'].OutputValue" --output text
```

## Destroy (mandatory when done)

```bash
cdk destroy DataLakeStack
```

The lab stacks use `removal_policy=DESTROY` + `auto_delete_objects=True` so `cdk destroy` also empties the buckets. **This is a learning-environment setting only** — production stacks retain data on delete. Verify nothing is left:

```bash
aws s3 ls | grep ade-retail-lake    # should print nothing
```

## 💰 Cost warning

The S3 stack itself costs cents with lab-sized data, but S3 charges for storage, requests, and **old versions on versioned buckets**. `cdk bootstrap` also leaves a small staging bucket in your account (that one is normal to keep). Never leave lab stacks deployed overnight "to save time tomorrow."

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `cdk: command not found` | CDK CLI not installed | `npm install -g aws-cdk`, or use `npx aws-cdk@2 ...` |
| `Unsupported feature flag ...` on synth | Stale CDKv1 flags in `cdk.json` | This repo's `cdk.json` is already v2-clean; don't copy flags from old blog posts |
| `Unable to resolve AWS account to use` | No credentials/region configured | `aws configure`, or pass `-c account=<id> -c region=<region>` |
| `...is not bootstrapped` on deploy | Bootstrap never ran in this account+region | `cdk bootstrap` |
| `bucket already exists` | Leftover bucket from a previous run, or prefix collision | `aws s3 ls \| grep ade-retail-lake`, delete leftovers or pass a different `lake_prefix` |
| `cdk destroy` leaves a bucket | Bucket not empty (old object versions) | `aws s3 rm s3://<bucket> --recursive` then retry; for versioned buckets delete versions via console or `aws s3api delete-objects` |
| Python `ModuleNotFoundError: aws_cdk` | venv not activated / deps not installed | `source .venv/bin/activate && pip install -r requirements.txt` |

## Layout

```
infra/cdk/
├── app.py                        # CDK app: instantiates the stacks
├── cdk.json                      # how to run the app + v2 feature flags
├── requirements.txt              # aws-cdk-lib, constructs
└── stacks/
    ├── s3_data_lake_stack.py     # DataLakeStack (Lab 01)
    └── glue_catalog_stack.py     # GlueCatalogStack (Lab 02, in progress)
```
