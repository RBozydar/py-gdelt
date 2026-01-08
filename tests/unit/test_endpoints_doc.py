"""
Unit tests for DocEndpoint.

Tests cover parameter building, API interaction, response parsing,
and error handling for the GDELT DOC 2.0 API endpoint.
"""

from __future__ import annotations

from datetime import datetime

import httpx
import pytest
import respx

from py_gdelt.endpoints.doc import DocEndpoint
from py_gdelt.exceptions import APIError
from py_gdelt.filters import DocFilter


class TestBuildParams:
    """Test query parameter building from DocFilter."""

    def test_build_params_basic(self) -> None:
        """Test basic parameter building with minimal filter."""
        filter = DocFilter(query="test query")
        endpoint = DocEndpoint()
        params = endpoint._build_params(filter)

        assert params["query"] == "test query"
        assert params["format"] == "json"
        assert params["mode"] == "artlist"
        assert params["maxrecords"] == "250"
        assert params["sort"] == "date"

    def test_build_params_with_timespan(self) -> None:
        """Test params with timespan constraint."""
        filter = DocFilter(query="test", timespan="24h")
        endpoint = DocEndpoint()
        params = endpoint._build_params(filter)

        assert params["timespan"] == "24h"
        assert "startdatetime" not in params
        assert "enddatetime" not in params

    def test_build_params_with_datetime_range(self) -> None:
        """Test params with start and end datetime."""
        filter = DocFilter(
            query="test",
            start_datetime=datetime(2024, 1, 1, 12, 0, 0),
            end_datetime=datetime(2024, 1, 2, 12, 0, 0),
        )
        endpoint = DocEndpoint()
        params = endpoint._build_params(filter)

        assert params["startdatetime"] == "20240101120000"
        assert params["enddatetime"] == "20240102120000"
        assert "timespan" not in params

    def test_build_params_with_start_datetime_only(self) -> None:
        """Test params with only start datetime (no end)."""
        filter = DocFilter(
            query="test",
            start_datetime=datetime(2024, 1, 1, 0, 0, 0),
        )
        endpoint = DocEndpoint()
        params = endpoint._build_params(filter)

        assert params["startdatetime"] == "20240101000000"
        assert "enddatetime" not in params

    def test_build_params_sort_mapping(self) -> None:
        """Test sort parameter mapping to API values."""
        test_cases = [
            ("date", "date"),
            ("relevance", "rel"),
            ("tone", "tonedesc"),
        ]

        for input_sort, expected in test_cases:
            filter = DocFilter(query="test", sort_by=input_sort)  # type: ignore[arg-type]
            endpoint = DocEndpoint()
            params = endpoint._build_params(filter)
            assert params["sort"] == expected

    def test_build_params_with_source_filters(self) -> None:
        """Test params with source language and country filters."""
        filter = DocFilter(
            query="test",
            source_language="en",
            source_country="US",
        )
        endpoint = DocEndpoint()
        params = endpoint._build_params(filter)

        assert params["sourcelang"] == "en"
        assert params["sourcecountry"] == "US"

    def test_build_params_max_results(self) -> None:
        """Test max_results parameter conversion."""
        filter = DocFilter(query="test", max_results=100)
        endpoint = DocEndpoint()
        params = endpoint._build_params(filter)

        assert params["maxrecords"] == "100"

    def test_build_params_timelinevol_mode(self) -> None:
        """Test params for timelinevol mode (used by timeline method)."""
        filter = DocFilter(query="test", mode="timelinevol")
        endpoint = DocEndpoint()
        params = endpoint._build_params(filter)

        assert params["mode"] == "timelinevol"


class TestBuildUrl:
    """Test URL building."""

    @pytest.mark.asyncio
    async def test_build_url(self) -> None:
        """Test URL building returns base URL."""
        endpoint = DocEndpoint()
        url = await endpoint._build_url()

        assert url == "https://api.gdeltproject.org/api/v2/doc/doc"


