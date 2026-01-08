"""TV and TVAI API endpoints for television news monitoring.

This module provides endpoints for querying GDELT's television news transcript database.
The TV API provides access to television news monitoring with search, timeline,
and station comparison capabilities. The TVAI API provides AI-enhanced analysis.

Example:
    Search for TV clips mentioning a topic:

        async with TVEndpoint() as tv:
            clips = await tv.search("climate change", station="CNN")
            for clip in clips:
                print(f"{clip.show_name}: {clip.snippet}")

    Get timeline of TV mentions:

        async with TVEndpoint() as tv:
            timeline = await tv.timeline("election", timespan="30d")
            for point in timeline.points:
                print(f"{point.date}: {point.count} mentions")

    Compare coverage across stations:

        async with TVEndpoint() as tv:
            chart = await tv.station_chart("healthcare")
            for station in chart.stations:
                print(f"{station.station}: {station.percentage}%")
"""

from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta
from typing import Any

from pydantic import BaseModel

from py_gdelt.endpoints.base import BaseEndpoint
from py_gdelt.filters import TVFilter


__all__ = [
    "TVAIEndpoint",
    "TVClip",
    "TVEndpoint",
    "TVStationChart",
    "TVStationData",
    "TVTimeline",
    "TVTimelinePoint",
]


class TVClip(BaseModel):
    """Television clip from TV API.

    Represents a single segment of television news content matching a search query.
    Contains metadata about the station, show, and timing, plus text snippet and
    preview image.

    Attributes:
        station: Station identifier (e.g., "CNN", "FOXNEWS", "MSNBC")
        show_name: Name of the show the clip is from
        clip_url: URL to the video clip
        preview_url: URL to thumbnail image
        date: Timestamp when the clip aired
        duration_seconds: Length of clip in seconds
        snippet: Text excerpt from the transcript
    """

    station: str
    show_name: str | None = None
    clip_url: str | None = None
    preview_url: str | None = None
    date: datetime | None = None
    duration_seconds: int | None = None
    snippet: str | None = None


class TVTimelinePoint(BaseModel):
    """Single point in TV timeline.

    Represents the number of mentions of a topic at a specific date/time,
    optionally broken down by station.

    Attributes:
        date: Date string in GDELT format
        station: Optional station filter
        count: Number of mentions at this point
    """

    date: str
    station: str | None = None
    count: int


class TVTimeline(BaseModel):
    """Timeline data from TV API.

    Time series of TV mentions showing how coverage of a topic
    evolved over time.

    Attributes:
        points: List of timeline data points
    """

    points: list[TVTimelinePoint]


class TVStationData(BaseModel):
    """Data for a single station in station chart.

    Attributes:
        station: Station identifier
        count: Number of mentions on this station
        percentage: Percentage of total mentions (if calculated)
    """

    station: str
    count: int
    percentage: float | None = None


class TVStationChart(BaseModel):
    """Station comparison data.

    Shows which stations covered a topic and how much coverage each provided.

    Attributes:
        stations: List of station data, typically sorted by count descending
    """

    stations: list[TVStationData]


