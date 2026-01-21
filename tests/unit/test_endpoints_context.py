"""Unit tests for Context 2.0 API endpoint."""

from __future__ import annotations

import httpx
import pytest
import respx

from py_gdelt.endpoints.context import (
    ContextEndpoint,
    ContextEntity,
    ContextResult,
    ContextTheme,
    ContextTone,
)


# Parameter Building Tests
def test_build_params_basic() -> None:
    """Test basic parameter building."""
    endpoint = ContextEndpoint()
    params = endpoint._build_params("test query")

    assert params["query"] == "test query"
    assert params["format"] == "json"
    assert params["mode"] == "artlist"


def test_build_params_with_timespan() -> None:
    """Test params with timespan."""
    endpoint = ContextEndpoint()
    params = endpoint._build_params("test", timespan="7d")

    assert params["timespan"] == "7d"


def test_build_params_without_timespan() -> None:
    """Test params without optional timespan."""
    endpoint = ContextEndpoint()
    params = endpoint._build_params("test")

    assert "timespan" not in params


# Model Tests
def test_context_theme_creation() -> None:
    """Test ContextTheme model."""
    theme = ContextTheme(theme="ENV_CLIMATE", count=100, score=0.85)
    assert theme.theme == "ENV_CLIMATE"
    assert theme.count == 100
    assert theme.score == 0.85


def test_context_theme_without_score() -> None:
    """Test ContextTheme with optional score omitted."""
    theme = ContextTheme(theme="POLITICS", count=50)
    assert theme.theme == "POLITICS"
    assert theme.count == 50
    assert theme.score is None


def test_context_entity_creation() -> None:
    """Test ContextEntity model."""
    entity = ContextEntity(name="John Doe", entity_type="PERSON", count=50)
    assert entity.name == "John Doe"
    assert entity.entity_type == "PERSON"
    assert entity.count == 50


def test_context_tone_creation() -> None:
    """Test ContextTone model."""
    tone = ContextTone(average_tone=-2.5, positive_count=100, negative_count=150, neutral_count=50)
    assert tone.average_tone == -2.5
    assert tone.positive_count == 100
    assert tone.negative_count == 150
    assert tone.neutral_count == 50


def test_context_result_creation() -> None:
    """Test ContextResult model."""
    result = ContextResult(
        query="climate",
        article_count=1000,
        themes=[ContextTheme(theme="ENV", count=500)],
        entities=[],
    )
    assert result.query == "climate"
    assert result.article_count == 1000
    assert len(result.themes) == 1
    assert len(result.entities) == 0


def test_context_result_defaults() -> None:
    """Test ContextResult with default values."""
    result = ContextResult(query="test")
    assert result.query == "test"
    assert result.article_count == 0
    assert result.themes == []
    assert result.entities == []
    assert result.tone is None
    assert result.related_queries == []


# API Tests (using respx)
@respx.mock
@pytest.mark.asyncio
async def test_analyze() -> None:
    """Test analyze method."""
    respx.get("https://api.gdeltproject.org/api/v2/context/context").mock(
        return_value=httpx.Response(
            200,
            json={
                "article_count": 500,
                "themes": [
                    {"theme": "ENV_CLIMATE", "count": 100, "score": 0.9},
                    {"theme": "POLITICS", "count": 50},
                ],
                "entities": [{"name": "United Nations", "type": "ORG", "count": 30}],
                "tone": {
                    "average": -1.5,
                    "positive": 100,
                    "negative": 200,
                    "neutral": 200,
                },
                "related_queries": ["global warming", "carbon emissions"],
            },
        ),
    )

    async with ContextEndpoint() as ctx:
        result = await ctx.analyze("climate change")

        assert result.article_count == 500
        assert len(result.themes) == 2
        assert result.themes[0].theme == "ENV_CLIMATE"
        assert result.themes[0].count == 100
        assert result.themes[0].score == 0.9
        assert result.themes[1].theme == "POLITICS"
        assert result.themes[1].count == 50
        assert result.themes[1].score is None
        assert len(result.entities) == 1
        assert result.entities[0].name == "United Nations"
        assert result.entities[0].entity_type == "ORG"
        assert result.tone is not None
        assert result.tone.average_tone == -1.5
        assert result.tone.positive_count == 100
        assert result.tone.negative_count == 200
        assert result.tone.neutral_count == 200
        assert len(result.related_queries) == 2
        assert "global warming" in result.related_queries


@respx.mock
@pytest.mark.asyncio
async def test_analyze_with_timespan() -> None:
    """Test analyze method with timespan parameter."""
    route = respx.get("https://api.gdeltproject.org/api/v2/context/context").mock(
        return_value=httpx.Response(200, json={"article_count": 100}),
    )

    async with ContextEndpoint() as ctx:
        await ctx.analyze("test", timespan="24h")

        # Verify timespan was included in request
        assert route.called
        assert route.calls.last.request.url.params["timespan"] == "24h"


@respx.mock
@pytest.mark.asyncio
async def test_get_themes() -> None:
    """Test get_themes convenience method."""
    respx.get("https://api.gdeltproject.org/api/v2/context/context").mock(
        return_value=httpx.Response(
            200,
            json={
                "themes": [
                    {"theme": "A", "count": 10},
                    {"theme": "B", "count": 30},
                    {"theme": "C", "count": 20},
                ],
            },
        ),
    )

    async with ContextEndpoint() as ctx:
        themes = await ctx.get_themes("test", limit=2)

        assert len(themes) == 2
        assert themes[0].theme == "B"  # Sorted by count
        assert themes[0].count == 30
        assert themes[1].theme == "C"
        assert themes[1].count == 20


