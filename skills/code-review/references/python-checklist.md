# Python Review Checklist

## Table of Contents
- [Python Standards](#python-standards)
- [Security](#security)
- [Bandit Findings](#bandit-findings)
- [Pip-audit](#pip-audit)
- [Type Safety (ty)](#type-safety-ty)
- [Complexity (Radon)](#complexity-radon)
- [Pandas / Polars](#pandas-polars)
- [SQLAlchemy / Database Access](#sqlalchemy--database-access)
- [Error Handling](#error-handling)
- [Code Quality](#code-quality)
- [Testing](#testing)
- [Performance](#performance)
- [Design Principles (conditional)](#design-principles-conditional)

---

## Python Standards

```
🔴 BLOCKER — all items below are mandatory for Python/data projects
```

### `from __future__ import annotations`

- [ ] Present in **every** new `.py` file, as the **first import**
- Enables PEP 563 deferred annotation evaluation (required for forward refs)

```python
# ✅ Correct — first line after module docstring
from __future__ import annotations

import time
from pathlib import Path

import typer
from rich.console import Console

from myapp.services.pipeline import run_pipeline
```

### Import Order

1. `from __future__ import annotations`
2. Standard Library
3. Third-party
4. Local

Each group separated by **one blank line**. Enforced by `ruff`.

### Console Output — `rich` only

- [ ] **Never** `print()` in library or service code
- [ ] **Never** `typer.echo()`
- [ ] **Never** redundant `style=` when using Rich tags
- Use icon/color scheme consistently:

| Intent | Pattern |
|--------|---------|
| Success | `[green]✓[/green]` |
| Error | `[red]✗[/red]` |
| Warning/Progress | `[yellow]...[/yellow]` |
| Info/Timing | `[cyan]...[/cyan]` or `[dim]...[/dim]` |

```python
from rich.console import Console
console = Console()

# ✅ Correct
console.print("[green]✓[/green] Pipeline concluded.")
console.print(f"[cyan][{elapsed:.2f}s][/cyan] Check done.")

# ❌ Wrong
print("✓ Done")
typer.echo("Error!")
console.print("[red]✗[/red] Failed", style="red")  # style= + tags = redundant
```

### Google/NumPy Docstrings

All public functions and classes **must** have docstrings in Google style:

```python
# ✅ Correct
def run_git_init(project_path: Path) -> bool:
    """Initializes a git repository at the specified path.

    Args:
        project_path: Path to the project directory.

    Returns:
        True if repository was successfully initialized, False otherwise.
    """

# ❌ Wrong — no docstring
def run_git_init(project_path: Path) -> bool:
    ...
```

### Python 3.11+ Type Syntax

- [ ] `list[str]` not `List[str]` (no `typing` imports for built-in generics)
- [ ] `dict[str, Any]` not `Dict[str, Any]`
- [ ] `X | None` not `Optional[X]`
- [ ] `X | Y` not `Union[X, Y]`

```python
# ✅ Correct (Python 3.11+ syntax)
def process(items: list[str], opts: dict[str, Any] | None = None) -> bool: ...

# ❌ Wrong (legacy typing imports)
from typing import List, Optional
def process(items: List[str], opts: Optional[dict] = None) -> bool: ...
```

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Classes | `PascalCase` | `RuffLinterCheckRunner` |
| Functions / Variables | `snake_case` | `project_path`, `run_checks()` |
| Constants | `UPPER_CASE` | `DEFAULT_PATH` |
| Private Constants | `_UPPER_CASE` | `_NAME`, `_HAS_FIX` |
| Private Attributes | `_snake_case` | `_is_initialized` |

---

## Security

```
🔴 BLOCKER — any single item here = merge blocked
```

- [ ] No f-string SQL: `f"SELECT ... {var}"` → use `cursor.execute(sql, params)`
- [ ] No `eval()` or `exec()` on user-controlled input
- [ ] No `pickle.loads()` on untrusted data (use `json` or `msgpack`)
- [ ] `subprocess` uses list form: `subprocess.run(["cmd", arg])` not shell=True
- [ ] Secrets via `os.environ.get("KEY")` or a vault — never hardcoded
- [ ] No `yaml.load()` without `Loader=yaml.SafeLoader`
- [ ] File paths sanitized with `pathlib.Path` before open (traversal risk)
- [ ] `tempfile.mkstemp()` for temp files, not `open("/tmp/fixed_name")`
- [ ] `bandit -r src/ -ll` passes — see [Bandit Findings](#bandit-findings)

---

## Bandit Findings

Run: `bandit -r src/ -ll` (reports medium and high severity only).

Common findings to flag as 🔴:

| Bandit ID | Issue | Fix |
|-----------|-------|-----|
| B101 | `assert` in production code (removed by `-O`) | Replace with explicit `if/raise` |
| B105/B106 | Hardcoded password string | Move to `os.environ` |
| B108 | Insecure temp file (`/tmp/name`) | `tempfile.mkstemp()` |
| B301/B302 | `pickle` / `marshal` on untrusted data | Use `json` |
| B303 | Broken hash algorithm (MD5, SHA1 for security) | `hashlib.sha256()` or higher |
| B307 | `eval()` usage | Refactor to avoid |
| B324 | MD5/SHA1 for cryptographic use | `hashlib.sha256()` |
| B501-B506 | TLS/SSL misconfiguration | Enforce cert validation |
| B601/B602 | `subprocess` shell injection | Use list args, `shell=False` |
| B608 | SQL string construction | Parameterized queries |

---

## Pip-audit

Run: `pip-audit` (checks installed packages against CVE database).

- [ ] Output is clean — no vulnerabilities listed
- [ ] If vulnerabilities found: patch or document risk with team approval
- [ ] Run in CI as a mandatory gate

```bash
# Run in project virtualenv
uv run pip-audit

# Generate report
uv run pip-audit --format json -o pip-audit-report.json
```

---

## Type Safety (ty)

> `ty` (Astral, built in Rust) is the modern alternative to `mypy`, optimized for Python 3.11+.

Run: `ty check src/`

- [ ] All public functions annotated: `def fn(x: int) -> str:`
- [ ] `X | None` for nullable parameters (not `Optional[X]`)
- [ ] No bare `Any` — document with inline comment if needed
- [ ] Return types explicit; no implicit `None` returns
- [ ] Generic types use built-in lowercase: `list[str]`, `dict[str, Any]`
- [ ] TypedDict or Pydantic model for dicts with known shape
- [ ] `Protocol` preferred over `ABC` for structural typing

**Pydantic patterns:**
```python
# Good: external data always enters through a model
class UserPayload(BaseModel):
    name: str
    email: EmailStr
    age: int = Field(gt=0, lt=150)

# Bad: raw dict from request
def create_user(data: dict) -> None: ...
```

---

## Complexity (Radon)

Run: `radon cc src/ -a -nb` (shows only functions graded B or worse in `-nb` mode).

| Grade | CC Score | Meaning | Action |
|-------|----------|---------|--------|
| A | 1–5 | Simple | ✅ OK |
| B | 6–10 | Moderate | ✅ OK |
| C | 11–15 | Complex | 🟡 Refactor or justify |
| D | 16–20 | Very complex | 🔴 Must refactor |
| F | >20 | Unmaintainable | 🔴 Must refactor |

- [ ] No function graded D or F (hard blocker)
- [ ] C-graded functions have documented reason (complexity is inherent, not accidental)
- [ ] Prefer early returns to reduce nesting (flattens complexity)

```bash
# Show all functions with grade (verbose)
radon cc src/ -a

# Show only B and worse
radon cc src/ -a -nb
```

---

## Type Safety

- [ ] All public functions annotated: `def fn(x: int) -> str:`
- [ ] `Optional[T]` (or `T | None` on py3.10+) for nullable parameters
- [ ] No bare `Any` — document with `# type: ignore[...]` and a reason
- [ ] Return types explicit on functions that return multiple types
- [ ] Generic types used correctly: `list[str]` not `list` (py3.9+)
- [ ] TypedDict or Pydantic model for dicts with known shape
- [ ] `Protocol` preferred over `ABC` for structural typing
- [ ] `@overload` for functions with multiple call signatures
- [ ] `mypy --strict` must pass (or targeted suppressions justified)

**Pydantic patterns:**
```python
# Good: external data always enters through a model
class UserPayload(BaseModel):
    name: str
    email: EmailStr
    age: int = Field(gt=0, lt=150)

# Bad: raw dict from request
def create_user(data: dict) -> None: ...
```

---

## Pandas / Polars

```
Performance anti-patterns to block or flag 🟡
```

**Iteration:**
- [ ] No `iterrows()` on DataFrames > 1k rows → vectorize or use `numpy`
- [ ] No nested `apply(lambda ...)` chains → use `.assign()` + built-in ops
- [ ] `df.itertuples()` is acceptable when iteration is unavoidable (10x faster than iterrows)

**Memory:**
- [ ] Explicit `dtype=` on `read_csv()` / `read_parquet()` for large files
- [ ] `chunksize=` parameter for incremental CSV reads > 500k rows
- [ ] `category` dtype for low-cardinality string columns (10-20x memory reduction)
- [ ] Polars lazy API (`LazyFrame`) for pipelines not needing materialization

**Correctness:**
- [ ] No silent `inplace=True` on a DataFrame that will be shared/returned
- [ ] Date parsing: `parse_dates=True` or explicit `pd.to_datetime()` — no string comparison
- [ ] Avoid chained indexing: `df[cond]["col"] = val` → use `.loc[cond, "col"] = val`
- [ ] `fillna()` before comparisons — float NaN propagates silently

**Examples:**
```python
# Bad: O(n) Python loop
for _, row in df.iterrows():
    result.append(row["a"] * row["b"])

# Good: vectorized
df["result"] = df["a"] * df["b"]

# Bad: string comparison on dates
df[df["date"] > "2024-01-01"]

# Good: proper type
df[df["date"] > pd.Timestamp("2024-01-01")]
```

---

## SQLAlchemy / Database Access

- [ ] Parameterized queries always — no string interpolation into raw SQL
- [ ] `text()` with `bindparams` for raw SQL in SQLAlchemy
- [ ] Session lifecycle managed via context manager: `with Session() as s:`
- [ ] `expire_on_commit=False` justified comment if overriding default
- [ ] N+1 pattern: use `selectinload()` / `joinedload()` for related entities
- [ ] Bulk operations: `session.bulk_insert_mappings()` for > 1k inserts
- [ ] Connection pool settings documented in config, not hardcoded

```python
# Bad — SQL injection
stmt = text(f"SELECT * FROM users WHERE email = '{email}'")

# Good — parameterized
stmt = text("SELECT * FROM users WHERE email = :email")
result = session.execute(stmt, {"email": email})
```

---

## Error Handling

- [ ] No bare `except:` (catches KeyboardInterrupt, SystemExit — dangerous)
- [ ] No `except Exception: pass` — always log or re-raise
- [ ] Catch specific exceptions: `except (ValueError, KeyError) as e:`
- [ ] Log with `logger.exception(msg)` inside `except` block to capture traceback
- [ ] External calls (HTTP, DB, file I/O) wrapped with retry or error boundary
- [ ] Custom exceptions inherit from domain base class, not raw `Exception`

```python
# Bad
try:
    result = process(data)
except:
    pass

# Good
try:
    result = process(data)
except ProcessingError as e:
    logger.exception("Processing failed for record %s", record_id)
    raise
```

---

## Code Quality

- [ ] `ruff check` and `ruff format --check` pass without suppressions
- [ ] No magic numbers — named constants or config values
- [ ] `logging` module or `rich.console.Console` used — no `print()` in library/service code
- [ ] New logs follow the project's logging pattern (logger, levels, structured fields, correlation IDs). Log at I/O boundaries and in every error path with the domain identifiers and the original exception; never secrets, tokens, personal data or whole payloads (🟡; a secret in a log is 🔴)
- [ ] Functions < 50 lines; extract helpers if longer
- [ ] No commented-out code in PR (use git for history)
- [ ] `TODO: TICKET-123` format if deferring — not naked TODOs
- [ ] No circular imports — restructure via dependency injection or lazy import
- [ ] `__all__` defined in public modules to control API surface

---

## Testing

Naming convention: `test_<function>_<scenario>`

```python
# Good
class TestValidateProjectName:
    """Test suite for validate_project_name function."""

    def test_valid_simple_name(self):
        """Test simple valid project name."""
        assert validate_project_name("myproject") is None

    def test_empty_name_rejected(self):
        """Test empty project name raises validation error."""
        error = validate_project_name("")
        assert error == "Project name cannot be empty"

# Bad (flat functions, no class grouping)
def test1():
    assert validate_project_name("myproject") is None
```

**Avoid test redundancy:**
- Generic/base behaviour (initialization, basic attributes) tested **once** in base class only
- Specific runners/subclasses test only their **unique** behaviour
- Do not repeat `test_runner_initialization` in every concrete class

```python
# ✅ Correct — test only BanditRunner-specific behaviour
class TestBanditCheckRunner:
    def test_command_generation(self):
        """Test _command returns correct bandit command."""
        runner = BanditCheckRunner(path=self.test_path, fix=False)
        assert "bandit" in runner._command()[0]

# ❌ Wrong — generic test duplicated in every runner
class TestBanditCheckRunner:
    def test_runner_initialization(self):  # already in base class!
        runner = BanditCheckRunner(path=self.test_path, fix=False)
        assert runner.path == self.test_path
```

- [ ] Test classes group related tests (`class TestMyFunction:`)
- [ ] Each test has a **concise** docstring: `"""Test X with Y."""`
- [ ] Generic behavior tested once; only specific behavior in subclass tests
- [ ] `@pytest.fixture` for shared setup; no copy-paste setup blocks
- [ ] `@pytest.mark.parametrize` for equivalence classes:

```python
@pytest.mark.parametrize(
    "prereqs,missing",
    [
        ({"uv": False, "git": True}, ["uv"]),
        ({"uv": True, "git": False}, ["git"]),
        ({"uv": False, "git": False}, ["uv", "git"]),
    ],
)
def test_missing_prerequisites(prereqs: dict[str, bool], missing: list[str]) -> None:
    """Test missing prerequisites detection."""
    result = check_prerequisites(prereqs)
    for tool in missing:
        assert tool in result
```

- [ ] No `time.sleep()` in tests — use mocked time or event-driven waits
- [ ] Tests are deterministic: seed random, freeze time with `freezegun`
- [ ] Coverage ≥ 80% for new code; 100% for critical paths (auth, payments, pipelines)
- [ ] Run via `uv run pytest`

---

## Performance

- [ ] `__slots__` on data classes instantiated thousands of times
- [ ] Generators (`yield`) preferred over lists when caller doesn't need random access
- [ ] `functools.lru_cache` / `functools.cache` for pure functions called repeatedly
- [ ] Profile with `cProfile` / `line_profiler` before optimizing — no premature work
- [ ] `asyncio` event loop not blocked by synchronous I/O operations
- [ ] `concurrent.futures.ThreadPoolExecutor` for I/O-bound; `ProcessPoolExecutor` for CPU-bound
- [ ] `numpy` operations preferred over pure-Python loops for numeric work

---

## Design Principles (conditional)

Apply only when the change touches the situation described. Each is a review question, not a blanket rule.

- **Parse once at the boundary.** External data (HTTP bodies, files, env, DB rows) is validated and converted where it enters; inner code trusts the typed result. Re-validating deep inside is noise; skipping validation at the edge is a defect.
- **Business logic in pure functions.** If a function needs I/O to be tested, ask whether the decision can be separated from the I/O.
- **Re-run after a partial failure.** For jobs that write more than one thing, ask what state a crash halfway leaves, and whether running again ends in the same state (see idempotency in the data-pipeline checklist).
- **Do not share mutable state you do not need.** If two actors do not need the same mutable object, give each its own copy or make the data immutable. If they do share it, ask who owns it and what guards concurrent writes (single owner, queue, lock), and whether the invariants hold under the concurrency model the code already uses.
