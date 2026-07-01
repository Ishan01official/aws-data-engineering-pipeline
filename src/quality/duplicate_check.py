"""
Duplicate detection on a natural/business key.

Purpose:
    Detect duplicate records by key (e.g. duplicate order_id). Duplicates arise
    from at-least-once delivery, retries, or overlapping backfills; catching them
    supports the idempotency discipline (dedupe before/at load).

Example:
    from quality.duplicate_check import check_unique
    result = check_unique(rows, key="order_id")
    assert result.ok, result.summary()
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field


@dataclass
class DuplicateResult:
    ok: bool
    duplicate_keys: dict[str, int] = field(default_factory=dict)
    checked_rows: int = 0

    def summary(self) -> str:
        return ("dup-check OK " if self.ok else "dup-check FAIL ") + \
            f"rows={self.checked_rows} dups={self.duplicate_keys or 'none'}"


def check_unique(rows: list[dict], key: str) -> DuplicateResult:
    """Flag any key value appearing more than once."""
    counts = Counter(r.get(key) for r in rows)
    dups = {str(k): n for k, n in counts.items() if k is not None and n > 1}
    return DuplicateResult(ok=not dups, duplicate_keys=dups, checked_rows=len(rows))
