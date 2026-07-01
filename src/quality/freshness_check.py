"""
Freshness check: is the newest record recent enough?

Purpose:
    Detect stale feeds. If the latest event timestamp is older than an SLA
    threshold, the upstream feed is late/broken and downstream marts shouldn't be
    trusted as current. Freshness is a core data-quality dimension.

Example:
    from quality.freshness_check import check_freshness
    result = check_freshness(rows, ts_column="order_ts", max_age_hours=26,
                             now_iso="2026-07-02T00:00:00Z")
    assert result.ok, result.summary()
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class FreshnessResult:
    ok: bool
    newest_ts: str | None
    age_hours: float | None

    def summary(self) -> str:
        return ("freshness OK " if self.ok else "freshness FAIL ") + \
            f"newest={self.newest_ts} age_h={self.age_hours}"


def _parse(ts: str) -> datetime:
    # Accept ...Z or offset ISO 8601
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def check_freshness(rows: list[dict], ts_column: str, max_age_hours: float,
                    now_iso: str | None = None) -> FreshnessResult:
    """ok if the newest ts_column value is within max_age_hours of `now`."""
    now = _parse(now_iso) if now_iso else datetime.now(timezone.utc)
    stamps = [_parse(r[ts_column]) for r in rows if r.get(ts_column)]
    if not stamps:
        return FreshnessResult(ok=False, newest_ts=None, age_hours=None)
    newest = max(stamps)
    age_h = (now - newest).total_seconds() / 3600.0
    return FreshnessResult(ok=age_h <= max_age_hours,
                           newest_ts=newest.isoformat(), age_hours=round(age_h, 2))