class TVEndpoint(BaseEndpoint):
    """TV API endpoint for television news monitoring.

    Searches transcripts from major US television networks including CNN,
    Fox News, MSNBC, and others. Provides three query modes:
    - Clip gallery: Individual video clips matching query
    - Timeline: Time series of mention frequency
    - Station chart: Breakdown by network

    The endpoint handles date formatting, parameter building, and response
    parsing automatically.

    Attributes:
        BASE_URL: API endpoint URL for TV queries

    Example:
        async with TVEndpoint() as tv:
            clips = await tv.search("election", station="CNN")
            for clip in clips:
                print(f"{clip.show_name}: {clip.snippet}")
    """

    BASE_URL = "https://api.gdeltproject.org/api/v2/tv/tv"

    async def _build_url(self, **kwargs: Any) -> str:
        """Build the request URL.

        TV API uses a fixed URL with query parameters.

        Args:
            **kwargs: Unused, but required by BaseEndpoint interface.

        Returns:
            The base TV API URL.
        """
        return self.BASE_URL

    def _build_params(self, query_filter: TVFilter) -> dict[str, str]:
        """Build query parameters from TVFilter.

        Constructs query parameters for the TV API from a TVFilter object.
        Handles both timespan and datetime range parameters, station/market
        filtering, and output mode selection.

        Note: GDELT TV API requires station to be in the query string itself
        (e.g., "election station:CNN") rather than as a separate parameter.

        Args:
            query_filter: Validated TV filter object

        Returns:
            Dictionary of query parameters ready for HTTP request
        """
        # Build query string - GDELT TV API requires station in query
        query = query_filter.query
        if query_filter.station:
            query = f"{query} station:{query_filter.station}"
        if query_filter.market:
            query = f"{query} market:{query_filter.market}"

        params: dict[str, str] = {
            "query": query,
            "format": "json",
            "mode": query_filter.mode,
            "maxrecords": str(query_filter.max_results),
        }

        # Convert timespan to explicit datetime range (GDELT TV API TIMESPAN is unreliable)
        if query_filter.timespan:
            delta = _parse_timespan(query_filter.timespan)
            if delta:
                end_dt = datetime.now(UTC)
                start_dt = end_dt - delta
                params["STARTDATETIME"] = start_dt.strftime("%Y%m%d%H%M%S")
                params["ENDDATETIME"] = end_dt.strftime("%Y%m%d%H%M%S")
        elif query_filter.start_datetime:
            params["STARTDATETIME"] = query_filter.start_datetime.strftime("%Y%m%d%H%M%S")
            if query_filter.end_datetime:
                params["ENDDATETIME"] = query_filter.end_datetime.strftime("%Y%m%d%H%M%S")

        return params

    async def search(
        self,
        query: str,
        *,
        timespan: str | None = None,
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None,
        station: str | None = None,
        market: str | None = None,
        max_results: int = 250,
    ) -> list[TVClip]:
        """Search TV transcripts for clips.

        Searches television news transcripts and returns matching video clips
        with metadata and text excerpts.

        Args:
            query: Search query (keywords, phrases, or boolean expressions)
            timespan: Time range (e.g., "24h", "7d", "30d")
            start_datetime: Start of date range (alternative to timespan)
            end_datetime: End of date range (alternative to timespan)
            station: Filter by station (CNN, FOXNEWS, MSNBC, etc.)
            market: Filter by market (National, Philadelphia, etc.)
            max_results: Maximum clips to return (1-250)

        Returns:
            List of TVClip objects matching the query

        Raises:
            APIError: If the API returns an error
            RateLimitError: If rate limit is exceeded
            APIUnavailableError: If the API is unavailable

        Example:
            clips = await tv.search("climate change", station="CNN", timespan="7d")
        """
        query_filter = TVFilter(
            query=query,
            timespan=timespan,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            station=station,
            market=market,
            max_results=max_results,
            mode="ClipGallery",
        )
        return await self.query_clips(query_filter)

    async def query_clips(self, query_filter: TVFilter) -> list[TVClip]:
        """Query for TV clips with a filter.

        Lower-level method that accepts a TVFilter object for more control
        over query parameters.

        Args:
            query_filter: TVFilter object with query parameters

        Returns:
            List of TVClip objects

        Raises:
            APIError: If the API returns an error
            RateLimitError: If rate limit is exceeded
            APIUnavailableError: If the API is unavailable
        """
        params = self._build_params(query_filter)
        params["mode"] = "ClipGallery"
        url = await self._build_url()

        data = await self._get_json(url, params=params)

        clips: list[TVClip] = [
            TVClip(
                station=item.get("station", ""),
                show_name=item.get("show"),
                clip_url=item.get("url"),
                preview_url=item.get("preview"),
                date=_parse_date(item.get("date")),
                duration_seconds=item.get("duration"),
                snippet=item.get("snippet"),
            )
            for item in data.get("clips", [])
        ]

        return clips

    async def timeline(
        self,
        query: str,
        *,
        timespan: str | None = "7d",
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None,
        station: str | None = None,
    ) -> TVTimeline:
        """Get timeline of TV mentions.

        Returns a time series showing when a topic was mentioned on television,
        useful for tracking coverage patterns over time.

        Args:
            query: Search query
            timespan: Time range (default: "7d")
            start_datetime: Start of date range (alternative to timespan)
            end_datetime: End of date range (alternative to timespan)
            station: Optional station filter

        Returns:
            TVTimeline with time series data

        Raises:
            APIError: If the API returns an error
            RateLimitError: If rate limit is exceeded
            APIUnavailableError: If the API is unavailable

        Example:
            timeline = await tv.timeline("election", timespan="30d")
            for point in timeline.points:
                print(f"{point.date}: {point.count} mentions")
        """
        query_filter = TVFilter(
            query=query,
            timespan=timespan if not start_datetime else None,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            station=station,
            mode="TimelineVol",
        )

        params = self._build_params(query_filter)
        url = await self._build_url()

        data = await self._get_json(url, params=params)

        points: list[TVTimelinePoint] = [
            TVTimelinePoint(
                date=item.get("date", ""),
                station=item.get("station"),
                count=item.get("count", 0),
            )
            for item in data.get("timeline", [])
        ]

        return TVTimeline(points=points)

    async def station_chart(
        self,
        query: str,
        *,
        timespan: str | None = "7d",
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None,
    ) -> TVStationChart:
        """Get station comparison chart.

        Shows which stations covered a topic the most, useful for understanding
        which networks are focusing on particular stories.

        Args:
            query: Search query
            timespan: Time range (default: "7d")
            start_datetime: Start of date range (alternative to timespan)
            end_datetime: End of date range (alternative to timespan)

        Returns:
            TVStationChart with station breakdown

        Raises:
            APIError: If the API returns an error
            RateLimitError: If rate limit is exceeded
            APIUnavailableError: If the API is unavailable

        Example:
            chart = await tv.station_chart("healthcare")
            for station in chart.stations:
                print(f"{station.station}: {station.percentage}%")
        """
        query_filter = TVFilter(
            query=query,
            timespan=timespan if not start_datetime else None,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            mode="StationChart",
        )

        params = self._build_params(query_filter)
        url = await self._build_url()

        data = await self._get_json(url, params=params)

        stations: list[TVStationData] = []
        if "stations" in data:
            total = sum(s.get("count", 0) for s in data["stations"])
            for item in data["stations"]:
                count = item.get("count", 0)
                stations.append(
                    TVStationData(
                        station=item.get("station", ""),
                        count=count,
                        percentage=count / total * 100 if total > 0 else None,
                    ),
                )

        return TVStationChart(stations=stations)


