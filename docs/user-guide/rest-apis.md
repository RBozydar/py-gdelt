# REST APIs

GDELT provides several REST APIs for searching and analyzing global news.

## DOC 2.0 API - Article Search

Search for news articles:

```python
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

```python
timeline = await client.doc.timeline(
    query="artificial intelligence",
    timespan="7d",
)

for point in timeline.points:
    print(f"{point.date}: {point.count} articles")
```

## GEO 2.0 API - Geographic Search

Find geographic locations mentioned in news:

```python
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

```python
# Europe bounding box
europe_bbox = (35.0, -10.0, 70.0, 40.0)

result = await client.geo.search(
    "protests",
    timespan="7d",
    bounding_box=europe_bbox,
)
```

### GeoJSON Output

```python
geojson = await client.geo.to_geojson(
    "climate protest",
    timespan="30d",
)

# Use with folium, leaflet, etc.
```

## Context 2.0 API - Contextual Analysis

Analyze themes, entities, and sentiment:

```python
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

```python
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

```python
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

```python
timeline = await client.tv.timeline(
    "election",
    timespan="7d",
)
```

### Station Comparison

```python
chart = await client.tv.station_chart(
    "immigration",
    timespan="7d",
)

for station in chart.stations:
    print(f"{station.station}: {station.count} ({station.percentage}%)")
```

## TVAI API - AI-Enhanced TV Search

Use AI for better TV transcript search:

```python
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

GDELT APIs may rate limit. Handle gracefully:

```python
from py_gdelt.exceptions import APIError

try:
    result = await client.doc.query(doc_filter)
except APIError as e:
    if "rate limit" in str(e).lower():
        # Wait and retry
        await asyncio.sleep(60)
```

## Best Practices

- Use appropriate timespans (shorter = faster)
- Limit result counts to what you need
- Handle empty results gracefully
- Respect rate limits
- Cache results when appropriate
