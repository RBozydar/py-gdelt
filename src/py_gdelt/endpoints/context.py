"""Context 2.0 API endpoint for contextual analysis.

This module provides the ContextEndpoint class for accessing GDELT's Context API,
which provides contextual information about search terms including related themes,
entities, and sentiment analysis.

See: https://blog.gdeltproject.org/announcing-the-gdelt-context-2-0-api/
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from py_gdelt.endpoints.base import BaseEndpoint


__all__ = [
    "ContextEndpoint",
    "ContextEntity",
    "ContextResult",
    "ContextTheme",
    "ContextTone",
]


class ContextTheme(BaseModel):
    """Theme mentioned in context.

    Represents a GDELT theme that appears in articles related to the search query.
    Themes are standardized categories that GDELT assigns to content.

    Attributes:
        theme: Theme identifier (e.g., "ENV_CLIMATE", "POLITICS")
        count: Number of times the theme appears
        score: Optional relevance score (0.0 to 1.0)
    """

    theme: str
    count: int
    score: float | None = None


class ContextEntity(BaseModel):
    """Entity mentioned in context.

    Represents a named entity (person, organization, location) extracted from
    articles related to the search query.

    Attributes:
        name: Entity name
        entity_type: Type of entity (PERSON, ORG, LOCATION, UNKNOWN)
        count: Number of mentions
    """

    name: str
    entity_type: str
    count: int


class ContextTone(BaseModel):
    """Tone analysis for context.

    Sentiment analysis aggregated across all articles related to the search query.

    Attributes:
        average_tone: Average tone score (negative = negative sentiment)
        positive_count: Number of articles with positive tone
        negative_count: Number of articles with negative tone
        neutral_count: Number of articles with neutral tone
    """

    average_tone: float
    positive_count: int
    negative_count: int
    neutral_count: int


class ContextResult(BaseModel):
    """Result from Context API query.

    Complete contextual analysis for a search term, including themes, entities,
    sentiment, and related search queries.

    Attributes:
        query: Original search query
        article_count: Total number of articles analyzed
        themes: List of themes found in the context
        entities: List of entities found in the context
        tone: Aggregate tone analysis (if available)
        related_queries: Suggested related search terms
    """

    query: str
    article_count: int = 0
    themes: list[ContextTheme] = []
    entities: list[ContextEntity] = []
    tone: ContextTone | None = None
    related_queries: list[str] = []


class ContextEndpoint(BaseEndpoint):
    """Context 2.0 API endpoint for contextual analysis.

    Provides contextual information about search terms including
    related themes, entities, and sentiment analysis.

    Attributes:
        BASE_URL: Base URL for the Context API endpoint

    Example:
        async with ContextEndpoint() as ctx:
            result = await ctx.analyze("climate change")
            for theme in result.themes[:5]:
                print(f"{theme.theme}: {theme.count} mentions")
    """

    BASE_URL = "https://api.gdeltproject.org/api/v2/context/context"

    async def __aenter__(self) -> ContextEndpoint:
        """Async context manager entry.

        Returns:
            Self for use in async with statement.
        """
        await super().__aenter__()
        return self

    async def _build_url(self, **kwargs: Any) -> str:
        """Build Context API URL.

        The Context API uses a single endpoint URL with query parameters.

        Args:
            **kwargs: Unused, included for BaseEndpoint compatibility.

        Returns:
            Base URL for Context API.
        """
        return self.BASE_URL

    def _build_params(
        self,
        query: str,
        timespan: str | None = None,
    ) -> dict[str, str]:
        """Build query parameters for Context API request.

        Args:
            query: Search term to analyze
            timespan: Time range (e.g., "24h", "7d", "30d")

        Returns:
            Dictionary of query parameters for the API request.
        """
        params: dict[str, str] = {
            "query": query,
            "format": "json",
            "mode": "artlist",  # GDELT Context API only supports 'artlist' mode
        }

        if timespan:
            params["timespan"] = timespan

        return params

    async def analyze(
        self,
        query: str,
        *,
        timespan: str | None = None,
    ) -> ContextResult:
        """Get contextual analysis for a search term.

        Retrieves comprehensive contextual information including themes, entities,
        tone analysis, and related queries for the specified search term.

        Args:
            query: Search term to analyze
            timespan: Time range (e.g., "24h", "7d", "30d")

        Returns:
            ContextResult with themes, entities, and tone analysis

        Raises:
            RateLimitError: On 429 response
            APIUnavailableError: On 5xx response or connection error
            APIError: On other HTTP errors or invalid JSON
        """
        params = self._build_params(query, timespan)
        url = await self._build_url()

        data = await self._get_json(url, params=params)

        # Parse themes
        themes: list[ContextTheme] = [
            ContextTheme(
                theme=item.get("theme", ""),
                count=item.get("count", 0),
                score=item.get("score"),
            )
            for item in data.get("themes", [])
        ]

        # Parse entities
        entities: list[ContextEntity] = [
            ContextEntity(
                name=item.get("name", ""),
                entity_type=item.get("type", "UNKNOWN"),
                count=item.get("count", 0),
            )
            for item in data.get("entities", [])
        ]

        # Parse tone
        tone: ContextTone | None = None
        if "tone" in data:
            t = data["tone"]
            tone = ContextTone(
                average_tone=t.get("average", 0.0),
                positive_count=t.get("positive", 0),
                negative_count=t.get("negative", 0),
                neutral_count=t.get("neutral", 0),
            )

        # Parse related queries
        related = data.get("related_queries", [])
        related_queries = [str(q) for q in related] if isinstance(related, list) else []

        return ContextResult(
            query=query,
            article_count=data.get("article_count", 0),
            themes=themes,
            entities=entities,
            tone=tone,
            related_queries=related_queries,
        )

    async def get_themes(
        self,
        query: str,
        *,
        timespan: str | None = None,
        limit: int = 10,
    ) -> list[ContextTheme]:
        """Get top themes for a search term.

        Convenience method that returns just themes sorted by count.

        Args:
            query: Search term
            timespan: Time range
            limit: Max themes to return

        Returns:
            List of top themes sorted by count (descending)

        Raises:
            RateLimitError: On 429 response
            APIUnavailableError: On 5xx response or connection error
            APIError: On other HTTP errors or invalid JSON
        """
        result = await self.analyze(query, timespan=timespan)
        sorted_themes = sorted(result.themes, key=lambda t: t.count, reverse=True)
        return sorted_themes[:limit]

    async def get_entities(
        self,
        query: str,
        *,
        timespan: str | None = None,
        entity_type: str | None = None,
        limit: int = 10,
    ) -> list[ContextEntity]:
        """Get top entities for a search term.

        Convenience method that returns entities, optionally filtered by type
        and sorted by count.

        Args:
            query: Search term
            timespan: Time range
            entity_type: Filter by type (PERSON, ORG, LOCATION)
            limit: Max entities to return

        Returns:
            List of top entities sorted by count (descending)

        Raises:
            RateLimitError: On 429 response
            APIUnavailableError: On 5xx response or connection error
            APIError: On other HTTP errors or invalid JSON
        """
        result = await self.analyze(query, timespan=timespan)

        entities = result.entities
        if entity_type:
            entities = [e for e in entities if e.entity_type == entity_type]

        sorted_entities = sorted(entities, key=lambda e: e.count, reverse=True)
        return sorted_entities[:limit]
