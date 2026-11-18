# Advanced Testing Techniques

Advanced patterns beyond basic unit testing, applicable to any Python
data-processing pipeline.

## Table of Contents

- [Property-Based Testing with Hypothesis](#property-based-testing-with-hypothesis)
- [Time Control with Freezegun](#time-control-with-freezegun)
- [Parametrized Tests Best Practices](#parametrized-tests-best-practices)
- [Test Markers and Selective Execution](#test-markers-and-selective-execution)
- [Coverage Configuration](#coverage-configuration)
- [Testing Aggregation Metrics](#testing-aggregation-metrics)
- [Testing Pipeline Robustness](#testing-pipeline-robustness)
- [Debugging Test Failures](#debugging-test-failures)
- [Testing Retry and Resilience Logic](#testing-retry-and-resilience-logic)

## Property-Based Testing with Hypothesis

Test invariants with generated inputs — especially useful for normalization
functions and metric calculations:

```python
from hypothesis import given, strategies as st, assume
import pandas as pd
import numpy as np

@given(
    n_rows=st.integers(min_value=2, max_value=100),
    base_value=st.floats(min_value=1.0, max_value=100000.0, allow_nan=False),
)
def test_normalize_preserves_row_count(n_rows, base_value):
    df = pd.DataFrame({
        "time": pd.date_range("2026-01-01", periods=n_rows, freq="h"),
        "value": [base_value] * n_rows,
    })
    result = normalize_records(df)
    assert len(result) == n_rows

@given(
    values=st.lists(st.floats(min_value=0.01, max_value=100000.0, allow_nan=False), min_size=2),
)
def test_correlation_with_self_is_one(values):
    assume(len(set(values)) > 1)  # correlation is undefined for a constant series
    s = pd.Series(values)
    assert abs(correlation(s, s) - 1.0) < 1e-10

@given(
    actual=st.lists(st.floats(min_value=1.0, max_value=1000.0, allow_nan=False), min_size=5),
)
def test_relative_error_is_non_negative(actual):
    actual_s = pd.Series(actual)
    assert relative_error(actual_s, actual_s + 1.0) >= 0
```

**When to use Hypothesis:** `processing.py` functions, metric calculations
(relative error, correlation, R²), classification thresholds.

## Time Control with Freezegun

Deterministic time-dependent tests — critical for batch-file naming and
interval calculations:

```python
from freezegun import freeze_time
from datetime import datetime

@freeze_time("2026-01-15 10:30:00")
def test_batch_filename_generation():
    assert batch_filename() == "batch_20260115_1030.parquet"

@freeze_time("2026-01-01 00:00:00")
def test_interval_calculation():
    from src.myproject.client import Interval
    interval = Interval("5m")
    assert interval.minutes == 5

def test_time_travel_through_batches():
    """Test batch generation across time progression."""
    with freeze_time("2026-01-01 00:00:00") as frozen:
        assert get_current_time().hour == 0

        frozen.move_to("2026-01-01 00:05:00")
        assert get_current_time().minute == 5

        frozen.move_to("2026-01-01 01:00:00")
        assert get_current_time().hour == 1
```

## Parametrized Tests Best Practices

### Use Descriptive IDs

```python
@pytest.mark.parametrize("col_input,expected", [
    pytest.param("time", "timestamp", id="time-to-timestamp"),
    pytest.param("date", "timestamp", id="date-to-timestamp"),
    pytest.param("datetime", "timestamp", id="datetime-to-timestamp"),
    pytest.param("created_at", "created_at", id="created_at-unchanged"),
    pytest.param("timestamp", "timestamp", id="timestamp-already-correct"),
], ids=str)
def test_column_rename(col_input, expected):
    df = pd.DataFrame({col_input: pd.date_range("2026-01-01", periods=3, freq="h")})
    result = normalize_records(df)
    assert expected in result.columns
```

### Stack Parametrize for Multi-Source Testing

```python
@pytest.mark.parametrize("source_name", [
    "source_a", "source_b", "source_c", "source_d",
])
@pytest.mark.parametrize("percentile", [0, 25, 50, 75, 100])
def test_value_columns_present(source_name, percentile):
    """Runs 20 times (4 sources x 5 percentiles)."""
    df = SummaryBuilder(source_name=source_name).build()
    result = normalize_records(df, source_name=source_name)
    assert f"{source_name}_p{percentile}_value" in result.columns
```

### Parametrized Fixtures for Data Scenarios

```python
@pytest.fixture(params=[
    pytest.param({"n_rows": 50, "base_value": 100.0}, id="small-stable"),
    pytest.param({"n_rows": 200, "base_value": 50000.0}, id="large-high-value"),
    pytest.param({"n_rows": 100, "base_value": 1.5, "noise_scale": 0.01}, id="small-low-value"),
])
def varied_records(request):
    """Run tests against multiple record scenarios."""
    return RecordBuilder(**request.param).build()

def test_classification_with_varied_data(varied_records):
    label = classify_value(
        varied_records["value"].iloc[-1], threshold_high=70, threshold_low=30
    )
    assert label in ("HIGH", "LOW", "NORMAL")
```

## Test Markers and Selective Execution

### Define Markers

```toml
# pyproject.toml [tool.pytest.ini_options]
markers = [
    "unit: fast isolated tests (no I/O or API calls)",
    "integration: tests requiring data files or configs",
    "e2e: full pipeline workflow tests",
    "slow: tests that run heavy computations",
    "requires_service: tests that need an external service or optional dependency",
]
```

### Apply and Run Selectively

```python
@pytest.mark.unit
def test_normalize_columns():
    df = pd.DataFrame({"time": [], "value": []})
    result = normalize_records(df)
    assert "timestamp" in result.columns

@pytest.mark.integration
def test_parquet_roundtrip(sample_records_parquet):
    df = pd.read_parquet(sample_records_parquet)
    assert "value" in df.columns

@pytest.mark.slow
@pytest.mark.integration
def test_full_pipeline(batch_files):
    results = run_pipeline(batches=batch_files)
    assert len(results) > 0
```

```bash
pytest -m unit                          # Fast feedback
pytest -m "not slow"                    # Skip heavy runs
pytest -m "integration and not slow"    # Quick integration
pytest -m "not requires_service"        # Skip tests needing external services
```

> Using the `uv` runner? Prefix each command with `uv run`.

### Skip Conditionally

```python
import importlib.util

_fast_backend_available = importlib.util.find_spec("fast_backend") is not None
_service_reachable = service_health_check()  # project-specific helper

@pytest.mark.skipif(not _fast_backend_available, reason="Requires fast_backend dependency")
def test_fast_backend_selection():
    backend = resolve_backend(config={"backend": "auto"})
    assert backend == "fast_backend"

@pytest.mark.skipif(not _service_reachable, reason="Requires reachable external service")
def test_remote_service_selection():
    backend = resolve_backend(config={"backend": "auto"})
    assert backend == "remote"

@pytest.mark.xfail(reason="Known issue with empty input, fix pending")
def test_empty_input_handling():
    df = pd.DataFrame()
    result = normalize_records(df)
```

## Coverage Configuration

```toml
# pyproject.toml
[tool.coverage.run]
source = ["src"]
omit = [
    "*/tests/*",
    "*/sandbox/*",
    "*/__main__.py",
    "*/__pycache__/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
    "@abstractmethod",
    "if __name__ == .__main__.:",
]
fail_under = 70

[tool.coverage.html]
directory = "htmlcov"
```

```bash
# Run with coverage
pytest --cov=src --cov-report=term-missing --cov-report=html

# Fail below threshold
pytest --cov=src --cov-fail-under=70

# Show uncovered lines
pytest --cov=src --cov-report=term-missing
```

> Using the `uv` runner? Prefix each command with `uv run`.

## Testing Aggregation Metrics

Patterns for testing evaluation metrics (correlation, relative error, R²).
Call the project's metric functions (here `r_squared`, `correlation` and
`relative_error`); never re-implement the formula inside the test, because the
test would then pass with the production function deleted.

```python
import numpy as np
import pandas as pd

class TestAggregationMetrics:
    """Thematic group: metric calculation accuracy."""

    def test_perfect_prediction_r2_is_one(self):
        actual = pd.Series([100.0, 101.0, 102.0, 103.0, 104.0])
        assert abs(r_squared(actual, actual.copy()) - 1.0) < 1e-10

    def test_correlation_identical_series(self):
        values = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        assert abs(correlation(values, values) - 1.0) < 1e-10

    def test_relative_error_zero(self):
        actual = pd.Series([100.0, 200.0, 300.0])
        assert relative_error(actual, actual.copy()) == 0.0

    def test_relative_error_known_value(self):
        actual = pd.Series([100.0, 200.0])
        predicted = pd.Series([110.0, 180.0])
        # Worked by hand: (10% + 10%) / 2
        assert relative_error(actual, predicted) == pytest.approx(10.0)

    @pytest.mark.parametrize("actual,predicted,expected_corr", [
        ([1, 2, 3], [1, 2, 3], 1.0),
        ([1, 2, 3], [3, 2, 1], -1.0),
        ([1, 2, 3], [2, 2, 2], 0.0),
    ], ids=["perfect", "inverse", "constant"])
    def test_correlation_scenarios(self, actual, predicted, expected_corr):
        corr = correlation(pd.Series(actual), pd.Series(predicted))
        assert abs(corr - expected_corr) < 0.01
```

## Testing Pipeline Robustness

```python
class TestPipelineTolerance:
    """Verify the pipeline continues when an individual source fails."""

    def test_pipeline_continues_on_source_failure(self, multi_source_summaries):
        sources = ["source_a", "invalid_source", "source_b"]

        results = run_pipeline(sources, summaries=multi_source_summaries)

        assert set(results.succeeded) == {"source_a", "source_b"}
        assert "invalid_source" in results.failed

    def test_missing_source_excluded_from_ranking(self, multi_source_summaries):
        sources = ["source_a", "invalid_source", "source_b"]
        results = run_pipeline(sources, summaries=multi_source_summaries)

        ranked = [r["source"] for r in rank_sources(results)]

        assert set(ranked) == {"source_a", "source_b"}
```

## Debugging Test Failures

```bash
# Stop on first failure
pytest -x

# Drop into debugger on failure
pytest --pdb

# Show full diff for assertion errors
pytest -vv

# Run only last failed tests
pytest --lf

# Run failed first, then all
pytest --ff

# Capture print output
pytest -s

# Run specific test by name pattern
pytest -k "test_normalize"

# Parallel execution
pytest -n auto  # requires pytest-xdist
```

> Using the `uv` runner? Prefix each command with `uv run`.

## Testing Retry and Resilience Logic

```python
from unittest.mock import Mock

def test_retries_on_api_error():
    client = Mock()
    client.fetch_records.side_effect = [
        ConnectionError("timeout"),
        ConnectionError("timeout"),
        API_RECORDS_SUCCESS,
    ]

    result = fetch_with_retry(client, page=1, max_retries=3)

    assert len(result["records"]) > 0
    assert client.fetch_records.call_count == 3

def test_gives_up_after_max_retries():
    client = Mock()
    client.fetch_records.side_effect = ConnectionError("timeout")

    with pytest.raises(ConnectionError):
        fetch_with_retry(client, page=1, max_retries=3)

    assert client.fetch_records.call_count == 3

def test_no_retry_on_permanent_error():
    client = Mock()
    client.fetch_records.side_effect = ValueError("invalid endpoint")

    with pytest.raises(ValueError):
        fetch_with_retry(client, page=-1, max_retries=3)

    assert client.fetch_records.call_count == 1
```
