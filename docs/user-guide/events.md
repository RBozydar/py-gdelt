# Events & Mentions

Query GDELT Events and Mentions data from files or BigQuery.

## Overview

Events are the core of GDELT - structured records of "who did what to whom, when, where, and how" extracted from global news articles.

## Basic Event Queries

```python
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

```python
event_filter = EventFilter(
    date_range=DateRange(start=date(2024, 1, 1)),
    actor1_country="USA",
    actor2_country="CHN",
)
```

### By Event Type

```python
event_filter = EventFilter(
    date_range=DateRange(start=date(2024, 1, 1)),
    event_code="14",  # Protest
)
```

### By Tone

```python
event_filter = EventFilter(
    date_range=DateRange(start=date(2024, 1, 1)),
    min_tone=-5.0,  # Negative events
    max_tone=0.0,
)
```

### By Location

```python
event_filter = EventFilter(
    date_range=DateRange(start=date(2024, 1, 1)),
    country_code="US",
)
```

## Streaming Events

For large datasets, use streaming:

```python
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

```python
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

```python
async with GDELTClient() as client:
    mentions = await client.mentions.query("123456789", event_filter)
```

## Analytics (BigQuery)

When BigQuery is configured, powerful SQL-level analytics are available directly on the events endpoint. These push computation to BigQuery rather than downloading raw rows.

### Time Series

```python
from py_gdelt import GDELTClient, TimeGranularity, EventMetric
from py_gdelt.filters import DateRange, EventFilter
from datetime import date

async with GDELTClient(settings=settings) as client:
    event_filter = EventFilter(
        date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 3, 31)),
        actor1_country="USA",
    )

    # Daily event counts with 7-day moving average
    result = await client.events.time_series(
        event_filter,
        granularity=TimeGranularity.DAY,
        metrics=[EventMetric.COUNT, EventMetric.AVG_GOLDSTEIN],
        moving_average_window=7,
    )

    for bucket in result.buckets:
        print(f"{bucket['bucket']}: {bucket['count']} events, MA7={bucket.get('count_ma7')}")
```

### Trend Detection

```python
    # Detect escalation/de-escalation trends
    trend = await client.events.trend(
        event_filter,
        metric=EventMetric.AVG_GOLDSTEIN,
        granularity=TimeGranularity.WEEK,
    )
    print(f"Direction: {trend.direction}, R²={trend.r_squared:.3f}")
```

### Country Comparison

```python
    # Compare event patterns between countries
    comparison = await client.events.compare(
        event_filter,
        compare_by="Actor1CountryCode",
        values=["USA", "CHN", "RUS"],
        metric=EventMetric.COUNT,
        granularity=TimeGranularity.WEEK,
    )
    for row in comparison.rows:
        print(f"{row['bucket']}: USA={row.get('USA_count')}, CHN={row.get('CHN_count')}")
```

### Extreme Events

```python
    # Find most extreme events by Goldstein scale
    extremes = await client.events.extremes(
        event_filter,
        criterion="GoldsteinScale",
        most_negative=5,
        most_positive=5,
    )
    print("Most negative:")
    for evt in extremes.most_negative:
        print(f"  {evt['GoldsteinScale']}: {evt.get('EventCode')}")
```

### Dyadic Analysis

```python
    # Analyze bilateral relationship between two actors
    dyad = await client.events.dyad_analysis(
        event_filter,
        actor_a="USA",
        actor_b="RUS",
        metrics=[EventMetric.COUNT, EventMetric.AVG_GOLDSTEIN],
    )
    print(f"USA→RUS: {len(dyad.a_to_b)} periods")
    print(f"RUS→USA: {len(dyad.b_to_a)} periods")
```

All analytics methods have synchronous wrappers (e.g., `time_series_sync()`).
See the [Analytics API Reference](../api/analytics.md) for full details.

## BigQuery Fallback

When file sources fail, automatically fallback to BigQuery:

```python
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
