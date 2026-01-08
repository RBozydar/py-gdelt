"""
DOC 2.0 API endpoint for searching GDELT articles.

This module provides the DocEndpoint class for querying GDELT's article database
through the DOC 2.0 API. The API supports full-text search across monitored news
sources with flexible filtering, sorting, and output modes.

API Documentation: https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from py_gdelt.endpoints.base import BaseEndpoint
from py_gdelt.filters import DocFilter


if TYPE_CHECKING:
    from py_gdelt.models.articles import Article, Timeline

__all__ = ["DocEndpoint"]


class DocEndpoint(BaseEndpoint):
    """
    DOC 2.0 API endpoint for searching GDELT articles.

    The DOC API provides full-text search across GDELT's monitored news sources
    with support for various output modes (article lists, timelines, galleries)
    and flexible filtering by time, source, language, and relevance.

    Attributes:
        BASE_URL: Base URL for the DOC API endpoint

    Example:
        Basic article search:

        >>> async with DocEndpoint() as doc:
        ...     articles = await doc.search("climate change", max_results=100)
        ...     for article in articles:
        ...         print(article.title, article.url)

        Using filters for advanced queries:

        >>> from py_gdelt.filters import DocFilter
        >>> async with DocEndpoint() as doc:
        ...     filter = DocFilter(
        ...         query="elections",
        ...         timespan="7d",
        ...         source_country="US",
        ...         sort_by="relevance"
        ...     )
        ...     articles = await doc.query(filter)

        Getting timeline data:

        >>> async with DocEndpoint() as doc:
        ...     timeline = await doc.timeline("protests", timespan="30d")
        ...     for point in timeline.points:
        ...         print(point.date, point.value)
    """

    BASE_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

    async def _build_url(self, **kwargs: Any) -> str:
        """Build DOC API URL.

        The DOC API uses a fixed URL with all parameters passed as query strings.

        Args:
            **kwargs: Unused, but required by BaseEndpoint interface.

        Returns:
            Base URL for DOC API requests.
        """
        return self.BASE_URL

    def _build_params(self, query_filter: DocFilter) -> dict[str, str]:
        """
        Build query parameters from DocFilter.

        Converts the DocFilter model into URL query parameters expected by
        the DOC API, including proper format conversion for dates and
        mapping of sort values to API parameter names.

        Args:
            query_filter: Query filter with search parameters.

        Returns:
            Dict of query parameters ready for API request.

        Example:
            >>> filter = DocFilter(query="test", timespan="24h", sort_by="relevance")
            >>> endpoint = DocEndpoint()
            >>> params = endpoint._build_params(filter)
            >>> params["query"]
            'test'
            >>> params["sort"]
            'rel'
        """
        params: dict[str, str] = {
            "query": query_filter.query,
            "format": "json",
            "mode": query_filter.mode,
            "maxrecords": str(query_filter.max_results),
        }

        # Map sort values to API parameter names
        sort_map = {
            "date": "date",
            "relevance": "rel",
            "tone": "tonedesc",
        }
        params["sort"] = sort_map[query_filter.sort_by]

        # Time constraints - timespan takes precedence over datetime range
        if query_filter.timespan:
            params["timespan"] = query_filter.timespan
        elif query_filter.start_datetime:
            params["startdatetime"] = query_filter.start_datetime.strftime("%Y%m%d%H%M%S")
            if query_filter.end_datetime:
                params["enddatetime"] = query_filter.end_datetime.strftime("%Y%m%d%H%M%S")

        # Source filters
        if query_filter.source_language:
            params["sourcelang"] = query_filter.source_language
        if query_filter.source_country:
            params["sourcecountry"] = query_filter.source_country

        return params

    async def search(
        self,
        query: str,
        *,
        timespan: str | None = None,
        max_results: int = 250,
        sort_by: Literal["date", "relevance", "tone"] = "date",
        source_language: str | None = None,
        source_country: str | None = None,
    ) -> list[Article]:
        """
        Search for articles matching a query.

        This is a convenience method that constructs a DocFilter internally.
        For more control over query parameters, use query() with a DocFilter directly.

        Args:
            query: Search query string (supports boolean operators, phrases).
            timespan: Time range like "24h", "7d", "30d". If None, searches all time.
            max_results: Maximum results to return (1-250, default: 250).
            sort_by: Sort order - "date", "relevance", or "tone" (default: "date").
            source_language: Filter by source language (ISO 639 code).
            source_country: Filter by source country (FIPS country code).

        Returns:
            List of Article objects matching the query.

        Raises:
            APIError: On HTTP errors or invalid responses.
            APIUnavailableError: When API is down or unreachable.
            RateLimitError: When rate limited by the API.

        Example:
            >>> async with DocEndpoint() as doc:
            ...     # Search recent articles about climate
            ...     articles = await doc.search(
            ...         "climate change",
            ...         timespan="7d",
            ...         max_results=50,
            ...         sort_by="relevance"
            ...     )
            ...     # Filter by country
            ...     us_articles = await doc.search(
            ...         "elections",
            ...         source_country="US",
            ...         timespan="24h"
            ...     )
        """
        query_filter = DocFilter(
            query=query,
            timespan=timespan,
            max_results=max_results,
            sort_by=sort_by,
            source_language=source_language,
            source_country=source_country,
        )
        return await self.query(query_filter)

    async def query(self, query_filter: DocFilter) -> list[Article]:
        """
        Query the DOC API with a filter.

        Executes a search using a pre-configured DocFilter object, providing
        full control over all query parameters.

        Args:
            query_filter: DocFilter with query parameters and constraints.

        Returns:
            List of Article objects matching the filter criteria.

        Raises:
            APIError: On HTTP errors or invalid responses.
            APIUnavailableError: When API is down or unreachable.
            RateLimitError: When rate limited by the API.

        Example:
            >>> from py_gdelt.filters import DocFilter
            >>> from datetime import datetime
            >>> async with DocEndpoint() as doc:
            ...     # Complex query with datetime range
            ...     doc_filter = DocFilter(
            ...         query='"machine learning" AND python',
            ...         start_datetime=datetime(2024, 1, 1),
            ...         end_datetime=datetime(2024, 1, 31),
            ...         source_country="US",
            ...         max_results=100,
            ...         sort_by="relevance"
            ...     )
            ...     articles = await doc.query(doc_filter)
        """
        from py_gdelt.models.articles import Article

        params = self._build_params(query_filter)
        url = await self._build_url()

        data = await self._get_json(url, params=params)

        # Parse response - handle both empty and populated responses
        return [Article.model_validate(item) for item in data.get("articles", [])]

    async def timeline(
        self,
        query: str,
        *,
        timespan: str | None = "7d",
    ) -> Timeline:
        """
        Get timeline data for a query.

        Returns time series data showing article volume over time for a given
        search query. Useful for visualizing trends and tracking story evolution.

        Args:
            query: Search query string.
            timespan: Time range to analyze (default: "7d" - 7 days).
                     Common values: "24h", "7d", "30d", "3mon".

        Returns:
            Timeline object with time series data points.

        Raises:
            APIError: On HTTP errors or invalid responses.
            APIUnavailableError: When API is down or unreachable.
            RateLimitError: When rate limited by the API.

        Example:
            >>> async with DocEndpoint() as doc:
            ...     # Get article volume over last month
            ...     timeline = await doc.timeline("protests", timespan="30d")
            ...     for point in timeline.points:
            ...         print(f"{point.date}: {point.value} articles")
        """
        from py_gdelt.models.articles import Timeline

        query_filter = DocFilter(
            query=query,
            timespan=timespan,
            mode="timelinevol",  # GDELT API uses 'timelinevol', not 'timeline'
        )

        params = self._build_params(query_filter)
        url = await self._build_url()

        data = await self._get_json(url, params=params)
        return Timeline.model_validate(data)
