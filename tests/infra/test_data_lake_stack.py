"""CDK assertion tests for DataLakeStack (the Lab 01 stack).

Asserts the security and layout invariants Lab 01 documents: five buckets,
encryption, Block Public Access, versioning, TLS-only policy, and the five
outputs Lab 02 consumes.

Run: pytest tests/infra -q
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "infra", "cdk"))

import aws_cdk as cdk
from aws_cdk.assertions import Match, Template

from stacks.s3_data_lake_stack import DataLakeStack


@pytest.fixture(scope="module")
def template() -> Template:
    app = cdk.App()
    stack = DataLakeStack(app, "DataLakeStackTest")
    return Template.from_stack(stack)


def test_creates_exactly_five_buckets(template):
    template.resource_count_is("AWS::S3::Bucket", 5)


def test_every_bucket_blocks_public_access_and_encrypts(template):
    buckets = template.find_resources("AWS::S3::Bucket")
    for logical_id, bucket in buckets.items():
        props = bucket["Properties"]
        bpa = props["PublicAccessBlockConfiguration"]
        assert all(bpa[k] is True for k in
                   ("BlockPublicAcls", "BlockPublicPolicy",
                    "IgnorePublicAcls", "RestrictPublicBuckets")), logical_id
        algo = props["BucketEncryption"]["ServerSideEncryptionConfiguration"][0][
            "ServerSideEncryptionByDefault"]["SSEAlgorithm"]
        assert algo == "AES256", logical_id


def test_zone_buckets_are_versioned_results_bucket_is_not(template):
    buckets = template.find_resources("AWS::S3::Bucket")
    versioned = {lid: b["Properties"].get("VersioningConfiguration", {}).get("Status")
                 for lid, b in buckets.items()}
    zone_ids = [lid for lid in versioned if "AthenaResults" not in lid]
    assert len(zone_ids) == 4
    assert all(versioned[lid] == "Enabled" for lid in zone_ids)
    results_ids = [lid for lid in versioned if "AthenaResults" in lid]
    assert results_ids and versioned[results_ids[0]] is None


def test_every_bucket_policy_denies_non_tls(template):
    policies = template.find_resources("AWS::S3::BucketPolicy")
    assert len(policies) == 5
    for lid, pol in policies.items():
        statements = pol["Properties"]["PolicyDocument"]["Statement"]
        assert any(
            s.get("Effect") == "Deny"
            and s.get("Condition", {}).get("Bool", {}).get("aws:SecureTransport") == "false"
            for s in statements
        ), lid


def test_raw_bucket_lifecycle_tiers_to_ia_and_glacier(template):
    template.has_resource_properties("AWS::S3::Bucket", Match.object_like({
        "LifecycleConfiguration": {
            "Rules": Match.array_with([Match.object_like({
                "Transitions": [
                    {"StorageClass": "STANDARD_IA", "TransitionInDays": 30},
                    {"StorageClass": "GLACIER", "TransitionInDays": 90},
                ],
            })])
        }
    }))


def test_outputs_expose_all_five_bucket_names(template):
    outputs = template.to_json().get("Outputs", {})
    assert set(outputs) == {
        "RawBucketName", "BronzeBucketName", "SilverBucketName",
        "GoldBucketName", "AthenaResultsBucketName",
    }