class TVAIEndpoint(BaseEndpoint):
    """TVAI API endpoint for AI-enhanced TV analysis.

    Similar to TVEndpoint but uses AI-powered features for enhanced analysis.
    Uses the same data models and similar interface as TVEndpoint.

    Attributes:
        BASE_URL: API endpoint URL for TVAI queries

    Example:
        async with TVAIEndpoint() as tvai:
            clips = await tvai.search("artificial intelligence")
    """

    BASE_URL = "https://api.gdeltproject.org/api/v2/tvai/tvai"

    async def _build_url(self, **kwargs: Any) -> str:
        """Build the request URL.

        TVAI API uses a fixed URL with query parameters.

        Args:
            **kwargs: Unused, but required by BaseEndpoint interface.

        Returns:
            The base TVAI API URL.
        """
        return self.BASE_URL

    async def search(
        self,
        query: str,
        *,
        timespan: str | None = None,
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None,
        station: str | None = None,
        max_results: int = 250,
    ) -> list[TVClip]:
        """Search using AI-enhanced analysis.

        Searches television transcripts using AI-powered analysis for potentially
        better semantic matching and relevance.

        Args:
            query: Search query
            timespan: Time range (e.g., "24h", "7d")
            start_datetime: Start of date range (alternative to timespan)
            end_datetime: End of date range (alternative to timespan)
            station: Filter by station
            max_results: Maximum clips to return (1-250)

        Returns:
            List of TVClip objects

        Raises:
            APIError: If the API returns an error
            RateLimitError: If rate limit is exceeded
            APIUnavailableError: If the API is unavailable

        Example:
            clips = await tvai.search("machine learning", timespan="7d")
        """
        # Build query string - GDELT TV API requires station in query
        query_str = query
        if station:
            query_str = f"{query} station:{station}"

        params: dict[str, str] = {
            "query": query_str,
            "format": "json",
            "mode": "ClipGallery",
            "maxrecords": str(max_results),
        }

        # Use explicit datetime range if provided, otherwise convert timespan
        if start_datetime:
            params["STARTDATETIME"] = start_datetime.strftime("%Y%m%d%H%M%S")
            if end_datetime:
                params["ENDDATETIME"] = end_datetime.strftime("%Y%m%d%H%M%S")
        elif timespan:
            delta = _parse_timespan(timespan)
            if delta:
                end_dt = datetime.now(UTC)
                start_dt = end_dt - delta
                params["STARTDATETIME"] = start_dt.strftime("%Y%m%d%H%M%S")
                params["ENDDATETIME"] = end_dt.strftime("%Y%m%d%H%M%S")

        url = await self._build_url()
        data = await self._get_json(url, params=params)

        clips: list[TVClip] = [
            TVClip(
                station=item.get("station", ""),
                show_name=item.get("show"),
                clip_url=item.get("url"),
                preview_url=item.get("preview"),
                date=_parse_date(item.get("date")),
                duration_seconds=item.get("duration"),
                snippet=item.get("snippet"),
            )
            for item in data.get("clips", [])
        ]

        return clips


