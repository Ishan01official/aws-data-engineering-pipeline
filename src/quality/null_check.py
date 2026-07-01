"""
Null / blank value checks for critical columns.

Purpose:
    Ensure columns that must never be empty (keys, foreign keys, amounts) are
    populated. A null customer_id in an orders feed is a data-quality defect that
    should quarantine the batch, not silently flow to the warehouse.

Example:
    from quality.null_check import check_not_null
    result = check_not_null(rows, columns=["order_id", "customer_id"])
    assert result.ok, result.summary()
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class NullResult:
    ok: bool
    null_counts: dict[str, int] = field(default_factory=dict)
    checked_rows: int = 0

    def summary(self) -> str:
        bad = {c: n for c, n in self.null_counts.items() if n}
        return ("null-check OK " if self.ok else "null-check FAIL ") + \
            f"rows={self.checked_rows} nulls={bad or 'none'}"


def _is_blank(v) -> bool:
    return v is None or (isinstance(v, str) and v.strip() == "")


def check_not_null(rows: list[dict], columns: list[str]) -> NullResult:
    """Count blank/None values per column; ok only if all are zero."""
    counts = {c: 0 for c in columns}
    for r in rows:
        for c in columns:
            if _is_blank(r.get(c)):
                counts[c] += 1
    ok = all(v == 0 for v in counts.values())
    return NullResult(ok=ok, null_counts=counts, checked_rows=len(rows))
