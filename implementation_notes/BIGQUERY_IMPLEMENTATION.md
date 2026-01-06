# BigQuery Source Implementation

## Overview

The `BigQuerySource` class provides secure, cost-aware access to GDELT's BigQuery public datasets as a fallback when REST APIs fail or rate limit. It implements a security-first design with parameterized queries, column allowlisting, and mandatory partition filters.

## Security Features

### 1. Parameterized Queries (SQL Injection Prevention)

**ALL** queries use BigQuery's parameterized query mechanism - NO string formatting or interpolation:

```python
# ✅ CORRECT: Parameterized query
query = """
    SELECT * FROM `gdelt-bq.gdeltv2.events_partitioned`
    WHERE Actor1CountryCode = @country
"""
job_config = bigquery.QueryJobConfig(
    query_parameters=[
        bigquery.ScalarQueryParameter("country", "STRING", "USA"),
    ]
)
```

```python
# ❌ WRONG: String formatting (vulnerable to SQL injection)
query = f"""
    SELECT * FROM events
    WHERE Actor1CountryCode = '{country}'
"""
```

This is enforced throughout the codebase:
- `_build_where_clause_for_events()`: Builds WHERE clauses with parameters
- `_build_where_clause_for_gkg()`: Builds WHERE clauses with parameters
- All column names are validated against allowlists before being used in SQL

### 2. Column Allowlisting

Every column name is validated against an explicit allowlist before being used in queries:

```python
ALLOWED_COLUMNS: Final[dict[TableType, frozenset[str]]] = {
    "events": frozenset({
        "GLOBALEVENTID",
        "Actor1CountryCode",
        "EventCode",
        # ... only allowed columns
    }),
}
```

This prevents:
- Unauthorized access to sensitive columns
- SQL injection via column names
- Typos causing expensive queries

### 3. Mandatory Partition Filters (Cost Control)

**ALL** queries include `_PARTITIONTIME` filters to prevent accidental full table scans:

```python
# Every query automatically includes:
WHERE _PARTITIONTIME >= @start_date
  AND _PARTITIONTIME <= @end_date
```

This ensures:
- Only relevant partitions are scanned
- Query costs are predictable and bounded
- No accidental multi-terabyte queries

### 4. Credential Security

Credentials are handled with extreme care:

```python
# ✅ Path validation prevents directory traversal
cred_path = _validate_credential_path(settings.bigquery_credentials)

# ✅ Credentials NEVER logged
logger.debug("Loading credentials from: %s", cred_path)  # Path only, not content

# ✅ Credentials NEVER in error messages
except GoogleCloudError as e:
    raise BigQueryError(f"Query failed: {e}") from e  # No credential info
```

Features:
- Path validation prevents directory traversal attacks
- Null byte detection
- Credentials never logged or exposed in errors
- Support for both ADC and explicit credential files

## Architecture

### Async Wrapper Pattern

BigQuery's Python client is synchronous, but we provide an async interface:

```python
async def _execute_query(self, query: str, parameters: list) -> AsyncIterator[dict]:
    # Get event loop
    loop = asyncio.get_event_loop()

    # Execute query in thread pool
    query_job = await loop.run_in_executor(
        None,
        lambda: client.query(query, job_config=job_config),
    )

    # Wait for completion
    await loop.run_in_executor(None, query_job.result)

    # Stream results
    for row in query_job:
        yield dict(row.items())
```

This allows:
- Non-blocking query execution
- Integration with async/await code
- Concurrent query execution when needed

### Query Building

Query building is separated into reusable functions:

```python
def _build_where_clause_for_events(
    filter_obj: EventFilter,
) -> tuple[str, list[bigquery.ScalarQueryParameter]]:
    """Build WHERE clause with parameterized queries."""
    conditions = []
    parameters = []

    # Mandatory partition filter
    conditions.append("_PARTITIONTIME >= @start_date")
    parameters.append(
        bigquery.ScalarQueryParameter("start_date", "TIMESTAMP", start_datetime)
    )

    # Optional filters
    if filter_obj.actor1_country:
        conditions.append("Actor1CountryCode = @actor1_country")
        parameters.append(
            bigquery.ScalarQueryParameter("actor1_country", "STRING", filter_obj.actor1_country)
        )

    return " AND ".join(conditions), parameters
```

Benefits:
- Testable in isolation
- Reusable across query methods
- Type-safe with Pydantic filters

## Usage Examples

### Basic Events Query

```python
from datetime import date
from py_gdelt.filters import DateRange, EventFilter
from py_gdelt.sources import BigQuerySource

async with BigQuerySource() as source:
    filter_obj = EventFilter(
        date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 7)),
        actor1_country="USA",
        actor2_country="CHN",
        min_tone=-5.0,
    )

    async for event in source.query_events(filter_obj, limit=100):
        print(event["GLOBALEVENTID"], event["EventCode"])
```

### GKG Query with Themes

