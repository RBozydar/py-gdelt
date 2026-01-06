# Quick Start

This guide will get you up and running with py-gdelt in 5 minutes.

## Your First Query

Let's query recent events from the US:

```python
import asyncio
from datetime import date, timedelta
from py_gdelt import GDELTClient
from py_gdelt.filters import DateRange, EventFilter

async def main():
    async with GDELTClient() as client:
        # Query yesterday's events
        yesterday = date.today() - timedelta(days=1)

        event_filter = EventFilter(
            date_range=DateRange(start=yesterday, end=yesterday),
            actor1_country="USA",
        )

        result = await client.events.query(event_filter)
        print(f"Found {len(result)} events")

        if result:
            event = result[0]
            print(f"First event: {event.global_event_id}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Search Articles

Use the DOC API to search for articles:

```python
from py_gdelt.filters import DocFilter

async with GDELTClient() as client:
    doc_filter = DocFilter(
        query="climate change",
        timespan="24h",
        max_results=10,
    )

    articles = await client.doc.query(doc_filter)

    for article in articles:
        print(f"{article.title}")
        print(f"  {article.url}")
```

## Geographic Search

Find locations mentioned in news:

```python
async with GDELTClient() as client:
    result = await client.geo.search(
        "earthquake",
        timespan="7d",
        max_points=20,
    )

    for point in result.points:
        print(f"{point.name}: {point.count} articles")
```

## Contextual Analysis

Analyze themes and entities:

```python
async with GDELTClient() as client:
    result = await client.context.analyze(
        "artificial intelligence",
        timespan="7d",
    )

    print(f"Articles analyzed: {result.article_count}")

    for theme in result.themes[:5]:
        print(f"  {theme.theme}: {theme.count}")
```

## Streaming Large Datasets

For memory efficiency, use streaming:

```python
async with GDELTClient() as client:
    yesterday = date.today() - timedelta(days=1)

    event_filter = EventFilter(
        date_range=DateRange(start=yesterday, end=yesterday),
    )

    count = 0
    async for event in client.events.stream(event_filter):
        count += 1
        # Process event without loading all into memory

    print(f"Processed {count} events")
```

## Synchronous Usage

For non-async code:

```python
with GDELTClient() as client:
    yesterday = date.today() - timedelta(days=1)

    event_filter = EventFilter(
        date_range=DateRange(start=yesterday, end=yesterday),
        actor1_country="USA",
    )

    result = client.events.query_sync(event_filter)
    print(f"Found {len(result)} events")
```

## Using Lookup Tables

Access CAMEO codes and other lookups:

```python
async with GDELTClient() as client:
    # CAMEO event codes
    cameo = client.lookups.cameo
    event_code = cameo.get("14")
    print(f"Code 14: {event_code.name}")  # "PROTEST"

    # Country conversions
    countries = client.lookups.countries
    iso3 = countries.fips_to_iso3("US")
    print(f"US -> {iso3}")  # "USA"
```

## Error Handling

Always handle errors gracefully:

```python
from py_gdelt.exceptions import APIError, DataError

async with GDELTClient() as client:
    try:
        result = await client.doc.query(doc_filter)
    except APIError as e:
        print(f"API error: {e}")
    except DataError as e:
        print(f"Data error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
```

## Next Steps

- [Configuration Guide](configuration.md) - Customize settings
- [User Guide](../user-guide/events.md) - Deep dive into features
- [Examples](../examples/index.md) - More complete examples
- [API Reference](../api/client.md) - Full API documentation