@respx.mock
@pytest.mark.asyncio
async def test_get_themes_no_limit() -> None:
    """Test get_themes returns all themes when count is less than limit."""
    respx.get("https://api.gdeltproject.org/api/v2/context/context").mock(
        return_value=httpx.Response(200, json={"themes": [{"theme": "A", "count": 10}]}),
    )

    async with ContextEndpoint() as ctx:
        themes = await ctx.get_themes("test", limit=10)

        assert len(themes) == 1


@respx.mock
@pytest.mark.asyncio
async def test_get_entities_with_filter() -> None:
    """Test get_entities with type filter."""
    respx.get("https://api.gdeltproject.org/api/v2/context/context").mock(
        return_value=httpx.Response(
            200,
            json={
                "entities": [
                    {"name": "John", "type": "PERSON", "count": 10},
                    {"name": "Acme Corp", "type": "ORG", "count": 20},
                    {"name": "Jane", "type": "PERSON", "count": 15},
                ],
            },
        ),
    )

    async with ContextEndpoint() as ctx:
        entities = await ctx.get_entities("test", entity_type="PERSON")

        assert len(entities) == 2
        assert all(e.entity_type == "PERSON" for e in entities)
        assert entities[0].name == "Jane"  # Higher count
        assert entities[0].count == 15
        assert entities[1].name == "John"
        assert entities[1].count == 10


@respx.mock
@pytest.mark.asyncio
async def test_get_entities_without_filter() -> None:
    """Test get_entities without type filter."""
    respx.get("https://api.gdeltproject.org/api/v2/context/context").mock(
        return_value=httpx.Response(
            200,
            json={
                "entities": [
                    {"name": "A", "type": "PERSON", "count": 10},
                    {"name": "B", "type": "ORG", "count": 20},
                ],
            },
        ),
    )

    async with ContextEndpoint() as ctx:
        entities = await ctx.get_entities("test", limit=10)

        assert len(entities) == 2
        assert entities[0].name == "B"  # Sorted by count


@respx.mock
@pytest.mark.asyncio
async def test_get_entities_with_limit() -> None:
    """Test get_entities respects limit parameter."""
    respx.get("https://api.gdeltproject.org/api/v2/context/context").mock(
        return_value=httpx.Response(
            200,
            json={
                "entities": [
                    {"name": "A", "type": "PERSON", "count": 30},
                    {"name": "B", "type": "ORG", "count": 20},
                    {"name": "C", "type": "LOCATION", "count": 10},
                ],
            },
        ),
    )

    async with ContextEndpoint() as ctx:
        entities = await ctx.get_entities("test", limit=2)

        assert len(entities) == 2
        assert entities[0].count == 30
        assert entities[1].count == 20


@respx.mock
@pytest.mark.asyncio
async def test_empty_response() -> None:
    """Test handling of empty response."""
    respx.get("https://api.gdeltproject.org/api/v2/context/context").mock(
        return_value=httpx.Response(200, json={}),
    )

    async with ContextEndpoint() as ctx:
        result = await ctx.analyze("nonexistent")

        assert result.article_count == 0
        assert result.themes == []
        assert result.entities == []
        assert result.tone is None
        assert result.related_queries == []


@respx.mock
@pytest.mark.asyncio
async def test_partial_response() -> None:
    """Test handling of response with only some fields."""
    respx.get("https://api.gdeltproject.org/api/v2/context/context").mock(
        return_value=httpx.Response(
            200,
            json={
                "article_count": 50,
                "themes": [{"theme": "TEST", "count": 5}],
                # Missing entities, tone, related_queries
            },
        ),
    )

    async with ContextEndpoint() as ctx:
        result = await ctx.analyze("test")

        assert result.article_count == 50
        assert len(result.themes) == 1
        assert result.entities == []
        assert result.tone is None
        assert result.related_queries == []


@respx.mock
@pytest.mark.asyncio
async def test_malformed_related_queries() -> None:
    """Test handling of non-list related_queries."""
    respx.get("https://api.gdeltproject.org/api/v2/context/context").mock(
        return_value=httpx.Response(
            200,
            json={"related_queries": "not a list"},  # Invalid type
        ),
    )

    async with ContextEndpoint() as ctx:
        result = await ctx.analyze("test")

        assert result.related_queries == []


@respx.mock
@pytest.mark.asyncio
async def test_build_url() -> None:
    """Test _build_url returns correct base URL."""
    endpoint = ContextEndpoint()
    url = await endpoint._build_url()

    assert url == "https://api.gdeltproject.org/api/v2/context/context"


@pytest.mark.asyncio
async def test_context_manager() -> None:
    """Test async context manager lifecycle."""
    async with ContextEndpoint() as ctx:
        assert ctx._client is not None
        assert ctx._owns_client is True

    # Client should be closed after context exit
    # Note: We can't directly test if client is closed, but no exception is good


def test_base_url_attribute() -> None:
    """Test BASE_URL class attribute is set correctly."""
    assert ContextEndpoint.BASE_URL == "https://api.gdeltproject.org/api/v2/context/context"