```python
from py_gdelt.filters import GKGFilter

async with BigQuerySource() as source:
    filter_obj = GKGFilter(
        date_range=DateRange(start=date(2024, 1, 1)),
        themes=["ENV_CLIMATECHANGE"],
        country="USA",
    )

    async for record in source.query_gkg(filter_obj, limit=50):
        print(record["GKGRECORDID"], record["V2Themes"])
```

### Event Mentions Query

```python
async with BigQuerySource() as source:
    async for mention in source.query_mentions(
        global_event_id="123456789",
        date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 7)),
    ):
        print(mention["MentionSourceName"], mention["Confidence"])
```

## Configuration

### Using Application Default Credentials (Recommended)

```bash
# Authenticate with gcloud
gcloud auth application-default login

# Set project ID
export GDELT_BIGQUERY_PROJECT="your-project-id"
```

```python
from py_gdelt.sources import BigQuerySource

# Uses ADC automatically
async with BigQuerySource() as source:
    ...
```

### Using Explicit Credentials

```bash
# Set credentials path and project
export GDELT_BIGQUERY_PROJECT="your-project-id"
export GDELT_BIGQUERY_CREDENTIALS="/path/to/credentials.json"
```

```python
from py_gdelt.config import GDELTSettings
from py_gdelt.sources import BigQuerySource

settings = GDELTSettings(
    bigquery_project="your-project-id",
    bigquery_credentials="/path/to/credentials.json",
)

async with BigQuerySource(settings=settings) as source:
    ...
```

## Cost Considerations

### Query Costs

BigQuery charges based on data processed:
- **Events table**: ~50GB per day (partitioned)
- **GKG table**: ~200GB per day (partitioned)
- **Mentions table**: ~100GB per day (partitioned)

**Important**: Always use date filters to limit data scanned!

```python
# ✅ GOOD: Only scans 7 days of data
filter_obj = EventFilter(
    date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 7)),
)

# ❌ EXPENSIVE: Could scan entire table
filter_obj = EventFilter(
    date_range=DateRange(start=date(2015, 1, 1), end=date(2024, 1, 1)),
)
```

### Limiting Results

Use the `limit` parameter to reduce data transfer:

```python
# Only process first 100 rows
async for event in source.query_events(filter_obj, limit=100):
    ...
```

### Column Selection

Only select columns you need:

```python
# ✅ GOOD: Only 3 columns
async for event in source.query_events(
    filter_obj,
    columns=["GLOBALEVENTID", "EventCode", "AvgTone"],
):
    ...

# ❌ EXPENSIVE: All 60+ columns
async for event in source.query_events(filter_obj):  # Defaults to all columns
    ...
```

## Testing

The implementation includes comprehensive tests covering:

1. **Credential Validation**: Path validation, null bytes, traversal attempts
2. **Column Validation**: Allowlist enforcement, SQL injection prevention
3. **Query Building**: Parameterization, filter combinations
4. **Async Execution**: Context managers, error handling
5. **Security Features**: No string formatting, mandatory filters

Run tests:

```bash
uv run pytest tests/test_sources_bigquery.py -v
```

All tests use mocks - no actual BigQuery calls are made during testing.

## Error Handling

The implementation provides clear error messages while protecting sensitive information:

```python
try:
    async for event in source.query_events(filter_obj):
        ...
except ConfigurationError as e:
    # Missing or invalid credentials
    print(f"Configuration error: {e}")
except BigQueryError as e:
    # Query execution failed
    print(f"BigQuery error: {e}")
except Exception as e:
    # Unexpected error
    print(f"Unexpected error: {e}")
```

Common errors:
- `ConfigurationError`: Credentials not configured or invalid
- `BigQueryError`: Query failed, quota exceeded, authentication failed
- `ValidationError`: Invalid filter parameters (caught by Pydantic)

## Performance Tips

1. **Use specific date ranges**: Smaller date ranges = less data scanned
2. **Limit results**: Use `limit` parameter for exploration
3. **Select specific columns**: Don't fetch columns you don't need
4. **Batch processing**: Process results in batches if memory is limited
5. **Cache results**: Store frequently used queries locally

## Future Enhancements

Potential improvements for future versions:

1. **Query caching**: Cache query results to reduce costs
2. **Batch queries**: Execute multiple queries in parallel
3. **Result pagination**: Better handling of large result sets
4. **Cost estimation**: Estimate query costs before execution
5. **NGrams support**: Add support for NGrams 3.0 tables
6. **Dry-run mode**: Estimate costs without executing queries

## References

- [GDELT BigQuery Tables](https://blog.gdeltproject.org/google-bigquery-gkg-2-0-sample-queries/)
- [BigQuery Parameterized Queries](https://cloud.google.com/bigquery/docs/parameterized-queries)
- [BigQuery Best Practices](https://cloud.google.com/bigquery/docs/best-practices-performance-overview)
- [Authentication Options](https://cloud.google.com/docs/authentication/application-default-credentials)
