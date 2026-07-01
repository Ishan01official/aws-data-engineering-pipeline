# 02 · Cost

Storage is the cheap part of a data lake; *scanning* it carelessly is where money leaks. The levers, by impact.

## 1. Columnar + partitioned format (biggest lever)
Athena and Redshift Spectrum bill **per byte scanned**. Two changes cut that dramatically:
- **Parquet instead of CSV/JSON** — columnar means a query reads only the columns it needs, and compression shrinks bytes. Often 90%+ scan reduction.
- **Partitioning on the filter column** — partition pruning skips whole folders. `WHERE order_date = X` scans one day, not the whole table.

Together these are the difference between a $5 query and a $500 one on the same data.

## 2. Storage classes + lifecycle
S3 Standard (~$0.023/GB-mo) is for hot data. Move cold data down tiers automatically:
| Class | Rough use |
|---|---|
| Standard | Frequently queried (silver/gold) |
| Standard-IA | Infrequently accessed (older raw) |
| Glacier / Deep Archive | Archive, rarely read |

The stack's raw bucket already tiers to IA @30d and Glacier @90d. Tune to your access pattern.

## 3. Expire what you don't need
- **Non-current versions:** versioned buckets keep old versions forever unless you expire them — the stack expires them at 30–90 days.
- **Athena query results:** expire at 14 days (the stack does this) so result files don't pile up.

## 4. Avoid the small-files tax
Millions of tiny files inflate request costs and slow scans. Don't over-partition; compact small files; buffer streaming writes (Firehose).

## Quick cost checklist
- [ ] Analytics data is partitioned Parquet, not raw CSV
- [ ] Partitioned on the column you filter by
- [ ] Lifecycle tiering cold data down
- [ ] Non-current versions + query results expiring
- [ ] No tiny-file explosion from over-partitioning
- [ ] Budget alarm + cost anomaly detection on

See the repo-wide [COST-OPTIMIZATION](../COST-OPTIMIZATION.md).
