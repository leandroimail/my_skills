# SQL Review Checklist

## Table of Contents
- [Security](#security)
- [Correctness](#correctness)
- [Performance](#performance)
- [Schema Design](#schema-design)
- [Migrations](#migrations)
- [Tool: sqruff](#tool-sqruff)

---

## Security

```
🔴 BLOCKER — any single item here = merge blocked
```

- [ ] All SQL executed from TypeScript uses parameterized binds — no template
  literals, no string concatenation of values
- [ ] Table/column/sequence names are **never** dynamic from user input (use an allowlist)
- [ ] No `TRUNCATE` or `DROP` inside application code — only in controlled migration scripts
- [ ] Dynamic SQL in stored procedures (`EXECUTE IMMEDIATE`) uses `DBMS_ASSERT`
  (Oracle) / `QUOTE_IDENT` (Postgres) on identifiers
- [ ] Least-privilege DB user: application user cannot `DROP`, `CREATE`, or access other schemas

**TypeScript injection patterns to flag:**
```typescript
// 🔴 BLOCK: template literal
const rows = await dataSource.query(`SELECT * FROM orders WHERE user_id = ${userId}`);

// 🔴 BLOCK: concatenation
const sql = "SELECT * FROM orders WHERE status = '" + status + "'";

// ✅ SAFE: positional binds (Oracle style — :1, :2 with a params array)
const rows = await dataSource.query(
  'SELECT * FROM orders WHERE user_id = :1 AND status = :2',
  [userId, status],
);

// ✅ SAFE: TypeORM QueryBuilder with named params
const order = await repo
  .createQueryBuilder('o')
  .where('o.userId = :userId', { userId })
  .getOne();

// ✅ SAFE: Prisma tagged template (auto-parameterized)
const rows = await prisma.$queryRaw`SELECT * FROM orders WHERE user_id = ${userId}`;
// ⚠️ but prisma.$queryRawUnsafe(interpolated) is a 🔴 BLOCK
```

**Identifier interpolation** (sequence/procedure names) is acceptable only from
code-owned constants, never request data:
```typescript
// OK — sequenceName comes from an entity decorator/constant, not user input
await dataSource.query(`SELECT ${sequenceName}.NEXTVAL AS NEXT_VAL FROM DUAL`);
```

---

## Correctness

- [ ] No accidental Cartesian join: every `FROM a, b` must have explicit `ON` or `WHERE` linkage
- [ ] `NULL` comparisons use `IS NULL` / `IS NOT NULL` — never `= NULL`
- [ ] `COALESCE(col, default)` (or Oracle `NVL`) for nullable columns used in aggregations or comparisons
- [ ] `DISTINCT` usage justified: often signals a missing join condition, not a style choice
- [ ] Aggregate functions (`SUM`, `COUNT`) behave correctly with `NULL` (they skip NULLs — intentional?)
- [ ] `GROUP BY` includes all non-aggregated `SELECT` columns
- [ ] Joins on nullable foreign keys use `LEFT JOIN` intentionally — document when `INNER JOIN` drops rows
- [ ] Date binds converted explicitly: Oracle `TO_DATE(:1, 'YYYY-MM-DD')` for string
  binds, or pass `Date` objects — no implicit NLS-dependent conversion
- [ ] Oracle empty string `''` **is** `NULL` — flag code that distinguishes them
- [ ] `BETWEEN` is inclusive on both ends — verify expected boundary behavior
- [ ] Window functions: `PARTITION BY` and `ORDER BY` both explicit when semantics require it

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
  WHERE TRUNC(created_at) = DATE '2026-01-01'

  -- Good (index used)
  WHERE created_at >= DATE '2026-01-01' AND created_at < DATE '2026-01-02'
  ```
- [ ] CTEs (`WITH ...`) for readability when > 2 joins; note CTEs may inhibit optimization in some engines
- [ ] Correlated subqueries replaced with `JOIN` or window function when called per-row
- [ ] `EXISTS` preferred over `COUNT(*) > 0` for existence checks
- [ ] `IN (subquery)` on large sets: consider `JOIN` or `EXISTS` (planner-dependent)

### ORM-Specific

- [ ] N+1 pattern: relations loaded with the parent (`relations: [...]`,
  `leftJoinAndSelect`) when iterated — not lazy-loaded per row
- [ ] `select` limited to needed columns for wide tables (`qb.select([...])`)
- [ ] Bulk inserts/updates batched (`insert().values([...])`) — no per-row `save()` loops

### Pagination

- [ ] `OFFSET` pagination avoided for large tables (cost grows with offset):
  ```sql
  -- Bad for large offsets
  SELECT * FROM events ORDER BY id OFFSET 50000 ROWS FETCH NEXT 100 ROWS ONLY;

  -- Good: keyset/cursor-based
  SELECT * FROM events WHERE id > :last_seen_id ORDER BY id FETCH FIRST 100 ROWS ONLY;
  ```

### Indexes

- [ ] Composite index column order matches query filter patterns (leftmost prefix rule)
- [ ] Function-based indexes for unavoidable function predicates (Oracle)
- [ ] `EXPLAIN PLAN` / `EXPLAIN ANALYZE` reviewed for queries touching tables > 100k rows
- [ ] New indexes do not duplicate existing ones

### Aggregations

- [ ] `HAVING` vs `WHERE`: push non-aggregate filters to `WHERE` (filters before grouping)
- [ ] Materialized views or pre-aggregation considered for dashboards hitting > 10M rows

---

## Schema Design

- [ ] Primary keys use `NUMBER`/`BIGINT` from a sequence, or UUID v7 — sized for growth
- [ ] Timestamps stored timezone-aware (`TIMESTAMP WITH TIME ZONE` / `TIMESTAMPTZ`)
- [ ] Enum-like columns: static controlled values only (`CHECK (fl_ativo IN ('S','N'))`);
  use a lookup table for anything that changes
- [ ] Foreign keys defined in schema for referential integrity (unless intentionally denormalized)
- [ ] Soft-delete pattern: nullable `deleted_at` + filtered access (ORM scope or view)
- [ ] Entity classes (TypeORM) mirror the real schema: nullability, lengths, precision

---

## Migrations

```
🔴 Blocker — breaking schema changes = block until safe deploy plan confirmed
```

**Safe (non-breaking):**
- Adding a nullable column with `DEFAULT`
- Adding a new table
- Adding an index `CONCURRENTLY`/`ONLINE` (engine-dependent)

**Blocking (requires 2-phase deploy):**
- Dropping a column (phase 1: stop reading/writing; phase 2: drop)
- Renaming a column (phase 1: add new, dual-write; phase 2: drop old)
- Adding a `NOT NULL` column without default (locks table during backfill)
- Changing column type (locks table; may lose data)

**Migration file review:**
- [ ] `up` and `down` migrations both present and tested
- [ ] No data migration mixed with DDL in the same transaction (lock escalation;
  Oracle DDL auto-commits — order operations deliberately)
- [ ] Index created online/concurrently to avoid table lock
- [ ] Large backfill done in batches, not a single `UPDATE` on millions of rows

---

## Tool: sqruff

`sqruff` lints standalone `.sql` files (built in Rust — fast, language-agnostic).
There is no npm package; install the binary for your OS (Linux, Windows, macOS).

```bash
sqruff lint --dialect ansi path/to/queries/
sqruff fix --dialect ansi path/to/queries/
```

`sqruff` config (`.sqruff`):
```ini
[sqruff]
dialect = ansi          # or oracle-compatible dialect available in your version

[sqruff:rules:capitalisation.keywords]
capitalisation_policy = upper

[sqruff:rules:capitalisation.identifiers]
extended_capitalisation_policy = upper
```

SQL embedded in TypeScript template strings is not reachable by SQL linters —
review it manually against this checklist, and keep non-trivial statements in
dedicated service methods (or `.sql` files) so they stay reviewable.
