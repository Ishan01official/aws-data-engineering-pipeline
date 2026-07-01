"""Tests for the reusable data-quality checks. No AWS / Spark needed.
Run: pytest tests/data_quality -q
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from quality.schema_validation import validate_schema
from quality.null_check import check_not_null
from quality.duplicate_check import check_unique
from quality.freshness_check import check_freshness
from quality.reconciliation_check import reconcile_counts, reconcile_sum

ROWS = [
    {"order_id": "O1", "customer_id": "C1", "order_ts": "2026-07-01T09:00:00Z", "amount": "10.0"},
    {"order_id": "O2", "customer_id": "C2", "order_ts": "2026-07-01T10:00:00Z", "amount": "20.0"},
]


def test_schema_ok_and_missing():
    assert validate_schema(ROWS, required={"order_id", "customer_id"}).ok
    r = validate_schema(ROWS, required={"order_id", "missing_col"})
    assert not r.ok and "missing_col" in r.missing_columns


def test_schema_empty_rows_not_ok():
    assert not validate_schema([], required={"order_id"}).ok


def test_null_check():
    assert check_not_null(ROWS, ["order_id", "customer_id"]).ok
    bad = ROWS + [{"order_id": "", "customer_id": "C3", "order_ts": "x", "amount": "1"}]
    r = check_not_null(bad, ["order_id"])
    assert not r.ok and r.null_counts["order_id"] == 1


def test_duplicate_check():
    assert check_unique(ROWS, "order_id").ok
    dup = ROWS + [{"order_id": "O1", "customer_id": "C9", "order_ts": "x", "amount": "1"}]
    r = check_unique(dup, "order_id")
    assert not r.ok and r.duplicate_keys["O1"] == 2


def test_freshness():
    fresh = check_freshness(ROWS, "order_ts", max_age_hours=48,
                            now_iso="2026-07-02T09:00:00Z")
    assert fresh.ok
    stale = check_freshness(ROWS, "order_ts", max_age_hours=1,
                            now_iso="2026-07-05T09:00:00Z")
    assert not stale.ok


def test_freshness_no_data_fails():
    assert not check_freshness([], "order_ts", max_age_hours=1,
                               now_iso="2026-07-02T00:00:00Z").ok


def test_reconciliation():
    assert reconcile_counts(1000, 1000).ok
    assert reconcile_counts(1000, 998, allowed_drop=2).ok
    assert not reconcile_counts(1000, 990, allowed_drop=2).ok
    assert not reconcile_counts(1000, 1001).ok      # invented rows
    assert reconcile_sum(19999.50, 19999.50).ok
    assert not reconcile_sum(100.0, 105.0).ok
