"""Validate the sample retail CSVs have the expected schema and clean data.
Run: pytest tests/unit -q   (no AWS needed)
"""
import csv
import os

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample", "retail")

EXPECTED = {
    "orders": (
        "orders/orders_2026_07_01.csv",
        ["order_id", "customer_id", "product_id", "order_ts", "quantity",
         "unit_price", "currency", "channel", "region"],
    ),
    "customers": (
        "customers/customers_2026_07_01.csv",
        ["customer_id", "first_name", "last_name", "email", "signup_date",
         "segment", "region"],
    ),
    "products": (
        "products/products_2026_07_01.csv",
        ["product_id", "product_name", "category", "subcategory", "list_price",
         "currency", "active"],
    ),
}


def _rows(rel):
    with open(os.path.join(BASE, rel), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_files_exist_with_expected_headers():
    for _, (rel, headers) in EXPECTED.items():
        path = os.path.join(BASE, rel)
        assert os.path.exists(path), f"missing sample file: {path}"
        with open(path, newline="", encoding="utf-8") as f:
            assert next(csv.reader(f)) == headers


def test_no_empty_rows_and_ids_unique():
    for entity, (rel, _) in EXPECTED.items():
        rows = _rows(rel)
        assert rows, f"{entity} has no data rows"
        id_col = {"orders": "order_id", "customers": "customer_id",
                  "products": "product_id"}[entity]
        ids = [r[id_col] for r in rows]
        assert all(ids), f"{entity} has blank id"
        assert len(ids) == len(set(ids)), f"{entity} has duplicate ids"


def test_orders_reference_valid_customers_and_products():
    cust_ids = {r["customer_id"] for r in _rows(EXPECTED["customers"][0])}
    prod_ids = {r["product_id"] for r in _rows(EXPECTED["products"][0])}
    for r in _rows(EXPECTED["orders"][0]):
        assert r["customer_id"] in cust_ids, f"order {r['order_id']} bad customer"
        assert r["product_id"] in prod_ids, f"order {r['order_id']} bad product"
        assert int(r["quantity"]) > 0
        assert float(r["unit_price"]) >= 0
