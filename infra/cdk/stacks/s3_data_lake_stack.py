"""
S3 Data Lake CDK stack — raw/bronze, silver, gold, and Athena results buckets.

Purpose:
    Provision the storage foundation for the data platform with production-safe
    defaults: encryption, versioning, blocked public access, lifecycle tiering,
    and tags. This is the stack Lab 01 deploys.

Creates:
    - Raw bucket          (landing zone, exactly as received; lifecycle tiers
                           old data to IA/Glacier)
    - Bronze bucket       (typed / lightly-cleaned copy of raw)
    - Silver bucket       (cleaned, deduplicated, query-ready)
    - Gold bucket         (business marts)
    - Athena results bucket (query output; short expiry lifecycle)
    All with: SSE (S3-managed) encryption, versioning, BlockPublicAccess.ALL,
    lifecycle rules, and tags. Bucket names get an account+region suffix to be
    globally unique without hardcoding your account ID.

Inputs (context / env):
    - env account/region come from the CDK app (see app.py).
    - Optional context "lake_prefix" to override the bucket name prefix.

Outputs (CloudFormation):
    RawBucketName, BronzeBucketName, SilverBucketName, GoldBucketName,
    AthenaResultsBucketName.

Deploy:
    cd infra/cdk
    pip install -r requirements.txt
    cdk bootstrap
    cdk deploy DataLakeStack

Cost warning:
    S3 storage + request costs only. With the tiny Lab 01 sample data this is a
    few cents at most, but the buckets are REAL. Empty + destroy them via the
    Lab 01 cleanup when finished (versioned buckets must be emptied first).
"""
from __future__ import annotations

from aws_cdk import (
    Aws,
    CfnOutput,
    Duration,
    RemovalPolicy,
    Stack,
    Tags,
)
from aws_cdk import aws_s3 as s3
from constructs import Construct


class DataLakeStack(Stack):
    def __init__(self, scope: Construct, construct_id: str,
                 lake_prefix: str = "ade-retail-lake", **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Account+region suffix keeps names globally unique without hardcoding
        # an account ID in source. Aws.ACCOUNT_ID/REGION resolve at deploy time.
        suffix = f"{Aws.ACCOUNT_ID}-{Aws.REGION}"

        self.raw_bucket = self._make_bucket(
            "RawBucket", f"{lake_prefix}-raw-{suffix}", zone="raw",
            lifecycle=[
                s3.LifecycleRule(
                    id="raw-tiering",
                    enabled=True,
                    transitions=[
                        s3.Transition(storage_class=s3.StorageClass.INFREQUENT_ACCESS,
                                      transition_after=Duration.days(30)),
                        s3.Transition(storage_class=s3.StorageClass.GLACIER,
                                      transition_after=Duration.days(90)),
                    ],
                    noncurrent_version_expiration=Duration.days(90),
                )
            ],
        )
        self.bronze_bucket = self._make_bucket(
            "BronzeBucket", f"{lake_prefix}-bronze-{suffix}", zone="bronze",
            lifecycle=[
                s3.LifecycleRule(id="bronze-noncurrent-cleanup", enabled=True,
                                 noncurrent_version_expiration=Duration.days(60))
            ],
        )
        self.silver_bucket = self._make_bucket(
            "SilverBucket", f"{lake_prefix}-silver-{suffix}", zone="silver",
            lifecycle=[
                s3.LifecycleRule(id="silver-noncurrent-cleanup", enabled=True,
                                 noncurrent_version_expiration=Duration.days(30))
            ],
        )
        self.gold_bucket = self._make_bucket(
            "GoldBucket", f"{lake_prefix}-gold-{suffix}", zone="gold",
            lifecycle=[
                s3.LifecycleRule(id="gold-noncurrent-cleanup", enabled=True,
                                 noncurrent_version_expiration=Duration.days(30))
            ],
        )
        self.athena_results_bucket = self._make_bucket(
            "AthenaResultsBucket", f"{lake_prefix}-athena-results-{suffix}",
            zone="athena-results", versioned=False,
            lifecycle=[
                s3.LifecycleRule(id="expire-query-results", enabled=True,
                                 expiration=Duration.days(14))
            ],
        )

        for name, bucket in {
            "RawBucketName": self.raw_bucket,
            "BronzeBucketName": self.bronze_bucket,
            "SilverBucketName": self.silver_bucket,
            "GoldBucketName": self.gold_bucket,
            "AthenaResultsBucketName": self.athena_results_bucket,
        }.items():
            CfnOutput(self, name, value=bucket.bucket_name)

    def _make_bucket(self, cid: str, name: str, *, zone: str,
                     versioned: bool = True,
                     lifecycle: list[s3.LifecycleRule] | None = None) -> s3.Bucket:
        bucket = s3.Bucket(
            self, cid,
            bucket_name=name,
            encryption=s3.BucketEncryption.S3_MANAGED,      # SSE-S3 at rest
            versioned=versioned,                            # recover from bad writes
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            enforce_ssl=True,                               # deny non-TLS access
            lifecycle_rules=lifecycle or [],
            # For a learning lab we allow cleanup to delete the bucket. In real
            # production you'd use RETAIN to prevent accidental data loss.
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,                       # lab convenience only
        )
        Tags.of(bucket).add("project", "aws-data-engineering-pipeline")
        Tags.of(bucket).add("zone", zone)
        Tags.of(bucket).add("managed-by", "cdk")
        return bucket
