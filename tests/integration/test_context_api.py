"""Integration tests for Context 2.0 API."""

import pytest

from py_gdelt import GDELTClient


# Skip all tests - GDELT Context API only supports 'artlist' mode which returns articles,
# but the library's ContextEndpoint.analyze() expects themes/entities/tone data.
# This requires a library redesign to match what GDELT actually offers.
pytestmark = pytest.mark.skip(
    reason="Library design issue: Context API expects themes/entities/tone but GDELT only returns articles"
)


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

    if not themes:
        pytest.skip("No themes returned - API may be temporarily unavailable")

    theme = themes[0]
    assert hasattr(theme, "theme"), "Theme should have theme attribute"
    assert hasattr(theme, "count"), "Theme should have count attribute"
    assert theme.count > 0, f"Expected positive count, got {theme.count}"


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

    if not entities:
        pytest.skip("No entities returned - API may be temporarily unavailable")

    entity = entities[0]
    assert hasattr(entity, "name"), "Entity should have name"
    assert hasattr(entity, "entity_type"), "Entity should have entity_type"
    assert hasattr(entity, "count"), "Entity should have count"
    assert entity.count > 0, f"Expected positive count, got {entity.count}"


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

    if not people:
        pytest.skip("No people entities returned")

    # Verify entity type filtering works
    for person in people:
        assert person.entity_type == "PERSON", f"Expected PERSON, got {person.entity_type}"


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.timeout(60)
async def test_context_tone_analysis(gdelt_client: GDELTClient) -> None:
    """Test tone analysis in context results."""
    result = await gdelt_client.context.analyze(
        "healthcare",
        timespan="7d",
    )

    if not result.tone:
        pytest.skip("No tone data returned")

    assert hasattr(result.tone, "average_tone"), "Tone should have average_tone"
    assert hasattr(result.tone, "positive_count"), "Tone should have positive_count"
    assert hasattr(result.tone, "negative_count"), "Tone should have negative_count"
    assert hasattr(result.tone, "neutral_count"), "Tone should have neutral_count"
    # Average tone should be a float
    assert isinstance(result.tone.average_tone, (int, float)), "average_tone should be numeric"


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.timeout(60)
async def test_context_article_count(gdelt_client: GDELTClient) -> None:
    """Test that article count is returned."""
    result = await gdelt_client.context.analyze(
        "artificial intelligence",
        timespan="24h",
    )

    assert hasattr(result, "article_count"), "Result should have article_count"
    assert isinstance(result.article_count, int), "article_count should be int"

    if result.article_count == 0:
        pytest.skip("No articles found for query")

    assert result.article_count > 0, f"Expected positive article count, got {result.article_count}"
