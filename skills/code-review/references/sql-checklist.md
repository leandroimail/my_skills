# SQL Review Checklist

## Table of Contents
- [Security](#security)
- [Correctness](#correctness)
- [Performance](#performance)
- [Schema Design](#schema-design)
- [Migrations](#migrations)
- [Tool: sqlfluff](#tool-sqlfluff)

---

## Security

```
🔴 BLOCKER — any single item here = merge blocked
```

- [ ] All SQL executed from Python uses parameterized queries — no f-strings, no `.format()`
- [ ] Table/column names are **never** dynamic from user input (use an allowlist)
- [ ] No `TRUNCATE` or `DROP` inside application code — only in controlled migration scripts
- [ ] `EXECUTE IMMEDIATE` / dynamic SQL in stored procs use `QUOTE_IDENT` / `QUOTE_LITERAL`
- [ ] Least-privilege DB user: application user cannot `DROP`, `CREATE`, or access other schemas

**Python injection patterns to flag:**
```python
# 🔴 BLOCK: f-string
query = f"SELECT * FROM orders WHERE user_id = {user_id}"

# 🔴 BLOCK: .format()
query = "SELECT * FROM orders WHERE status = '{}'".format(status)

# ✅ SAFE: parameterized
query = "SELECT * FROM orders WHERE user_id = %s AND status = %s"
cursor.execute(query, (user_id, status))

# ✅ SAFE: SQLAlchemy ORM / core
stmt = select(Order).where(Order.user_id == user_id, Order.status == status)
```

---

## Correctness

- [ ] No accidental Cartesian join: every `FROM a, b` must have explicit `ON` or `WHERE` linkage
- [ ] `NULL` comparisons use `IS NULL` / `IS NOT NULL` — never `= NULL`
- [ ] `COALESCE(col, default)` for nullable columns used in aggregations or comparisons
- [ ] `DISTINCT` usage justified: often signals a missing join condition, not a style choice
- [ ] Aggregate functions (`SUM`, `COUNT`) behave correctly with `NULL` (they skip NULLs — intentional?)
- [ ] `GROUP BY` includes all non-aggregated `SELECT` columns (or dialect allows functional dependency)
- [ ] Joins on nullable foreign keys use `LEFT JOIN` intentionally — document when `INNER JOIN` drops rows
- [ ] Date/time comparisons use correct timezone-aware approach for the target DB engine
- [ ] `BETWEEN` is inclusive on both ends — verify expected boundary behavior
- [ ] Window functions: `PARTITION BY` and `ORDER BY` are both explicitly stated when semantics require it

**NULL trap example:**
```sql
-- Bug: users where email is not 'admin@co' — misses NULL emails
SELECT * FROM users WHERE email != 'admin@co';

-- Correct
SELECT * FROM users WHERE email != 'admin@co' OR email IS NULL;
```

---

## Performance

### Query Structure

- [ ] No `SELECT *` in production code — enumerate columns
- [ ] `WHERE` clauses use indexed columns; avoid wrapping indexed cols in functions:
  ```sql
  -- Bad (index not used)
  WHERE EXTRACT(YEAR FROM created_at) = 2024

  -- Good (index used)
  WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01'
  ```
- [ ] CTEs (`WITH ...`) for readability when > 2 joins; note CTEs may inhibit optimization in some engines
- [ ] Correlated subqueries replaced with `JOIN` or window function when called per-row
- [ ] `EXISTS` preferred over `COUNT(*) > 0` for existence checks
- [ ] `IN (subquery)` on large sets: consider `JOIN` or `EXISTS` (planner-dependent)

### Pagination

- [ ] `OFFSET` pagination avoided for large tables (cost grows with offset):
  ```sql
  -- Bad for large offsets
  SELECT * FROM events ORDER BY id LIMIT 100 OFFSET 50000;

  -- Good: cursor-based
  SELECT * FROM events WHERE id > :last_seen_id ORDER BY id LIMIT 100;
  ```

### Indexes

- [ ] Composite index column order matches query filter patterns (leftmost prefix rule)
- [ ] Partial indexes considered for queries with constant `WHERE` filters (e.g., `WHERE deleted_at IS NULL`)
- [ ] `EXPLAIN ANALYZE` reviewed for queries touching tables > 100k rows
- [ ] New indexes do not duplicate existing ones

### Aggregations

- [ ] `HAVING` vs `WHERE`: push non-aggregate filters to `WHERE` (filters before grouping)
- [ ] Materialized views or pre-aggregation considered for dashboards hitting > 10M rows

---

## Schema Design

- [ ] Primary keys use `BIGINT` or `UUID v7` — avoid `SERIAL`/`INT` for high-volume tables
- [ ] Timestamps stored as `TIMESTAMPTZ` (timezone-aware), not `TIMESTAMP`
- [ ] `ENUM` types: static controlled values only; use lookup table for anything that changes
- [ ] `TEXT` preferred over `VARCHAR(n)` in Postgres (no performance difference, less migration pain)
- [ ] Foreign keys defined in schema for referential integrity (unless intentionally denormalized)
- [ ] Soft-delete pattern: `deleted_at TIMESTAMPTZ DEFAULT NULL` + partial index + views

---

## Migrations

```
🔴 Blocker — breaking schema changes = block until safe deploy plan confirmed
```

**Safe (non-breaking):**
- Adding a nullable column with `DEFAULT`
- Adding a new table
- Adding an index `CONCURRENTLY` (Postgres)

**Blocking (requires 2-phase deploy):**
- Dropping a column (phase 1: stop reading/writing; phase 2: drop)
- Renaming a column (phase 1: add new, dual-write; phase 2: drop old)
- Adding a `NOT NULL` column without default (locks table during backfill)
- Changing column type (locks table; may lose data)

**Migration file review:**
- [ ] `UP` and `DOWN` migrations both present and tested
- [ ] No data migration mixed with DDL in same transaction (risk of lock escalation)
- [ ] Index created with `CONCURRENTLY` in Postgres to avoid table lock
- [ ] Large backfill done in batches, not a single `UPDATE` on millions of rows

---

## Tool: sqruff / sqlfluff

**`sqruff` is preferred** (built in Rust — significantly faster than sqlfluff).

```bash
# sqruff (preferred — built in Rust, faster)
sqruff lint --dialect ansi path/to/queries/
sqruff fix --dialect ansi path/to/queries/

# sqlfluff (alternative)
sqlfluff lint --dialect postgres path/to/queries/
sqlfluff fix --dialect postgres path/to/queries/
```

`sqruff` config (`.sqruff`):
```ini
[sqruff]
dialect = ansi          # or postgres, bigquery, etc.
templater = dbt         # or jinja

[sqruff:rules:capitalisation.keywords]
capitalisation_policy = upper

[sqruff:rules:capitalisation.identifiers]
extended_capitalisation_policy = lower
```

`sqlfluff` config (`.sqlfluff` fallback):
```ini
[sqlfluff]
dialect = postgres
templater = dbt
rules = L001,L002,L003,L010,L011,L012,L013,L017,L019,L022,L032,L034,L036,L044

[sqlfluff:rules:L010]
capitalisation_policy = upper

[sqlfluff:rules:L014]
extended_capitalisation_policy = lower
```
