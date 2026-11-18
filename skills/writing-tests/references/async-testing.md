# Async Testing Reference

Patterns for testing async code with pytest-asyncio. The examples assume the
project uses async code in `src/myproject/client.py` for concurrent
external REST API fetching.

## Table of Contents

- [Setup](#setup)
- [Testing Async API Fetching](#testing-async-api-fetching)
- [Async Mocking](#async-mocking)
- [Testing Concurrent Fetches](#testing-concurrent-fetches)
- [Testing Event Loop Patterns](#testing-event-loop-patterns)
- [Async Error Handling](#async-error-handling)

## Setup

```toml
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

```txt
# Dependency declared in pyproject.toml
pytest-asyncio>=0.21.0
```

## Testing Async API Fetching

Suppose the primary async code is `fetch_records_as_df()` and
`fetch_page()` in `src/myproject/client.py`, which use
`asyncio.gather()` and `loop.run_in_executor()` to parallelize
external API calls.

```python
# tests/unit/test_client_async.py
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock, AsyncMock

from tests.mocks.data_builders import RecordBuilder

@pytest.mark.asyncio
async def test_fetch_records_returns_dataframe():
    mock_df = RecordBuilder(n_rows=50).build()

    with patch("src.myproject.client.fetch_page", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_df
        # Run the real subject; only its boundary (`fetch_page`) is mocked.
        result = await fetch_records_as_df(endpoint="records", pages=[1])

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 50
    assert "value" in result.columns

@pytest.mark.asyncio
async def test_fetch_records_concurrent():
    """Test that multiple pages are fetched concurrently."""
    mock_df_1 = RecordBuilder(n_rows=50, base_value=100.0).build()
    mock_df_2 = RecordBuilder(n_rows=50, base_value=200.0).build()

    with patch("src.myproject.client.fetch_page", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.side_effect = [mock_df_1, mock_df_2]
        result = await fetch_records_as_df(
            endpoint="records",
            pages=[1, 2],
        )

    assert len(result) == 100  # 2 pages x 50 rows, combined
    assert mock_fetch.await_count == 2
```

## Async Mocking

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
@patch("src.myproject.client.fetch_page", new_callable=AsyncMock)
async def test_async_mock_return_value(mock_fetch):
    mock_fetch.return_value = RecordBuilder(n_rows=30).build()

    result = await fetch_records_as_df(endpoint="records", pages=[1])

    assert len(result) == 30
    mock_fetch.assert_awaited_once()

@pytest.mark.asyncio
@patch("src.myproject.client.fetch_page", new_callable=AsyncMock)
async def test_fetch_retries_after_transient_error(mock_fetch):
    # Assumes `fetch_records_as_df` retries transient errors. The side effects
    # drive the real retry logic; a test that awaits the mock directly would
    # only test `AsyncMock`.
    mock_fetch.side_effect = [
        ConnectionError("API timeout"),
        RecordBuilder(n_rows=50).build(),
    ]

    result = await fetch_records_as_df(endpoint="records", pages=[1])

    assert len(result) == 50
    assert mock_fetch.await_count == 2
```

## Testing Concurrent Fetches

`fetch_records_as_df` uses `asyncio.gather()` to fetch multiple pages
concurrently. Test that all pages are fetched and results are combined:

```python
import asyncio

@pytest.mark.asyncio
async def test_concurrent_page_fetches():
    """Verify all pages are fetched concurrently."""
    pages = [1, 2, 3]
    expected_dfs = [
        RecordBuilder(n_rows=50, base_value=100.0 * p).build()
        for p in pages
    ]

    with patch("src.myproject.client.fetch_page", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.side_effect = expected_dfs

        result = await fetch_records_as_df(endpoint="records", pages=pages)

    assert len(result) == 150  # 3 pages x 50 rows, combined
    assert mock_fetch.await_count == 3

@pytest.mark.asyncio
async def test_partial_failure_with_return_exceptions():
    """Verify one failed page doesn't break the others."""
    results = await asyncio.gather(
        _fetch_or_fail(1, should_fail=False),
        _fetch_or_fail(2, should_fail=True),
        _fetch_or_fail(3, should_fail=False),
        return_exceptions=True,
    )
    assert isinstance(results[1], Exception)
    assert isinstance(results[0], pd.DataFrame)
    assert isinstance(results[2], pd.DataFrame)
```

## Testing Event Loop Patterns

If the project uses `asyncio.run()` and `nest_asyncio.apply()` in some places,
mock at the API client level, not the event loop level:

```python
def test_sync_wrapper_calls_async():
    """Test that sync functions correctly call async counterparts."""
    with patch("src.myproject.client.fetch_page", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = RecordBuilder(n_rows=50).build()
        result = fetch_records_as_df_sync(page=1, page_size=50)

    assert isinstance(result, pd.DataFrame)
```

## Async Error Handling

```python
@pytest.mark.asyncio
async def test_api_connection_error():
    """Verify connection errors are raised properly."""
    with patch("src.myproject.client.fetch_page", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.side_effect = ConnectionError("API unreachable")

        with pytest.raises(ConnectionError, match="unreachable"):
            await fetch_page(page=1, page_size=50)

@pytest.mark.asyncio
async def test_api_timeout():
    """Verify timeout errors are handled."""
    with patch("src.myproject.client.fetch_page", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.side_effect = asyncio.TimeoutError()

        with pytest.raises(asyncio.TimeoutError):
            await fetch_page(page=1, page_size=50)
```
