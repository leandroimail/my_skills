# Mock Patterns Reference

Patterns for organizing and using mocks in `tests/mocks/`, applicable to any
Python project that talks to external services and processes tabular data.

## Table of Contents

- [Mock Organization by Type](#mock-organization-by-type)
- [External API Response Mocks](#external-api-response-mocks)
- [Service Output Mocks](#service-output-mocks)
- [Data Builders / Factories](#data-builders--factories)
- [Optional Dependency Mocks](#optional-dependency-mocks)
- [Side-Effect Chains](#side-effect-chains)
- [Autospec for Safety](#autospec-for-safety)
- [Async Mocks](#async-mocks)
- [Mock Injection via Fixtures](#mock-injection-via-fixtures)
- [Monkeypatch Patterns](#monkeypatch-patterns)
- [Anti-Patterns to Avoid](#anti-patterns-to-avoid)

## Mock Organization by Type

```
tests/mocks/
├── __init__.py
├── api_responses.py        # External API response payloads
├── service_outputs.py      # Processing-service output data
├── data_builders.py        # Factory pattern for record/summary DataFrames
└── dependency_mocks.py     # Optional-dependency availability mocks
```

**Why by type?** Multiple test files need the same mock data. Centralizing
by type prevents duplicating mock definitions and ensures consistency.

## External API Response Mocks

Static response payloads matching the external REST API format:

```python
# tests/mocks/api_responses.py
"""Mock responses from the external REST API."""

API_RECORDS_SUCCESS = {
    "status": "ok",
    "page": 1,
    "records": [
        {"id": 1, "timestamp": "2026-01-01T00:00:00Z", "value": "42.50", "category": "A"},
    ],
}

API_RECORDS_MULTI = {
    "status": "ok",
    "page": 1,
    "records": [
        {"id": 1, "timestamp": "2026-01-01T00:00:00Z", "value": "42.50", "category": "A"},
        {"id": 2, "timestamp": "2026-01-01T01:00:00Z", "value": "123.45", "category": "B"},
    ],
}

API_RECORDS_EMPTY = {"status": "ok", "page": 1, "records": []}

API_ACCOUNT_INFO = {
    "status": "ok",
    "account": {
        "id": "acct_123",
        "balance": "0.001",
        "tier": "standard",
        "active": True,
    },
}

API_NO_ACCOUNT = {"status": "ok", "account": None}
```

## Service Output Mocks

Mock output from the processing service, matching the expected
parquet schema with `timestamp` and value columns:

```python
# tests/mocks/service_outputs.py
"""Mock outputs from the data-processing service."""
import pandas as pd

SOURCE_A_OUTPUT = pd.DataFrame({
    "timestamp": pd.date_range("2026-01-01", periods=12, freq="h"),
    "batch_id": "2026-01-01",
    "min_value": [100.0 + i * 0.1 for i in range(12)],
    "p25_value": [100.2 + i * 0.1 for i in range(12)],
    "median_value": [100.5 + i * 0.1 for i in range(12)],
    "p75_value": [100.8 + i * 0.1 for i in range(12)],
    "max_value": [101.0 + i * 0.1 for i in range(12)],
})

SOURCE_B_OUTPUT = pd.DataFrame({
    "timestamp": pd.date_range("2026-01-01", periods=12, freq="h"),
    "batch_id": "2026-01-01",
    "min_value": [99.8 + i * 0.1 for i in range(12)],
    "p25_value": [100.0 + i * 0.1 for i in range(12)],
    "median_value": [100.3 + i * 0.1 for i in range(12)],
    "p75_value": [100.6 + i * 0.1 for i in range(12)],
    "max_value": [100.8 + i * 0.1 for i in range(12)],
})

SOURCE_C_OUTPUT = pd.DataFrame({
    "timestamp": pd.date_range("2026-01-01", periods=12, freq="h"),
    "batch_id": "2026-01-01",
    "min_value": [99.5 + i * 0.12 for i in range(12)],
    "p25_value": [99.8 + i * 0.12 for i in range(12)],
    "median_value": [100.2 + i * 0.12 for i in range(12)],
    "p75_value": [100.6 + i * 0.12 for i in range(12)],
    "max_value": [100.9 + i * 0.12 for i in range(12)],
})
```

## Data Builders / Factories

Build domain DataFrames with sensible defaults and easy overrides:

```python
# tests/mocks/data_builders.py
"""Test data factories using the builder pattern for record DataFrames."""
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
    seed: int = 42

    def build(self) -> pd.DataFrame:
        rng = np.random.default_rng(self.seed)
        ts_index = pd.date_range(self.start_date, periods=self.n_rows, freq=self.freq)
        noise = rng.normal(0, self.noise_scale, self.n_rows)
        value = self.base_value + np.cumsum(noise)
        return pd.DataFrame({
            "id": list(range(self.n_rows)),
            "timestamp": ts_index,
            "value": value,
            "category": rng.choice(["A", "B", "C"], self.n_rows),
        })

    def with_trend(self, direction: float = 0.1) -> "RecordBuilder":
        """Add a linear trend to values."""
        self._trend = direction
        return self

    def with_gap(self, position: int = 50, size: float = 5.0) -> "RecordBuilder":
        """Add a value gap at a specific position."""
        self._gap = (position, size)
        return self


@dataclass
class SummaryBuilder:
    """Builder for processing-service summary DataFrames with value columns."""
    source_name: str = "test_source"
    n_rows: int = 12
    start_date: str = "2026-01-01"
    freq: str = "h"
    base_value: float = 100.0
    percentiles: tuple = (0, 25, 50, 75, 100)

    def build(self) -> pd.DataFrame:
        ts_index = pd.date_range(self.start_date, periods=self.n_rows, freq=self.freq)
        data = {
            "timestamp": ts_index,
            "batch_id": pd.Timestamp(self.start_date),
        }
        for p in self.percentiles:
            offset = (p - 50) * 0.02
            data[f"p{p}_value"] = [self.base_value + offset + i * 0.1 for i in range(self.n_rows)]
        if 50 in self.percentiles:
            data[f"{self.source_name}_mean"] = data["p50_value"]
        return pd.DataFrame(data)


@dataclass
class BatchBuilder:
    """Builder for historical batch file patterns (batch_YYYYMMDD_HHMM.parquet)."""
    n_batches: int = 5
    rows_per_batch: int = 100
    freq: str = "h"

    def build_list(self) -> list[pd.DataFrame]:
        """Generate a list of incremental batch DataFrames."""
        full = RecordBuilder(
            n_rows=self.n_batches * self.rows_per_batch,
            freq=self.freq,
        ).build()
        return [
            full.iloc[: (i + 1) * self.rows_per_batch].copy()
            for i in range(self.n_batches)
        ]

    def build_filenames(self) -> list[str]:
        """Generate expected filenames from batch DataFrames."""
        batches = self.build_list()
        return [
            f"batch_{batch['timestamp'].iloc[-1].strftime('%Y%m%d_%H%M')}.parquet"
            for batch in batches
        ]
```

Usage in tests:

```python
def test_classify_on_rising_trend():
    df = RecordBuilder(n_rows=100, base_value=100.0).with_trend(0.5).build()
    label = classify_value(df["value"].iloc[-1], threshold_high=70, threshold_low=30)
    assert label in ("HIGH", "NORMAL")

def test_summary_has_all_percentiles():
    df = SummaryBuilder(source_name="source_a", n_rows=12).build()
    assert "p0_value" in df.columns
    assert "p100_value" in df.columns
```

## Optional Dependency Mocks

Mock the availability of an optional dependency or external service for
`dependency_selector.py` tests:

```python
# tests/mocks/dependency_mocks.py
"""Mocks for optional-dependency / external-service availability checks."""
from unittest.mock import Mock

def create_dependency_available_mock(*, available: bool = True) -> Mock:
    """Mock a fast optional accelerator backend."""
    mock = Mock()
    mock.fast_backend.is_available.return_value = available
    if available:
        mock.fast_backend.device_count.return_value = 1
        mock.fast_backend.get_device_name.return_value = "Accelerator-X"
    return mock

def create_service_reachable_mock(*, reachable: bool = True) -> Mock:
    """Mock an external service health check."""
    mock = Mock()
    mock.service.ping.return_value = reachable
    mock.service.is_built.return_value = reachable
    return mock
```

## Side-Effect Chains

Simulate transient external API failures followed by success:

```python
from unittest.mock import Mock

def test_retries_on_api_timeout():
    client = Mock()
    client.fetch_records.side_effect = [
        ConnectionError("Read timed out"),
        ConnectionError("Read timed out"),
        API_RECORDS_SUCCESS,
    ]

    result = fetch_records(client, page=1)
    assert len(result["records"]) > 0
    assert client.fetch_records.call_count == 3
```

## Autospec for Safety

`autospec=True` catches API misuse (wrong method names, wrong argument count):

```python
from unittest.mock import patch

@patch("src.myproject.client.fetch_page", autospec=True)
def test_with_autospec(mock_fetch):
    mock_fetch.return_value = RecordBuilder(n_rows=50).build()

    df = fetch_records_as_df(page=1, page_size=50)
    assert "value" in df.columns
```

## Async Mocks

Mock async external API calls used in `client.py`:

```python
from unittest.mock import AsyncMock, patch
import pytest

@pytest.mark.asyncio
@patch("src.myproject.client.fetch_page", new_callable=AsyncMock)
async def test_async_records_fetch(mock_fetch):
    mock_fetch.return_value = RecordBuilder(n_rows=50).build()

    # Run the real subject; only its boundary (`fetch_page`) is mocked.
    result = await fetch_records_as_df(page=1, page_size=50)

    assert len(result) == 50
    mock_fetch.assert_awaited_once()
```

## Mock Injection via Fixtures

When mock data needs to be written to data files:

```python
# tests/fixtures/data_files.py
from tests.mocks.data_builders import SummaryBuilder

@pytest.fixture
def multi_source_summaries(data_dir):
    """Write mock summaries from multiple sources to parquet files."""
    paths = {}
    for source_name in ["source_a", "source_b", "source_c"]:
        df = SummaryBuilder(source_name=source_name, n_rows=12).build()
        path = data_dir / f"{source_name}_summary.parquet"
        df.to_parquet(path, index=False)
        paths[source_name] = path

    yield paths

    for p in paths.values():
        p.unlink(missing_ok=True)
```

## Monkeypatch Patterns

Use `monkeypatch` for environment variables and config overrides:

```python
def test_dependency_fallback_to_default(monkeypatch):
    monkeypatch.setattr("src.myproject.runtime.fast_backend_available", lambda: False)
    monkeypatch.setattr("src.myproject.runtime.service_reachable", lambda: False)
    backend = resolve_backend(config={"backend": "auto"})
    assert backend == "default"

def test_config_from_env(monkeypatch):
    monkeypatch.setenv("MYPROJECT_MODE", "fast")
    config = load_config()
    assert config["mode"] == "fast"
```

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Fix |
|---|---|---|
| Mocks defined inside each test | Duplication, inconsistency | Define in `tests/mocks/` |
| Over-mocking (mock everything) | Tests pass but code is broken | Mock only the external API and file I/O boundaries |
| Mock without autospec | Silent API drift | Use `autospec=True` |
| Shared mutable mock state | Tests interfere with each other | Create fresh mocks per test |
| Mocking DataFrame operations | Tests become fragile | Use real DataFrames from builders |
| Hardcoded data-file paths | Tests fail on other machines | Use temp directory fixtures |
| Mock never checked | Mock silently ignored | Assert the call when the outgoing call is the behavior under test; otherwise assert on the result it feeds |
| Asserting on the mock's own return value | Tests the mock, not the code | Run the real subject; mock only its boundary |
