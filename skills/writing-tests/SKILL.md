---
name: writing-tests
description: >
  Designs, structures, and implements pytest test suites for Python projects.
  Handles temp-file fixtures, DataFrame and dataclass factories, external API
  mocks, and async client mocks. Use when creating tests, writing unit or
  integration tests, setting up test infrastructure, designing fixtures,
  organizing mocks, or configuring conftest.py. Also handles mutation testing
  with mutmut: running mutmut, improving weak tests, killing surviving mutants.
  Use whenever the user mentions testing, test coverage, pytest fixtures, test
  patterns, mutation testing, mutmut, or test quality, even if not explicit.
compatibility: >
  Requires Python 3.11+, pytest >=7.0.0. Optional: pytest-asyncio, pytest-cov,
  pytest-xdist, hypothesis, freezegun, mutmut. Run tests via `pytest`
  (or `uv run pytest`).
metadata:
  author: generic
  version: "2.1"
---

# Writing Python Tests

## Purpose

Enforces a production-grade testing workflow for Python projects. Tests follow
strict directory conventions with temp-file fixtures, data factories, and
external service mocks. The patterns below are domain-neutral: substitute the
generic placeholders (records, the data-processing service, the REST API
client) with your project's actual modules.

## When To Use

- Creating or extending test suites for any module
- Setting up test infrastructure for new modules in `src/`
- Designing fixtures for file I/O (CSV/JSON/parquet), DataFrames, or YAML configs
- Organizing mocks for external API responses, service outputs, or optional dependencies
- Configuring `conftest.py` for test ordering and fixture registration
- Testing business-logic services (`service.py`)
- Testing data transformation and normalization (`processing.py`)
- Testing async I/O against external APIs (`client.py`)
- Testing pipeline workflows end to end
- Running mutation testing with mutmut and improving test quality
- Killing surviving mutants by strengthening assertions or adding boundary tests

## When Not To Use

- Non-Python projects
- Performance/load testing (use Locust or k6)
- UI/browser testing
- Static analysis or linting (use ruff, mypy)

## Inputs

Before writing tests, collect from the user or infer from context:

1. **Source module** — which module under `src/` is being tested
2. **Test scope** — unit, integration, e2e, or combination
3. **Data dependencies** — files (CSV/JSON/parquet), YAML configs, external APIs, service outputs
4. **Coverage target** — default ≥70% overall, 100% for critical/business-logic modules
5. **Async requirements** — needed when testing async API clients

## Directory Structure (Mandatory)

Tests follow a **thematic grouping** model aligned with the project's module
boundaries. Each test directory represents a cohesive domain.

```
tests/
├── conftest.py                    # ONLY test ordering + fixture registration
├── fixtures/                      # All fixtures live here
│   ├── __init__.py
│   ├── data_files.py              # Temp data-file lifecycle fixtures
│   ├── dataframes.py              # Record and summary DataFrame fixtures
│   ├── configs.py                 # YAML config loading fixtures
│   └── api_client.py              # Async API client fixtures
├── mocks/                         # All mocks live here, by type
│   ├── __init__.py
│   ├── service_outputs.py         # Processing-service output mocks
│   ├── api_responses.py           # External API response mocks
│   ├── data_builders.py           # Record / summary DataFrame factories
│   └── dependency_mocks.py        # Optional-dependency availability mocks
├── unit/                          # Thematic: fast, isolated tests
│   ├── __init__.py
│   ├── test_processing.py
│   ├── test_dependency_selector.py
│   ├── test_service.py
│   └── test_client.py
├── integration/                   # Thematic: component interaction
│   ├── __init__.py
│   ├── test_file_io.py
│   └── test_pipeline_workflow.py
└── e2e/                           # Thematic: full workflow
    ├── __init__.py
    └── test_full_pipeline.py
```

**Why thematic grouping?** When `test_service.py` fails, you know the
issue is in `src/myproject/service.py`. It also enables selective
execution with markers (`pytest -m unit`).

## Method

### Before Step 1: Settle the Seams

A seam is the public boundary where a test observes behavior without reaching
inside: the subject, its entry point, the outputs the test may observe, and the
dependencies it may replace. Settle the seams before you create any test
infrastructure.

