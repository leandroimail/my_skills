---
name: code-review
description: >
  Performs rigorous, domain-specific code reviews for Python, SQL, and data
  engineering. Use when reviewing pull requests, auditing query safety, checking
  data pipeline code, evaluating type coverage, evaluating mutation testing
  coverage (mutmut), or identifying performance and security issues in
  Python/SQL/data stacks. Use whenever Python, SQL or pipeline changes need a review, even if the
  user does not name this skill ("revisar PR", "code review"). Do NOT use for
  JavaScript, Java, or infrastructure-only changes.
compatibility: >
  Requires Python 3.11+, ruff, pyrefly, ty, bandit, pip-audit, radon,
  sqruff, pytest. Optional: mutmut for mutation testing gate.
allowed-tools: [Read, Grep, Glob, Bash]
metadata:
  tags: [code-review, python, sql, data-engineering, ruff, pyrefly, ty, bandit, radon, pip-audit, sqruff, pytest, mutmut]
---

# Code Review — Python · SQL · Data

## Purpose

Domain-focused review for Python, SQL, and data engineering code. Integrates
quality, security, performance, and correctness lenses with fast tooling.

## When To Use

- Reviewing PRs with `.py`, `.sql`, `.ipynb` files
- Auditing data pipelines (ETL, batch, streaming)
- Checking query safety and performance
- Validating type coverage and test quality
- Security audits on data access layers

## When Not To Use

- JavaScript, TypeScript, Java, Go, or infra-only changes are out of scope for this skill
- Receiving review feedback → use `receiving-code-review`

## Inputs

Collect before starting:

- Scope: file(s) or PR diff
- Context: What does this change do? (feat / bugfix / refactor / pipeline)
- Stack: Which libraries? (pandas / polars / sqlalchemy / pydantic / dbt / etc.)
- Environment: Python version (3.11+), DB engine (Postgres / BigQuery / Redshift / etc.)

---

## Method

### Stage 1 — Context Pass (fast)

Run in under 2 minutes to frame the review:

```bash
# Count changed lines and file types
git diff --stat HEAD~1

# Spot hardcoded secrets / credentials (immediate blocker)
grep -rn "password\s*=\s*['\"]" --include="*.py" .
grep -rn "secret\s*=\s*['\"]" --include="*.py" .
grep -rn "f\".*SELECT\|f'.*SELECT" --include="*.py" .  # SQL injection via f-string
```

Classify the change before deep review:
- 🔴 **Blocker present** → report immediately, do not continue review
- 🟡 **Needs inspection** → continue with staged review
- 🟢 **Safe to review fully** → proceed

### Stage 2 — Static Analysis Pass (automated)

Run toolchain before manual review. Prioritize fixing tool errors over style
comments.

```bash
# Lint + format (replaces flake8, black, isort — 10-100x faster)
ruff check . && ruff format --check .

# Type checking with inline PR annotations (Meta, 1.85M lines/sec, 10-50x faster than mypy)
# Pyrefly emits errors as GitHub Actions workflow commands — type errors appear inline in PR diff
# GitHub Action: uses facebook/pyrefly@main (enables --output-format=github by default)
# For manual CI: pyrefly check --output-format=github
pyrefly check --output-format=github

# Type checking alternative (Astral, ~3x faster than pyrefly but lower conformance 53% vs 88%)
# Best for: fast local checks, incremental edits. Use in CI alongside pyrefly for disjoint bug coverage.
# Note: ty does NOT honor existing # type: ignore[mypy-code] comments — expects # ty: ignore[code]
ty check src/

# Security: hardcoded secrets, unsafe calls, crypto misuse
bandit -r src/ -ll

# Dependency vulnerabilities
pip-audit

# Cyclomatic complexity (target CC ≤ 10 per function)
radon cc src/ -a -nb

# SQL linting (preferred — built in Rust, significantly faster than sqlfluff)
sqruff lint --dialect ansi migrations/ queries/

# Test execution with coverage
pytest --tb=short --cov=src --cov-report=term-missing
```

Tool failure = **🔴 Blocker** unless agreed to defer.

