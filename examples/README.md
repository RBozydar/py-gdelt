# py-gdelt Examples

This directory contains example code demonstrating how to use the py-gdelt library.

## EventsEndpoint Examples

### Basic Usage

```python
from datetime import date
from py_gdelt.endpoints import EventsEndpoint
from py_gdelt.filters import DateRange, EventFilter
from py_gdelt.sources import FileSource

async with FileSource() as file_source:
    endpoint = EventsEndpoint(file_source=file_source)

    filter_obj = EventFilter(
        date_range=DateRange(start=date(2024, 1, 1)),
        actor1_country="USA",
    )

    result = await endpoint.query(filter_obj)
    print(f"Found {len(result)} events")
```

### Streaming for Large Datasets

```python
async with FileSource() as file_source:
    endpoint = EventsEndpoint(file_source=file_source)

    filter_obj = EventFilter(
        date_range=DateRange(
            start=date(2024, 1, 1),
            end=date(2024, 1, 7),
        ),
    )

    async for event in endpoint.stream(filter_obj):
        process(event)
```

### Deduplication

```python
from py_gdelt.utils.dedup import DedupeStrategy

result = await endpoint.query(
    filter_obj,
    deduplicate=True,
    dedupe_strategy=DedupeStrategy.URL_DATE_LOCATION,
)
```

## Running Examples

```bash
# Run the events endpoint example
python examples/events_endpoint_example.py
```

## Available Examples

- `events_endpoint_example.py` - Comprehensive EventsEndpoint usage examples
