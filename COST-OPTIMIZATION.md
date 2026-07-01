# Cost Optimization

On AWS, an architecture you can't afford is a wrong architecture. Cost is a design constraint, not an afterthought. This is the cross-cutting reference; each module has its own `cost.md` for service specifics.

## The five biggest data-engineering cost levers

1. **Storage format & partitioning.** Athena and Redshift Spectrum bill by **data scanned**. Converting CSV/JSON to partitioned, compressed **Parquet** routinely cuts scan cost by 90%+. This is the single highest-ROI change in most lakes.
2. **Serverless vs provisioned at the right utilization.** Serverless scales to zero (great for spiky/idle); provisioned is cheaper per-unit at sustained high utilization (~60–70%+). Match the billing model to the workload shape. → [Service Decision Framework](./SERVICE-DECISION-FRAMEWORK.md#13-serverless-vs-provisioned)
3. **S3 storage classes & lifecycle.** Move cold data Standard → IA → Glacier on a lifecycle policy. Raw/bronze data that's rarely re-read is the obvious candidate. Don't pay Standard rates for data nobody queries.
4. **Right-sizing compute.** Over-provisioned Glue DPUs, idle EMR clusters, and oversized Redshift are common money sinks. Use auto-scaling, EMR Serverless, and Redshift Serverless where load is variable.
5. **Killing idle and orphaned resources.** Forgotten dev clusters, unattached resources, and resources in non-default regions. The capstone and every lab include cleanup for exactly this reason.

## Cost anti-patterns to hunt for
- `SELECT *` on unpartitioned data in Athena — the classic surprise-bill generator.
- Always-on MWAA or EMR clusters for intermittent workloads.
- Streaming (Kinesis/MSK) provisioned for volume that batch would handle.
- Tiny-file explosions from over-partitioning, which inflate request costs and slow scans.
- No budget alarm — you find out from the bill instead of an alert.

## A cost-review checklist for any pipeline
- [ ] Is analytics data in columnar (Parquet/Iceberg) and partitioned on the common filter?
- [ ] Does each compute choice match its workload's utilization shape?
- [ ] Are lifecycle policies moving cold data to cheaper tiers?
- [ ] Are dev/test resources auto-stopped or torn down?
- [ ] Is there a budget alarm and cost anomaly detection?
- [ ] Have you modeled the cost *before* building, not after?

> See the AWS **Well-Architected Data Analytics Lens** for the authoritative cost-optimization pillar guidance, and pair this with [TROUBLESHOOTING-RUNBOOK.md](./TROUBLESHOOTING-RUNBOOK.md) for "why is this query so expensive."
