# Events & Mentions

Query GDELT Events and Mentions data from files or BigQuery.

## Overview

Events are the core of GDELT - structured records of "who did what to whom, when, where, and how" extracted from global news articles.

## Basic Event Queries

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

    events = await client.events.query(event_filter)
    print(f"Found {len(events)} events")
```

## Event Model

Events contain:

- **global_event_id**: Unique identifier
- **date**: Event date
- **actor1**, **actor2**: Participants (country, name, codes)
- **event_code**: CAMEO event type code
- **goldstein_scale**: Conflict/cooperation score (-10 to +10)
- **avg_tone**: Sentiment (-100 to +100)
- **action_geo**: Location information
- **source_url**: Article URL

## Filtering Options

### By Actors

```
event_filter = EventFilter(
    date_range=DateRange(start=date(2024, 1, 1)),
    actor1_country="USA",
    actor2_country="CHN",
)
```

### By Event Type

```
event_filter = EventFilter(
    date_range=DateRange(start=date(2024, 1, 1)),
    event_code="14",  # Protest
)
```

### By Tone

```
event_filter = EventFilter(
    date_range=DateRange(start=date(2024, 1, 1)),
    min_tone=-5.0,  # Negative events
    max_tone=0.0,
)
```

### By Location

```
event_filter = EventFilter(
    date_range=DateRange(start=date(2024, 1, 1)),
    country_code="US",
)
```

## Streaming Events

For large datasets, use streaming:

```
async with GDELTClient() as client:
    event_filter = EventFilter(
        date_range=DateRange(
            start=date(2024, 1, 1),
            end=date(2024, 1, 7),
        ),
    )

    async for event in client.events.stream(event_filter):
        process(event)  # Process one at a time
```

## Deduplication

GDELT often contains duplicate events. Use deduplication:

```
from py_gdelt.utils.dedup import DedupeStrategy

result = await client.events.query(
    event_filter,
    deduplicate=True,
    dedupe_strategy=DedupeStrategy.URL_DATE_LOCATION,
)
```

Available strategies:

- `URL_ONLY` - By source URL
- `URL_DATE` - By URL and date
- `URL_DATE_LOCATION` - By URL, date, and location
- `ACTOR_PAIR` - By actor pair
- `FULL` - By all fields

## Mentions

Mentions track article citations of events:

```
async with GDELTClient() as client:
    mentions = await client.mentions.query("123456789", event_filter)
```

## BigQuery Fallback

When file sources fail, automatically fallback to BigQuery:

```
settings = GDELTSettings(
    fallback_to_bigquery=True,
    bigquery_project="my-project",
)

async with GDELTClient(settings=settings) as client:
    # Automatically uses BigQuery if files unavailable
    events = await client.events.query(event_filter)
```

## Best Practices

- Use streaming for >1000 events
- Enable deduplication for cleaner data
- Use specific filters to reduce data volume
- Handle empty results gracefully
- Set appropriate date ranges (files available for 2015+)
