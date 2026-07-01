"""Tests for the Spark-free core of the bronze->silver orders transform.
Run: pytest tests/unit -q  (no Spark/AWS needed)
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from glue_jobs.bronze_to_silver_orders import clean_orders_records

GOOD = {"order_id": "O1", "customer_id": "C1", "product_id": "P1",
        "order_ts": "2026-07-01T09:00:00Z", "quantity": "2", "unit_price": "10.0",
        "currency": "USD", "channel": "web", "region": "north"}


def test_happy_path_derives_fields():
    out = clean_orders_records([GOOD])
    assert len(out) == 1
    row = out[0]
    assert row["quantity"] == 2 and row["unit_price"] == 10.0
    assert row["gross_amount"] == 20.0
    assert row["order_date"] == "2026-07-01"


def test_drops_missing_keys():
    bad = dict(GOOD, customer_id="")
    assert clean_orders_records([bad]) == []


def test_dedupes_on_order_id():
    out = clean_orders_records([GOOD, dict(GOOD, region="south")])
    assert len(out) == 1
    assert out[0]["region"] == "north"  # first kept


def test_drops_non_numeric_and_nonpositive():
    assert clean_orders_records([dict(GOOD, quantity="abc")]) == []
    assert clean_orders_records([dict(GOOD, quantity="0")]) == []
    assert clean_orders_records([dict(GOOD, unit_price="-5")]) == []


def test_drops_row_without_timestamp():
    assert clean_orders_records([dict(GOOD, order_ts="")]) == []
