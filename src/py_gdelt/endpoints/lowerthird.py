"""LowerThird (Chyron) API endpoint for television news chyron search.

This module provides the LowerThirdEndpoint for searching OCR'd text from
television lower-third overlays (chyrons). Chyrons are the text overlays
typically shown at the bottom of news broadcasts.

Example:
    Search for chyron clips mentioning a topic:

        async with LowerThirdEndpoint() as lt:
            clips = await lt.search("breaking news", timespan="24h")
            for clip in clips:
                print(f"{clip.station}: {clip.chyron_text}")

    Get timeline of chyron mentions:

        async with LowerThirdEndpoint() as lt:
            timeline = await lt.timeline("election", timespan="7d")
            for point in timeline.points:
                print(f"{point.date}: {point.count} mentions")

    Compare chyron coverage across stations:

        async with LowerThirdEndpoint() as lt:
            chart = await lt.station_chart("healthcare")
            for station in chart.stations:
                print(f"{station.station}: {station.percentage}%")
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel

from py_gdelt.endpoints.base import BaseEndpoint
from py_gdelt.endpoints.tv import (
    TVStationChart,
    TVStationData,
    TVTimeline,
    TVTimelinePoint,
)
from py_gdelt.filters import LowerThirdFilter


__all__ = [
    "LowerThirdClip",
    "LowerThirdEndpoint",
]


def _parse_date(date_str: str | None) -> datetime | None:
    """Parse GDELT date string to datetime.

    Handles both GDELT's native YYYYMMDDHHMMSS format and ISO 8601 format.

    Args:
        date_str: Date string in GDELT or ISO format.

    Returns:
        Parsed datetime object, or None if input is None or invalid.
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


class LowerThirdClip(BaseModel):
    """A single chyron clip from the LowerThird API.

    Represents OCR'd text from television lower-third overlays (chyrons).

    Attributes:
        station: Station identifier (CNN, MSNBC, FOXNEWS, BBCNEWS).
        show_name: Name of the TV show.
        date: Datetime of the chyron appearance.
        preview_url: URL to preview thumbnail.
        clip_url: URL to video clip.
        chyron_text: OCR'd text from the chyron overlay.
    """

    station: str
    show_name: str | None = None
    date: datetime | None = None
    preview_url: str | None = None
    clip_url: str | None = None
    chyron_text: str | None = None


