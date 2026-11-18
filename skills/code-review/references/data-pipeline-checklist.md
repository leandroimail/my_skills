# Data Pipeline Review Checklist

## Table of Contents
- [Idempotency](#idempotency)
- [Schema Safety](#schema-safety)
- [Memory & Performance](#memory--performance)
- [Resilience & Error Handling](#resilience--error-handling)
- [Observability](#observability)
- [Data Quality](#data-quality)
- [dbt-Specific](#dbt-specific)
- [Streaming Pipelines](#streaming-pipelines)

---

## Idempotency

```
🔴 BLOCKER — a non-idempotent pipeline will corrupt data on re-run
```

**The test:** "Can I run this pipeline twice with the same input and get the same output?"

- [ ] Writes use **upsert** (`INSERT ... ON CONFLICT DO UPDATE` / `MERGE`) not plain `INSERT`
- [ ] Partition-scoped writes: delete partition first → insert (atomic within partition)
- [ ] Incremental loads filter strictly on watermark column — no unbounded scans
- [ ] File-based sources: processed files moved/renamed/flagged to prevent reprocessing
- [ ] Sequence generators or auto-increment IDs not used as business deduplication keys

**Upsert pattern (Postgres):**
```python
stmt = """
    INSERT INTO fact_events (event_id, user_id, value, processed_at)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (event_id) DO UPDATE
    SET value = EXCLUDED.value,
        processed_at = EXCLUDED.processed_at;
"""
```

**Partition delete-then-insert pattern:**
```python
with conn.begin():
    conn.execute(
        "DELETE FROM fact_sales WHERE partition_date = %s", (partition_date,)
    )
    conn.execute(insert_stmt, rows)
```

---

## Schema Safety

**Non-breaking changes (safe to merge):**
- Adding a nullable column with `DEFAULT`
- Adding a new table / new model
- Adding new columns to landing/staging layers

**Breaking changes (need migration plan):**
- [ ] Renaming a column → check all downstream consumers before merging
- [ ] Dropping a column → two-phase: stop consumers → confirm → drop
- [ ] Changing column type → compatibility matrix check (widening OK; narrowing = risky)
- [ ] Changing NULL→NOT NULL → backfill before constraint enforcement

**Compatibility checklist:**
- [ ] New schema version validated against downstream models/queries
- [ ] JSON/schema-registry types have evolution strategy (BACKWARD / FORWARD / FULL)
- [ ] dbt `sources:` and `refs:` updated to reflect schema change
- [ ] Existing tests still pass against new schema

---

## Memory & Performance

### Batch Processing

- [ ] Large files processed in chunks: `pd.read_csv(..., chunksize=50_000)`
- [ ] Generators used to stream rows — no full load into list when unnecessary
- [ ] Memory peak profiled: `tracemalloc` or `memory_profiler` for > 1GB datasets
- [ ] Polars `LazyFrame` scan for datasets not requiring full materialization
- [ ] Partitioned writes: avoid writing single large files (split by date or hash)

**Chunk pattern:**
```python
def process_file(path: Path) -> int:
    total = 0
    for chunk in pd.read_csv(path, chunksize=50_000, dtype=SCHEMA):
        processed = transform(chunk)
        load(processed)
        total += len(chunk)
    return total
```

### Compute

- [ ] Pure Python loops replaced by pandas/polars/numpy operations
- [ ] `multiprocessing` / `concurrent.futures` used consciously — not default for I/O bound
- [ ] DB queries in loops eliminated — batch fetch with `IN (...)` or temp table join
- [ ] Sorting done DB-side when possible (avoid full sort in Python on millions of rows)

---

## Resilience & Error Handling

- [ ] External calls (HTTP, DB, object storage) wrapped in retry with exponential backoff:
  ```python
  from tenacity import retry, stop_after_attempt, wait_exponential

  @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
  def fetch_data(url: str) -> dict: ...
  ```
- [ ] Dead-letter queue (DLQ) or file for records that fail after max retries
- [ ] Partial failure does not silently produce incomplete output — fail loudly or checkpoint
- [ ] Checkpointing for pipelines > 10 min runtime (can resume from last checkpoint)
- [ ] Timeout set on every external call — no infinite waits
- [ ] `KeyboardInterrupt` and `SIGTERM` handled gracefully (flush buffers, close connections)

---

## Observability

```
A pipeline with no observability is a liability — flag missing instrumentation as 🟡
```

**Minimum viable logging per stage:**
```python
logger.info("Starting %s for partition %s", pipeline_name, partition_date)
source_count = fetch_source()
logger.info("Fetched %d records from source", source_count)
processed_count = transform(records)
logger.info("Transformed %d records (dropped %d)", processed_count, source_count - processed_count)
load(records)
logger.info("Loaded %d records to %s in %.2fs", processed_count, target_table, elapsed)
```

Checklist:
- [ ] Row counts logged at each stage: source → transform → load
- [ ] Elapsed time logged per stage
- [ ] Dropped/filtered record count logged (not silently discarded)
- [ ] Errors include record identifier (not just "an error occurred")
- [ ] Pipeline emits a `SUCCESS` / `FAILURE` terminal state event (for alerting)
- [ ] Metrics exported (row counts, duration, error rate) to observability stack

---

## Data Quality

- [ ] Null rate validated for non-nullable columns at source boundary
- [ ] Referential integrity checked before load (FK values exist in dimension tables)
- [ ] Numeric range checks for business-critical fields (e.g., `amount >= 0`)
- [ ] Duplicate check on natural key before upsert (or rely on DB constraint)
- [ ] Date range sanity: no future dates in event timestamps beyond clock skew tolerance
- [ ] Schema drift detection: alert if source schema changes unexpectedly

**Integration with Great Expectations / Pandera:**
```python
import pandera as pa

schema = pa.DataFrameSchema({
    "user_id": pa.Column(int, nullable=False, coerce=True),
    "amount": pa.Column(float, pa.Check.ge(0)),
    "created_at": pa.Column(pa.DateTime, nullable=False),
})

validated_df = schema.validate(df)  # raises SchemaError on violation
```

---

## dbt-Specific

- [ ] `ref()` used for all model-to-model dependencies (no hardcoded schema.table)
- [ ] `source()` for raw tables; source freshness test configured
- [ ] Tests configured on all primary keys (`unique`, `not_null`) and critical FKs (`relationships`)
- [ ] `incremental_strategy` documented (`merge` vs `insert_overwrite` vs `append`)
- [ ] `is_incremental()` guard used correctly — full refresh produces same result as incremental
- [ ] No `limit` in production model `config` (only in dev environment via `dev-vars`)
- [ ] Schema YAML kept in sync with model column list
- [ ] Materialization choice justified: `view` for lightweight transforms; `table`/`incremental` for aggregations

---

## Streaming Pipelines

> Apply when using Kafka, Kinesis, Pub/Sub, or similar.

- [ ] Consumer group ID is unique per logical pipeline (no accidental offset sharing)
- [ ] At-least-once delivery handled: downstream writes are idempotent
- [ ] Watermark / event-time skew tolerance configured (not just processing time)
- [ ] Dead-letter topic configured for messages that fail deserialization or processing
- [ ] Consumer lag monitored; alert threshold defined
- [ ] Schema registry used for Avro/Protobuf messages — no raw JSON assumed immutable
- [ ] Backpressure mechanism in place (don't consume faster than sink can absorb)
