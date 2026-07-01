"""Unit tests for the S3 raw-zone key layout helpers.
Run: pytest tests/unit -q   (no AWS needed)
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))
import pytest
import lake_layout as ll


def test_raw_prefix_shape():
    assert ll.raw_prefix("orders", "2026-07-01") == \
        "raw/source=retail/entity=orders/ingestion_date=2026-07-01/"


def test_raw_key_appends_filename():
    key = ll.raw_key("customers", "2026-07-01", "customers_2026_07_01.csv")
    assert key == ("raw/source=retail/entity=customers/"
                   "ingestion_date=2026-07-01/customers_2026_07_01.csv")


def test_default_filename():
    assert ll.default_filename("products", "2026-07-01") == "products_2026_07_01.csv"


def test_all_entities_have_hive_partitions():
    for e in ll.ENTITIES:
        p = ll.raw_prefix(e, "2026-07-01")
        assert "source=retail" in p and f"entity={e}" in p and "ingestion_date=" in p


def test_rejects_unknown_entity():
    with pytest.raises(ValueError):
        ll.raw_prefix("invoices", "2026-07-01")


def test_rejects_bad_date():
    with pytest.raises(ValueError):
        ll.raw_prefix("orders", "07-01-2026")


def test_rejects_filename_with_slash():
    with pytest.raises(ValueError):
        ll.raw_key("orders", "2026-07-01", "sub/dir/file.csv")
