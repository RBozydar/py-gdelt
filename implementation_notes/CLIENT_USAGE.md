# GDELTClient Usage Guide

The `GDELTClient` class is the main entry point for accessing all GDELT data sources. It provides a unified interface to:

- **Events, Mentions, GKG** - From files or BigQuery with automatic fallback
- **NGrams** - Word and phrase tracking (files only)
- **REST APIs** - DOC, GEO, Context, TV, TVAI endpoints
- **Lookup Tables** - CAMEO codes, GKG themes, country codes

## Quick Start

### Basic Usage

```python
from py_gdelt import GDELTClient
from py_gdelt.filters import EventFilter, DateRange
from datetime import date

async with GDELTClient() as client:
    # Query events
    filter_obj = EventFilter(
        date_range=DateRange(start=date(2024, 1, 1)),
        actor1_country="USA"
    )
    events = await client.events.query(filter_obj)

    # Search articles
    articles = await client.doc.search("climate change")

    # Access lookups
    event_name = client.lookups.cameo["14"]  # "PROTEST"
```

### Synchronous Usage

The client also supports synchronous usage:

```python
with GDELTClient() as client:
    events = client.events.query_sync(filter_obj)
```

## Configuration

### Default Configuration

```python
# Uses defaults + environment variables
async with GDELTClient() as client:
    pass
```

### Custom Settings

```python
from py_gdelt import GDELTSettings

settings = GDELTSettings(
    timeout=60,
    max_retries=5,
    max_concurrent_downloads=10,
    fallback_to_bigquery=True,
    validate_codes=True
)

async with GDELTClient(settings=settings) as client:
    pass
```

### TOML Configuration File

```python
from pathlib import Path

# Create gdelt.toml:
# [gdelt]
# timeout = 60
# max_retries = 5
# bigquery_project = "my-project"
# bigquery_credentials = "/path/to/credentials.json"

async with GDELTClient(config_path=Path("gdelt.toml")) as client:
    pass
```

### Environment Variables

All settings can be configured via environment variables with `GDELT_` prefix:

```bash
export GDELT_TIMEOUT=60
export GDELT_MAX_RETRIES=5
export GDELT_BIGQUERY_PROJECT="my-project"
export GDELT_BIGQUERY_CREDENTIALS="/path/to/credentials.json"
```

Priority order: `settings` parameter > environment variables > TOML config > defaults

## Accessing Endpoints

### File-Based Endpoints (with BigQuery Fallback)

#### Events Endpoint

```python
async with GDELTClient() as client:
    from py_gdelt.filters import EventFilter, DateRange
    from datetime import date

    filter_obj = EventFilter(
        date_range=DateRange(start=date(2024, 1, 1)),
        actor1_country="USA",
        event_code="14"  # Protest events
    )

    # Batch query
    events = await client.events.query(filter_obj)

    # Streaming query (memory-efficient)
    async for event in client.events.stream(filter_obj):
        print(event.global_event_id)
```

#### Mentions Endpoint

```python
async with GDELTClient() as client:
    # Query all mentions of a specific event
    mentions = await client.mentions.query(
        global_event_id="123456789",
        filter_obj=filter_obj
    )
```

#### GKG Endpoint

```python
async with GDELTClient() as client:
    from py_gdelt.filters import GKGFilter

    filter_obj = GKGFilter(
        date_range=DateRange(start=date(2024, 1, 1)),
        themes=["ENV_CLIMATECHANGE"],
        country="USA"
    )

    records = await client.gkg.query(filter_obj)
```

#### NGrams Endpoint

```python
async with GDELTClient() as client:
    from py_gdelt.filters import NGramsFilter

    filter_obj = NGramsFilter(
        date_range=DateRange(start=date(2024, 1, 1)),
        language="en",
        ngram="climate"
    )

    records = await client.ngrams.query(filter_obj)
```

### REST API Endpoints

#### DOC API (Article Search)

```python
async with GDELTClient() as client:
    from py_gdelt.filters import DocFilter

    # Simple search
    articles = await client.doc.search("climate change", max_results=100)

    # Advanced search with filter
    filter_obj = DocFilter(
        query="elections",
        timespan="7d",
        source_country="US",
        sort_by="relevance"
    )
    articles = await client.doc.query(filter_obj)

    # Timeline analysis
    timeline = await client.doc.timeline("protests", timespan="30d")
```

#### GEO API (Geographic Data)

```python
async with GDELTClient() as client:
    # Find locations mentioned in articles
    result = await client.geo.search("earthquake", max_points=100)

    for point in result.points:
        print(f"{point.name}: {point.count} articles at ({point.lat}, {point.lon})")
```

#### Context API (Contextual Analysis)

```python
async with GDELTClient() as client:
    # Get contextual analysis of a topic
    result = await client.context.analyze("climate change")

    print(f"Article count: {result.article_count}")
    print(f"Top themes: {result.themes[:5]}")
    print(f"Top entities: {result.entities[:5]}")
    print(f"Average tone: {result.tone.average_tone}")
```

#### TV API (Television News)

```python
async with GDELTClient() as client:
    # Search TV transcripts
    clips = await client.tv.search("climate change", station="CNN")

    # Get timeline of mentions
    timeline = await client.tv.timeline("election", timespan="30d")

    # Compare coverage across stations
    chart = await client.tv.station_chart("healthcare")
```

#### TVAI API (AI-Enhanced TV Analysis)

```python
async with GDELTClient() as client:
    # AI-enhanced analysis
    result = await client.tv_ai.analyze("election coverage")
```

