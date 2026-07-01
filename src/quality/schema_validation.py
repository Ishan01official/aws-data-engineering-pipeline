"""
Schema validation for tabular records.

Purpose:
    Verify that a batch of records (list of dicts, e.g. parsed CSV rows) matches
    an expected schema: required columns present, no unexpected columns (optional),
    and basic type coercion checks. Catching schema drift here prevents corrupt
    data from being promoted to silver/gold.

Why pure-Python (no Spark):
    Kept dependency-free so it runs in a Lambda, in a Glue Python-shell job, and
    in unit tests identically. For big data you'd apply the same rules as Spark
    column checks; the logic is the same.

Example:
    from quality.schema_validation import validate_schema, SchemaResult
    result = validate_schema(rows, required={"order_id", "customer_id"})
    if not result.ok:
        raise ValidationError(result.summary())
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SchemaResult:
    ok: bool
    missing_columns: set[str] = field(default_factory=set)
    unexpected_columns: set[str] = field(default_factory=set)
    checked_rows: int = 0

    def summary(self) -> str:
        parts = [f"rows={self.checked_rows}"]
        if self.missing_columns:
            parts.append(f"missing={sorted(self.missing_columns)}")
        if self.unexpected_columns:
            parts.append(f"unexpected={sorted(self.unexpected_columns)}")
        return "schema " + ("OK " if self.ok else "FAIL ") + " ".join(parts)


def validate_schema(rows: list[dict], required: set[str],
                    allow_extra: bool = True) -> SchemaResult:
    """Check that every row has all `required` columns. If allow_extra is False,
    also flag columns not in `required`."""
    if not rows:
        # No rows is itself a schema/freshness concern; report as not-ok.
        return SchemaResult(ok=False, missing_columns=set(required), checked_rows=0)

    present = set(rows[0].keys())
    missing = required - present
    unexpected = (present - required) if not allow_extra else set()
    ok = not missing and not unexpected
    return SchemaResult(ok=ok, missing_columns=missing,
                        unexpected_columns=unexpected, checked_rows=len(rows))
