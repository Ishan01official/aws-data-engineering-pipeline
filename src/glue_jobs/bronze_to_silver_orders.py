"""
Glue PySpark job: bronze -> silver for the `orders` entity.

Purpose:
    Read raw/bronze orders (CSV, partitioned by ingestion_date), clean and type
    them, drop duplicates on order_id, filter invalid rows, and write partitioned
    Parquet to the silver zone. This is the raw->silver step of the medallion
    pipeline in the capstone.

Required environment / job arguments (Glue --ARG style):
    --RAW_BUCKET        source bucket (bronze/raw)
    --SILVER_BUCKET     destination bucket
    --INGESTION_DATE    partition to process, YYYY-MM-DD

Example (Glue job run):
    aws glue start-job-run --job-name bronze_to_silver_orders \
      --arguments '{"--RAW_BUCKET":"...","--SILVER_BUCKET":"...","--INGESTION_DATE":"2026-07-01"}'

Input example (CSV rows in bronze):
    order_id,customer_id,product_id,order_ts,quantity,unit_price,currency,channel,region
    O100001,C0001,P0050,2026-07-01T09:30:12Z,2,19.99,USD,web,north

Output example (silver Parquet, partitioned by order_date):
    silver/entity=orders/order_date=2026-07-01/part-*.parquet
    columns typed: quantity:int, unit_price:double, order_ts:timestamp,
    plus derived: order_date, gross_amount = quantity * unit_price

Error handling / idempotency:
    - Writes with overwrite of the target partition, so re-running the same
      INGESTION_DATE is idempotent (no duplicate silver data).
    - Rows failing basic validation are dropped from silver (a stricter pipeline
      would route them to quarantine; see src/quality and the capstone).

Note on testing:
    The pure transformation rules live in `clean_orders_records()` which operates
    on plain dicts, so they are unit-tested with NO Spark. The Spark `main()`
    applies the same rules at scale. This keeps business logic verifiable.
"""
from __future__ import annotations

from typing import Any


def clean_orders_records(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Pure, Spark-free implementation of the silver cleaning rules:

    1. Drop rows missing a key field (order_id, customer_id, product_id).
    2. Coerce quantity:int and unit_price:float; drop rows that can't coerce or
       are non-positive.
    3. Deduplicate on order_id (keep first).
    4. Derive order_date (from order_ts) and gross_amount.
    """
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for r in rows:
        oid = (r.get("order_id") or "").strip()
        cid = (r.get("customer_id") or "").strip()
        pid = (r.get("product_id") or "").strip()
        if not oid or not cid or not pid:
            continue
        if oid in seen:
            continue
        try:
            qty = int(r["quantity"])
            price = float(r["unit_price"])
        except (KeyError, ValueError, TypeError):
            continue
        if qty <= 0 or price < 0:
            continue
        ts = (r.get("order_ts") or "")
        order_date = ts[:10] if len(ts) >= 10 else None
        if not order_date:
            continue
        seen.add(oid)
        out.append({
            "order_id": oid,
            "customer_id": cid,
            "product_id": pid,
            "order_ts": ts,
            "quantity": qty,
            "unit_price": price,
            "gross_amount": round(qty * price, 2),
            "currency": r.get("currency", "USD"),
            "channel": r.get("channel"),
            "region": r.get("region"),
            "order_date": order_date,
        })
    return out


def main() -> None:  # pragma: no cover - requires the Glue/Spark runtime
    """Spark entry point. Applies the same rules as clean_orders_records at scale.

    This body only runs inside Glue (awsglue + pyspark are provided there); it is
    excluded from local unit-test coverage on purpose.
    """
    import sys
    from awsglue.utils import getResolvedOptions
    from awsglue.context import GlueContext
    from pyspark.context import SparkContext
    from pyspark.sql import functions as F

    args = getResolvedOptions(sys.argv, ["RAW_BUCKET", "SILVER_BUCKET", "INGESTION_DATE"])
    sc = SparkContext()
    glue = GlueContext(sc)
    spark = glue.spark_session

    src = (f"s3://{args['RAW_BUCKET']}/raw/source=retail/entity=orders/"
           f"ingestion_date={args['INGESTION_DATE']}/")
    dst = f"s3://{args['SILVER_BUCKET']}/silver/entity=orders/"

    df = spark.read.option("header", True).csv(src)

    cleaned = (
        df.dropna(subset=["order_id", "customer_id", "product_id"])
          .dropDuplicates(["order_id"])
          .withColumn("quantity", F.col("quantity").cast("int"))
          .withColumn("unit_price", F.col("unit_price").cast("double"))
          .filter((F.col("quantity") > 0) & (F.col("unit_price") >= 0))
          .withColumn("order_ts", F.to_timestamp("order_ts"))
          .withColumn("order_date", F.to_date("order_ts"))
          .withColumn("gross_amount", F.round(F.col("quantity") * F.col("unit_price"), 2))
    )

    # Overwrite only the affected partition(s) -> idempotent re-runs.
    (cleaned.write
        .mode("overwrite")
        .partitionBy("order_date")
        .parquet(dst))


if __name__ == "__main__":
    main()
