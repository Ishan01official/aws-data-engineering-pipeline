"""CDK assertion tests for GlueCatalogStack.

These synthesize the stack in-process and assert on the CloudFormation
template — catching wiring regressions (wrong bucket, missing targets,
over-broad IAM) without deploying anything.

Run: pytest tests/infra -q     (needs aws-cdk-lib installed, see infra/cdk/requirements.txt)
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "infra", "cdk"))

import aws_cdk as cdk
from aws_cdk.assertions import Match, Template

from stacks.glue_catalog_stack import (CRAWLER_NAME, CSV_CLASSIFIER_NAME, ENTITIES,
                                        TABLE_PREFIX, GlueCatalogStack)

RAW_BUCKET = "ade-retail-lake-raw-123456789012-us-east-1"


@pytest.fixture(scope="module")
def template() -> Template:
    app = cdk.App()
    stack = GlueCatalogStack(app, "GlueCatalogStackTest", raw_bucket_name=RAW_BUCKET)
    return Template.from_stack(stack)


def test_creates_database_named_retail_lake(template):
    template.resource_count_is("AWS::Glue::Database", 1)
    template.has_resource_properties("AWS::Glue::Database", {
        "DatabaseInput": Match.object_like({"Name": "retail_lake"}),
    })


def test_crawler_targets_one_path_per_entity_in_the_raw_bucket(template):
    """The core DataLakeStack->GlueCatalogStack wiring: every crawler target
    must point inside the raw bucket, at entity level (not at raw/ root)."""
    expected_paths = [
        f"s3://{RAW_BUCKET}/raw/source=retail/entity={e}/" for e in ENTITIES
    ]
    template.has_resource_properties("AWS::Glue::Crawler", {
        "Targets": {"S3Targets": [{"Path": p} for p in expected_paths]},
    })


def test_crawler_name_prefix_and_schema_policy(template):
    template.has_resource_properties("AWS::Glue::Crawler", {
        "Name": CRAWLER_NAME,
        "TablePrefix": TABLE_PREFIX,
        "DatabaseName": "retail_lake",
        "SchemaChangePolicy": {
            "UpdateBehavior": "UPDATE_IN_DATABASE",
            "DeleteBehavior": "LOG",
        },
    })


def test_crawler_role_s3_access_is_scoped_to_raw_prefix(template):
    """Least privilege: the inline policy must name the raw bucket and its
    raw/* prefix only — no wildcards over other buckets."""
    template.has_resource_properties("AWS::IAM::Policy", {
        "PolicyDocument": {
            "Statement": Match.array_with([
                Match.object_like({
                    "Action": ["s3:GetObject", "s3:ListBucket"],
                    "Effect": "Allow",
                    "Resource": [
                        f"arn:aws:s3:::{RAW_BUCKET}",
                        f"arn:aws:s3:::{RAW_BUCKET}/raw/*",
                    ],
                })
            ])
        }
    })


def test_crawler_role_trusts_only_glue(template):
    template.has_resource_properties("AWS::IAM::Role", {
        "AssumeRolePolicyDocument": {
            "Statement": [Match.object_like({
                "Principal": {"Service": "glue.amazonaws.com"},
                "Action": "sts:AssumeRole",
            })]
        }
    })


def test_csv_classifier_declares_header_and_is_attached(template):
    """Guards the customers.csv all-strings header bug: the classifier must
    declare the header row and the crawler must use it."""
    template.has_resource_properties("AWS::Glue::Classifier", {
        "CsvClassifier": Match.object_like({
            "Name": CSV_CLASSIFIER_NAME,
            "ContainsHeader": "PRESENT",
            "Delimiter": ",",
        })
    })
    template.has_resource_properties("AWS::Glue::Crawler", {
        "Classifiers": [CSV_CLASSIFIER_NAME],
    })


def test_outputs_expose_database_and_crawler_names(template):
    outputs = template.to_json().get("Outputs", {})
    assert set(outputs) == {"GlueDatabaseName", "CrawlerName"}
    assert outputs["GlueDatabaseName"]["Value"] == "retail_lake"
    assert outputs["CrawlerName"]["Value"] == CRAWLER_NAME


def test_rejects_invalid_bucket_names():
    for bad in ("", "s3://bucket", "bucket/with/path"):
        app = cdk.App()
        with pytest.raises(ValueError):
            GlueCatalogStack(app, f"Bad{abs(hash(bad))}", raw_bucket_name=bad)