- A seam the user named in the request ("add a regression test for
  `normalize_records`") or approved in an earlier plan is settled. Do not ask again.
- When the choice is open and the user can answer, list the proposed seams with
  one line each on what it catches and what it misses, and ask once.
- When the user cannot be asked (an unattended run), choose the seams yourself
  and state them, with the same one-line notes, in the final report.

### Step 1: Create the Directory Skeleton

Create the directory structure above. Adapt thematic folders to match the
project's module boundaries (e.g., `tests/reporting/`, `tests/ingestion/`).

### Step 2: Write Fixtures in `tests/fixtures/`

Fixtures manage lifecycles of test resources. Every fixture **must**:

1. **Check resource availability** before attempting to create it
2. **Provision the resource** only if it is not already available
3. **Yield** the ready-to-use resource to the test
4. **Teardown** cleanly after the test completes

```python
# tests/fixtures/data_files.py
import pytest
import pandas as pd
from pathlib import Path
import tempfile
import shutil

@pytest.fixture(scope="session")
def data_dir():
    """Session-scoped temp directory for test data files."""
    tmpdir = tempfile.mkdtemp(prefix="myproject_test_data_")
    yield Path(tmpdir)
    shutil.rmtree(tmpdir, ignore_errors=True)

@pytest.fixture(scope="function")
def sample_records_parquet(data_dir):
    """Creates a sample records.parquet with a simple tabular dataset."""
    df = pd.DataFrame({
        "id": list(range(100)),
        "timestamp": pd.date_range("2026-01-01", periods=100, freq="h"),
        "value": [100.0 + i * 0.1 for i in range(100)],
        "category": ["A" if i % 2 == 0 else "B" for i in range(100)],
    })
    path = data_dir / "records.parquet"
    df.to_parquet(path, index=False)
    yield path
    path.unlink(missing_ok=True)
```

> **For detailed fixture patterns** (config YAML, async API client,
> DataFrame fixtures): See [fixture-patterns.md](references/fixture-patterns.md)

### Step 3: Organize Mocks in `tests/mocks/`

Mocks are categorized **by type**, not by consumer test. This prevents
duplication and ensures consistent mock behavior across the test suite.

```python
# tests/mocks/api_responses.py
"""Mock responses from the external REST API."""

API_RECORDS_SUCCESS = {
    "status": "ok",
    "page": 1,
    "records": [
        {"id": 1, "value": "42.50", "category": "A"},
        {"id": 2, "value": "123.45", "category": "B"},
    ],
}

API_RECORDS_EMPTY = {"status": "ok", "page": 1, "records": []}

# tests/mocks/data_builders.py
"""Test data factories for record DataFrames."""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

@dataclass
class RecordBuilder:
    """Builder for synthetic record DataFrames."""
    n_rows: int = 100
    start_date: str = "2026-01-01"
    freq: str = "h"
    base_value: float = 100.0
    noise_scale: float = 0.5

    def build(self) -> pd.DataFrame:
        rng = np.random.default_rng(42)
        ts_index = pd.date_range(self.start_date, periods=self.n_rows, freq=self.freq)
        noise = rng.normal(0, self.noise_scale, self.n_rows)
        value = self.base_value + np.cumsum(noise)
        return pd.DataFrame({
            "id": list(range(self.n_rows)),
            "timestamp": ts_index,
            "value": value,
            "category": ["A" if i % 2 == 0 else "B" for i in range(self.n_rows)],
        })
```

When mocks need to be **injected into resources** (e.g., seed a temp directory
with mock data files), use a fixture that composes mocks + resource:

```python
# tests/fixtures/data_files.py
from tests.mocks.data_builders import RecordBuilder

@pytest.fixture
def seeded_data_dir(data_dir):
    """Fixture that seeds temp dir with mock data file batches."""
    builder = RecordBuilder(n_rows=200)
    df = builder.build()
    for i, ts in enumerate(df["timestamp"].unique()[:5]):
        batch = df[df["timestamp"] <= ts].copy()
        path = data_dir / f"batch_{pd.Timestamp(ts).strftime('%Y%m%d_%H%M')}.parquet"
        batch.to_parquet(path, index=False)
    yield data_dir
```

> **For mock patterns** (service outputs, dependency mocks, autospec,
> side_effect chains): See [mock-patterns.md](references/mock-patterns.md)

### Step 4: Configure `conftest.py` — Ordering Only

The root `conftest.py` has **one responsibility**: register fixtures and control
test execution order. No business logic, no test helpers.

```python
# tests/conftest.py
"""
Test configuration: fixture registration and test ordering ONLY.
All fixture implementations live in tests/fixtures/.
All mock definitions live in tests/mocks/.
"""
import pytest

# Register fixtures from the fixtures package
pytest_plugins = [
    "tests.fixtures.data_files",
    "tests.fixtures.dataframes",
    "tests.fixtures.configs",
    "tests.fixtures.api_client",
]

def pytest_collection_modifyitems(items):
    """Enforce test execution order: unit → integration → e2e."""
    order = {"unit": 0, "integration": 1, "e2e": 2}

    def sort_key(item):
        for marker_name, priority in order.items():
            if marker_name in str(item.fspath):
                return priority
        return 99

    items.sort(key=sort_key)
```

### Step 5: Write Tests Following AAA + TDD

Every test follows the **Arrange → Act → Assert** pattern inside a
**TDD cycle** (Red → Green → Refactor).

In the Red step, run the test and confirm it fails for the expected reason (the
assertion about the behavior, not an import error or a typo) before you write
the code. If an honest test is impractical, state the alternative verification
instead of writing a weak test.

A test for behavior that already exists (a characterization test, or one that
kills a surviving mutant in Step 8) has no Green step: it passes at once. Prove
that it is sensitive by breaking the code temporarily, or by checking that the
mutant dies.

Avoid these three anti-patterns:

- **Implementation-coupled**: the test replaces a collaborator that sits inside
  the seam, calls non-public functions, or reads state that is not an output of the seam.
  For an API test that means the database; for a persistence adapter the
  persisted rows are the output, and asserting on them is correct.
  Test doubles belong at the system boundaries: network, database, clock,
  filesystem, environment. Assert on a call to a double only when that outgoing
  call is the behavior under test. The tell: the test breaks on a refactor that
  did not change behavior.
- **Tautological**: the expected value is produced by copying the production
  algorithm into the test, so both share the same bug; or the test asserts on
  what a mock was configured to return without running the real subject. Derive
  expected values independently: a known-good literal, a worked example, the
  spec. Properties taken from the spec (idempotence, round-trip, invariants)
  are valid.
- **Horizontal slicing**: when building new or changed behavior, writing all
  tests first and then all the implementation. Work in vertical slices instead:
  one behavior (a parametrized set counts as one), Red, minimal Green, Refactor,
  repeat, so each test responds to what the previous cycle taught you.

```python
# tests/unit/test_processing.py
import pytest
import pandas as pd
import numpy as np
from src.myproject.processing import (
    normalize_records,
    merge_dataframes_with_prefix,
)

class TestNormalizeRecords:
    """Thematic group: record normalization."""

    @pytest.mark.parametrize("input_col,expected", [
        ("time", "timestamp"),
        ("created_at", "created_at"),
        ("date", "timestamp"),
        ("datetime", "timestamp"),
    ], ids=["time", "created_at", "date", "datetime"])
    def test_column_rename_to_timestamp(self, input_col, expected):
        # Arrange
        df = pd.DataFrame({input_col: pd.date_range("2026-01-01", periods=3, freq="h")})
        # Act
        result = normalize_records(df)
        # Assert
        assert expected in result.columns

    def test_value_columns_preserved(self):
        # Arrange
        df = pd.DataFrame({
            "timestamp": pd.date_range("2026-01-01", periods=3, freq="h"),
            "min_value": [1.0, 2.0, 3.0],
            "median_value": [1.5, 2.5, 3.5],
            "max_value": [2.0, 3.0, 4.0],
        })
        # Act
        result = normalize_records(df)
        # Assert
        assert "min_value" in result.columns
        assert "max_value" in result.columns
```

### Step 6: Configure pytest and Coverage

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
asyncio_mode = "auto"
addopts = [
    "-v",
    "--strict-markers",
    "--tb=short",
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-fail-under=70",
]
markers = [
    "unit: fast isolated tests (no I/O or API calls)",
    "integration: tests requiring data files or configs",
    "e2e: full pipeline workflow tests",
    "slow: tests that run heavy computations",
    "requires_service: tests that need an external service or optional dependency",
]
```

### Step 7: Verify and Iterate

Run the validation checklist below. Fix any failures. Re-run until all pass.

```bash
pytest -m unit -v
pytest --cov=src --cov-report=term-missing
```

> Using the `uv` runner? Prefix the commands with `uv run` (e.g.
> `uv run pytest -m unit -v`).

### Step 8: Run Mutation Testing with mutmut

After achieving ≥80% line coverage, validate that tests actually enforce behavior — not just execution. Start with the highest-priority modules (`processing.py`, `service.py`).

```bash
# Install mutmut if not already present
pip install mutmut

# Run mutation testing on a specific module
mutmut run --paths-to-mutate src/myproject/processing.py

# Inspect surviving mutants
mutmut results
mutmut show <id>   # read exact diff for each survivor

# Generate HTML report
mutmut html
# open html/index.html with your browser: xdg-open (Linux), open (macOS), start (Windows)
```

Work in this order: cover uncovered lines first, then kill survivors. For each surviving mutant: identify the missing assertion (boundary, exact value, or inverse case), add it to the test, and re-run. If the mutant is equivalent, justify it with the exact behavior. A survivor can also point to dead code: report it, and remove it only when the removal is in scope. Target 80%+ mutation score on critical modules with 100% coverage targets.

> **Full guide**: [mutation-testing.md](references/mutation-testing.md) — covers configuration, all mutation types, Python examples, and workflow.

## Quality Checklist

- [ ] Every test directory represents a single module or feature (thematic)
- [ ] All fixtures live in `tests/fixtures/` and are registered in `conftest.py`
- [ ] Every data-file fixture creates files in a temp directory with cleanup
- [ ] Every fixture with setup includes proper teardown (`yield` + cleanup)
- [ ] All mocks are in `tests/mocks/`, separated by type
- [ ] Mock DataFrames use the project's actual column conventions
- [ ] `conftest.py` contains ONLY fixture registration and test ordering
- [ ] Tests follow AAA pattern (Arrange → Act → Assert)
- [ ] Each test verifies exactly one behavior
- [ ] Parametrized tests use descriptive `ids`
- [ ] Coverage is ≥70% overall, 100% for critical/business-logic modules
- [ ] Mutation score ≥80% for critical modules (after 100% line coverage)
- [ ] No assertions that only check truthiness (`is not None`, `> 0`) for exact-value logic
- [ ] Boundary conditions tested for every comparison operator (at, above, and below threshold)
- [ ] Seams were settled before any test was written, and the final report states them
- [ ] Test doubles sit only at system boundaries; a call to a double is asserted only when that call is the behavior under test
- [ ] Every test runs the real subject, and no expected value copies the production algorithm
- [ ] Each new test fails when the behavior it describes is removed (break the code temporarily, or check surviving mutants); strengthen tests that still pass
- [ ] Functions this task changes that are complex and poorly covered get tests or are split (optional diagnostic: CRAP, see the `code-review` skill, which has the install steps)
- [ ] Test names follow `test_<unit>_<scenario>_<expected>` convention
- [ ] No shared mutable state between tests
- [ ] External API calls are mocked (no real network calls in tests)
- [ ] Async tests use `@pytest.mark.asyncio` for async functions

## Outputs

This skill produces:

1. **Directory structure** — `tests/` with thematic, fixtures, and mocks folders
2. **Fixture files** — data-file, DataFrame, config, and async client fixtures in `tests/fixtures/`
3. **Mock files** — service outputs, API responses, DataFrame factories in `tests/mocks/`
4. **conftest.py** — ordering and fixture registration
5. **Test files** — AAA-structured tests with parametrization and markers
6. **pytest config** — `pyproject.toml` section with coverage and markers
7. **mutmut config** — `[tool.mutmut]` block in `pyproject.toml` (when Step 8 is executed)
8. **Mutation report** — HTML report at `html/index.html` identifying surviving mutants (when Step 8 is executed)

## Reference Documentation

- **Fixture Patterns**: [fixture-patterns.md](references/fixture-patterns.md)
- **Mock Patterns**: [mock-patterns.md](references/mock-patterns.md)
- **Async Testing**: [async-testing.md](references/async-testing.md)
- **Advanced Techniques**: [advanced-techniques.md](references/advanced-techniques.md)
- **Mutation Testing**: [mutation-testing.md](references/mutation-testing.md)