class TestSearchMethod:
    """Test the convenience search() method."""

    @respx.mock
    @pytest.mark.asyncio
    async def test_search_basic(self) -> None:
        """Test basic search with minimal parameters."""
        respx.get("https://api.gdeltproject.org/api/v2/doc/doc").mock(
            return_value=httpx.Response(
                200,
                json={
                    "articles": [
                        {
                            "url": "https://example.com/article1",
                            "title": "Test Article",
                            "seendate": "20240101120000",
                            "sourcecountry": "US",
                            "language": "English",
                            "domain": "example.com",
                        },
                    ],
                },
            ),
        )

        async with DocEndpoint() as doc:
            articles = await doc.search("test query")
            assert len(articles) == 1
            assert articles[0].title == "Test Article"
            assert articles[0].url == "https://example.com/article1"
            assert articles[0].source_country == "US"

    @respx.mock
    @pytest.mark.asyncio
    async def test_search_with_all_params(self) -> None:
        """Test search with all optional parameters."""
        route = respx.get("https://api.gdeltproject.org/api/v2/doc/doc").mock(
            return_value=httpx.Response(200, json={"articles": []}),
        )

        async with DocEndpoint() as doc:
            await doc.search(
                "climate change",
                timespan="7d",
                max_results=50,
                sort_by="relevance",
                source_language="en",
                source_country="US",
            )

            # Verify request params
            request = route.calls.last.request
            assert request.url.params["query"] == "climate change"
            assert request.url.params["timespan"] == "7d"
            assert request.url.params["maxrecords"] == "50"
            assert request.url.params["sort"] == "rel"
            assert request.url.params["sourcelang"] == "en"
            assert request.url.params["sourcecountry"] == "US"

    @respx.mock
    @pytest.mark.asyncio
    async def test_search_multiple_articles(self) -> None:
        """Test search returning multiple articles."""
        respx.get("https://api.gdeltproject.org/api/v2/doc/doc").mock(
            return_value=httpx.Response(
                200,
                json={
                    "articles": [
                        {
                            "url": "https://example.com/1",
                            "title": "Article 1",
                            "seendate": "20240101120000",
                        },
                        {
                            "url": "https://example.com/2",
                            "title": "Article 2",
                            "seendate": "20240101130000",
                        },
                        {
                            "url": "https://example.com/3",
                            "title": "Article 3",
                            "seendate": "20240101140000",
                        },
                    ],
                },
            ),
        )

        async with DocEndpoint() as doc:
            articles = await doc.search("test")
            assert len(articles) == 3
            assert [a.title for a in articles] == ["Article 1", "Article 2", "Article 3"]


class TestQueryMethod:
    """Test the query() method with DocFilter."""

    @respx.mock
    @pytest.mark.asyncio
    async def test_query_with_filter(self) -> None:
        """Test query method with DocFilter object."""
        respx.get("https://api.gdeltproject.org/api/v2/doc/doc").mock(
            return_value=httpx.Response(
                200,
                json={
                    "articles": [
                        {
                            "url": "https://example.com/test",
                            "title": "Filtered Article",
                            "seendate": "20240101120000",
                        },
                    ],
                },
            ),
        )

        async with DocEndpoint() as doc:
            filter = DocFilter(query="climate change", timespan="24h", max_results=10)
            articles = await doc.query(filter)

            assert len(articles) == 1
            assert articles[0].title == "Filtered Article"

    @respx.mock
    @pytest.mark.asyncio
    async def test_query_empty_results(self) -> None:
        """Test query with no matching articles."""
        respx.get("https://api.gdeltproject.org/api/v2/doc/doc").mock(
            return_value=httpx.Response(200, json={"articles": []}),
        )

        async with DocEndpoint() as doc:
            filter = DocFilter(query="nonexistent query string")
            articles = await doc.query(filter)

            assert articles == []

    @respx.mock
    @pytest.mark.asyncio
    async def test_query_complex_filter(self) -> None:
        """Test query with complex filter parameters."""
        route = respx.get("https://api.gdeltproject.org/api/v2/doc/doc").mock(
            return_value=httpx.Response(200, json={"articles": []}),
        )

        async with DocEndpoint() as doc:
            filter = DocFilter(
                query='"machine learning" AND python',
                start_datetime=datetime(2024, 1, 1, 0, 0, 0),
                end_datetime=datetime(2024, 1, 31, 23, 59, 59),
                source_country="US",
                source_language="en",
                max_results=100,
                sort_by="relevance",
            )
            await doc.query(filter)

            # Verify parameters
            request = route.calls.last.request
            assert request.url.params["startdatetime"] == "20240101000000"
            assert request.url.params["enddatetime"] == "20240131235959"
            assert request.url.params["sourcecountry"] == "US"
            assert request.url.params["sort"] == "rel"