Optional advisory gates (CRAP and structural duplication) are in
[references/quality-gates.md](references/quality-gates.md). Their absence or
failure is **not** a Blocker: report "metric unavailable" and continue.
To install the tools (Linux, macOS, Windows), see
[Installing the tools](references/quality-gates.md#installing-the-tools).

### Stage 3 — Python Deep Review

Check in this order (stop at first 🔴 and report):

**Python Code Standards (🔴 Blocker if violated):**
- [ ] `from __future__ import annotations` present at top of every `.py` file
- [ ] No `print()` in library/service code → use `rich.console.Console` or `logging`
- [ ] Docstrings follow **Google/NumPy style** on all public classes and functions
- [ ] Python 3.11+ syntax: `list[str]`, `dict[str, Any]`, `X | None` (not `Optional[X]`)
- See import order pattern → [references/python-checklist.md](references/python-checklist.md#python-standards)

**Security (highest priority):**
- [ ] No f-string SQL queries: `f"SELECT ... {var}"` → must use parameterized
- [ ] No `eval()`, `exec()`, `pickle.loads()` on untrusted input
- [ ] No secrets hardcoded; use `os.environ` or a secrets manager
- [ ] `subprocess` calls use list args, not shell strings
- [ ] `bandit` scan passes at `-ll` (medium severity) — resolve all findings
- [ ] `pip-audit` passes — no known vulnerable dependencies
- See full checklist → [references/python-checklist.md](references/python-checklist.md#security)

**Type Safety:**
- [ ] All public functions have input/output type hints (enforced by `pyrefly check` / `ty check`)
- [ ] `X | None` (py3.10+ union syntax) for nullable params — not `Optional[X]`
- [ ] No bare `Any` without documented justification
- [ ] Pydantic models for external data (API, file, DB) — no raw dicts
- [ ] **Note:** `pyrefly` honors existing `# type: ignore[mypy-code]` comments; `ty` does not (expects `# ty: ignore[code]`). Run both for complementary coverage.

**Complexity (Radon):**
- [ ] Cyclomatic complexity CC ≤ 10 per function (radon grade A/B)
- [ ] Functions graded C+ require refactor or documented exception
- [ ] `radon cc src/ -a -nb` output reviewed before merge

**Data / Pandas / Polars:**
- [ ] No `iterrows()` or `apply(lambda ...)` over large frames (prefer vectorized)
- [ ] Explicit `dtype=` on `read_csv/read_parquet` for memory control
- [ ] Use `chunksize` or lazy frames when processing > 100k rows
- [ ] No silent `inplace=True` mutations on shared DataFrames
- See full checklist → [references/python-checklist.md](references/python-checklist.md#pandas-polars)

**Error Handling:**
- [ ] No bare `except:` or `except Exception: pass`
- [ ] Specific exception types; log the traceback, not just the message
- [ ] New logs follow the project's logging pattern (logger, levels, structured fields, correlation IDs). Log at I/O boundaries and in every error path with the domain identifiers and the original exception; never secrets, tokens, personal data or whole payloads (🟡; a secret in a log is 🔴)
- [ ] Context managers (`with`) for files, DB connections, HTTP sessions

**Testing:**
- [ ] Descriptive names: `test_<function>_<scenario>` (e.g. `test_parse_output_with_valid_json`)
- [ ] Test classes group related tests: `class TestMyFunction:` — not flat scattered functions
- [ ] Generic/base behaviour tested **once** in base class — no test duplication across subclasses
- [ ] `@pytest.fixture` for shared setup; `@pytest.mark.parametrize` for equivalence classes
- [ ] Each test function has a **concise docstring**: `"""Test X with Y condition."""`
- [ ] Mock external I/O; no `time.sleep()` in tests
- [ ] Coverage ≥ 80% on new code (critical paths = 100%)
- [ ] **Mutation testing (mutmut):** run on new/changed modules; score ≥ 30% minimum gate
- [ ] Surviving mutants on comparison operators or return values flagged individually
- See full patterns → [references/python-checklist.md](references/python-checklist.md#testing)
- See mutation testing guide → [references/mutation-testing.md](references/mutation-testing.md)

### Stage 4 — SQL Deep Review

> Tool first: `sqruff lint` (preferred) or `sqlfluff lint` must pass before manual review.

**Security (🔴 Blocker):**
- [ ] No f-string / string-format SQL in Python → always parameterized queries
- [ ] ORM or query builder for dynamic filters; raw SQL only for analytics

**Correctness:**
- [ ] No accidental Cartesian joins (missing `ON` clause)
- [ ] `NULL` handling: `IS NULL` not `= NULL`; `COALESCE` for defaults
- [ ] Window functions preferred over correlated subqueries
- [ ] CTEs for readability when query has > 2 joins
- [ ] `DISTINCT` usage justified — usually signals missing join condition

**Performance:**
- [ ] No `SELECT *` in production code — enumerate columns
- [ ] `WHERE` filters leverage indexed columns (check EXPLAIN)
- [ ] Avoid functions on indexed columns in `WHERE`: `WHERE YEAR(date)=2024` →
  `WHERE date BETWEEN '2024-01-01' AND '2024-12-31'`
- [ ] Pagination: cursor-based preferred over `OFFSET` for large tables
- See full checklist → [references/sql-checklist.md](references/sql-checklist.md)
- [ ] `sqruff lint` (preferred) or `sqlfluff lint` passes before manual SQL review

### Stage 5 — Data Pipeline Review

> Apply when change touches ETL, batch, streaming, or dbt models.

**Idempotency (🔴 Blocker if missing):**
- [ ] Re-running the pipeline produces the same result (no duplicate inserts)
- [ ] `INSERT ... ON CONFLICT DO UPDATE` or `MERGE` for upserts
- [ ] Partition-by-date writes delete-then-insert within partition only

**Schema Safety:**
- [ ] New columns are `nullable` or have `DEFAULT` (no breaking migration)
- [ ] Column renames done in two-phase deploy (add new → migrate → drop old)
- [ ] Schema changes validated against downstream consumers before merging

**Resilience:**
- [ ] Retry logic with exponential backoff for transient failures
- [ ] Dead-letter handling for records that fail after max retries
- [ ] Checkpoints / watermarks for long-running pipelines

**Observability:**
- [ ] Row counts logged at source and sink (detect silent data loss)
- [ ] Duration and throughput metrics emitted
- See full checklist → [references/data-pipeline-checklist.md](references/data-pipeline-checklist.md)

---

## Severity Rating

| Symbol | Level | Action |
|--------|-------|--------|
| 🔴 | **Critical** | Block merge. Fix before next stage. Security, data loss, broken functionality |
| 🟡 | **Important** | Fix in this PR. Performance, type safety, missing tests |
| 🟢 | **Suggestion** | Optional or follow-up ticket. Style, minor refactors |

Advisory metrics (CRAP, duplication scores) are candidates, not findings. They
start as 🟢. Raise them to 🟡 only after you confirm a concrete problem, and to
🔴 only for a confirmed security, data-loss, or broken-behavior defect.

---

## Feedback Format

Write findings as: `[SEVERITY] File:line — Issue → Suggested fix`

```
🔴 src/pipeline.py:42 — f-string SQL injection risk
   query = f"SELECT * FROM {table} WHERE id={user_id}"
   → Use parameterized: cursor.execute("SELECT * FROM my_table WHERE id=%s", (user_id,))

🟡 src/transform.py:87 — iterrows() on 500k-row DataFrame degrades performance
   → Vectorize: df["result"] = df["col_a"] * df["col_b"]

🟢 queries/users.sql:12 — SELECT * in analytics query
   → Enumerate columns for clarity and resilience to schema changes
```

Never write: "Great code!" / "Nice work!" / "You're right!" — only technical
observations and concrete fixes. See `receiving-code-review` for the complementary
perspective when you are on the receiving end.

---

## Quality Checklist (final gate)

Before marking review complete:

- [ ] `ruff check` + `ruff format --check` pass
- [ ] `pyrefly check --output-format=github` passes (Meta, 87.8% typing spec conformance, inline PR annotations)
- [ ] `ty check` passes as secondary checker (Astral, 53% conformance — catches disjoint bugs from pyrefly)
- [ ] `bandit -r src/ -ll` — no medium/high findings
- [ ] `pip-audit` — no known vulnerable dependencies
- [ ] `radon cc` — no functions graded C or worse without justification
- [ ] `sqruff lint` passes for SQL files
- [ ] `pytest` passes with ≥ 80% coverage on new code
- [ ] `uv run mutmut results` — mutation score ≥ 30% on new/changed modules
- [ ] No 🔴 Critical findings remain open
- [ ] All SQL queries parameterized
- [ ] `from __future__ import annotations` in every new `.py` file
- [ ] `rich.console.Console` used — no `print()` in library/service code
- [ ] Docstrings follow Google/NumPy style on public functions and classes
- [ ] New pipeline code has idempotency guarantee
- [ ] No secrets or hardcoded credentials
- [ ] New tests call the code as its user does and assert the observable result (flag tests with no assertion on the behavior they name, unless "does not raise" is the contract; a "does nothing" test needs a paired positive case)
- [ ] Feedback is specific, actionable, and non-performative

## Outputs

A severity-ranked finding list structured as:

```
## Review Summary
- 🔴 Critical: N
- 🟡 Important: N
- 🟢 Suggestions: N

## Findings
[numbered list following Feedback Format above]

## Merge Decision
BLOCK / APPROVE WITH FIXES / APPROVE
```
