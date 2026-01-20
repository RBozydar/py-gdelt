"""GDELT MCP Server for geopolitical research.

This MCP server exposes the py-gdelt library capabilities as structured tools
for AI agents to query GDELT data sources (Events, GKG, DOC API, etc.).
"""

from __future__ import annotations

import asyncio
import heapq
import logging
import math
import threading
from datetime import date, timedelta
from typing import TYPE_CHECKING, Any

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

from py_gdelt import GDELTClient
from py_gdelt.filters import DateRange, DocFilter, EventFilter, GKGFilter
from py_gdelt.lookups.cameo import CAMEOCodes


if TYPE_CHECKING:
    from py_gdelt.models.articles import Article
    from py_gdelt.models.gkg import GKGRecord


__all__ = [
    "get_cameo_codes",
    "get_client",
    "mcp",
]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Pydantic models for tool responses


class NameCount(BaseModel):
    """A named item with a count."""

    name: str
    count: int


class EventSummary(BaseModel):
    """Summary of a GDELT event."""

    global_event_id: int
    date: str
    actor1_country: str | None
    actor1_name: str | None
    actor2_country: str | None
    actor2_name: str | None
    event_code: str
    event_name: str | None
    goldstein_scale: float
    avg_tone: float
    source_url: str | None


class GKGSummary(BaseModel):
    """Summary of GKG entity and theme data."""

    total_records: int
    top_themes: list[NameCount]
    top_persons: list[NameCount]
    top_organizations: list[NameCount]
    avg_tone: float
    date_range: str


class EventCodeCount(BaseModel):
    """Event code with count and name."""

    code: str
    count: int
    name: str | None


class ActorRelationship(BaseModel):
    """Actor relationship summary."""

    actor: str
    relationship_type: str  # "source" | "target" | "both"
    interaction_count: int
    avg_goldstein: float
    top_event_codes: list[EventCodeCount]


class TrendPoint(BaseModel):
    """Single point in a trend time series."""

    date: str
    value: float


class ArticleSummary(BaseModel):
    """Summary of a GDELT article."""

    url: str
    title: str | None
    seendate: str
    tone: float | None
    language: str | None


# Initialize MCP server
mcp = FastMCP("GDELT Research Server")


# Shared GDELT client (initialized on first use)
_client: GDELTClient | None = None
_cameo_codes: CAMEOCodes | None = None

# Thread-safe initialization locks
_client_lock: asyncio.Lock | None = None
_cameo_lock = threading.Lock()

# Heap stability counter for tie-breaking
_heap_counter = 0


async def get_client() -> GDELTClient:
    """Get or create the shared GDELT client."""
    global _client, _client_lock
    if _client_lock is None:
        _client_lock = asyncio.Lock()
    if _client is None:
        async with _client_lock:
            if _client is None:  # Double-check after acquiring lock
                _client = GDELTClient()
                await _client._initialize()
    return _client


def get_cameo_codes() -> CAMEOCodes:
    """Get or create the shared CAMEO codes lookup."""
    global _cameo_codes
    if _cameo_codes is None:
        with _cameo_lock:
            if _cameo_codes is None:
                _cameo_codes = CAMEOCodes()
    return _cameo_codes


def _top_n(counts: dict[str, int], n: int) -> list[dict[str, Any]]:
    """Extract top N items from a counter dictionary.

    Args:
        counts: Dictionary mapping items to counts.
        n: Number of top items to return.

    Returns:
        List of dicts with 'name' and 'count' keys, sorted by count descending.
    """
    return [{"name": k, "count": v} for k, v in sorted(counts.items(), key=lambda x: -x[1])[:n]]


