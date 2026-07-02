"""Unit tests for the Lab 02 catalog validation logic (no AWS — fake Glue client).
Run: pytest tests/unit -q
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))

import validate_glue_catalog as vgc


def make_table(name: str, entity: str, partition_keys=None, drop_column: str | None = None):
    cols = [c for c in vgc.EXPECTED_COLUMNS[entity] if c != drop_column]
    return {
        "Name": name,
        "PartitionKeys": [{"Name": k} for k in (partition_keys
                                                if partition_keys is not None
                                                else ["ingestion_date"])],
        "StorageDescriptor": {"Columns": [{"Name": c} for c in cols]},
    }


GOOD_TABLES = [
    make_table("raw_entity_orders", "orders"),
    make_table("raw_entity_customers", "customers"),
    make_table("raw_entity_products", "products"),
]


class FakeGlue:
    """Just enough of the Glue client for validate()."""

    def __init__(self, tables, partitions=True, database_exists=True):
        self.tables = tables
        self.partitions = partitions
        self.database_exists = database_exists

    def get_database(self, Name):
        if not self.database_exists:
            from botocore.exceptions import ClientError
            raise ClientError(
                {"Error": {"Code": "EntityNotFoundException", "Message": "no db"}},
                "GetDatabase")
        return {"Database": {"Name": Name}}

    def get_paginator(self, op):
        assert op == "get_tables"
        tables = self.tables

        class P:
            def paginate(self, **kw):
                yield {"TableList": tables}
        return P()

    def get_partitions(self, DatabaseName, TableName, Expression):
        return {"Partitions": [{"Values": ["2026-07-01"]}] if self.partitions else []}


def test_all_good_returns_zero(capsys):
    rc = vgc.validate(FakeGlue(GOOD_TABLES), "retail_lake", "2026-07-01")
    assert rc == 0
    out = capsys.readouterr().out
    assert out.count("[PASS] table") == 3
    assert out.count("[PASS] partition") == 3


def test_missing_database_fails(capsys):
    rc = vgc.validate(FakeGlue(GOOD_TABLES, database_exists=False), "retail_lake",
                      "2026-07-01")
    assert rc == 1
    assert "not found" in capsys.readouterr().out


def test_missing_entity_table_fails(capsys):
    rc = vgc.validate(FakeGlue(GOOD_TABLES[:2]), "retail_lake", "2026-07-01")
    assert rc == 1
    assert "no table for 'products'" in capsys.readouterr().out


def test_wrong_partition_key_fails(capsys):
    tables = GOOD_TABLES[:2] + [make_table("raw_entity_products", "products",
                                           partition_keys=["source", "entity"])]
    rc = vgc.validate(FakeGlue(tables), "retail_lake", "2026-07-01")
    assert rc == 1
    assert "partition keys" in capsys.readouterr().out


def test_missing_column_fails(capsys):
    tables = GOOD_TABLES[:2] + [make_table("raw_entity_products", "products",
                                           drop_column="brand")]
    rc = vgc.validate(FakeGlue(tables), "retail_lake", "2026-07-01")
    assert rc == 1
    assert "missing columns ['brand']" in capsys.readouterr().out


def test_unregistered_partition_fails(capsys):
    rc = vgc.validate(FakeGlue(GOOD_TABLES, partitions=False), "retail_lake",
                      "2026-07-01")
    assert rc == 1
    assert "[FAIL] partition" in capsys.readouterr().out


def test_find_entity_table_matches_by_substring():
    assert vgc.find_entity_table(GOOD_TABLES, "customers")["Name"] == "raw_entity_customers"
    assert vgc.find_entity_table([], "orders") is None


def test_cli_rejects_bad_date():
    assert vgc.main(["--ingestion-date", "01-07-2026"]) == 2
