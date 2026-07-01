"""
Reconciliation check: does the processed output match the source counts/sums?

Purpose:
    After transforming raw -> silver, confirm nothing was lost or invented:
    row counts match (allowing for known drops) and a control total (e.g. sum of
    amounts) reconciles within tolerance. Reconciliation is how you prove a
    pipeline is trustworthy, not just that it ran.

Example:
    from quality.reconciliation_check import reconcile_counts, reconcile_sum
    assert reconcile_counts(src_n=1000, dst_n=998, allowed_drop=2).ok
    assert reconcile_sum(19999.50, 19999.50).ok
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ReconResult:
    ok: bool
    detail: str


def reconcile_counts(src_n: int, dst_n: int, allowed_drop: int = 0) -> ReconResult:
    """ok if dst is within [src - allowed_drop, src]. Gaining rows is always a
    failure (data invented); dropping more than allowed is a failure."""
    if dst_n > src_n:
        return ReconResult(False, f"dst {dst_n} > src {src_n} (rows invented)")
    if src_n - dst_n > allowed_drop:
        return ReconResult(False, f"dropped {src_n - dst_n} > allowed {allowed_drop}")
    return ReconResult(True, f"counts ok src={src_n} dst={dst_n}")


def reconcile_sum(src_total: float, dst_total: float, tolerance: float = 0.01) -> ReconResult:
    """ok if control totals match within an absolute tolerance (float safety)."""
    diff = abs(src_total - dst_total)
    if diff > tolerance:
        return ReconResult(False, f"sum mismatch {src_total} vs {dst_total} (diff {diff})")
    return ReconResult(True, f"sum ok {src_total}")