@mcp.tool()
async def gdelt_events(
    actor1_country: str | None = None,
    actor2_country: str | None = None,
    event_type: str = "all",
    days_back: int = 7,
    min_goldstein: float | None = None,
    max_goldstein: float | None = None,
) -> dict[str, Any]:
    """Query CAMEO-coded events from GDELT with streaming aggregation.

    Streams events matching actor and event type criteria, computing aggregated
    statistics without materializing the full result set in memory. Returns
    summary statistics, distributions, and sample events.

    Args:
        actor1_country: Country code for actor 1. Accepts both formats:
            - FIPS (2 chars): US, UK, IR, FR, GM, CH, RS
            - ISO3 (3 chars): USA, GBR, IRN, FRA, DEU, CHN, RUS
        actor2_country: Country code for actor 2 (same formats as actor1)
        event_type: Type filter - "conflict" (codes 14-20), "cooperation" (01-08), or "all"
        days_back: Number of days to look back (default: 7, max: 365)
        min_goldstein: Minimum Goldstein scale (-10 to 10, negative=conflict)
        max_goldstein: Maximum Goldstein scale (-10 to 10, positive=cooperation)

    Returns:
        Aggregated event summary containing:
            - summary: total_events, date_range, goldstein_mean, goldstein_std
            - goldstein_distribution: counts by conflict/cooperation category
            - events_by_type: top 10 event types with counts and percentages
            - events_by_day: daily event counts
            - top_actor1_countries: top 10 actor1 countries by event count
            - top_actor2_countries: top 10 actor2 countries by event count
            - sample_events: 10 sample events with extreme Goldstein scores
    """
    try:
        client = await get_client()
        cameo = get_cameo_codes()

        # Validate MCP-specific parameters
        if event_type not in {"all", "conflict", "cooperation"}:
            return {
                "error": f"Invalid event_type: {event_type}. Must be one of: all, conflict, cooperation"
            }

        # Build date range
        end_date = date.today() - timedelta(days=1)  # Yesterday
        start_date = end_date - timedelta(days=min(days_back, 365))

        # Build filter
        event_filter = EventFilter(
            date_range=DateRange(start=start_date, end=end_date),
            actor1_country=actor1_country,
            actor2_country=actor2_country,
        )

        logger.info(
            "Streaming events: actor1=%s, actor2=%s, type=%s, days=%d",
            actor1_country,
            actor2_country,
            event_type,
            days_back,
        )

        global _heap_counter

        # Initialize aggregation counters
        total_events = 0
        goldstein_sum = 0.0
        goldstein_sq_sum = 0.0
        goldstein_buckets: dict[str, int] = {
            "highly_conflictual": 0,
            "moderately_conflictual": 0,
            "mildly_conflictual": 0,
            "cooperative": 0,
        }
        events_by_day: dict[str, int] = {}
        events_by_type: dict[str, int] = {}
        actor1_countries: dict[str, int] = {}
        actor2_countries: dict[str, int] = {}

        # Reservoir sampling for extreme events (5 most negative, 5 most positive)
        most_negative_heap: list[tuple[float, int, dict[str, Any]]] = []
        most_positive_heap: list[tuple[float, int, dict[str, Any]]] = []

        # Stream and aggregate
        async for event in client.events.stream(event_filter):
            # Apply Goldstein filter
            if min_goldstein is not None and event.goldstein_scale < min_goldstein:
                continue
            if max_goldstein is not None and event.goldstein_scale > max_goldstein:
                continue

            # Apply event type filter
            if event_type == "conflict":
                if not cameo.is_conflict(event.event_code):
                    continue
            elif event_type == "cooperation":
                if not cameo.is_cooperation(event.event_code):
                    continue

            # Update counters
            total_events += 1
            goldstein_sum += event.goldstein_scale
            goldstein_sq_sum += event.goldstein_scale**2

            # Update Goldstein distribution
            bucket = cameo.get_goldstein_category(event.goldstein_scale)
            goldstein_buckets[bucket] += 1

            # Update daily counts
            date_str = event.date.isoformat()
            events_by_day[date_str] = events_by_day.get(date_str, 0) + 1

            # Update event type counts
            events_by_type[event.event_code] = events_by_type.get(event.event_code, 0) + 1

            # Update actor country counts
            if event.actor1 and event.actor1.country_code:
                country = event.actor1.country_code
                actor1_countries[country] = actor1_countries.get(country, 0) + 1

            if event.actor2 and event.actor2.country_code:
                country = event.actor2.country_code
                actor2_countries[country] = actor2_countries.get(country, 0) + 1

            # Reservoir sampling for extreme events
            cameo_entry = cameo.get(event.event_code)
            event_dict = {
                "global_event_id": event.global_event_id,
                "date": event.date.isoformat(),
                "actor1_country": event.actor1.country_code if event.actor1 else None,
                "actor1_name": event.actor1.name if event.actor1 else None,
                "actor2_country": event.actor2.country_code if event.actor2 else None,
                "actor2_name": event.actor2.name if event.actor2 else None,
                "event_code": event.event_code,
                "event_name": cameo_entry.name if cameo_entry else None,
                "goldstein_scale": event.goldstein_scale,
                "avg_tone": event.avg_tone,
                "source_url": event.source_url,
            }

            # Keep 5 most negative (use max heap with negated values)
            _heap_counter += 1
            if len(most_negative_heap) < 5:
                heapq.heappush(
                    most_negative_heap, (-event.goldstein_scale, _heap_counter, event_dict)
                )
            elif event.goldstein_scale < -most_negative_heap[0][0]:
                heapq.heapreplace(
                    most_negative_heap, (-event.goldstein_scale, _heap_counter, event_dict)
                )

            # Keep 5 most positive (use min heap)
            _heap_counter += 1
            if len(most_positive_heap) < 5:
                heapq.heappush(
                    most_positive_heap, (event.goldstein_scale, _heap_counter, event_dict)
                )
            elif event.goldstein_scale > most_positive_heap[0][0]:
                heapq.heapreplace(
                    most_positive_heap, (event.goldstein_scale, _heap_counter, event_dict)
                )

        # Calculate summary statistics
        goldstein_mean = goldstein_sum / total_events if total_events > 0 else 0.0
        if total_events > 0:
            variance = (goldstein_sq_sum / total_events) - (goldstein_mean**2)
            goldstein_std = math.sqrt(
                max(0.0, variance)
            )  # Avoid negative due to floating point errors
        else:
            goldstein_std = 0.0

        # Build events_by_type with percentages
        events_by_type_list = []
        for code, count in sorted(events_by_type.items(), key=lambda x: -x[1])[:10]:
            cameo_entry = cameo.get(code)
            events_by_type_list.append(
                {
                    "code": code,
                    "name": cameo_entry.name if cameo_entry else None,
                    "count": count,
                    "pct": (count / total_events * 100) if total_events > 0 else 0.0,
                }
            )

        # Build events_by_day sorted by date
        events_by_day_list = [
            {"date": date_str, "count": count} for date_str, count in sorted(events_by_day.items())
        ]

        # Build top countries lists
        top_actor1_countries = _top_n(actor1_countries, 10)
        top_actor2_countries = _top_n(actor2_countries, 10)

        # Extract sample events from heaps
        sample_events = []
        sample_events.extend([event_dict for _, _, event_dict in most_negative_heap])
        sample_events.extend([event_dict for _, _, event_dict in most_positive_heap])

        result = {
            "summary": {
                "total_events": total_events,
                "date_range": f"{start_date.isoformat()} to {end_date.isoformat()}",
                "goldstein_mean": goldstein_mean,
                "goldstein_std": goldstein_std,
            },
            "goldstein_distribution": goldstein_buckets,
            "events_by_type": events_by_type_list,
            "events_by_day": events_by_day_list,
            "top_actor1_countries": top_actor1_countries,
            "top_actor2_countries": top_actor2_countries,
            "sample_events": sample_events,
        }

        logger.info("Returning aggregated summary for %d events", total_events)
        return result
    except Exception as e:
        return {"error": f"GDELT API error: {e!s}"}


