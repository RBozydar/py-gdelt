# Basic Usage Examples

Common usage patterns for py-gdelt.

## Query Events

```
from datetime import date, timedelta
from py_gdelt import GDELTClient
from py_gdelt.filters import DateRange, EventFilter

async with GDELTClient() as client:
    yesterday = date.today() - timedelta(days=1)

    event_filter = EventFilter(
        date_range=DateRange(start=yesterday, end=yesterday),
        actor1_country="USA",
    )

    result = await client.events.query(event_filter)
    print(f"Found {len(result)} events")
```

## Search Articles

```
from py_gdelt.filters import DocFilter

async with GDELTClient() as client:
    doc_filter = DocFilter(
        query="climate change",
        timespan="24h",
        max_results=10,
    )

    articles = await client.doc.query(doc_filter)
```

## Geographic Search

```
async with GDELTClient() as client:
    result = await client.geo.search(
        "earthquake",
        timespan="7d",
        max_points=20,
    )
```

See complete examples in `examples/` directory.
