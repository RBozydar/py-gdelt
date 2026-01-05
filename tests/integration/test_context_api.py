"""Integration tests for Context 2.0 API."""

import pytest

from py_gdelt import GDELTClient


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.timeout(60)
async def test_context_analyze_returns_result(gdelt_client: GDELTClient) -> None:
    """Test contextual analysis returns structured result."""
    result = await gdelt_client.context.analyze(
        "technology",
        timespan="7d",
    )

    assert hasattr(result, "query")
    assert result.query == "technology"
    assert hasattr(result, "themes")
    assert hasattr(result, "entities")
    assert isinstance(result.themes, list)
    assert isinstance(result.entities, list)


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.timeout(60)
async def test_context_get_themes(gdelt_client: GDELTClient) -> None:
    """Test getting themes for a topic."""
    themes = await gdelt_client.context.get_themes(
        "climate change",
        limit=5,
    )

    assert isinstance(themes, list)
    assert len(themes) <= 5

    if themes:
        theme = themes[0]
        assert hasattr(theme, "theme")
        assert hasattr(theme, "count")
        assert theme.count >= 0


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.timeout(60)
async def test_context_get_entities(gdelt_client: GDELTClient) -> None:
    """Test getting entities for a topic."""
    entities = await gdelt_client.context.get_entities(
        "economy",
        limit=10,
    )

    assert isinstance(entities, list)
    assert len(entities) <= 10

    if entities:
        entity = entities[0]
        assert hasattr(entity, "name")
        assert hasattr(entity, "entity_type")
        assert hasattr(entity, "count")
        assert entity.count > 0


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.timeout(60)
async def test_context_get_entities_by_type(gdelt_client: GDELTClient) -> None:
    """Test filtering entities by type."""
    people = await gdelt_client.context.get_entities(
        "election",
        entity_type="PERSON",
        timespan="7d",
        limit=5,
    )

    assert isinstance(people, list)

    # If we got results, verify they're people
    if people:
        for person in people:
            assert person.entity_type == "PERSON"


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.timeout(60)
async def test_context_tone_analysis(gdelt_client: GDELTClient) -> None:
    """Test tone analysis in context results."""
    result = await gdelt_client.context.analyze(
        "healthcare",
        timespan="7d",
    )

    # Tone may be None if not available
    if result.tone:
        assert hasattr(result.tone, "average_tone")
        assert hasattr(result.tone, "positive_count")
        assert hasattr(result.tone, "negative_count")
        assert hasattr(result.tone, "neutral_count")
        # Average tone should be a float
        assert isinstance(result.tone.average_tone, (int, float))


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.timeout(60)
async def test_context_article_count(gdelt_client: GDELTClient) -> None:
    """Test that article count is returned."""
    result = await gdelt_client.context.analyze(
        "artificial intelligence",
        timespan="24h",
    )

    assert hasattr(result, "article_count")
    assert isinstance(result.article_count, int)
    assert result.article_count >= 0
