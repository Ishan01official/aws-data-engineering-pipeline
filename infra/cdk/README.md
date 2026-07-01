# Infrastructure (AWS CDK, Python)

Infrastructure-as-code for the capstone platform. **Every stack here creates billable AWS resources** — read each stack's docstring and the cost note before deploying.

## Prerequisites
- AWS CLI v2 configured (a sandbox account you control).
- Node.js + `npm install -g aws-cdk`.
- Python 3.11, `pip install -r requirements.txt`.
- A budget alarm set on the account.

## Usage
```bash
cdk bootstrap            # one-time per account/region (creates a deploy bucket)
cdk synth                # renders CloudFormation locally — no cost
cdk deploy <StackName>   # deploys real, billable resources
cdk destroy <StackName>  # tear down — run this when done to stop charges
```

## Stacks (built module-by-module)
| Stack | Creates | Module |
|---|---|---|
| StorageStack | S3 raw/silver/gold buckets, lifecycle | 02 |
| IamStack | Least-privilege roles for jobs/functions | 01 |
| LambdaStack | Validation/router Lambda | 03 |
| GlueStack | Glue DB, crawler, PySpark job | 04 |
| OrchestrationStack | Step Functions + EventBridge | 06 |
| ObservabilityStack | CloudWatch alarms + SNS topic | 11 |
| AthenaStack | Athena workgroup + results location | 02 |
| RedshiftStack (optional) | Redshift Serverless namespace/workgroup | 07 |

> **Status:** SKELETON. `app.py` and `stacks/` are scaffolded; stacks are implemented as their modules are built. Marked example-only until then.