class LowerThirdEndpoint(BaseEndpoint):
    """Endpoint for searching TV news chyrons (lower-third text overlays).

    Provides access to OCR'd chyron text from CNN, MSNBC, Fox News, and BBC News
    dating back to August 2017. Supports clip gallery, timeline, and station
    chart query modes.

    Note:
        OCR accuracy varies and there may be processing delays of 2-12 hours.
        Results may be incomplete due to station feed outages.

    Attributes:
        BASE_URL: API endpoint URL.

    Example:
        async with LowerThirdEndpoint() as lt:
            clips = await lt.search("breaking news", timespan="24h")
            for clip in clips:
                print(f"{clip.station}: {clip.chyron_text}")
    """

    BASE_URL: str = "https://api.gdeltproject.org/api/v2/lowerthird/lowerthird"

    async def _build_url(self, **kwargs: Any) -> str:
        """Build the request URL.

        Args:
            **kwargs: Unused, required by BaseEndpoint interface.

        Returns:
            The base LowerThird API URL.
        """
        return self.BASE_URL

    def _build_params(self, query_filter: LowerThirdFilter) -> dict[str, str]:
        """Build query parameters from LowerThirdFilter.

        Args:
            query_filter: Validated filter object.

        Returns:
            Dictionary of query parameters for HTTP request.
        """
        params: dict[str, str] = {
            "query": query_filter.query,
            "format": "json",
            "mode": query_filter.mode,
            "maxrecords": str(query_filter.max_results),
        }

        if query_filter.timespan:
            params["timespan"] = query_filter.timespan
        if query_filter.start_datetime:
            params["STARTDATETIME"] = query_filter.start_datetime.strftime("%Y%m%d%H%M%S")
        if query_filter.end_datetime:
            params["ENDDATETIME"] = query_filter.end_datetime.strftime("%Y%m%d%H%M%S")
        if query_filter.sort:
            params["sort"] = query_filter.sort

        return params

    async def search(
        self,
        query: str,
        *,
        timespan: str | None = None,
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None,
        max_results: int = 250,
        sort: Literal["DateDesc", "DateAsc"] | None = None,
    ) -> list[LowerThirdClip]:
        """Search for chyron clips matching the query.

        Args:
            query: Search terms (supports boolean operators, station: and show: filters).
            timespan: Time offset (e.g., "24h", "7d").
            start_datetime: Start of date range.
            end_datetime: End of date range.
            max_results: Maximum clips to return (1-3000).
            sort: Sort order (DateDesc, DateAsc, or None for relevance).

        Returns:
            List of matching chyron clips.

        Raises:
            APIError: If the API request fails.
            RateLimitError: If rate limit is exceeded.
            APIUnavailableError: If the API is temporarily unavailable.
        """
        query_filter = LowerThirdFilter(
            query=query,
            timespan=timespan,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            mode="ClipGallery",
            max_results=max_results,
            sort=sort,
        )
        return await self.query_clips(query_filter)

    async def query_clips(self, query_filter: LowerThirdFilter) -> list[LowerThirdClip]:
        """Query clips using a filter object.

        Args:
            query_filter: LowerThirdFilter with query parameters.

        Returns:
            List of LowerThirdClip objects.

        Raises:
            APIError: If the API request fails.
            RateLimitError: If rate limit is exceeded.
            APIUnavailableError: If the API is temporarily unavailable.
        """
        params = self._build_params(query_filter)
        url = await self._build_url()

        data = await self._get_json(url, params=params)

        return [
            LowerThirdClip(
                station=item.get("station", ""),
                show_name=item.get("show"),
                clip_url=item.get("url"),
                preview_url=item.get("preview"),
                date=_parse_date(item.get("date")),
                chyron_text=item.get("snippet"),
            )
            for item in data.get("clips", [])
        ]

    async def timeline(
        self,
        query: str,
        *,
        timespan: str | None = "7d",
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None,
    ) -> TVTimeline:
        """Get timeline of chyron mention volume over time.

        Args:
            query: Search query.
            timespan: Time range (default: "7d").
            start_datetime: Start of date range (alternative to timespan).
            end_datetime: End of date range.

        Returns:
            TVTimeline with time series data (reuses TV model).

        Raises:
            APIError: If the API request fails.
            RateLimitError: If rate limit is exceeded.
            APIUnavailableError: If the API is temporarily unavailable.
        """
        query_filter = LowerThirdFilter(
            query=query,
            timespan=timespan if not start_datetime else None,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            mode="TimelineVol",
        )

        params = self._build_params(query_filter)
        url = await self._build_url()

        data = await self._get_json(url, params=params)

        points = [
            TVTimelinePoint(
                date=item.get("date", ""),
                station=item.get("series"),
                count=item.get("value", 0),
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
        """Get station-level breakdown of chyron mentions.

        Args:
            query: Search query.
            timespan: Time range (default: "7d").
            start_datetime: Start of date range (alternative to timespan).
            end_datetime: End of date range.

        Returns:
            TVStationChart with station comparison data (reuses TV model).

        Raises:
            APIError: If the API request fails.
            RateLimitError: If rate limit is exceeded.
            APIUnavailableError: If the API is temporarily unavailable.
        """
        query_filter = LowerThirdFilter(
            query=query,
            timespan=timespan if not start_datetime else None,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            mode="StationChart",
        )

        params = self._build_params(query_filter)
        url = await self._build_url()

        data = await self._get_json(url, params=params)

        stations = [
            TVStationData(
                station=item.get("station", ""),
                count=item.get("value", 0),
                percentage=item.get("share"),
            )
            for item in data.get("stationchart", [])
        ]

        return TVStationChart(stations=stations)
