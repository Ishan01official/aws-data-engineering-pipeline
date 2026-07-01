"""Unit tests for the ingestion validation Lambda.
Run: pytest tests/unit -q   (no AWS credentials required)
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src", "lambda"))
import handler  # noqa: E402


def test_accepts_valid_raw_object():
    decision, _ = handler.validate_object("raw/sales/2025-01-15/orders.csv", 2048)
    assert decision == "accept"


def test_rejects_wrong_prefix():
    decision, reason = handler.validate_object("staging/x.csv", 10)
    assert decision == "reject" and "prefix" in reason


def test_rejects_empty_object():
    decision, reason = handler.validate_object("raw/x.csv", 0)
    assert decision == "reject" and "empty" in reason


def test_rejects_folder_marker():
    decision, _ = handler.validate_object("raw/sales/", 0)
    assert decision == "reject"


def test_handler_processes_sample_event():
    out = handler.handler(handler.SAMPLE_EVENT, None)
    assert out["validated"] == 1
    assert out["results"][0]["decision"] == "accept"


def test_handler_unwraps_sns():
    import json
    sns_event = {"Records": [{"Sns": {"Message": json.dumps(handler.SAMPLE_EVENT)}}]}
    out = handler.handler(sns_event, None)
    assert out["validated"] == 1
