# 02 · Deployment

Exact commands to deploy the S3 data lake. This is the same flow Lab 01 uses.

## Prerequisites
- AWS CLI v2 configured (`aws sts get-caller-identity` works).
- `npm install -g aws-cdk`.
- `pip install -r infra/cdk/requirements.txt`.

## Deploy
```bash
cd infra/cdk
cdk bootstrap            # one-time per account/region; creates the CDK assets bucket
cdk synth               # render CloudFormation locally — NO cost, good sanity check
cdk deploy DataLakeStack
```

On success CDK prints Outputs:
```
DataLakeStack.RawBucketName = ade-retail-lake-raw-<account>-<region>
DataLakeStack.SilverBucketName = ...
DataLakeStack.GoldBucketName = ...
DataLakeStack.AthenaResultsBucketName = ...
```

Fetch a name programmatically:
```bash
aws cloudformation describe-stacks --stack-name DataLakeStack \
  --query "Stacks[0].Outputs[?OutputKey=='RawBucketName'].OutputValue" --output text
```

## Populate and validate
```bash
RAW_BUCKET=$(aws cloudformation describe-stacks --stack-name DataLakeStack \
  --query "Stacks[0].Outputs[?OutputKey=='RawBucketName'].OutputValue" --output text)
python scripts/upload_sample_data.py --bucket "$RAW_BUCKET" --ingestion-date 2026-07-01
python scripts/validate_s3_layout.py --bucket "$RAW_BUCKET" --ingestion-date 2026-07-01
```

## Environments (dev / uat / prod)
For real platforms, parameterize the `lake_prefix` per environment and deploy separate stacks (often in separate accounts). CI/CD via GitHub Actions + OIDC is in Module 11. The `cdk-deploy-dev.yml` workflow is the starting point.

## 💰 Cost note
Buckets themselves cost nothing; you pay for stored bytes and requests. The sample data is trivial. **Always run cleanup when done.**

## Cleanup
```bash
aws s3 rm "s3://$RAW_BUCKET" --recursive   # if you uploaded a lot
cd infra/cdk && cdk destroy DataLakeStack
```