def _parse_date(date_str: str | None) -> datetime | None:
    """Parse GDELT date string to datetime.

    Handles both GDELT's native YYYYMMDDHHMMSS format and ISO 8601 format.

    Args:
        date_str: Date string in GDELT or ISO format

    Returns:
        Parsed datetime object, or None if input is None or invalid

    Example:
        >>> _parse_date("20240115120000")
        datetime(2024, 1, 15, 12, 0, 0)
        >>> _parse_date("2024-01-15T12:00:00")
        datetime(2024, 1, 15, 12, 0, 0)
    """
    if not date_str:
        return None
    try:
        # Try YYYYMMDDHHMMSS format
        if len(date_str) == 14:
            return datetime.strptime(date_str, "%Y%m%d%H%M%S").replace(tzinfo=UTC)
        # Try ISO format - add UTC if naive
        result = datetime.fromisoformat(date_str)
        return result if result.tzinfo else result.replace(tzinfo=UTC)
    except ValueError:
        return None


def _parse_timespan(timespan: str) -> timedelta | None:
    """Parse timespan string to timedelta.

    Converts GDELT-style timespan strings (e.g., "24h", "7d") to Python timedelta.

    Args:
        timespan: Timespan like "24h", "7d", "4w", "3m", "1y"

    Returns:
        timedelta or None if unparseable

    Example:
        >>> _parse_timespan("24h")
        timedelta(hours=24)
        >>> _parse_timespan("7d")
        timedelta(days=7)
    """
    match = re.match(r"(\d+)\s*([hdwmy])", timespan.lower())
    if not match:
        return None

    value, unit = int(match.group(1)), match.group(2)
    # Map unit to timedelta kwargs (days approximations for months/years)
    unit_map: dict[str, timedelta] = {
        "h": timedelta(hours=value),
        "d": timedelta(days=value),
        "w": timedelta(weeks=value),
        "m": timedelta(days=value * 30),
        "y": timedelta(days=value * 365),
    }
    return unit_map.get(unit)
