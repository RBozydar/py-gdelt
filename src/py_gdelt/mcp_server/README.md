# GDELT MCP Server

MCP server exposing the py-gdelt library for geopolitical research agents.

## Overview

This MCP server provides structured access to GDELT (Global Database of Events, Language, and Tone) data sources through 6 specialized tools. It's designed for AI agents conducting geopolitical analysis, conflict monitoring, and news research.

All tools use **streaming aggregation** to process large datasets with O(1) memory, making them safe for queries spanning weeks or months of data.

## Installation

The MCP server is included in the py-gdelt package:

```bash
pip install py-gdelt
# or with uv
uv pip install py-gdelt
```

## Running the Server

```bash
# From the py-gdelt package directory
python -m py_gdelt.mcp_server.server
```

## Claude Desktop / Claude Code Configuration

Add the following to your MCP server configuration:

```json
{
  "mcpServers": {
    "gdelt": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/py-gdelt", "python", "-m", "py_gdelt.mcp_server.server"]
    }
  }
}
```

Or if py-gdelt is installed in your environment:

```json
{
  "mcpServers": {
    "gdelt": {
      "command": "python",
      "args": ["-m", "py_gdelt.mcp_server.server"]
    }
  }
}
```

## Available Tools

### 1. `gdelt_events`
Query CAMEO-coded events from GDELT Events database with streaming aggregation.

**Parameters:**
- `actor1_country` (str, optional): ISO3 country code for actor 1 (e.g., "USA", "RUS", "CHN")
- `actor2_country` (str, optional): ISO3 country code for actor 2
- `event_type` (str, default="all"): Filter by event type - "conflict", "cooperation", or "all"
- `days_back` (int, default=7): Number of days to look back (max: 365)
- `min_goldstein` (float, optional): Minimum Goldstein scale (-10 to 10, negative=conflict)
- `max_goldstein` (float, optional): Maximum Goldstein scale (-10 to 10, positive=cooperation)

**Returns:** Aggregated event summary containing:
- `summary`: total_events, date_range, goldstein_mean, goldstein_std
- `goldstein_distribution`: counts by conflict/cooperation category (highly_conflictual, moderately_conflictual, mildly_conflictual, cooperative)
- `events_by_type`: top 10 event types with code, name, count, and percentage
- `events_by_day`: daily event counts
- `top_actor1_countries`: top 10 actor1 countries by event count
- `top_actor2_countries`: top 10 actor2 countries by event count
- `sample_events`: 10 sample events with extreme Goldstein scores (5 most negative, 5 most positive)

**Example Request:**
```json
{
  "actor1_country": "USA",
  "actor2_country": "CHN",
  "event_type": "conflict",
  "days_back": 30,
  "max_goldstein": -2.0
}
```

**Example Response:**
```json
{
  "summary": {
    "total_events": 1847,
    "date_range": "2026-01-10 to 2026-01-17",
    "goldstein_mean": -2.3,
    "goldstein_std": 3.1
  },
  "goldstein_distribution": {
    "highly_conflictual": 234,
    "moderately_conflictual": 445,
    "mildly_conflictual": 312,
    "cooperative": 856
  },
  "events_by_type": [
    {"code": "14", "name": "PROTEST", "count": 523, "pct": 28.3},
    {"code": "17", "name": "COERCE", "count": 312, "pct": 16.9}
  ],
  "events_by_day": [
    {"date": "2026-01-15", "count": 234},
    {"date": "2026-01-16", "count": 289}
  ],
  "top_actor1_countries": [
    {"name": "USA", "count": 567},
    {"name": "CHN", "count": 234}
  ],
  "top_actor2_countries": [],
  "sample_events": [
    {
      "global_event_id": 123456789,
      "date": "2026-01-15",
      "actor1_country": "USA",
      "actor1_name": "UNITED STATES",
      "actor2_country": "CHN",
      "actor2_name": "CHINA",
      "event_code": "17",
      "event_name": "COERCE",
      "goldstein_scale": -4.0,
      "avg_tone": -2.5,
      "source_url": "https://..."
    }
  ]
}
```

---

### 2. `gdelt_gkg`
Query Global Knowledge Graph for entities and themes with streaming aggregation.

**Parameters:**
- `query` (str, optional): Text query to filter records (searches themes, persons, organizations)
- `themes` (list[str], optional): List of GKG theme codes (e.g., ["ENV_CLIMATECHANGE", "LEADER"])
- `days_back` (int, default=7): Number of days to look back (max: 365)

**Returns:** Aggregated summary with:
- Total record count
- Top 10 themes with counts
- Top 10 persons with counts
- Top 10 organizations with counts
- Average tone
- Date range

**Example:**
```json
{
  "query": "climate",
  "days_back": 14
}
```

---

