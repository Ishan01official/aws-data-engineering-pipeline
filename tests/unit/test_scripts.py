"""Unit tests for the Lab 01 scripts (no AWS calls — dry-run and pure logic only).
Run: pytest tests/unit -q
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))

import pytest

import build_s3_prefix as bsp
import create_local_lake_layout as cll
import upload_sample_data as usd

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(REPO_ROOT, "data", "sample", "retail")


# ---------- build_s3_prefix ----------

def test_build_prefix_without_filename():
    assert bsp.build("orders", "2026-07-01", None) == \
        "raw/source=retail/entity=orders/ingestion_date=2026-07-01/"


def test_build_key_with_filename_and_bucket_uri():
    uri = bsp.build("products", "2026-07-01", "products_2026_07_01.csv",
                    bucket="my-raw-bucket")
    assert uri == ("s3://my-raw-bucket/raw/source=retail/entity=products/"
                   "ingestion_date=2026-07-01/products_2026_07_01.csv")


def test_build_rejects_bad_inputs():
    with pytest.raises(ValueError):
        bsp.build("invoices", "2026-07-01", None)
    with pytest.raises(ValueError):
        bsp.build("orders", "01-07-2026", None)


def test_build_cli_prints_key(capsys):
    rc = bsp.main(["--entity", "customers", "--ingestion-date", "2026-07-01",
                   "--filename", "customers_2026_07_01.csv"])
    assert rc == 0
    out = capsys.readouterr().out.strip()
    assert out.endswith("customers_2026_07_01.csv")
    assert out.startswith("raw/source=retail/entity=customers/")


def test_build_cli_bad_date_exits_nonzero():
    assert bsp.main(["--entity", "orders", "--ingestion-date", "bad"]) == 2


# ---------- create_local_lake_layout ----------

def test_create_layout_makes_all_zones(tmp_path):
    created = cll.create_layout(tmp_path / "lake")
    names = sorted(d.name for d in created)
    assert names == ["bronze", "gold", "raw", "silver"]
    for d in created:
        assert (d / "README.md").is_file()


def test_create_layout_cli(tmp_path, capsys):
    rc = cll.main(["--base", str(tmp_path / "lake2")])
    assert rc == 0
    assert "Created local lake" in capsys.readouterr().out
    assert (tmp_path / "lake2" / "raw" / "README.md").is_file()


# ---------- upload_sample_data ----------

def test_find_local_csv_locates_each_entity():
    from pathlib import Path
    for entity in ("orders", "customers", "products"):
        found = usd.find_local_csv(Path(DATA_DIR), entity)
        assert found.name.startswith(entity)
        assert found.suffix == ".csv"


def test_find_local_csv_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        usd.find_local_csv(tmp_path, "orders")


def test_upload_dry_run_prints_plan_and_makes_no_aws_calls(capsys):
    rc = usd.main(["--bucket", "unit-test-bucket", "--data-dir", DATA_DIR,
                   "--ingestion-date", "2026-07-01", "--dry-run"])
    assert rc == 0
    out = capsys.readouterr().out
    assert out.count("DRY-RUN") == 3
    assert "s3://unit-test-bucket/raw/source=retail/entity=orders/" in out
    assert "Dry run complete" in out


def test_upload_rejects_bad_date():
    assert usd.main(["--bucket", "b", "--ingestion-date", "2026/07/01",
                     "--dry-run"]) == 2


def test_upload_rejects_missing_data_dir(tmp_path):
    missing = str(tmp_path / "nope")
    assert usd.main(["--bucket", "b", "--data-dir", missing, "--dry-run"]) == 2
