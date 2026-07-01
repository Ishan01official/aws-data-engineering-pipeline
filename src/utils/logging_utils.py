"""
Structured logging helpers for data-engineering Lambdas and jobs.

Purpose:
    Give every component one consistent, JSON-structured logging setup so
    CloudWatch Logs Insights queries and alerting work uniformly. Structured
    logs (one JSON object per line) are far easier to filter and aggregate than
    free-text logs.

Required environment variables:
    LOG_LEVEL   Optional. One of DEBUG/INFO/WARNING/ERROR (default INFO).

Example:
    from utils.logging_utils import get_logger, log_event
    log = get_logger(__name__)
    log_event(log, "ingestion_start", source="retail", entity="orders")

Design notes:
    - We suppress noisy third-party loggers (boto/botocore) at WARNING so real
      signal isn't drowned out — a common production hygiene step.
    - Payload dumps belong at DEBUG only, never INFO, to avoid leaking data and
      bloating logs in normal operation.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any

_NOISY = ("boto3", "botocore", "s3transfer", "urllib3")


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger. Idempotent — safe to call per-module."""
    level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
    logger.setLevel(level)
    for noisy in _NOISY:
        logging.getLogger(noisy).setLevel(logging.WARNING)
    return logger


def log_event(logger: logging.Logger, event: str, level: int = logging.INFO,
              **fields: Any) -> None:
    """Emit one structured JSON log line: {"event": ..., **fields}.

    Keeps a stable 'event' key so alerts can match on event type regardless of
    the other fields present.
    """
    record = {"event": event}
    record.update(fields)
    logger.log(level, json.dumps(record, default=str))