def _matches_query(record: GKGRecord, query: str) -> bool:
    """Check if a GKG record matches a text query.

    Args:
        record: The GKG record to check.
        query: The text query string.

    Returns:
        True if the query matches themes, persons, or organizations.
    """
    query_lower = query.lower()
    for theme in record.themes:
        if query_lower in theme.name.lower():
            return True
    for person in record.persons:
        if query_lower in person.name.lower():
            return True
    for org in record.organizations:
        if query_lower in org.name.lower():
            return True
    return False


@mcp.tool()
async def gdelt_gkg(
    query: str | None = None,
    themes: list[str] | None = None,
    days_back: int = 7,
) -> dict[str, Any]:
    """Query Global Knowledge Graph for entities and themes.

    Searches GKG records and aggregates extracted themes, persons, organizations, and tone.

    Args:
        query: Text query to filter records (searches themes, persons, organizations)
        themes: List of GKG theme codes to filter by (e.g., ["ENV_CLIMATECHANGE", "LEADER"])
        days_back: Number of days to look back (default: 7, max: 365)

    Returns:
        Aggregated summary with top themes, entities, and tone analysis
    """
    try:
        client = await get_client()

        # Build date range
        end_date = date.today() - timedelta(days=1)
        start_date = end_date - timedelta(days=min(days_back, 365))

        # Build filter
        gkg_filter = GKGFilter(
            date_range=DateRange(start=start_date, end=end_date),
            themes=themes,
        )

        # Stream GKG records and aggregate
        logger.info("Querying GKG: query=%s, themes=%s, days=%d", query, themes, days_back)

        theme_counts: dict[str, int] = {}
        person_counts: dict[str, int] = {}
        org_counts: dict[str, int] = {}
        tone_sum = 0.0
        tone_count = 0
        total_records = 0

        async for record in client.gkg.stream(gkg_filter):
            # Apply text query filter if provided
            if query and not _matches_query(record, query):
                continue

            total_records += 1

            # Aggregate themes
            for theme in record.themes:
                theme_counts[theme.name] = theme_counts.get(theme.name, 0) + 1

            # Aggregate persons
            for person in record.persons:
                person_counts[person.name] = person_counts.get(person.name, 0) + 1

            # Aggregate organizations
            for org in record.organizations:
                org_counts[org.name] = org_counts.get(org.name, 0) + 1

            # Aggregate tone
            if record.tone:
                tone_sum += record.tone.tone
                tone_count += 1

        # Sort and get top items
        top_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        top_persons = sorted(person_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        top_orgs = sorted(org_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        avg_tone = tone_sum / tone_count if tone_count > 0 else 0.0

        result = {
            "total_records": total_records,
            "top_themes": [{"name": name, "count": count} for name, count in top_themes],
            "top_persons": [{"name": name, "count": count} for name, count in top_persons],
            "top_organizations": [{"name": name, "count": count} for name, count in top_orgs],
            "avg_tone": avg_tone,
            "date_range": f"{start_date.isoformat()} to {end_date.isoformat()}",
        }

        logger.info("Returning GKG summary: %d records", total_records)
        return result
    except Exception as e:
        return {"error": f"GDELT API error: {e!s}"}


@mcp.tool()
async def gdelt_actors(
    country: str,
    relationship: str = "both",
    days_back: int = 30,
) -> list[dict[str, Any]]:
    """Map actor relationships - who interacts with a given country.

    Analyzes events to find which actors/countries interact with the specified country.

    Args:
        country: Country code. Accepts both formats:
            - FIPS (2 chars): US, UK, IR, FR, GM, CH, RS
            - ISO3 (3 chars): USA, GBR, IRN, FRA, DEU, CHN, RUS
        relationship: Relationship type - "source" (country as actor1), "target" (as actor2), or "both"
        days_back: Number of days to look back (default: 30, max: 365)

    Returns:
        List of actor relationships with interaction counts, avg Goldstein scale, and top event types
    """
    try:
        client = await get_client()
        cameo = get_cameo_codes()

        # Validate MCP-specific parameters
        if relationship not in {"source", "target", "both"}:
            return [
                {
                    "error": f"Invalid relationship: {relationship}. Must be one of: source, target, both"
                }
            ]

        # Build date range
        end_date = date.today() - timedelta(days=1)
        start_date = end_date - timedelta(days=min(days_back, 365))

        # Single accumulator for all relationships - O(1) relative to event count
        actor_stats: dict[str, dict[str, Any]] = {}

        def get_or_create_stats(actor: str) -> dict[str, Any]:
            """Get or create stats entry for an actor."""
            if actor not in actor_stats:
                actor_stats[actor] = {
                    "source_count": 0,
                    "target_count": 0,
                    "goldstein_sum": 0.0,
                    "event_codes": {},
                }
            return actor_stats[actor]

        # Process source events (country as actor1)
        if relationship in ("source", "both"):
            filter1 = EventFilter(
                date_range=DateRange(start=start_date, end=end_date),
                actor1_country=country,
            )
            logger.info("Streaming source events for %s", country)
            async for event in client.events.stream(filter1):
                if not event.actor2 or not event.actor2.country_code:
                    continue
                actor = event.actor2.country_code
                stats = get_or_create_stats(actor)
                stats["source_count"] += 1
                stats["goldstein_sum"] += event.goldstein_scale
                code = event.event_code
                stats["event_codes"][code] = stats["event_codes"].get(code, 0) + 1

        # Process target events (country as actor2) - filter1 stream already done
        if relationship in ("target", "both"):
            filter2 = EventFilter(
                date_range=DateRange(start=start_date, end=end_date),
                actor2_country=country,
            )
            logger.info("Streaming target events for %s", country)
            async for event in client.events.stream(filter2):
                if not event.actor1 or not event.actor1.country_code:
                    continue
                actor = event.actor1.country_code
                stats = get_or_create_stats(actor)
                stats["target_count"] += 1
                stats["goldstein_sum"] += event.goldstein_scale
                code = event.event_code
                stats["event_codes"][code] = stats["event_codes"].get(code, 0) + 1

        # Convert to results list (same format as before)
        results: list[dict[str, Any]] = []
        for actor, stats in actor_stats.items():
            total_count = stats["source_count"] + stats["target_count"]
            if total_count == 0:
                continue

            top_codes = sorted(stats["event_codes"].items(), key=lambda x: x[1], reverse=True)[:5]

            # Determine relationship type based on counts
            if stats["source_count"] > 0 and stats["target_count"] > 0:
                rel_type = "both"
            elif stats["source_count"] > 0:
                rel_type = "source"
            else:
                rel_type = "target"

            results.append(
                {
                    "actor": actor,
                    "relationship_type": rel_type,
                    "interaction_count": total_count,
                    "avg_goldstein": stats["goldstein_sum"] / total_count,
                    "top_event_codes": [
                        {
                            "code": code,
                            "count": count,
                            "name": entry.name if (entry := cameo.get(code)) else None,
                        }
                        for code, count in top_codes
                    ],
                }
            )

        # Sort by interaction count and limit
        results.sort(key=lambda x: x["interaction_count"], reverse=True)

        logger.info("Returning %d actor relationships for %s", len(results), country)
        return results[:50]  # Limit to top 50
    except Exception as e:
        return [{"error": f"GDELT API error: {e!s}"}]


@mcp.tool()
async def gdelt_trends(
    query: str,
    metric: str = "volume",
    days_back: int = 30,
) -> list[dict[str, Any]]:
    """Get coverage trends over time for a query.

    Analyzes article volume or tone trends for a search query over time.

    Args:
        query: Search query string
        metric: Metric to track - "volume" (article count) or "tone" (average tone)
        days_back: Number of days to look back (default: 30, max: 90)

    Returns:
        Time series data with date and value for each point
    """
    try:
        client = await get_client()

        # Limit to 90 days for timeline queries
        days = min(days_back, 90)

        # Use DOC API timeline mode
        timespan = f"{days}d"

        logger.info("Querying trends: query=%s, metric=%s, days=%d", query, metric, days)

        if metric == "volume":
            # Get timeline data
            timeline = await client.doc.timeline(query, timespan=timespan)

            # Convert to trend points
            results = [
                {"date": point.date, "value": float(point.value)} for point in timeline.points
            ]

        else:  # tone
            # For tone, we need to query articles and aggregate by date
            doc_filter = DocFilter(
                query=query,
                timespan=timespan,
                max_results=250,  # API limit
                sort_by="date",
            )
            articles = await client.doc.query(doc_filter)

            # Group by date and calculate average tone
            date_tones: dict[str, list[float]] = {}
            for article in articles:
                if article.tone is not None and article.seendate:
                    if len(article.seendate) >= 8:
                        date_str = article.seendate[:8]  # YYYYMMDD
                    else:
                        date_str = article.seendate  # Use as-is if too short
                    if date_str not in date_tones:
                        date_tones[date_str] = []
                    date_tones[date_str].append(article.tone)

            # Calculate averages
            results = []
            for date_str, tones in sorted(date_tones.items()):
                avg_tone = sum(tones) / len(tones) if tones else 0.0
                # Format date as YYYY-MM-DD (only if date_str is long enough)
                if len(date_str) == 8:
                    formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                else:
                    formatted_date = date_str
                results.append({"date": formatted_date, "value": avg_tone})

        logger.info("Returning %d trend points", len(results))
        return results
    except Exception as e:
        return [{"error": f"GDELT API error: {e!s}"}]


@mcp.tool()
async def gdelt_doc(
    query: str,
    days_back: int = 7,
    max_results: int = 100,
    sort_by: str = "date",
) -> list[dict[str, Any]]:
    """Full-text article search via GDELT DOC API.

    Search for news articles matching a query across GDELT's monitored sources.

    Args:
        query: Search query string (supports boolean operators, phrases)
        days_back: Number of days to look back (default: 7, max: 90)
        max_results: Maximum results to return (1-250, default: 100)
        sort_by: Sort order - "date", "relevance", or "tone" (default: "date")

    Returns:
        List of articles with url, title, tone, date, and language
    """
    try:
        client = await get_client()

        # Validate MCP-specific parameters
        if sort_by not in {"date", "relevance", "tone"}:
            return [{"error": f"Invalid sort_by: {sort_by}. Must be one of: date, relevance, tone"}]

        # Build timespan
        days = min(days_back, 90)
        timespan = f"{days}d"

        logger.info(
            "Searching articles: query=%s, days=%d, max=%d, sort=%s",
            query,
            days,
            max_results,
            sort_by,
        )

        articles: list[Article] = await client.doc.search(
            query=query,
            timespan=timespan,
            max_results=min(max_results, 250),
            sort_by=sort_by,  # type: ignore[arg-type]
        )

        # Convert to summaries
        results = [
            {
                "url": article.url,
                "title": article.title,
                "seendate": article.seendate,
                "tone": article.tone,
                "language": article.language,
            }
            for article in articles
        ]

        logger.info("Returning %d articles", len(results))
        return results
    except Exception as e:
        return [{"error": f"GDELT API error: {e!s}"}]


@mcp.tool()
async def gdelt_cameo_lookup(
    code: str | None = None,
    search: str | None = None,
) -> list[dict[str, Any]]:
    """Look up CAMEO code meanings and Goldstein scale values.

    Search or retrieve CAMEO event codes with their descriptions and conflict/cooperation scores.

    Args:
        code: Specific CAMEO code to look up (e.g., "14", "141", "20")
        search: Text search in code names/descriptions (substring match)

    Returns:
        List of CAMEO code entries with code, name, description, and Goldstein scale
    """
    try:
        cameo = get_cameo_codes()

        results: list[dict[str, Any]] = []

        if code:
            # Look up specific code
            entry = cameo.get(code)
            if entry:
                goldstein = cameo.get_goldstein(code)
                results.append(
                    {
                        "code": code,
                        "name": entry.name,
                        "description": entry.description,
                        "goldstein_scale": goldstein.value if goldstein else None,
                        "quad_class": cameo.get_quad_class(code),
                        "is_conflict": cameo.is_conflict(code),
                        "is_cooperation": cameo.is_cooperation(code),
                    }
                )

        elif search:
            # Search codes
            matching_codes = cameo.search(search)
            for matching_code in matching_codes[:20]:  # Limit to 20 results
                entry = cameo.get(matching_code)
                if entry:
                    goldstein = cameo.get_goldstein(matching_code)
                    results.append(
                        {
                            "code": matching_code,
                            "name": entry.name,
                            "description": entry.description,
                            "goldstein_scale": goldstein.value if goldstein else None,
                            "quad_class": cameo.get_quad_class(matching_code),
                            "is_conflict": cameo.is_conflict(matching_code),
                            "is_cooperation": cameo.is_cooperation(matching_code),
                        }
                    )

        else:
            # Return error - need either code or search
            msg = "Must provide either 'code' or 'search' parameter"
            raise ValueError(msg)

        logger.info("Returning %d CAMEO code entries", len(results))
        return results
    except Exception as e:
        return [{"error": f"GDELT API error: {e!s}"}]


# Entry point
if __name__ == "__main__":
    mcp.run()