## Lookup Tables

The client provides access to all GDELT lookup tables:

### CAMEO Event Codes

```python
async with GDELTClient() as client:
    cameo = client.lookups.cameo

    # Lookup by code
    event_name = cameo["14"]  # "PROTEST"

    # Validate code
    client.lookups.validate_cameo("14")  # Raises if invalid
```

### GKG Themes

```python
async with GDELTClient() as client:
    themes = client.lookups.themes

    # Get theme category
    category = themes.get_category("ENV_CLIMATECHANGE")  # "Environment"

    # Validate theme
    client.lookups.validate_theme("ENV_CLIMATECHANGE")
```

### Country Codes

```python
async with GDELTClient() as client:
    countries = client.lookups.countries

    # Convert FIPS to ISO
    iso_code = countries.fips_to_iso("US")  # "USA"

    # Convert ISO to FIPS
    fips_code = countries.iso_to_fips("USA")  # "US"

    # Validate country code
    client.lookups.validate_country("US")
```

## Advanced Features

### Streaming Large Datasets

For memory-efficient processing of large datasets:

```python
async with GDELTClient() as client:
    filter_obj = EventFilter(
        date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 31))
    )

    # Stream instead of loading all into memory
    count = 0
    async for event in client.events.stream(filter_obj):
        count += 1
        process(event)

    print(f"Processed {count} events")
```

### Deduplication

Events and mentions can be deduplicated:

```python
async with GDELTClient() as client:
    # Deduplicate by GlobalEventID (default)
    events = await client.events.query(
        filter_obj,
        deduplicate=True
    )

    # Custom deduplication strategy
    from py_gdelt.utils.dedup import DedupeStrategy

    events = await client.events.query(
        filter_obj,
        deduplicate=True,
        dedupe_strategy=DedupeStrategy.KEEP_FIRST
    )
```

### BigQuery Fallback

When BigQuery credentials are configured, the client automatically falls back to BigQuery if file downloads fail or are rate-limited:

```python
settings = GDELTSettings(
    bigquery_project="my-project",
    bigquery_credentials="/path/to/credentials.json",
    fallback_to_bigquery=True  # Default
)

async with GDELTClient(settings=settings) as client:
    # Automatically falls back to BigQuery on error
    events = await client.events.query(filter_obj)
```

You can also force BigQuery usage:

```python
events = await client.events.query(filter_obj, use_bigquery=True)
```

### Dependency Injection (Testing)

For testing, you can inject HTTP client and sources:

```python
import httpx

async with httpx.AsyncClient() as http_client:
    async with GDELTClient(http_client=http_client) as client:
        # Uses injected client instead of creating its own
        # Client will NOT close the HTTP client on exit
        pass
```

## Resource Management

The client manages all resources automatically when used as a context manager:

- HTTP client lifecycle
- File source connections
- BigQuery client (if configured)
- Cache management

**Always use the client as a context manager** to ensure proper cleanup:

```python
# Good
async with GDELTClient() as client:
    events = await client.events.query(filter_obj)

# Bad - resources may leak
client = GDELTClient()
events = await client.events.query(filter_obj)  # RuntimeError!
```

## Error Handling

All endpoints raise specific exceptions from `py_gdelt.exceptions`:

```python
from py_gdelt.exceptions import (
    RateLimitError,
    APIUnavailableError,
    BigQueryError,
    ConfigurationError
)

async with GDELTClient() as client:
    try:
        events = await client.events.query(filter_obj)
    except RateLimitError as e:
        print(f"Rate limited: {e}")
    except APIUnavailableError as e:
        print(f"API unavailable: {e}")
    except ConfigurationError as e:
        print(f"Configuration error: {e}")
```

## Complete Example

```python
from py_gdelt import GDELTClient, GDELTSettings
from py_gdelt.filters import EventFilter, DateRange, DocFilter
from datetime import date, timedelta
from pathlib import Path

async def analyze_recent_events():
    # Configure client
    settings = GDELTSettings(
        config_path=Path("gdelt.toml"),
        timeout=60,
        max_retries=5
    )

    async with GDELTClient(settings=settings) as client:
        # Query recent protest events
        yesterday = date.today() - timedelta(days=1)
        event_filter = EventFilter(
            date_range=DateRange(start=yesterday),
            event_code="14",  # Protests
            actor1_country="USA"
        )

        # Get events
        events = await client.events.query(event_filter, deduplicate=True)
        print(f"Found {len(events)} protest events")

        # Find related articles
        doc_filter = DocFilter(
            query="protest",
            timespan="24h",
            source_country="US"
        )
        articles = await client.doc.query(doc_filter)
        print(f"Found {len(articles)} related articles")

        # Get geographic distribution
        geo_result = await client.geo.search("protest", max_points=50)
        print(f"Protests mentioned in {len(geo_result.points)} locations")

        # Lookup event details
        for event in events[:5]:
            event_type = client.lookups.cameo[event.event_code]
            print(f"  {event.global_event_id}: {event_type}")

# Run the analysis
import asyncio
asyncio.run(analyze_recent_events())
```

## See Also

- [Events Endpoint Documentation](./EVENTS_ENDPOINT_SUMMARY.md)
- [Mentions Endpoint Documentation](./MENTIONS_ENDPOINT_IMPLEMENTATION.md)
- [NGrams Implementation](./NGRAMS_IMPLEMENTATION.md)
- [Configuration Guide](./src/py_gdelt/config.py)
- [Examples Directory](./examples/)
