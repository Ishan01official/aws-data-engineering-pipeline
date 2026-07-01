"""
Glue Catalog + Crawler CDK stack.

Purpose:
    Create a Glue database and a crawler that catalogs the raw retail data in the
    S3 lake, so Athena/Redshift/Glue can query it as tables with auto-detected
    partitions (source, entity, ingestion_date). This is the stack Lab 02 deploys.

Creates:
    - Glue database `retail_lake`
    - IAM role for the crawler (least privilege: read the raw bucket + Glue catalog)
    - Glue crawler pointed at s3://<raw>/raw/ that writes tables into the database

Inputs:
    raw_bucket_name  Name of the raw bucket (from the DataLakeStack output).

Outputs:
    GlueDatabaseName, CrawlerName.

Deploy:
    cd infra/cdk
    cdk deploy GlueCatalogStack \
      -c raw_bucket_name=ade-retail-lake-raw-<account>-<region>

Destroy:
    cdk destroy GlueCatalogStack

Cost warning:
    A crawler run is billed per DPU-hour (crawlers are cheap and short for small
    data, typically a few cents). The database and table definitions are free.
    Run the Lab 02 cleanup to remove them.
"""
from __future__ import annotations

from aws_cdk import CfnOutput, Stack
from aws_cdk import aws_glue as glue
from aws_cdk import aws_iam as iam
from constructs import Construct


class GlueCatalogStack(Stack):
    def __init__(self, scope: Construct, construct_id: str,
                 raw_bucket_name: str, database_name: str = "retail_lake",
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        db = glue.CfnDatabase(
            self, "RetailDatabase",
            catalog_id=self.account,
            database_input=glue.CfnDatabase.DatabaseInputProperty(
                name=database_name,
                description="Retail data lake catalog (raw/bronze tables).",
            ),
        )

        # Least-privilege crawler role: read only the raw bucket, plus the
        # managed Glue service policy for catalog operations.
        crawler_role = iam.Role(
            self, "CrawlerRole",
            assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
            description="Role assumed by the retail raw crawler.",
        )
        crawler_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSGlueServiceRole")
        )
        crawler_role.add_to_policy(iam.PolicyStatement(
            actions=["s3:GetObject", "s3:ListBucket"],
            resources=[
                f"arn:aws:s3:::{raw_bucket_name}",
                f"arn:aws:s3:::{raw_bucket_name}/raw/*",
            ],
        ))

        crawler = glue.CfnCrawler(
            self, "RawCrawler",
            role=crawler_role.role_arn,
            database_name=database_name,
            name="retail-raw-crawler",
            targets=glue.CfnCrawler.TargetsProperty(
                s3_targets=[glue.CfnCrawler.S3TargetProperty(
                    path=f"s3://{raw_bucket_name}/raw/"
                )]
            ),
            # Update the schema/partitions in place on re-crawl.
            schema_change_policy=glue.CfnCrawler.SchemaChangePolicyProperty(
                update_behavior="UPDATE_IN_DATABASE",
                delete_behavior="LOG",
            ),
        )
        crawler.add_dependency(db)

        CfnOutput(self, "GlueDatabaseName", value=database_name)
        CfnOutput(self, "CrawlerName", value="retail-raw-crawler")
