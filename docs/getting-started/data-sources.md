# Data Sources & Access Matrix

GDELT provides multiple data sources accessible through different methods. Understanding which source to use for your specific needs is crucial for efficient data retrieval.

## Complete Data Source Matrix

| Data Type | API | BigQuery | Raw Files | Time Constraint | Fallback Available |
|-----------|-----|----------|-----------|-----------------|-------------------|
| Articles (fulltext) | DOC 2.0 | - | - | Rolling 3 months | No equivalent |
| Article geo heatmaps | GEO 2.0 | - | - | Rolling 7 days | No equivalent |
| Sentence-level context | Context 2.0 | - | - | Rolling 72 hours | No equivalent |
| TV captions | TV 2.0 | - | - | July 2009+ (full) | No equivalent |
| TV visual/AI | TV AI 2.0 | - | - | 2010+, limited | No equivalent |
| Events v2 | - | Yes | Yes | Feb 2015+ | Files <-> BigQuery |
| Events v1 | - | Yes | Yes | 1979 - Feb 2015 | Files <-> BigQuery |
| Mentions | - | Yes | Yes | Feb 2015+ (v2 only) | Files <-> BigQuery |
| GKG v2 | - | Yes | Yes | Feb 2015+ | Files <-> BigQuery |
| GKG v1 | - | Yes | Yes | 2013 - Feb 2015 | Files <-> BigQuery |
| Web NGrams 3.0 | - | Yes | Yes | Jan 2020+ | Files <-> BigQuery |

## Historical Fulltext Search Strategy

Choosing the right source based on time range:

| Need | <3 months | 3mo - 5yr | >5yr |
|------|-----------|-----------|------|
| Fulltext search | DOC API | NGrams 3.0 | Not available |
| Entity/theme search | GKG | GKG | GKG (v1 to 2013) |
| Event tracking | Events | Events | Events (v1 to 1979) |

## API Endpoints Reference

### DOC 2.0 API

- **Endpoint**: `https://api.gdeltproject.org/api/v2/doc/doc`
- **Purpose**: Full-text article search
- **Time Window**: Rolling 3 months
- **Max Records**: 250
- **Output Modes**: artlist, timelinevol, timelinevolraw, timelinetone, timelinelang, timelinesourcecountry, imagecollage, tonechart

### GEO 2.0 API

- **Endpoint**: `https://api.gdeltproject.org/api/v2/geo/geo`
- **Purpose**: Geographic visualizations
- **Time Window**: Rolling 7 days
- **Max Points**: 1,000-25,000 (mode dependent)

### Context 2.0 API

- **Endpoint**: `https://api.gdeltproject.org/api/v2/context/context`
- **Purpose**: Sentence-level search (all terms in same sentence)
- **Time Window**: Rolling 72 hours
- **Max Records**: 200

### TV 2.0 API

- **Endpoint**: `https://api.gdeltproject.org/api/v2/tv/tv`
- **Purpose**: Television closed caption search
- **Time Window**: July 2009+ (full archive)
- **Max Records**: 3,000

### TV AI 2.0 API

- **Endpoint**: `https://api.gdeltproject.org/api/v2/tvai/tvai`
- **Purpose**: Visual television search (AI-powered)
- **Time Window**: 2010+ (limited channels)

### GKG GeoJSON API (v1.0 Legacy)

- **Endpoint**: `https://api.gdeltproject.org/api/v1/gkg_geojson`
- **Purpose**: GeoJSON by GKG theme/person/org
- **Note**: Uses uppercase parameters

## BigQuery Tables

| Table | Size | Project |
|-------|------|---------|
| `gdelt-bq.gdeltv2.events` | ~63GB | gdelt-bq |
| `gdelt-bq.gdeltv2.events_partitioned` | ~63GB | gdelt-bq |
| `gdelt-bq.gdeltv2.eventmentions` | ~104GB | gdelt-bq |
| `gdelt-bq.gdeltv2.gkg` | ~3.6TB | gdelt-bq |
| `gdelt-bq.gdeltv2.gkg_partitioned` | ~3.6TB | gdelt-bq |
| `gdelt-bq.gdeltv2.webngrams` | Variable | gdelt-bq |

!!! warning "BigQuery Cost"
    Always use partitioned tables with date filters to avoid full table scans:

    ```sql
    -- DANGEROUS: Scans entire 3.6TB GKG table (~$18)
    SELECT * FROM `gdelt-bq.gdeltv2.gkg` LIMIT 100

    -- SAFE: Use partitioned table with filter
    SELECT * FROM `gdelt-bq.gdeltv2.gkg_partitioned`
    WHERE _PARTITIONTIME >= '2024-01-01'
      AND _PARTITIONTIME < '2024-01-02'
    LIMIT 100
    ```

## Raw File Access

### Master File Lists

- English: `http://data.gdeltproject.org/gdeltv2/masterfilelist.txt`
- Translated: `http://data.gdeltproject.org/gdeltv2/masterfilelist-translation.txt`
- Last update: `http://data.gdeltproject.org/gdeltv2/lastupdate.txt`

### URL Patterns (v2)

```
http://data.gdeltproject.org/gdeltv2/YYYYMMDDHHMMSS.export.CSV.zip
http://data.gdeltproject.org/gdeltv2/YYYYMMDDHHMMSS.mentions.CSV.zip
http://data.gdeltproject.org/gdeltv2/YYYYMMDDHHMMSS.gkg.csv.zip
```

### NGrams 3.0

```
http://data.gdeltproject.org/gdeltv3/webngrams/YYYYMMDDHHMMSS.webngrams.json.gz
```

### Update Frequency

Files are updated every 15 minutes at :00, :15, :30, and :45 past the hour.

## How gdelt-py Handles Sources

The library provides automatic source selection:

```python
# Auto mode (default) - tries files first, falls back to BigQuery
events = await client.events.query(filter)

# Explicit source selection
events = await client.events.query(filter, source="bigquery")
events = await client.events.query(filter, source="files")
```

For API-only endpoints (DOC, GEO, Context, TV), there are no fallback options - the library will return an error if the API is unavailable.
