# 02 · Architecture

The diagrams the spec calls for: the zone model, the ingestion flow, partition pruning, and the raw→bronze→silver→gold progression.

## S3 data lake zone diagram

```mermaid
flowchart TB
    subgraph LAKE[S3 Data Lake]
        RAW["raw / bronze<br/>immutable · any format<br/>source of truth"]
        SILVER["silver<br/>cleaned · deduped · typed<br/>partitioned Parquet"]
        GOLD["gold<br/>aggregated marts<br/>business-ready"]
    end
    RAW --> SILVER --> GOLD
    ATHENA[Athena] -. query-in-place .-> SILVER & GOLD
    REDSHIFT[(Redshift)] -. COPY / Spectrum .-> GOLD
    CATALOG[Glue Data Catalog] -. schemas & partitions .-> ATHENA & REDSHIFT
```

Each zone is optimized for its job: raw for fidelity and replay, silver for query performance, gold for serving.

## File ingestion flow

```mermaid
sequenceDiagram
    participant SRC as Source system
    participant S3 as S3 raw zone
    participant EV as S3 event
    participant L as Lambda (validate)
    participant G as Glue (crawler/ETL)
    SRC->>S3: put orders_2026_07_01.csv<br/>at raw/source=retail/entity=orders/ingestion_date=.../
    S3->>EV: ObjectCreated event
    EV->>L: invoke validation
    L-->>S3: accept (or route reject to quarantine/)
    Note over G: later / scheduled
    G->>S3: crawl raw -> catalog table + partitions
    G->>S3: ETL raw -> silver (Parquet, partitioned)
```

The event-driven validation piece (Lambda) is built in Module 03; here it shows how a file's arrival kicks off the pipeline.

## Partition pruning explanation

```mermaid
flowchart LR
    Q["Query:<br/>WHERE order_date = '2026-07-02'"] --> ENGINE[Athena / Spectrum]
    ENGINE -->|reads| P2["order_date=2026-07-02/ ✅ scanned"]
    ENGINE -.->|skips| P1["order_date=2026-07-01/ ⛔ pruned"]
    ENGINE -.->|skips| P3["order_date=2026-07-03/ ⛔ pruned"]
```

Only the matching partition folder is read; the rest are skipped. Fewer bytes scanned = lower cost and faster results. This is why partitioning on the column you filter by is the highest-impact layout decision.

## Raw → bronze → silver → gold flow

```mermaid
flowchart LR
    SRC[Sources<br/>CSV/JSON/CDC/stream] --> RAW
    RAW["RAW<br/>as received<br/>immutable"] -->|type + light clean| BRONZE["BRONZE<br/>typed<br/>(often = raw)"]
    BRONZE -->|validate · dedupe · Parquet · partition| SILVER["SILVER<br/>clean · query-ready"]
    SILVER -->|join · aggregate| GOLD["GOLD<br/>marts · KPIs"]
    GOLD --> SERVE[BI / Redshift / ML]
```

Data gets more refined and more valuable left-to-right; it also gets smaller and more query-optimized. The transformations between zones are Glue/Spark jobs (Module 04); this module is about the *storage* those jobs read from and write to.

## Where this sits in the platform

This storage layer is the backbone of the [capstone platform](../projects/project-07-enterprise-data-platform/). Every ingestion source lands in raw; every processing job reads one zone and writes the next; every query engine reads silver or gold. Get these four diagrams into your head and the rest of the platform is "what fills the arrows."