### 3. `gdelt_actors`
Map actor relationships - who interacts with a given country.

Uses sequential streaming to avoid holding two large datasets in memory simultaneously.

**Parameters:**
- `country` (str): ISO3 country code (e.g., "USA", "RUS", "CHN")
- `relationship` (str, default="both"): Relationship type - "source" (country as actor1), "target" (as actor2), or "both"
- `days_back` (int, default=30): Number of days to look back (max: 365)

**Returns:** List of actor relationships with:
- Actor country code
- Relationship type
- Interaction count
- Average Goldstein scale
- Top 5 event codes with counts and names

**Example:**
```json
{
  "country": "UKR",
  "relationship": "both",
  "days_back": 60
}
```

---

### 4. `gdelt_trends`
Get coverage trends over time for a query.

**Parameters:**
- `query` (str): Search query string
- `metric` (str, default="volume"): Metric to track - "volume" (article count) or "tone" (average tone)
- `days_back` (int, default=30): Number of days to look back (max: 365)

**Returns:** Time series data with date and value for each point.

**Example:**
```json
{
  "query": "elections",
  "metric": "volume",
  "days_back": 30
}
```

---

### 5. `gdelt_doc`
Full-text article search via GDELT DOC API.

**Parameters:**
- `query` (str): Search query string (supports boolean operators, phrases)
- `days_back` (int, default=7): Number of days to look back (max: 365)
- `max_results` (int, default=100): Maximum results to return (1-250)
- `sort_by` (str, default="date"): Sort order - "date", "relevance", or "tone"

**Returns:** List of articles with url, title, tone, date, and language.

**Example:**
```json
{
  "query": "\"artificial intelligence\" AND regulation",
  "days_back": 14,
  "max_results": 50,
  "sort_by": "relevance"
}
```

---

### 6. `gdelt_cameo_lookup`
Look up CAMEO code meanings and Goldstein scale values.

**Parameters:**
- `code` (str, optional): Specific CAMEO code to look up (e.g., "14", "141", "20")
- `search` (str, optional): Text search in code names/descriptions

**Note:** Must provide either `code` or `search` parameter.

**Returns:** List of CAMEO code entries with:
- Code
- Name
- Description
- Goldstein scale value
- Quad class (1-4)
- Is conflict/cooperation flags

**Example:**
```json
{
  "search": "protest"
}
```

## CAMEO Event Codes

CAMEO codes classify events by type and intensity:

**Cooperation (01-08):**
- 01-05: Verbal cooperation (Quad class 1)
- 06-08: Material cooperation (Quad class 2)

**Conflict (14-20):**
- 09-13: Verbal conflict (Quad class 3)
- 14-20: Material conflict (Quad class 4)

**Goldstein Scale:** Ranges from -10 (most conflictual) to +10 (most cooperative).

**Goldstein Categories:**
- `highly_conflictual`: -10 to -5
- `moderately_conflictual`: -5 to -2
- `mildly_conflictual`: -2 to 0
- `cooperative`: 0 to +10

## Common GKG Theme Codes

- `ENV_CLIMATECHANGE` - Climate change
- `LEADER` - Political leaders
- `PROTEST` - Protests and demonstrations
- `TERROR` - Terrorism
- `ECON_INFLATION` - Inflation
- `MANMADE_DISASTER_IMPLIED` - Man-made disasters

For full theme taxonomy, use the GDELT documentation or query the lookup endpoints.

## Architecture

- **Server Framework:** FastMCP (async MCP server)
- **Data Source:** py-gdelt library (unified GDELT client)
- **Design:** Single shared GDELTClient instance, async-first, structured JSON responses

## Performance

All tools use **streaming aggregation** with O(1) memory consumption:

| Tool | Memory Strategy |
|------|----------------|
| `gdelt_events` | Streams events, aggregates counts/distributions, samples extreme events |
| `gdelt_gkg` | Streams records, aggregates theme/entity counts |
| `gdelt_actors` | Sequential streaming for source/target to avoid double memory |
| `gdelt_trends` | Uses DOC API timeline (volume) or bounded query (tone) |
| `gdelt_doc` | Bounded to 250 articles max |
| `gdelt_cameo_lookup` | Static lookup table |

This design allows queries spanning weeks or months without risk of OOM, even when matching 100k+ events.

## Error Handling

All tools handle errors gracefully:
- Invalid country codes → Pydantic validation error
- Invalid CAMEO codes → Validation error
- API failures → Clear error messages
- Empty results → Returns empty list/dict

## Development

### Linting
```bash
ruff check src/py_gdelt/mcp_server/
ruff format src/py_gdelt/mcp_server/
```

### Type Checking
```bash
mypy src/py_gdelt/mcp_server/
```

## License

MIT License (inherits from py-gdelt)
