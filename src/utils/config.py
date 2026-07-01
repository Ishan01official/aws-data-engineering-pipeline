"""
Configuration loader for pipeline components.

Purpose:
    One place to read configuration from environment variables (12-factor style)
    with clear errors when something required is missing, so components fail fast
    with a helpful message instead of a cryptic KeyError deep in the code.

Required/expected environment variables (per component; see get_config):
    RAW_BUCKET, SILVER_BUCKET, GOLD_BUCKET   S3 zone buckets
    QUARANTINE_PREFIX                         where rejected data goes (default: quarantine/)
    ALERT_TOPIC_ARN                           SNS topic for failures (optional)
    LOG_LEVEL                                 optional

Example:
    from utils.config import get_config
    cfg = get_config(["RAW_BUCKET", "SILVER_BUCKET"])
    bucket = cfg["RAW_BUCKET"]
"""
from __future__ import annotations

import os

from utils.errors import ConfigError


def get_config(required: list[str], defaults: dict[str, str] | None = None) -> dict[str, str]:
    """Return a dict of the requested env vars, raising ConfigError if any
    required one is unset. `defaults` supplies fallbacks for optional keys."""
    defaults = defaults or {}
    resolved: dict[str, str] = {}
    missing: list[str] = []
    for key in required:
        val = os.environ.get(key, defaults.get(key))
        if val is None:
            missing.append(key)
        else:
            resolved[key] = val
    if missing:
        raise ConfigError(f"missing required env vars: {', '.join(missing)}",
                          context={"missing": missing})
    # add any defaults not in required
    for k, v in defaults.items():
        resolved.setdefault(k, v)
    return resolved