class TestTimelineMethod:
    """Test the timeline() method."""

    @respx.mock
    @pytest.mark.asyncio
    async def test_timeline_basic(self) -> None:
        """Test timeline method with basic parameters."""
        respx.get("https://api.gdeltproject.org/api/v2/doc/doc").mock(
            return_value=httpx.Response(
                200,
                json={
                    "timeline": [
                        {"date": "2024-01-01", "value": 100},
                        {"date": "2024-01-02", "value": 150},
                        {"date": "2024-01-03", "value": 120},
                    ],
                },
            ),
        )

        async with DocEndpoint() as doc:
            timeline = await doc.timeline("test query")

            assert len(timeline.points) == 3
            assert timeline.points[0].date == "2024-01-01"
            assert timeline.points[0].value == 100
            assert timeline.points[1].value == 150

    @respx.mock
    @pytest.mark.asyncio
    async def test_timeline_custom_timespan(self) -> None:
        """Test timeline with custom timespan."""
        route = respx.get("https://api.gdeltproject.org/api/v2/doc/doc").mock(
            return_value=httpx.Response(200, json={"timeline": []}),
        )

        async with DocEndpoint() as doc:
            await doc.timeline("protests", timespan="30d")

            # Verify mode and timespan
            request = route.calls.last.request
            assert request.url.params["mode"] == "timelinevol"
            assert request.url.params["timespan"] == "30d"

    @respx.mock
    @pytest.mark.asyncio
    async def test_timeline_empty(self) -> None:
        """Test timeline with no data points."""
        respx.get("https://api.gdeltproject.org/api/v2/doc/doc").mock(
            return_value=httpx.Response(200, json={"timeline": []}),
        )

        async with DocEndpoint() as doc:
            timeline = await doc.timeline("nonexistent")

            assert timeline.points == []
            assert len(timeline.points) == 0


