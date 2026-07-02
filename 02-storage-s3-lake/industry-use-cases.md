# 02 · Industry Use Cases for the S3 Lake

How the same zone/partition machinery from this module is arranged in different industries. Full deep dives — zone-by-zone design, partition strategy, security/cost concerns, and failure stories — live in the repo-wide [INDUSTRY-USE-CASES](../INDUSTRY-USE-CASES.md#s3-data-lake-deep-dives); this page is the storage-layer summary.

| Industry | What lands in raw | Partition strategy | The storage-layer concern that dominates |
|---|---|---|---|
| **Retail** (this repo's scenario) | Daily order/customer/product extracts, clickstream via Firehose | `source= / entity= / ingestion_date=` | Small files from clickstream — buffer before writing |
| **Banking** | CDC streams from core banking, statements, market feeds | `entity= / txn_date=` (+ `source_system=`) | Immutability and audit — versioning, Object Lock, KMS, data events |
| **Healthcare** | Claims batches, HL7/FHIR extracts, device telemetry | `entity= / service_date=`, PHI split by sensitivity | PHI isolation — separate buckets + KMS keys per sensitivity class |
| **IoT / Manufacturing** | High-volume sensor events | `site= / device_type= / event_date=` (hour only if queried) | Volume — compress+aggregate early, tier aggressively, expire raw |
| **SaaS analytics** | Product events, billing, support exports | `event_date=` + tenant handling (column vs prefix) | Tenant isolation vs partition explosion — don't partition by tenant ID |

The pattern worth internalizing: **the mechanics never change — zones, Hive partitions, Parquet, lifecycle. What changes per industry is which constraint dominates:** freshness (retail), auditability (banking), confidentiality (healthcare), volume (IoT), isolation (SaaS). Architecture is choosing the layout that serves the dominant constraint without breaking the others.
