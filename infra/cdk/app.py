#!/usr/bin/env python3
"""
CDK app entry point for the Enterprise Retail Sales Data Platform.

Purpose: wire together the platform's stacks (S3, IAM, Lambda, Glue, Step
Functions, EventBridge, CloudWatch, SNS, Athena, optional Redshift).

Status: SKELETON. Individual stacks under stacks/ are built module-by-module.
Each stack creates billable AWS resources — review and deploy deliberately.

Deploy:
    cd infra/cdk
    pip install -r requirements.txt
    cdk bootstrap            # one-time per account/region
    cdk synth                # render CloudFormation, no cost
    cdk deploy <StackName>   # deploys real resources — COSTS MONEY
"""
import aws_cdk as cdk

app = cdk.App()
env = cdk.Environment(
    account=app.node.try_get_context("account") or "REPLACE_ACCOUNT_ID",
    region=app.node.try_get_context("region") or "REPLACE_REGION",
)

# TODO: instantiate stacks as they are built, in dependency order, e.g.:
# from stacks.storage_stack import StorageStack
# StorageStack(app, "RetailStorageDev", env=env)

app.synth()
