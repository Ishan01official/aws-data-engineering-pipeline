"""
S3-trigger ingestion validation Lambda.

Purpose:
    Invoked when a file lands in the raw/bronze S3 zone. Validates basic
    metadata (key shape, non-empty, expected prefix), emits a structured log
    line, and returns a routing decision (accept -> ready for cataloging,
    reject -> quarantine). This is the "validate & route" box in the
    capstone architecture.

Inputs:
    event: an S3 put notification (optionally wrapped in SNS), i.e. one or
           more records each describing a bucket + object key.

Outputs:
    A dict summarizing per-record decisions. Side effects (moving rejects to a
    quarantine prefix, publishing SNS alerts) are left as TODOs wired up in the
    capstone's LambdaStack so this module stays unit-testable with no AWS calls.

Run locally:
    python -c "import json,handler; print(handler.handler(handler.SAMPLE_EVENT, None))"

Deploy:
    Packaged by infra/cdk LambdaStack (Module 03). Needs an execution role with
    least-privilege s3:GetObject on the raw bucket and (when enabled)
    s3:PutObject on the quarantine prefix + sns:Publish on the alert topic.

Common errors:
    - KeyError on event shape: the event wasn't an S3 (or SNS-wrapped S3) event.
    - AccessDenied at deploy time: execution role missing s3:GetObject.

Cost warning:
    The function itself is near-free (per-ms). It does NOT create paid resources
    on its own, but the pipeline it feeds (Glue, Redshift) does.
"""
from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger()
logger.setLevel(logging.INFO)

EXPECTED_PREFIX = "raw/"  # only accept objects landing in the raw zone


def _structured_log(decision: str, bucket: str, key: str, reason: str) -> None:
    """Emit one concise, parseable log line. Structured logs make CloudWatch
    Logs Insights queries and alerting far easier than free-text logs."""
    logger.info(
        json.dumps(
            {
                "event": "ingestion_validation",
                "decision": decision,
                "bucket": bucket,
                "key": key,
                "reason": reason,
            }
        )
    )


def _iter_s3_records(event: dict[str, Any]):
    """Yield (bucket, key, size) from an S3 event, transparently unwrapping
    SNS-wrapped S3 events (a common pattern when S3 -> SNS -> Lambda)."""
    for record in event.get("Records", []):
        # SNS-wrapped: the S3 event is JSON inside record["Sns"]["Message"].
        if "Sns" in record:
            inner = json.loads(record["Sns"]["Message"])
            yield from _iter_s3_records(inner)
            continue
        s3 = record["s3"]
        bucket = s3["bucket"]["name"]
        obj = s3["object"]
        yield bucket, obj["key"], obj.get("size", 0)


def validate_object(key: str, size: int) -> tuple[str, str]:
    """Pure validation logic — no AWS calls, so it's trivially unit-testable.
    Returns (decision, reason) where decision is 'accept' or 'reject'."""
    if not key.startswith(EXPECTED_PREFIX):
        return "reject", f"key not under expected prefix '{EXPECTED_PREFIX}'"
    if size == 0:
        return "reject", "empty object"
    if key.endswith("/"):
        return "reject", "folder marker, not a file"
    return "accept", "passed basic validation"


def handler(event: dict[str, Any], _context: Any) -> dict[str, Any]:
    results = []
    for bucket, key, size in _iter_s3_records(event):
        decision, reason = validate_object(key, size)
        _structured_log(decision, bucket, key, reason)
        # TODO (capstone LambdaStack): on reject, copy to quarantine/ prefix
        #   and publish an SNS alert; on accept, optionally trigger the crawler.
        results.append({"bucket": bucket, "key": key, "decision": decision, "reason": reason})
    return {"validated": len(results), "results": results}


# A minimal sample event so the file is runnable standalone (see "Run locally").
SAMPLE_EVENT = {
    "Records": [
        {"s3": {"bucket": {"name": "REPLACE_BUCKET"},
                "object": {"key": "raw/sales/2025-01-15/orders.csv", "size": 2048}}}
    ]
}
