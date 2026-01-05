# DataFetcher Implementation Summary

## Overview

Implemented `src/py_gdelt/sources/fetcher.py` - the DataFetcher class that orchestrates source selection and fallback behavior for GDELT data fetching.

## Key Features

### 1. Primary/Fallback Pattern
- **Files are ALWAYS primary** (free, no credentials needed)
- **BigQuery is FALLBACK ONLY** (on 429/error, if credentials configured)
- Fallback logged at WARNING level (not silent)

### 2. Dependency Injection
```python
fetcher = DataFetcher(
    file_source=file_source,
    bigquery_source=bigquery_source,
    fallback_enabled=True,
    error_policy="warn",
)
```

### 3. Parser Protocol
```python
class Parser(Protocol[T]):
    def parse(self, data: bytes, is_translated: bool = False) -> AsyncIterator[T] | Iterator[T]:
        ...

    def detect_version(self, header: bytes) -> int:
        ...
```

### 4. Error Handling Policies
- `raise`: Re-raise errors (stop on first error)
- `warn`: Log warning and continue (default)
- `skip`: Silently skip errors and continue

### 5. Generic Fetch Method
```python
async def fetch(
    self,
    filter_obj: EventFilter | GKGFilter,
    parser: Parser[T],
    *,
    use_bigquery: bool = False,
) -> AsyncIterator[T]:
    """Generic fetch with automatic fallback."""
```

### 6. Convenience Methods
- `fetch_events(filter_obj)` - Fetch GDELT Events
- `fetch_mentions(global_event_id, filter_obj)` - Fetch Mentions (BigQuery only)
- `fetch_gkg(filter_obj)` - Fetch GKG records
- `fetch_ngrams(filter_obj)` - Fetch NGrams (files only)

## Implementation Details

### Source Selection Logic

1. **Primary (Files)**:
   - Downloads from `data.gdeltproject.org`
   - Free, no credentials
   - Supports 15-minute granularity
   - Handles translations automatically

2. **Fallback (BigQuery)**:
   - Only triggered on:
     - `RateLimitError` (429 status)
     - `APIError` / `APIUnavailableError`
   - Requires credentials configuration
   - Must be explicitly enabled
   - Logs warning when activated

### Fallback Behavior

```python
try:
    # Try file source first
    async for record in self._fetch_from_files(filter_obj, parser):
        yield record

except RateLimitError as e:
    if self._fallback:
        logger.warning("Rate limited, falling back to BigQuery")
        async for record in self._fetch_from_bigquery(filter_obj, parser):
            yield record
    else:
        raise
```

### Error Policy Handling

```python
def _handle_error(self, error: Exception) -> None:
    if self._error_policy == "raise":
        raise error
    elif self._error_policy == "warn":
        logger.warning("Error occurred: %s (continuing)", error)
    elif self._error_policy == "skip":
        logger.debug("Error occurred: %s (skipping)", error)
```

## Testing

### Test Coverage
- **22 test cases** covering:
  - Initialization with different configurations
  - Error policy handling (raise/warn/skip)
  - Fetching from file source
  - Fallback behavior on rate limit
  - Fallback behavior on API errors
  - Direct BigQuery usage
  - Convenience methods
  - Edge cases and error scenarios

### Test Results
- **19 tests passed** ✅
- **3 tests failed** due to pre-existing issue with `_internal.py` dataclass ordering (not related to DataFetcher implementation)

### Tests Run
```bash
uv run pytest tests/test_sources_fetcher.py -v
```

## Code Quality

### Linting
```bash
uv run ruff check src/py_gdelt/sources/fetcher.py
```
**Result**: All checks passed! ✅

### Type Hints
- Full type coverage with modern Python 3.12+ syntax
- Uses `TYPE_CHECKING` for import optimization
- Protocol-based parser interface
- Generic type parameter `[T]` for type safety

### Documentation
- Comprehensive docstrings (Google style)
- Inline comments explaining design decisions
- Example usage in docstrings
- Clear error messages

## Architecture Decisions

### 1. Protocol vs ABC
Used `Protocol` instead of `ABC` for parser interface:
- More flexible (structural subtyping)
- No inheritance required
- Better for third-party parsers

### 2. Dependency Injection
Sources are passed in constructor:
- Easier testing (mock injection)
- Explicit dependencies
- No hidden globals

### 3. Generic Type Parameter
Using Python 3.12+ syntax `[T]`:
- Type-safe async iteration
- Better IDE support
- Clearer intent

### 4. Async First
All fetch methods return `AsyncIterator`:
- Memory efficient
- Non-blocking I/O
- Composable with async/await

### 5. Structured Logging
All log messages structured:
- Uses `logger.info`, `logger.warning`, `logger.error`
- Includes context (filter params, record counts)
- No sensitive data in logs

## Files Created/Modified

### New Files
- `src/py_gdelt/sources/fetcher.py` (568 lines)
- `tests/test_sources_fetcher.py` (642 lines)
- `DATAFETCHER_IMPLEMENTATION.md` (this file)

### Modified Files
- `src/py_gdelt/sources/__init__.py` - Added DataFetcher exports

## Usage Examples

### Basic Usage
```python
from py_gdelt.sources import DataFetcher, FileSource
from py_gdelt.filters import EventFilter, DateRange
from datetime import date

async with FileSource() as file_source:
    fetcher = DataFetcher(file_source=file_source)

    filter_obj = EventFilter(
        date_range=DateRange(start=date(2024, 1, 1)),
        actor1_country="USA",
    )

    async for event in fetcher.fetch_events(filter_obj):
        print(event.global_event_id)
```

### With BigQuery Fallback
```python
from py_gdelt.sources import DataFetcher, FileSource, BigQuerySource
from py_gdelt.config import GDELTSettings

settings = GDELTSettings(
    bigquery_project="my-project",
    bigquery_credentials="/path/to/credentials.json",
)

async with FileSource(settings=settings) as file_source, \
           BigQuerySource(settings=settings) as bq_source:

    fetcher = DataFetcher(
        file_source=file_source,
        bigquery_source=bq_source,
        fallback_enabled=True,
        error_policy="warn",
    )

    async for event in fetcher.fetch_events(filter_obj):
        print(event)
```

### Direct BigQuery
```python
fetcher = DataFetcher(
    file_source=file_source,
    bigquery_source=bq_source,
)

async for event in fetcher.fetch_events(filter_obj, use_bigquery=True):
    print(event)
```

## Design Compliance

✅ Files are ALWAYS primary (free, no credentials)
✅ BigQuery is FALLBACK ONLY (on 429/error, if BQ credentials configured)
✅ Fallback logged at WARNING level (not silent)
✅ Configurable error policy (raise/warn/skip)
✅ Default error policy: warn and continue
✅ Dependency injection for testability
✅ Parser protocol for extensibility
✅ Structured logging for observability
✅ Async-first design for performance
✅ Full type coverage for safety

## Next Steps

1. Fix `_internal.py` dataclass ordering issue (separate task)
2. Add integration tests with real GDELT data
3. Add performance benchmarks (files vs BigQuery)
4. Add retry logic with exponential backoff
5. Add metrics collection (success/failure rates)

## Notes

- The implementation follows all Python best practices from the guidelines
- Uses modern Python 3.12+ features (type parameters, TYPE_CHECKING)
- No assertions in production code (only in tests)
- All errors logged with structured messages
- No mutable default arguments
- Absolute imports only
- Comprehensive type hints
- Google-style docstrings
