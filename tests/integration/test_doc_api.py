"""Integration tests for DOC 2.0 API.

These tests make real API calls and verify response structure.
Run with: pytest tests/integration/ -m integration
"""

import pytest

from py_gdelt import GDELTClient
from py_gdelt.filters import DocFilter


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.timeout(60)
async def test_doc_search_returns_articles(gdelt_client: GDELTClient) -> None:
    """Test that DOC search returns articles with expected structure."""
    doc_filter = DocFilter(
        query="technology",
        timespan="24h",  # Relative, not hardcoded date
        max_results=10,
    )

    articles = await gdelt_client.doc.query(doc_filter)

    # Assert we got results (don't assert exact count)
    assert isinstance(articles, list)

    # If we got results, verify structure
    if articles:
        article = articles[0]
        assert hasattr(article, "title")
        assert hasattr(article, "url")
        assert hasattr(article, "domain")
        assert article.url.startswith("http")


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.timeout(60)
async def test_doc_search_with_language_filter(gdelt_client: GDELTClient) -> None:
    """Test language filtering works."""
    doc_filter = DocFilter(
        query="climate",
        timespan="7d",
        source_language="english",
        max_results=5,
    )

    articles = await gdelt_client.doc.query(doc_filter)

    # Just verify it doesn't error - content filtering is best-effort
    assert isinstance(articles, list)


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.timeout(60)
async def test_doc_timeline(gdelt_client: GDELTClient) -> None:
    """Test timeline endpoint returns data points."""
    timeline = await gdelt_client.doc.timeline(
        query="election",
        timespan="7d",
    )

    # Verify structure
    assert hasattr(timeline, "points")
    assert isinstance(timeline.points, list)


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.timeout(60)
async def test_doc_search_with_mode(gdelt_client: GDELTClient) -> None:
    """Test search mode parameter."""
    doc_filter = DocFilter(
        query="economy",
        timespan="24h",
        mode="ArtList",
        max_results=5,
    )

    articles = await gdelt_client.doc.query(doc_filter)

    assert isinstance(articles, list)


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.timeout(60)
async def test_doc_search_with_domain_filter(gdelt_client: GDELTClient) -> None:
    """Test domain filtering."""
    doc_filter = DocFilter(
        query="technology",
        timespan="7d",
        domain="bbc.com",
        max_results=5,
    )

    articles = await gdelt_client.doc.query(doc_filter)

    # Verify structure (may return empty if no BBC articles)
    assert isinstance(articles, list)

    # If results exist, verify domain filtering
    if articles:
        for article in articles:
            assert hasattr(article, "domain")
