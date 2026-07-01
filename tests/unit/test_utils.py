"""Tests for shared utils. No AWS needed (s3 client is faked).
Run: pytest tests/unit -q
"""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

import pytest
from utils.s3_utils import parse_s3_event, quarantine_key, object_exists
from utils.config import get_config
from utils.errors import ConfigError


def test_parse_direct_s3_event():
    ev = {"Records": [{"s3": {"bucket": {"name": "b"},
                              "object": {"key": "raw/x.csv", "size": 5}}}]}
    assert list(parse_s3_event(ev)) == [("b", "raw/x.csv", 5)]


def test_parse_sns_wrapped_event():
    inner = {"Records": [{"s3": {"bucket": {"name": "b"},
                                 "object": {"key": "raw/y.csv", "size": 7}}}]}
    ev = {"Records": [{"Sns": {"Message": json.dumps(inner)}}]}
    assert list(parse_s3_event(ev)) == [("b", "raw/y.csv", 7)]


def test_quarantine_key_preserves_tail():
    assert quarantine_key("raw/source=retail/entity=orders/x.csv") == \
        "quarantine/source=retail/entity=orders/x.csv"


def test_get_config_missing_raises():
    with pytest.raises(ConfigError):
        get_config(["DEFINITELY_UNSET_VAR_XYZ"])


def test_get_config_with_default():
    cfg = get_config([], defaults={"QUARANTINE_PREFIX": "quarantine/"})
    assert cfg["QUARANTINE_PREFIX"] == "quarantine/"


class _FakeS3:
    def __init__(self, exists): self._exists = exists
    def head_object(self, Bucket, Key):
        if self._exists:
            return {}
        from botocore.exceptions import ClientError
        raise ClientError({"Error": {"Code": "404"}}, "HeadObject")


def test_object_exists_true_false():
    assert object_exists(_FakeS3(True), "b", "k") is True
    assert object_exists(_FakeS3(False), "b", "k") is False
