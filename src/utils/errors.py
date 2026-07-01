"""
Typed exceptions for data-engineering pipelines.

Purpose:
    Distinguish error classes so callers (and Step Functions Catch blocks) can
    react differently: a validation error should quarantine data and alert; a
    transient error should retry with backoff; a config error should fail fast.

Example:
    from utils.errors import ValidationError, TransientError
    if size == 0:
        raise ValidationError("empty object", context={"key": key})
"""
from __future__ import annotations

from typing import Any


class PipelineError(Exception):
    """Base class. Carries an optional structured context dict for logging."""

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.context = context or {}


class ValidationError(PipelineError):
    """Data failed a validation/quality rule. Quarantine + alert; do NOT retry."""


class TransientError(PipelineError):
    """A temporary failure (throttling, timeout). Safe to retry with backoff."""


class ConfigError(PipelineError):
    """Missing/invalid configuration. Fail fast; retrying won't help."""
