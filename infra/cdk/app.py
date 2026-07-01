#!/usr/bin/env python3
"""
CDK app entry point for the Enterprise Retail Sales Data Platform.

Wired stacks:
    - DataLakeStack     (S3 zones) — Lab 01 / Module 02
    - GlueCatalogStack  (Glue DB + crawler) — Lab 02 / Module 04
        Only instantiated when -c raw_bucket_name=... is provided, so `cdk synth`
        of just the lake works without it.

Additional stacks (IAM, Lambda, Glue jobs, Step Functions, etc.) are added as
their modules/labs are built.

Deploy:
    cd infra/cdk
    pip install -r requirements.txt
    cdk bootstrap
    cdk deploy DataLakeStack
    # then, using the RawBucketName output:
    cdk deploy GlueCatalogStack -c raw_bucket_name=<RawBucketName>
"""
import aws_cdk as cdk

from stacks.s3_data_lake_stack import DataLakeStack
from stacks.glue_catalog_stack import GlueCatalogStack

app = cdk.App()

env = cdk.Environment(
    account=app.node.try_get_context("account"),
    region=app.node.try_get_context("region"),
)

DataLakeStack(app, "DataLakeStack", env=env)

# Glue stack needs the raw bucket name; only build it when supplied.
raw_bucket_name = app.node.try_get_context("raw_bucket_name")
if raw_bucket_name:
    GlueCatalogStack(app, "GlueCatalogStack",
                     raw_bucket_name=raw_bucket_name, env=env)

app.synth()
