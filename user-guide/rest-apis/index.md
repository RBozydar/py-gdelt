# REST APIs

GDELT provides several REST APIs for searching and analyzing global news.

## DOC 2.0 API - Article Search

Search for news articles:

```
from py_gdelt.filters import DocFilter

async with GDELTClient() as client:
    doc_filter = DocFilter(
        query="climate change",
        timespan="24h",
        max_results=100,
        sort_by="relevance",
    )

    articles = await client.doc.query(doc_filter)

    for article in articles:
        print(f"{article.title}")
        print(f"  {article.url}")
```

### Timeline Analysis

```
timeline = await client.doc.timeline(
    query="artificial intelligence",
    timespan="7d",
)

for point in timeline.points:
    print(f"{point.date}: {point.count} articles")
```

## GEO 2.0 API - Geographic Search

Find geographic locations mentioned in news:

```
async with GDELTClient() as client:
    result = await client.geo.search(
        "earthquake",
        timespan="7d",
        max_points=50,
    )

    for point in result.points:
        print(f"{point.name}: {point.count} articles")
        print(f"  ({point.lat}, {point.lon})")
```

### Bounding Box Filtering

```
# Europe bounding box
europe_bbox = (35.0, -10.0, 70.0, 40.0)

result = await client.geo.search(
    "protests",
    timespan="7d",
    bounding_box=europe_bbox,
)
```

### GeoJSON Output

```
geojson = await client.geo.to_geojson(
    "climate protest",
    timespan="30d",
)

# Use with folium, leaflet, etc.
```

## Context 2.0 API - Contextual Analysis

Analyze themes, entities, and sentiment:

```
async with GDELTClient() as client:
    result = await client.context.analyze(
        "technology",
        timespan="7d",
    )

    print(f"Articles: {result.article_count}")

    # Top themes
    for theme in result.themes[:10]:
        print(f"  {theme.theme}: {theme.count}")

    # Top entities
    for entity in result.entities[:10]:
        print(f"  {entity.name} ({entity.entity_type}): {entity.count}")

    # Sentiment
    if result.tone:
        print(f"Average tone: {result.tone.average_tone}")
```

### Entity Filtering

```
# Get people mentioned
people = await client.context.get_entities(
    "election",
    entity_type="PERSON",
    limit=20,
)

# Get organizations
orgs = await client.context.get_entities(
    "economy",
    entity_type="ORG",
    limit=20,
)
```

## TV API - Television News

Search TV transcripts:

```
async with GDELTClient() as client:
    clips = await client.tv.search(
        "healthcare",
        timespan="24h",
        station="CNN",
        max_results=20,
    )

    for clip in clips:
        print(f"{clip.station} - {clip.show_name}")
        print(f"  {clip.snippet}")
```

### TV Timeline

```
timeline = await client.tv.timeline(
    "election",
    timespan="7d",
)
```

### Station Comparison

```
chart = await client.tv.station_chart(
    "immigration",
    timespan="7d",
)

for station in chart.stations:
    print(f"{station.station}: {station.count} ({station.percentage}%)")
```

## TVAI API - AI-Enhanced TV Search

Use AI for better TV transcript search:

```
clips = await client.tv_ai.search(
    "impact of artificial intelligence on employment",
    timespan="7d",
    max_results=10,
)
```

## Timespan Options

All REST APIs support these timespans:

- `"15min"` - Last 15 minutes
- `"30min"` - Last 30 minutes
- `"1h"` - Last hour
- `"6h"` - Last 6 hours
- `"24h"` - Last 24 hours
- `"7d"` - Last 7 days
- `"30d"` - Last 30 days

## Rate Limiting

GDELT APIs may return `429 Too Many Requests`. py-gdelt parses `Retry-After` headers and opens an endpoint-local circuit so repeated calls through the same endpoint instance fail fast instead of continuing to hit GDELT.

The circuit is local to each endpoint object. It uses the capped `Retry-After` value when GDELT provides one, otherwise it uses `rate_limit_circuit_seconds`. Later local `RateLimitError.retry_after` values report the remaining circuit time, so they count down as the circuit expires. Successful requests reset transient-error tracking, but an open rate-limit circuit expires by time instead of being cleared early.

Circuit state is not protected by locks. For strict isolation across concurrent workers, threads, or separate retry policies, create separate `GDELTClient` instances instead of sharing the same endpoint object.

```
import asyncio

from py_gdelt.exceptions import RateLimitError

try:
    result = await client.doc.query(doc_filter)
except RateLimitError as e:
    if e.retry_after is not None:
        await asyncio.sleep(e.retry_after)
```

## Best Practices

- Use appropriate timespans (shorter = faster)
- Limit result counts to what you need
- Handle empty results gracefully
- Respect rate limits
- Cache results when appropriate
