"""
S3 helper functions for pipeline components.

Purpose:
    Small, well-tested helpers for the S3 operations pipelines repeat: parsing
    S3 events, building deterministic keys, copying an object to a quarantine
    prefix, and checking existence. Keeping these here means the logic is tested
    once and reused everywhere.

Required environment variables:
    None directly; callers pass buckets/keys in.

Example:
    from utils.s3_utils import parse_s3_event, quarantine_key
    for bucket, key, size in parse_s3_event(event):
        ...
"""
from __future__ import annotations

import json
from typing import Any, Iterator


def parse_s3_event(event: dict[str, Any]) -> Iterator[tuple[str, str, int]]:
    """Yield (bucket, key, size) from an S3 event, unwrapping SNS-wrapped events.

    Handles both direct S3 notifications and S3 -> SNS -> Lambda, a common
    fan-out pattern.
    """
    for record in event.get("Records", []):
        if "Sns" in record:
            inner = json.loads(record["Sns"]["Message"])
            yield from parse_s3_event(inner)
            continue
        if "s3" in record:
            s3 = record["s3"]
            yield s3["bucket"]["name"], s3["object"]["key"], s3["object"].get("size", 0)


def quarantine_key(original_key: str, prefix: str = "quarantine/") -> str:
    """Map a raw key to its quarantine location, preserving the tail path.

    >>> quarantine_key("raw/source=retail/entity=orders/x.csv")
    'quarantine/source=retail/entity=orders/x.csv'
    """
    tail = original_key.split("raw/", 1)[-1] if "raw/" in original_key else original_key
    return prefix + tail


def object_exists(s3_client, bucket: str, key: str) -> bool:
    """True if the object exists. Requires a boto3 s3 client (dependency injected
    so this is unit-testable with a fake client)."""
    from botocore.exceptions import ClientError
    try:
        s3_client.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] in ("404", "NoSuchKey", "NotFound"):
            return False
        raise
