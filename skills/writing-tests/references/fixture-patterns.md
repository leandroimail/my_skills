# Fixture Patterns Reference

Detailed patterns for fixture lifecycle management in `tests/fixtures/`,
applicable to any file-based, tabular-data Python project.

## Table of Contents

- [Design Principles](#design-principles)
- [Data File Fixtures](#data-file-fixtures)
- [Record DataFrame Fixtures](#record-dataframe-fixtures)
- [Summary DataFrame Fixtures](#summary-dataframe-fixtures)
- [YAML Config Fixtures](#yaml-config-fixtures)
- [Async API Client Fixtures](#async-api-client-fixtures)
- [Temporary Directory Fixtures](#temporary-directory-fixtures)
- [Fixture Composition](#fixture-composition)
- [Fixture Scopes Decision Guide](#fixture-scopes-decision-guide)
- [Seeding with Mocks via Fixtures](#seeding-with-mocks-via-fixtures)

## Design Principles

Every fixture **must** follow this lifecycle contract:

```
1. CHECK  → Is the resource already available?
2. SETUP  → If not, provision it (or skip the test)
3. YIELD  → Hand the ready resource to the test
4. TEARDOWN → Clean up (delete files, close connections)
```

**Why check first?** Prevents redundant resource creation, avoids file
collisions, and allows graceful `pytest.skip()` when external services
(like a remote REST API) are unavailable.

## Data File Fixtures

### Data Directory with Cleanup

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
    """Creates a sample records.parquet for processing input."""
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

@pytest.fixture(scope="function")
def sample_metadata_csv(data_dir):
    """Creates a sample metadata.csv as a second illustrative file format."""
    df = pd.DataFrame({
        "id": list(range(20)),
        "weight": [0.5 + i * 0.01 for i in range(20)],
        "active": [i % 3 != 0 for i in range(20)],
    })
    path = data_dir / "metadata.csv"
    df.to_csv(path, index=False)
    yield path
    path.unlink(missing_ok=True)
```

### Multiple Batch Files (Pipeline Pattern)

```python
@pytest.fixture(scope="function")
def batch_files(data_dir):
    """Creates multiple batch_YYYYMMDD_HHMM.parquet files."""
    from tests.mocks.data_builders import RecordBuilder

    builder = RecordBuilder(n_rows=200)
    df = builder.build()
    paths = []
    for i in range(5):
        ts = df["timestamp"].iloc[i * 20]
        batch = df.iloc[: (i + 1) * 20].copy()
        path = data_dir / f"batch_{pd.Timestamp(ts).strftime('%Y%m%d_%H%M')}.parquet"
        batch.to_parquet(path, index=False)
        paths.append(path)

    yield paths

    for p in paths:
        p.unlink(missing_ok=True)
```

## Record DataFrame Fixtures

### Standard Record DataFrame

```python
# tests/fixtures/dataframes.py
import pytest
import pandas as pd
import numpy as np

@pytest.fixture(scope="function")
def records_df():
    """Standard record DataFrame with deterministic data."""
    rng = np.random.default_rng(42)
    n = 100
    ts_index = pd.date_range("2026-01-01", periods=n, freq="h")
    value = 100.0 + np.cumsum(rng.normal(0, 0.5, n))
    return pd.DataFrame({
        "id": list(range(n)),
        "timestamp": ts_index,
        "value": value,
        "category": rng.choice(["A", "B", "C"], n),
    })

@pytest.fixture(scope="function")
def records_with_derived(records_df):
    """Record DataFrame with derived analytic columns applied."""
    df = records_df.copy()
    df["value_rolling_mean"] = df["value"].rolling(window=14, min_periods=1).mean()
    df["value_pct_change"] = df["value"].pct_change().fillna(0.0)
    df["value_zscore"] = (df["value"] - df["value"].mean()) / df["value"].std()
    return df
```

## Summary DataFrame Fixtures

### Processing Output

```python
@pytest.fixture(scope="function")
def summary_df():
    """DataFrame matching normalize_records expected format."""
    ts_index = pd.date_range("2026-01-01", periods=12, freq="h")
    return pd.DataFrame({
        "timestamp": ts_index,
        "batch_id": "2026-01-01",
        "min_value": [100.0 + i * 0.1 for i in range(12)],
        "p25_value": [100.2 + i * 0.1 for i in range(12)],
        "median_value": [100.5 + i * 0.1 for i in range(12)],
        "p75_value": [100.8 + i * 0.1 for i in range(12)],
        "max_value": [101.0 + i * 0.1 for i in range(12)],
    })

@pytest.fixture(scope="function")
def merged_summary_df():
    """DataFrame matching merged multi-source output format."""
    ts_index = pd.date_range("2026-01-01", periods=12, freq="h")
    return pd.DataFrame({
        "timestamp": ts_index,
        "source_a_mean": [100.5 + i * 0.1 for i in range(12)],
        "source_a_min": [99.5 + i * 0.1 for i in range(12)],
        "source_a_max": [101.5 + i * 0.1 for i in range(12)],
        "source_b_mean": [100.3 + i * 0.1 for i in range(12)],
        "source_b_min": [99.3 + i * 0.1 for i in range(12)],
        "source_b_max": [101.3 + i * 0.1 for i in range(12)],
    })
```

## YAML Config Fixtures

### Config File Loading

```python
# tests/fixtures/configs.py
import pytest
import yaml
from pathlib import Path
import tempfile
import shutil

@pytest.fixture(scope="session")
def config_dir():
    """Session-scoped temp directory for YAML config files."""
    tmpdir = tempfile.mkdtemp(prefix="myproject_test_config_")
    yield Path(tmpdir)
    shutil.rmtree(tmpdir, ignore_errors=True)

@pytest.fixture(scope="function")
def app_config_yaml(config_dir):
    """Creates a minimal app.yaml config file."""
    config = {
        "app": {
            "name": "myproject",
            "interval": "1h",
            "mode": "full",
        }
    }
    path = config_dir / "app.yaml"
    with open(path, "w") as f:
        yaml.dump(config, f)
    yield path
    path.unlink(missing_ok=True)

@pytest.fixture(scope="function")
def processing_config_yaml(config_dir):
    """Creates a config with processing parameter definitions."""
    config = {
        "processing": {
            "window": 14,
            "min_periods": 1,
            "threshold_high": 70,
            "threshold_low": 30,
            "drop_nulls": True,
        }
    }
    path = config_dir / "processing_config.yaml"
    with open(path, "w") as f:
        yaml.dump(config, f)
    yield path
    path.unlink(missing_ok=True)
```

## Async API Client Fixtures

### Mocked Async API Client

Suppose the project fetches data from an external REST API in
`src/myproject/client.py` via `asyncio.run()` and `asyncio.gather()`.
Mock the client, not the event loop.

```python
# tests/fixtures/api_client.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from tests.mocks.api_responses import API_RECORDS_SUCCESS

@pytest.fixture
def mock_api_client():
    """Mock REST API client with default records response."""
    client = MagicMock()
    client.fetch_records = MagicMock(
        return_value=API_RECORDS_SUCCESS
    )
    return client

@pytest.fixture
def mock_api_client_empty():
    """Mock API client that returns an empty records page."""
    from tests.mocks.api_responses import API_RECORDS_EMPTY
    client = MagicMock()
    client.fetch_records = MagicMock(
        return_value=API_RECORDS_EMPTY
    )
    return client
```

## Temporary Directory Fixtures

```python
@pytest.fixture(scope="function")
def output_dir():
    """Function-scoped temp directory for test output files."""
    tmpdir = tempfile.mkdtemp(prefix="myproject_test_output_")
    yield Path(tmpdir)
    shutil.rmtree(tmpdir, ignore_errors=True)
```

## Fixture Composition

Compose small fixtures into higher-level ones:

```python
@pytest.fixture
def processing_test_env(data_dir, sample_records_parquet, sample_metadata_csv):
    """Composite fixture: input files ready for the processing pipeline."""
    return {
        "data_dir": data_dir,
        "records_path": sample_records_parquet,
        "metadata_path": sample_metadata_csv,
    }

@pytest.fixture
def pipeline_env(records_with_derived, app_config_yaml):
    """Composite fixture: records data + config ready for the pipeline."""
    return {
        "df": records_with_derived,
        "config_path": app_config_yaml,
    }
```

## Fixture Scopes Decision Guide

| Scope | Lifecycle | Use For |
|-------|-----------|---------|
| `function` | Each test | DataFrames, data files, mock clients, temp dirs |
| `class` | Each test class | Class-level setup for grouped tests |
| `module` | Each test file | Shared expensive resources within a module |
| `session` | Entire test run | Temp directories, config file directories |

**Rule of thumb:** Use the narrowest scope that avoids unnecessary re-creation.
Mutable resources (DataFrames, temp files) should be `function`-scoped.
Immutable infrastructure (session temp dirs) should be `session`-scoped.

## Seeding with Mocks via Fixtures

When mock data needs to be written to disk, create a **seeding fixture**
that composes mock data builders + file resource:

```python
# tests/fixtures/data_files.py
from tests.mocks.data_builders import RecordBuilder, SummaryBuilder

@pytest.fixture
def seeded_base_dir(data_dir):
    """Temp dir seeded with multiple historical batches."""
    builder = RecordBuilder(n_rows=500)
    df = builder.build()
    batch_marks = df["timestamp"].unique()[::100][:5]

    for ts in batch_marks:
        batch = df[df["timestamp"] <= ts].copy()
        path = data_dir / f"batch_{pd.Timestamp(ts).strftime('%Y%m%d_%H%M')}.parquet"
        batch.to_parquet(path, index=False)

    yield data_dir

@pytest.fixture
def summary_output_dir(data_dir):
    """Temp dir with mock summary parquet files from multiple sources."""
    for source_name in ["source_a", "source_b", "source_c"]:
        builder = SummaryBuilder(source_name=source_name, n_rows=12)
        df = builder.build()
        path = data_dir / f"{source_name}_summary.parquet"
        df.to_parquet(path, index=False)

    yield data_dir
```

**Key pattern:** Fixtures form a dependency chain where mock data builders
flow into data files naturally through fixture composition.