class TestResponseHandling:
    """Test response parsing and error handling."""

    @respx.mock
    @pytest.mark.asyncio
    async def test_empty_response(self) -> None:
        """Test handling of empty JSON response."""
        respx.get("https://api.gdeltproject.org/api/v2/doc/doc").mock(
            return_value=httpx.Response(200, json={}),
        )

        async with DocEndpoint() as doc:
            articles = await doc.search("test")
            assert articles == []

    @respx.mock
    @pytest.mark.asyncio
    async def test_missing_articles_key(self) -> None:
        """Test handling when 'articles' key is missing."""
        respx.get("https://api.gdeltproject.org/api/v2/doc/doc").mock(
            return_value=httpx.Response(200, json={"other_key": "value"}),
        )

        async with DocEndpoint() as doc:
            articles = await doc.search("test")
            assert articles == []

    @respx.mock
    @pytest.mark.asyncio
    async def test_http_error_handling(self) -> None:
        """Test handling of HTTP errors."""
        respx.get("https://api.gdeltproject.org/api/v2/doc/doc").mock(
            return_value=httpx.Response(400, text="Bad Request"),
        )

        async with DocEndpoint() as doc:
            with pytest.raises(APIError):
                await doc.search("test")

    @respx.mock
    @pytest.mark.asyncio
    async def test_article_with_optional_fields(self) -> None:
        """Test parsing article with all optional fields."""
        respx.get("https://api.gdeltproject.org/api/v2/doc/doc").mock(
            return_value=httpx.Response(
                200,
                json={
                    "articles": [
                        {
                            "url": "https://example.com/full",
                            "title": "Complete Article",
                            "seendate": "20240101120000",
                            "domain": "example.com",
                            "sourcecountry": "US",
                            "language": "English",
                            "socialimage": "https://example.com/image.jpg",
                            "tone": 2.5,
                            "sharecount": 1000,
                        },
                    ],
                },
            ),
        )

        async with DocEndpoint() as doc:
            articles = await doc.search("test")
            article = articles[0]

            assert article.url == "https://example.com/full"
            assert article.title == "Complete Article"
            assert article.domain == "example.com"
            assert article.source_country == "US"
            assert article.language == "English"
            assert article.socialimage == "https://example.com/image.jpg"
            assert article.tone == 2.5
            assert article.share_count == 1000


class TestContextManager:
    """Test async context manager functionality."""

    @respx.mock
    @pytest.mark.asyncio
    async def test_context_manager(self) -> None:
        """Test using endpoint as async context manager."""
        respx.get("https://api.gdeltproject.org/api/v2/doc/doc").mock(
            return_value=httpx.Response(200, json={"articles": []}),
        )

        async with DocEndpoint() as doc:
            articles = await doc.search("test")
            assert articles == []
            # Client should be open inside context
            assert doc._client is not None

    @pytest.mark.asyncio
    async def test_manual_lifecycle(self) -> None:
        """Test manual open/close of endpoint."""
        endpoint = DocEndpoint()
        assert endpoint._client is not None

        await endpoint.close()
        # Client should be closed (but reference still exists)
        assert endpoint._client is not None


class TestIntegrationScenarios:
    """Test realistic usage scenarios."""

    @respx.mock
    @pytest.mark.asyncio
    async def test_search_workflow(self) -> None:
        """Test a complete search workflow."""
        respx.get("https://api.gdeltproject.org/api/v2/doc/doc").mock(
            return_value=httpx.Response(
                200,
                json={
                    "articles": [
                        {
                            "url": f"https://example.com/{i}",
                            "title": f"Article {i}",
                            "seendate": f"2024010{i}120000",
                            "sourcecountry": "US",
                            "language": "English",
                        }
                        for i in range(1, 6)
                    ],
                },
            ),
        )

        async with DocEndpoint() as doc:
            # Search for articles
            articles = await doc.search(
                "artificial intelligence",
                timespan="7d",
                max_results=50,
                sort_by="relevance",
            )

            # Process results
            assert len(articles) == 5
            for article in articles:
                assert article.url.startswith("https://example.com/")
                assert article.source_country == "US"
                assert article.is_english

    @respx.mock
    @pytest.mark.asyncio
    async def test_timeline_analysis_workflow(self) -> None:
        """Test timeline analysis workflow."""
        respx.get("https://api.gdeltproject.org/api/v2/doc/doc").mock(
            return_value=httpx.Response(
                200,
                json={
                    "timeline": [
                        {"date": f"2024-01-{i:02d}", "value": i * 10} for i in range(1, 31)
                    ],
                },
            ),
        )

        async with DocEndpoint() as doc:
            timeline = await doc.timeline("climate protests", timespan="30d")

            # Analyze timeline
            assert len(timeline.points) == 30
            assert len(timeline.dates) == 30
            assert len(timeline.values) == 30

            # Check conversion to series
            series = timeline.to_series()
            assert "2024-01-15" in series
            assert series["2024-01-15"] == 150
