"""
Glue Catalog + Crawler CDK stack.

Purpose:
    Create a Glue database and a crawler that catalogs the raw retail data in
    the S3 lake, so Athena/Redshift/Glue can query it as tables with
    auto-detected partitions. This is the stack Lab 02 deploys.

Design decision — one crawler target PER ENTITY, not one target at raw/:
    The three entities (orders, customers, products) have different schemas.
    A single target at s3://<raw>/raw/ would ask the crawler to fold three
    incompatible schemas into one table — the exact "mixed schemas under one
    prefix" failure mode the repo runbook warns about. Entity-level targets
    give one correctly-typed table per entity, each partitioned by
    ingestion_date (the only key=value level below the target path).

Creates:
    - Glue database `retail_lake`
    - IAM role for the crawler (least privilege: read the raw bucket + the
      managed Glue service policy for catalog writes)
    - Glue crawler `retail-raw-crawler` with three entity-level S3 targets,
      table prefix `raw_`, in-place schema updates on re-crawl

Inputs:
    raw_bucket_name  Name of the raw bucket (from the DataLakeStack
                     `RawBucketName` output), passed via CDK context:
                     -c raw_bucket_name=...

Outputs:
    GlueDatabaseName, CrawlerName.

Deploy:
    cd infra/cdk
    cdk deploy GlueCatalogStack \
      -c raw_bucket_name=ade-retail-lake-raw-<account>-<region>

Destroy:
    cdk destroy GlueCatalogStack
    (Deleting the database cascades to the crawler-created tables.)

Cost warning:
    A crawler run is billed per DPU-hour (short and a few cents for this
    dataset). The database and table definitions are free. Run the Lab 02
    cleanup to remove everything.
"""
from __future__ import annotations

from aws_cdk import CfnOutput, Stack
from aws_cdk import aws_glue as glue
from aws_cdk import aws_iam as iam
from constructs import Construct

ENTITIES = ("orders", "customers", "products")
CRAWLER_NAME = "retail-raw-crawler"
TABLE_PREFIX = "raw_"
CSV_CLASSIFIER_NAME = "retail-raw-csv-header"


class GlueCatalogStack(Stack):
    def __init__(self, scope: Construct, construct_id: str,
                 raw_bucket_name: str, database_name: str = "retail_lake",
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        if not raw_bucket_name or "/" in raw_bucket_name or raw_bucket_name.startswith("s3://"):
            raise ValueError(
                f"raw_bucket_name must be a bare bucket name, got {raw_bucket_name!r}. "
                "Pass it via: cdk deploy GlueCatalogStack -c raw_bucket_name=<RawBucketName output>"
            )

        db = glue.CfnDatabase(
            self, "RetailDatabase",
            catalog_id=self.account,
            database_input=glue.CfnDatabase.DatabaseInputProperty(
                name=database_name,
                description="Retail data lake catalog (raw zone tables).",
            ),
        )

        # Least-privilege crawler role: read only the raw bucket's raw/ prefix,
        # plus the managed Glue service policy for catalog/log operations.
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

        # Explicit CSV classifier declaring the header row. Glue's built-in
        # CSV classifier GUESSES whether row 1 is a header, and guesses wrong
        # when every column is a string (like customers.csv) — producing
        # col0/col1/... column names. Declaring the header removes the guess.
        classifier = glue.CfnClassifier(
            self, "CsvHeaderClassifier",
            csv_classifier=glue.CfnClassifier.CsvClassifierProperty(
                name=CSV_CLASSIFIER_NAME,
                contains_header="PRESENT",
                delimiter=",",
                quote_symbol='"',
            ),
        )

        # One target per entity so each entity becomes its own table with the
        # correct schema; ingestion_date= is the partition level below each
        # target. Table names derive from the target folder (entity=orders ->
        # entity_orders) plus the prefix: raw_entity_orders, etc.
        targets = [
            glue.CfnCrawler.S3TargetProperty(
                path=f"s3://{raw_bucket_name}/raw/source=retail/entity={entity}/"
            )
            for entity in ENTITIES
        ]

        crawler = glue.CfnCrawler(
            self, "RawCrawler",
            role=crawler_role.role_arn,
            database_name=database_name,
            name=CRAWLER_NAME,
            table_prefix=TABLE_PREFIX,
            classifiers=[CSV_CLASSIFIER_NAME],
            targets=glue.CfnCrawler.TargetsProperty(s3_targets=targets),
            # Update the schema/partitions in place on re-crawl; log (don't
            # delete) tables whose source objects disappeared.
            schema_change_policy=glue.CfnCrawler.SchemaChangePolicyProperty(
                update_behavior="UPDATE_IN_DATABASE",
                delete_behavior="LOG",
            ),
            recrawl_policy=glue.CfnCrawler.RecrawlPolicyProperty(
                recrawl_behavior="CRAWL_EVERYTHING",  # tiny dataset; switch to
                # CRAWL_NEW_FOLDERS_ONLY for large production prefixes
            ),
        )
        crawler.add_dependency(db)

        CfnOutput(self, "GlueDatabaseName", value=database_name)
        CfnOutput(self, "CrawlerName", value=CRAWLER_NAME)
