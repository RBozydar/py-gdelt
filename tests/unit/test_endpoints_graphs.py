"""Unit tests for GraphEndpoint.

Tests cover initialization, streaming behavior, language filtering,
and all three error policies for the Graph datasets endpoint.
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, date, datetime
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from py_gdelt.endpoints.graphs import GraphEndpoint, _normalize_languages
from py_gdelt.filters import (
    DateRange,
    GALFilter,
    GEGFilter,
    GEMGFilter,
    GFGFilter,
    GGGFilter,
    GQGFilter,
)
from py_gdelt.models.graphs import (
    GALRecord,
    GEGRecord,
    GEMGRecord,
    GFGRecord,
    GGGRecord,
    GQGRecord,
)


if TYPE_CHECKING:
    from collections.abc import AsyncIterator


@pytest.fixture
def mock_file_source() -> MagicMock:
    """Create mock FileSource."""
    mock = MagicMock()
    mock.__aenter__ = AsyncMock(return_value=mock)
    mock.__aexit__ = AsyncMock(return_value=None)
    return mock


@pytest.fixture
def gqg_filter() -> GQGFilter:
    """Create test GQGFilter."""
    return GQGFilter(
        date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 1)),
    )


@pytest.fixture
def geg_filter() -> GEGFilter:
    """Create test GEGFilter."""
    return GEGFilter(
        date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 1)),
    )


@pytest.fixture
def gfg_filter() -> GFGFilter:
    """Create test GFGFilter."""
    return GFGFilter(
        date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 1)),
    )


@pytest.fixture
def ggg_filter() -> GGGFilter:
    """Create test GGGFilter."""
    return GGGFilter(
        date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 1)),
    )


@pytest.fixture
def gemg_filter() -> GEMGFilter:
    """Create test GEMGFilter."""
    return GEMGFilter(
        date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 1)),
    )


@pytest.fixture
def gal_filter() -> GALFilter:
    """Create test GALFilter."""
    return GALFilter(
        date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 1)),
    )


@pytest.fixture
def sample_gqg_json() -> bytes:
    """Create sample GQG JSON-NL data."""
    record = {
        "date": "20240101120000",
        "url": "https://example.com/article",
        "lang": "en",
        "quotes": [
            {"pre": "He said", "quote": "Hello world", "post": "today."},
        ],
    }
    return json.dumps(record).encode("utf-8")


@pytest.fixture
def sample_geg_json() -> bytes:
    """Create sample GEG JSON-NL data."""
    record = {
        "date": "20240101120000",
        "url": "https://example.com/article",
        "lang": "en",
        "entities": [
            {
                "name": "John Doe",
                "type": "PERSON",
                "salience": 0.9,
                "wikipedia_url": "https://en.wikipedia.org/wiki/John_Doe",
            },
        ],
    }
    return json.dumps(record).encode("utf-8")


@pytest.fixture
def sample_gfg_tsv() -> bytes:
    """Create sample GFG TSV data."""
    # Format: date\tfrom_url\tlink_url\tlink_text\tpage_position\tlang
    return b"20240101120000\thttps://example.com/\thttps://example.com/article\tRead more\t1\ten"


@pytest.fixture
def sample_ggg_json() -> bytes:
    """Create sample GGG JSON-NL data."""
    record = {
        "date": "20240101120000",
        "url": "https://example.com/article",
        "location_name": "New York City",
        "lat": 40.7128,
        "lon": -74.006,
        "context": "The event took place in New York City.",
    }
    return json.dumps(record).encode("utf-8")


@pytest.fixture
def sample_gemg_json() -> bytes:
    """Create sample GEMG JSON-NL data."""
    record = {
        "date": "20240101120000",
        "url": "https://example.com/article",
        "title": "Test Article",
        "lang": "en",
        "metatags": [
            {"key": "author", "type": "meta", "value": "John Doe"},
        ],
        "jsonld": ['{"@type": "Article"}'],
    }
    return json.dumps(record).encode("utf-8")


@pytest.fixture
def sample_gal_json() -> bytes:
    """Create sample GAL JSON-NL data."""
    record = {
        "date": "20240101120000",
        "url": "https://example.com/article",
        "title": "Test Article",
        "image": "https://example.com/image.jpg",
        "description": "A test article",
        "author": "John Doe",
        "lang": "en",
    }
    return json.dumps(record).encode("utf-8")


class TestGraphEndpointInit:
    """Test GraphEndpoint initialization."""

    def test_init_default_error_policy(self, mock_file_source: MagicMock) -> None:
        """Test initialization with default error policy."""
        endpoint = GraphEndpoint(file_source=mock_file_source)

        assert endpoint._error_policy == "warn"
        assert endpoint._fetcher is not None

    def test_init_with_raise_error_policy(self, mock_file_source: MagicMock) -> None:
        """Test initialization with raise error policy."""
        endpoint = GraphEndpoint(file_source=mock_file_source, error_policy="raise")

        assert endpoint._error_policy == "raise"

    def test_init_with_skip_error_policy(self, mock_file_source: MagicMock) -> None:
        """Test initialization with skip error policy."""
        endpoint = GraphEndpoint(file_source=mock_file_source, error_policy="skip")

        assert endpoint._error_policy == "skip"

    def test_init_with_warn_error_policy(self, mock_file_source: MagicMock) -> None:
        """Test initialization with warn error policy."""
        endpoint = GraphEndpoint(file_source=mock_file_source, error_policy="warn")

        assert endpoint._error_policy == "warn"

    def test_fetcher_created_with_no_fallback(self, mock_file_source: MagicMock) -> None:
        """Test that GraphEndpoint creates DataFetcher with fallback disabled.

        GraphEndpoint is designed for graph datasets which don't have BigQuery
        fallback support, so the fetcher is always created with fallback_enabled=False.
        """
        endpoint = GraphEndpoint(file_source=mock_file_source)

        # GraphEndpoint creates DataFetcher internally
        assert endpoint._fetcher is not None
        # Verify the fetcher was configured without fallback
        assert endpoint._fetcher._fallback is False


class TestGraphEndpointGQG:
    """Test GQG (Global Quotation Graph) methods."""

    @pytest.mark.asyncio
    async def test_stream_gqg_basic(
        self,
        mock_file_source: MagicMock,
        gqg_filter: GQGFilter,
        sample_gqg_json: bytes,
    ) -> None:
        """Test basic streaming of GQG records."""
        endpoint = GraphEndpoint(file_source=mock_file_source)

        # Mock fetch_graph_files to return sample data
        async def mock_fetch_graph_files(
            graph_type: str, date_range: DateRange
        ) -> AsyncIterator[tuple[str, bytes]]:
            yield ("http://test.url/gqg.jsonl.gz", sample_gqg_json)

        endpoint._fetcher.fetch_graph_files = mock_fetch_graph_files

        records = [record async for record in endpoint.stream_gqg(gqg_filter)]

        assert len(records) == 1
        assert isinstance(records[0], GQGRecord)
        assert records[0].url == "https://example.com/article"
        assert records[0].lang == "en"
        assert len(records[0].quotes) == 1
        assert records[0].quotes[0].quote == "Hello world"

    @pytest.mark.asyncio
    async def test_query_gqg_basic(
        self,
        mock_file_source: MagicMock,
        gqg_filter: GQGFilter,
        sample_gqg_json: bytes,
    ) -> None:
        """Test query_gqg returns FetchResult."""
        endpoint = GraphEndpoint(file_source=mock_file_source)

        async def mock_fetch_graph_files(
            graph_type: str, date_range: DateRange
        ) -> AsyncIterator[tuple[str, bytes]]:
            yield ("http://test.url/gqg.jsonl.gz", sample_gqg_json)

        endpoint._fetcher.fetch_graph_files = mock_fetch_graph_files

        result = await endpoint.query_gqg(gqg_filter)

        assert len(result.data) == 1
        assert isinstance(result.data[0], GQGRecord)
        assert result.failed == []

    @pytest.mark.asyncio
    async def test_stream_gqg_language_filter(
        self,
        mock_file_source: MagicMock,
        sample_gqg_json: bytes,
    ) -> None:
        """Test GQG language filtering."""
        endpoint = GraphEndpoint(file_source=mock_file_source)

        # Create filter with language restriction
        filter_with_lang = GQGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            languages=["de"],  # German only
        )

        async def mock_fetch_graph_files(
            graph_type: str, date_range: DateRange
        ) -> AsyncIterator[tuple[str, bytes]]:
            yield ("http://test.url/gqg.jsonl.gz", sample_gqg_json)

        endpoint._fetcher.fetch_graph_files = mock_fetch_graph_files

        # Should filter out English records
        records = [record async for record in endpoint.stream_gqg(filter_with_lang)]
        assert len(records) == 0

    @pytest.mark.asyncio
    async def test_stream_gqg_language_match(
        self,
        mock_file_source: MagicMock,
        sample_gqg_json: bytes,
    ) -> None:
        """Test GQG language filtering with matching language."""
        endpoint = GraphEndpoint(file_source=mock_file_source)

        filter_with_lang = GQGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            languages=["en"],  # English
        )

        async def mock_fetch_graph_files(
            graph_type: str, date_range: DateRange
        ) -> AsyncIterator[tuple[str, bytes]]:
            yield ("http://test.url/gqg.jsonl.gz", sample_gqg_json)

        endpoint._fetcher.fetch_graph_files = mock_fetch_graph_files

        records = [record async for record in endpoint.stream_gqg(filter_with_lang)]
        assert len(records) == 1


class TestGraphEndpointGEG:
    """Test GEG (Global Entity Graph) methods."""

    @pytest.mark.asyncio
    async def test_stream_geg_basic(
        self,
        mock_file_source: MagicMock,
        geg_filter: GEGFilter,
        sample_geg_json: bytes,
    ) -> None:
        """Test basic streaming of GEG records."""
        endpoint = GraphEndpoint(file_source=mock_file_source)

        async def mock_fetch_graph_files(
            graph_type: str, date_range: DateRange
        ) -> AsyncIterator[tuple[str, bytes]]:
            yield ("http://test.url/geg.jsonl.gz", sample_geg_json)

        endpoint._fetcher.fetch_graph_files = mock_fetch_graph_files

        records = [record async for record in endpoint.stream_geg(geg_filter)]

        assert len(records) == 1
        assert isinstance(records[0], GEGRecord)
        assert records[0].url == "https://example.com/article"
        assert len(records[0].entities) == 1
        assert records[0].entities[0].name == "John Doe"
        assert records[0].entities[0].entity_type == "PERSON"

    @pytest.mark.asyncio
    async def test_query_geg_basic(
        self,
        mock_file_source: MagicMock,
        geg_filter: GEGFilter,
        sample_geg_json: bytes,
    ) -> None:
        """Test query_geg returns FetchResult."""
        endpoint = GraphEndpoint(file_source=mock_file_source)

        async def mock_fetch_graph_files(
            graph_type: str, date_range: DateRange
        ) -> AsyncIterator[tuple[str, bytes]]:
            yield ("http://test.url/geg.jsonl.gz", sample_geg_json)

        endpoint._fetcher.fetch_graph_files = mock_fetch_graph_files

        result = await endpoint.query_geg(geg_filter)

        assert len(result.data) == 1
        assert isinstance(result.data[0], GEGRecord)

    @pytest.mark.asyncio
    async def test_stream_geg_language_filter(
        self,
        mock_file_source: MagicMock,
        sample_geg_json: bytes,
    ) -> None:
        """Test GEG language filtering."""
        endpoint = GraphEndpoint(file_source=mock_file_source)

        filter_with_lang = GEGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            languages=["fr"],  # French only
        )

        async def mock_fetch_graph_files(
            graph_type: str, date_range: DateRange
        ) -> AsyncIterator[tuple[str, bytes]]:
            yield ("http://test.url/geg.jsonl.gz", sample_geg_json)

        endpoint._fetcher.fetch_graph_files = mock_fetch_graph_files

        records = [record async for record in endpoint.stream_geg(filter_with_lang)]
        assert len(records) == 0


class TestGraphEndpointGFG:
    """Test GFG (Global Frontpage Graph) methods."""

    @pytest.mark.asyncio
    async def test_stream_gfg_basic(
        self,
        mock_file_source: MagicMock,
        gfg_filter: GFGFilter,
        sample_gfg_tsv: bytes,
    ) -> None:
        """Test basic streaming of GFG records."""
        endpoint = GraphEndpoint(file_source=mock_file_source)

        async def mock_fetch_graph_files(
            graph_type: str, date_range: DateRange
        ) -> AsyncIterator[tuple[str, bytes]]:
            yield ("http://test.url/gfg.tsv.gz", sample_gfg_tsv)

        endpoint._fetcher.fetch_graph_files = mock_fetch_graph_files

        records = [record async for record in endpoint.stream_gfg(gfg_filter)]

        assert len(records) == 1
        assert isinstance(records[0], GFGRecord)
        assert records[0].from_frontpage_url == "https://example.com/"
        assert records[0].link_url == "https://example.com/article"
        assert records[0].link_text == "Read more"
        assert records[0].page_position == 1
        assert records[0].lang == "en"

    @pytest.mark.asyncio
    async def test_query_gfg_basic(
        self,
        mock_file_source: MagicMock,
        gfg_filter: GFGFilter,
        sample_gfg_tsv: bytes,
    ) -> None:
        """Test query_gfg returns FetchResult."""
        endpoint = GraphEndpoint(file_source=mock_file_source)

        async def mock_fetch_graph_files(
            graph_type: str, date_range: DateRange
        ) -> AsyncIterator[tuple[str, bytes]]:
            yield ("http://test.url/gfg.tsv.gz", sample_gfg_tsv)

        endpoint._fetcher.fetch_graph_files = mock_fetch_graph_files

        result = await endpoint.query_gfg(gfg_filter)

        assert len(result.data) == 1
        assert isinstance(result.data[0], GFGRecord)

    @pytest.mark.asyncio
    async def test_stream_gfg_language_filter(
        self,
        mock_file_source: MagicMock,
        sample_gfg_tsv: bytes,
    ) -> None:
        """Test GFG language filtering."""
        endpoint = GraphEndpoint(file_source=mock_file_source)

        filter_with_lang = GFGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            languages=["es"],  # Spanish only
        )

        async def mock_fetch_graph_files(
            graph_type: str, date_range: DateRange
        ) -> AsyncIterator[tuple[str, bytes]]:
            yield ("http://test.url/gfg.tsv.gz", sample_gfg_tsv)

        endpoint._fetcher.fetch_graph_files = mock_fetch_graph_files

        records = [record async for record in endpoint.stream_gfg(filter_with_lang)]
        assert len(records) == 0


class TestGraphEndpointGGG:
    """Test GGG (Global Geographic Graph) methods."""

    @pytest.mark.asyncio
    async def test_stream_ggg_basic(
        self,
        mock_file_source: MagicMock,
        ggg_filter: GGGFilter,
        sample_ggg_json: bytes,
    ) -> None:
        """Test basic streaming of GGG records."""
        endpoint = GraphEndpoint(file_source=mock_file_source)

        async def mock_fetch_graph_files(
            graph_type: str, date_range: DateRange
        ) -> AsyncIterator[tuple[str, bytes]]:
            yield ("http://test.url/ggg.jsonl.gz", sample_ggg_json)

        endpoint._fetcher.fetch_graph_files = mock_fetch_graph_files

        records = [record async for record in endpoint.stream_ggg(ggg_filter)]

        assert len(records) == 1
        assert isinstance(records[0], GGGRecord)
        assert records[0].location_name == "New York City"
        assert records[0].lat == 40.7128
        assert records[0].lon == -74.006

    @pytest.mark.asyncio
    async def test_query_ggg_basic(
        self,
        mock_file_source: MagicMock,
        ggg_filter: GGGFilter,
        sample_ggg_json: bytes,
    ) -> None:
        """Test query_ggg returns FetchResult."""
        endpoint = GraphEndpoint(file_source=mock_file_source)

        async def mock_fetch_graph_files(
            graph_type: str, date_range: DateRange
        ) -> AsyncIterator[tuple[str, bytes]]:
            yield ("http://test.url/ggg.jsonl.gz", sample_ggg_json)

        endpoint._fetcher.fetch_graph_files = mock_fetch_graph_files

        result = await endpoint.query_ggg(ggg_filter)

        assert len(result.data) == 1
        assert isinstance(result.data[0], GGGRecord)


class TestGraphEndpointGEMG:
    """Test GEMG (Global Embedded Metadata Graph) methods."""

    @pytest.mark.asyncio
    async def test_stream_gemg_basic(
        self,
        mock_file_source: MagicMock,
        gemg_filter: GEMGFilter,
        sample_gemg_json: bytes,
    ) -> None:
        """Test basic streaming of GEMG records."""
        endpoint = GraphEndpoint(file_source=mock_file_source)

        async def mock_fetch_graph_files(
            graph_type: str, date_range: DateRange
        ) -> AsyncIterator[tuple[str, bytes]]:
            yield ("http://test.url/gemg.jsonl.gz", sample_gemg_json)

        endpoint._fetcher.fetch_graph_files = mock_fetch_graph_files

        records = [record async for record in endpoint.stream_gemg(gemg_filter)]

        assert len(records) == 1
        assert isinstance(records[0], GEMGRecord)
        assert records[0].title == "Test Article"
        assert len(records[0].metatags) == 1
        assert records[0].metatags[0].key == "author"

    @pytest.mark.asyncio
    async def test_query_gemg_basic(
        self,
        mock_file_source: MagicMock,
        gemg_filter: GEMGFilter,
        sample_gemg_json: bytes,
    ) -> None:
        """Test query_gemg returns FetchResult."""
        endpoint = GraphEndpoint(file_source=mock_file_source)

        async def mock_fetch_graph_files(
            graph_type: str, date_range: DateRange
        ) -> AsyncIterator[tuple[str, bytes]]:
            yield ("http://test.url/gemg.jsonl.gz", sample_gemg_json)

        endpoint._fetcher.fetch_graph_files = mock_fetch_graph_files

        result = await endpoint.query_gemg(gemg_filter)

        assert len(result.data) == 1
        assert isinstance(result.data[0], GEMGRecord)

    @pytest.mark.asyncio
    async def test_stream_gemg_language_filter(
        self,
        mock_file_source: MagicMock,
        sample_gemg_json: bytes,
    ) -> None:
        """Test GEMG language filtering."""
        endpoint = GraphEndpoint(file_source=mock_file_source)

        filter_with_lang = GEMGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            languages=["ja"],  # Japanese only
        )

        async def mock_fetch_graph_files(
            graph_type: str, date_range: DateRange
        ) -> AsyncIterator[tuple[str, bytes]]:
            yield ("http://test.url/gemg.jsonl.gz", sample_gemg_json)

        endpoint._fetcher.fetch_graph_files = mock_fetch_graph_files

        records = [record async for record in endpoint.stream_gemg(filter_with_lang)]
        assert len(records) == 0


class TestGraphEndpointGAL:
    """Test GAL (Article List) methods."""

    @pytest.mark.asyncio
    async def test_stream_gal_basic(
        self,
        mock_file_source: MagicMock,
        gal_filter: GALFilter,
        sample_gal_json: bytes,
    ) -> None:
        """Test basic streaming of GAL records."""
        endpoint = GraphEndpoint(file_source=mock_file_source)

        async def mock_fetch_graph_files(
            graph_type: str, date_range: DateRange
        ) -> AsyncIterator[tuple[str, bytes]]:
            yield ("http://test.url/gal.jsonl.gz", sample_gal_json)

        endpoint._fetcher.fetch_graph_files = mock_fetch_graph_files

        records = [record async for record in endpoint.stream_gal(gal_filter)]

        assert len(records) == 1
        assert isinstance(records[0], GALRecord)
        assert records[0].title == "Test Article"
        assert records[0].author == "John Doe"
        assert records[0].description == "A test article"

    @pytest.mark.asyncio
    async def test_query_gal_basic(
        self,
        mock_file_source: MagicMock,
        gal_filter: GALFilter,
        sample_gal_json: bytes,
    ) -> None:
        """Test query_gal returns FetchResult."""
        endpoint = GraphEndpoint(file_source=mock_file_source)

        async def mock_fetch_graph_files(
            graph_type: str, date_range: DateRange
        ) -> AsyncIterator[tuple[str, bytes]]:
            yield ("http://test.url/gal.jsonl.gz", sample_gal_json)

        endpoint._fetcher.fetch_graph_files = mock_fetch_graph_files

        result = await endpoint.query_gal(gal_filter)

        assert len(result.data) == 1
        assert isinstance(result.data[0], GALRecord)

    @pytest.mark.asyncio
    async def test_stream_gal_language_filter(
        self,
        mock_file_source: MagicMock,
        sample_gal_json: bytes,
    ) -> None:
        """Test GAL language filtering."""
        endpoint = GraphEndpoint(file_source=mock_file_source)

        filter_with_lang = GALFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            languages=["zh"],  # Chinese only
        )

        async def mock_fetch_graph_files(
            graph_type: str, date_range: DateRange
        ) -> AsyncIterator[tuple[str, bytes]]:
            yield ("http://test.url/gal.jsonl.gz", sample_gal_json)

        endpoint._fetcher.fetch_graph_files = mock_fetch_graph_files

        records = [record async for record in endpoint.stream_gal(filter_with_lang)]
        assert len(records) == 0


class TestGraphEndpointErrorPolicies:
    """Test error handling with different error policies.

    The GraphEndpoint uses try/except around parser calls to handle errors
    according to the configured error_policy. The parsers themselves handle
    line-level errors (logging warnings and continuing), but if the parser
    raises an unhandled exception, the endpoint's error handling kicks in.
    """

    @pytest.mark.asyncio
    async def test_error_policy_raise_with_parser_exception(
        self,
        mock_file_source: MagicMock,
        gqg_filter: GQGFilter,
    ) -> None:
        """Test that raise error policy re-raises exceptions from parser."""
        endpoint = GraphEndpoint(file_source=mock_file_source, error_policy="raise")

        async def mock_fetch_graph_files(
            graph_type: str, date_range: DateRange
        ) -> AsyncIterator[tuple[str, bytes]]:
            yield ("http://test.url/gqg.jsonl.gz", b'{"valid": "json"}')

        endpoint._fetcher.fetch_graph_files = mock_fetch_graph_files

        # Patch the parser to raise an exception
        with patch(
            "py_gdelt.endpoints.graphs.graph_parsers.parse_gqg",
            side_effect=ValueError("Simulated parser error"),
        ):
            with pytest.raises(ValueError, match="Simulated parser error"):
                _ = [record async for record in endpoint.stream_gqg(gqg_filter)]

    @pytest.mark.asyncio
    async def test_error_policy_warn_with_parser_exception(
        self,
        mock_file_source: MagicMock,
        gqg_filter: GQGFilter,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test that warn error policy logs warning and continues on exception."""
        endpoint = GraphEndpoint(file_source=mock_file_source, error_policy="warn")

        async def mock_fetch_graph_files(
            graph_type: str, date_range: DateRange
        ) -> AsyncIterator[tuple[str, bytes]]:
            yield ("http://test.url/gqg.jsonl.gz", b'{"valid": "json"}')

        endpoint._fetcher.fetch_graph_files = mock_fetch_graph_files

        # Patch the parser to raise an exception
        with patch(
            "py_gdelt.endpoints.graphs.graph_parsers.parse_gqg",
            side_effect=ValueError("Simulated parser error"),
        ):
            with caplog.at_level(logging.WARNING):
                records = [record async for record in endpoint.stream_gqg(gqg_filter)]

        # Should not raise, but should log warning
        assert len(records) == 0
        assert "Error parsing" in caplog.text
        assert "Simulated parser error" in caplog.text

    @pytest.mark.asyncio
    async def test_error_policy_skip_with_parser_exception(
        self,
        mock_file_source: MagicMock,
        gqg_filter: GQGFilter,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test that skip error policy continues silently on exception."""
        endpoint = GraphEndpoint(file_source=mock_file_source, error_policy="skip")

        async def mock_fetch_graph_files(
            graph_type: str, date_range: DateRange
        ) -> AsyncIterator[tuple[str, bytes]]:
            yield ("http://test.url/gqg.jsonl.gz", b'{"valid": "json"}')

        endpoint._fetcher.fetch_graph_files = mock_fetch_graph_files

        # Patch the parser to raise an exception
        with patch(
            "py_gdelt.endpoints.graphs.graph_parsers.parse_gqg",
            side_effect=ValueError("Simulated parser error"),
        ):
            with caplog.at_level(logging.WARNING):
                records = [record async for record in endpoint.stream_gqg(gqg_filter)]

        # Should not raise
        assert len(records) == 0
        # Skip policy should not log at WARNING level from the endpoint
        assert "Error parsing" not in caplog.text

    @pytest.mark.asyncio
    async def test_error_policy_warn_geg(
        self,
        mock_file_source: MagicMock,
        geg_filter: GEGFilter,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test warn error policy on GEG endpoint."""
        endpoint = GraphEndpoint(file_source=mock_file_source, error_policy="warn")

        async def mock_fetch_graph_files(
            graph_type: str, date_range: DateRange
        ) -> AsyncIterator[tuple[str, bytes]]:
            yield ("http://test.url/geg.jsonl.gz", b'{"valid": "json"}')

        endpoint._fetcher.fetch_graph_files = mock_fetch_graph_files

        with patch(
            "py_gdelt.endpoints.graphs.graph_parsers.parse_geg",
            side_effect=RuntimeError("GEG parsing failed"),
        ):
            with caplog.at_level(logging.WARNING):
                records = [record async for record in endpoint.stream_geg(geg_filter)]

        assert len(records) == 0
        assert "Error parsing" in caplog.text

    @pytest.mark.asyncio
    async def test_error_policy_raise_gfg(
        self,
        mock_file_source: MagicMock,
        gfg_filter: GFGFilter,
    ) -> None:
        """Test raise error policy on GFG endpoint."""
        endpoint = GraphEndpoint(file_source=mock_file_source, error_policy="raise")

        async def mock_fetch_graph_files(
            graph_type: str, date_range: DateRange
        ) -> AsyncIterator[tuple[str, bytes]]:
            yield ("http://test.url/gfg.tsv.gz", b"some\tvalid\ttsv\tdata")

        endpoint._fetcher.fetch_graph_files = mock_fetch_graph_files

        with patch(
            "py_gdelt.endpoints.graphs.graph_parsers.parse_gfg",
            side_effect=ValueError("GFG parsing failed"),
        ):
            with pytest.raises(ValueError, match="GFG parsing failed"):
                _ = [record async for record in endpoint.stream_gfg(gfg_filter)]

    @pytest.mark.asyncio
    async def test_error_policy_warn_ggg(
        self,
        mock_file_source: MagicMock,
        ggg_filter: GGGFilter,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test warn error policy on GGG endpoint."""
        endpoint = GraphEndpoint(file_source=mock_file_source, error_policy="warn")

        async def mock_fetch_graph_files(
            graph_type: str, date_range: DateRange
        ) -> AsyncIterator[tuple[str, bytes]]:
            yield ("http://test.url/ggg.jsonl.gz", b'{"valid": "json"}')

        endpoint._fetcher.fetch_graph_files = mock_fetch_graph_files

        with patch(
            "py_gdelt.endpoints.graphs.graph_parsers.parse_ggg",
            side_effect=RuntimeError("GGG parsing failed"),
        ):
            with caplog.at_level(logging.WARNING):
                records = [record async for record in endpoint.stream_ggg(ggg_filter)]

        assert len(records) == 0
        assert "Error parsing" in caplog.text

    @pytest.mark.asyncio
    async def test_error_policy_skip_gemg(
        self,
        mock_file_source: MagicMock,
        gemg_filter: GEMGFilter,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test skip error policy on GEMG endpoint."""
        endpoint = GraphEndpoint(file_source=mock_file_source, error_policy="skip")

        async def mock_fetch_graph_files(
            graph_type: str, date_range: DateRange
        ) -> AsyncIterator[tuple[str, bytes]]:
            yield ("http://test.url/gemg.jsonl.gz", b'{"valid": "json"}')

        endpoint._fetcher.fetch_graph_files = mock_fetch_graph_files

        with patch(
            "py_gdelt.endpoints.graphs.graph_parsers.parse_gemg",
            side_effect=RuntimeError("GEMG parsing failed"),
        ):
            with caplog.at_level(logging.WARNING):
                records = [record async for record in endpoint.stream_gemg(gemg_filter)]

        assert len(records) == 0
        # Skip policy: no WARNING level log from endpoint
        assert "Error parsing" not in caplog.text

    @pytest.mark.asyncio
    async def test_error_policy_raise_gal(
        self,
        mock_file_source: MagicMock,
        gal_filter: GALFilter,
    ) -> None:
        """Test raise error policy on GAL endpoint."""
        endpoint = GraphEndpoint(file_source=mock_file_source, error_policy="raise")

        async def mock_fetch_graph_files(
            graph_type: str, date_range: DateRange
        ) -> AsyncIterator[tuple[str, bytes]]:
            yield ("http://test.url/gal.jsonl.gz", b'{"valid": "json"}')

        endpoint._fetcher.fetch_graph_files = mock_fetch_graph_files

        with patch(
            "py_gdelt.endpoints.graphs.graph_parsers.parse_gal",
            side_effect=ValueError("GAL parsing failed"),
        ):
            with pytest.raises(ValueError, match="GAL parsing failed"):
                _ = [record async for record in endpoint.stream_gal(gal_filter)]

    @pytest.mark.asyncio
    async def test_malformed_json_handled_by_parser(
        self,
        mock_file_source: MagicMock,
        gqg_filter: GQGFilter,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test that malformed JSON is handled gracefully by the parser.

        Parsers log warnings for malformed lines and continue processing.
        This does NOT trigger the endpoint's error policy (only unhandled
        exceptions from the parser do).
        """
        endpoint = GraphEndpoint(file_source=mock_file_source, error_policy="warn")

        # Malformed JSON - parser handles this internally
        async def mock_fetch_graph_files(
            graph_type: str, date_range: DateRange
        ) -> AsyncIterator[tuple[str, bytes]]:
            yield ("http://test.url/gqg.jsonl.gz", b"invalid json {{{")

        endpoint._fetcher.fetch_graph_files = mock_fetch_graph_files

        with caplog.at_level(logging.WARNING):
            records = [record async for record in endpoint.stream_gqg(gqg_filter)]

        # Parser handles malformed JSON internally, logging a warning
        assert len(records) == 0
        assert "Malformed JSON" in caplog.text


class TestGraphEndpointMultipleRecords:
    """Test streaming multiple records."""

    @pytest.mark.asyncio
    async def test_stream_gqg_multiple_records(
        self,
        mock_file_source: MagicMock,
        gqg_filter: GQGFilter,
    ) -> None:
        """Test streaming multiple GQG records."""
        endpoint = GraphEndpoint(file_source=mock_file_source)

        # Create multiple JSON-NL records
        records_data = []
        for i in range(3):
            record = {
                "date": "20240101120000",
                "url": f"https://example.com/article{i}",
                "lang": "en",
                "quotes": [
                    {"pre": "Said", "quote": f"Quote {i}", "post": "."},
                ],
            }
            records_data.append(json.dumps(record))

        multi_record_data = "\n".join(records_data).encode("utf-8")

        async def mock_fetch_graph_files(
            graph_type: str, date_range: DateRange
        ) -> AsyncIterator[tuple[str, bytes]]:
            yield ("http://test.url/gqg.jsonl.gz", multi_record_data)

        endpoint._fetcher.fetch_graph_files = mock_fetch_graph_files

        records = [record async for record in endpoint.stream_gqg(gqg_filter)]

        assert len(records) == 3
        for i, record in enumerate(records):
            assert record.url == f"https://example.com/article{i}"

    @pytest.mark.asyncio
    async def test_stream_geg_multiple_languages(
        self,
        mock_file_source: MagicMock,
    ) -> None:
        """Test GEG with multiple languages, filtering some out."""
        endpoint = GraphEndpoint(file_source=mock_file_source)

        # Create records in different languages
        records_data = []
        for lang in ["en", "de", "fr", "en", "es"]:
            record = {
                "date": "20240101120000",
                "url": f"https://example.com/article-{lang}",
                "lang": lang,
                "entities": [],
            }
            records_data.append(json.dumps(record))

        multi_record_data = "\n".join(records_data).encode("utf-8")

        async def mock_fetch_graph_files(
            graph_type: str, date_range: DateRange
        ) -> AsyncIterator[tuple[str, bytes]]:
            yield ("http://test.url/geg.jsonl.gz", multi_record_data)

        endpoint._fetcher.fetch_graph_files = mock_fetch_graph_files

        # Filter for English only
        filter_obj = GEGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            languages=["en"],
        )

        records = [record async for record in endpoint.stream_geg(filter_obj)]

        assert len(records) == 2
        assert all(record.lang == "en" for record in records)


class TestGraphEndpointMultipleFiles:
    """Test streaming from multiple files."""

    @pytest.mark.asyncio
    async def test_stream_gqg_multiple_files(
        self,
        mock_file_source: MagicMock,
        gqg_filter: GQGFilter,
    ) -> None:
        """Test streaming GQG records from multiple files."""
        endpoint = GraphEndpoint(file_source=mock_file_source)

        file1_data = json.dumps(
            {
                "date": "20240101120000",
                "url": "https://example.com/article1",
                "lang": "en",
                "quotes": [],
            }
        ).encode("utf-8")

        file2_data = json.dumps(
            {
                "date": "20240101130000",
                "url": "https://example.com/article2",
                "lang": "en",
                "quotes": [],
            }
        ).encode("utf-8")

        async def mock_fetch_graph_files(
            graph_type: str, date_range: DateRange
        ) -> AsyncIterator[tuple[str, bytes]]:
            yield ("http://test.url/gqg1.jsonl.gz", file1_data)
            yield ("http://test.url/gqg2.jsonl.gz", file2_data)

        endpoint._fetcher.fetch_graph_files = mock_fetch_graph_files

        records = [record async for record in endpoint.stream_gqg(gqg_filter)]

        assert len(records) == 2
        assert records[0].url == "https://example.com/article1"
        assert records[1].url == "https://example.com/article2"


class TestGraphEndpointEmptyResults:
    """Test handling of empty results."""

    @pytest.mark.asyncio
    async def test_stream_gqg_empty(
        self,
        mock_file_source: MagicMock,
        gqg_filter: GQGFilter,
    ) -> None:
        """Test streaming with no data returns empty list."""
        endpoint = GraphEndpoint(file_source=mock_file_source)

        async def mock_fetch_graph_files(
            graph_type: str, date_range: DateRange
        ) -> AsyncIterator[tuple[str, bytes]]:
            return
            yield  # type: ignore[misc]

        endpoint._fetcher.fetch_graph_files = mock_fetch_graph_files

        records = [record async for record in endpoint.stream_gqg(gqg_filter)]

        assert len(records) == 0

    @pytest.mark.asyncio
    async def test_query_gqg_empty(
        self,
        mock_file_source: MagicMock,
        gqg_filter: GQGFilter,
    ) -> None:
        """Test query with no data returns empty FetchResult."""
        endpoint = GraphEndpoint(file_source=mock_file_source)

        async def mock_fetch_graph_files(
            graph_type: str, date_range: DateRange
        ) -> AsyncIterator[tuple[str, bytes]]:
            return
            yield  # type: ignore[misc]

        endpoint._fetcher.fetch_graph_files = mock_fetch_graph_files

        result = await endpoint.query_gqg(gqg_filter)

        assert len(result.data) == 0
        assert result.failed == []


class TestGraphEndpointDateParsing:
    """Test date parsing in records."""

    @pytest.mark.asyncio
    async def test_gqg_date_parsing(
        self,
        mock_file_source: MagicMock,
        gqg_filter: GQGFilter,
    ) -> None:
        """Test that GQG dates are parsed correctly."""
        endpoint = GraphEndpoint(file_source=mock_file_source)

        record = {
            "date": "20240115143000",  # Jan 15, 2024, 14:30:00
            "url": "https://example.com/article",
            "lang": "en",
            "quotes": [],
        }
        data = json.dumps(record).encode("utf-8")

        async def mock_fetch_graph_files(
            graph_type: str, date_range: DateRange
        ) -> AsyncIterator[tuple[str, bytes]]:
            yield ("http://test.url/gqg.jsonl.gz", data)

        endpoint._fetcher.fetch_graph_files = mock_fetch_graph_files

        records = [rec async for rec in endpoint.stream_gqg(gqg_filter)]

        assert len(records) == 1
        assert records[0].date == datetime(2024, 1, 15, 14, 30, 0, tzinfo=UTC)

    @pytest.mark.asyncio
    async def test_gfg_date_parsing(
        self,
        mock_file_source: MagicMock,
        gfg_filter: GFGFilter,
    ) -> None:
        """Test that GFG dates are parsed correctly."""
        endpoint = GraphEndpoint(file_source=mock_file_source)

        # TSV format: date\tfrom_url\tlink_url\tlink_text\tpage_position\tlang
        data = b"20240115143000\thttps://example.com/\thttps://example.com/article\tLink\t5\ten"

        async def mock_fetch_graph_files(
            graph_type: str, date_range: DateRange
        ) -> AsyncIterator[tuple[str, bytes]]:
            yield ("http://test.url/gfg.tsv.gz", data)

        endpoint._fetcher.fetch_graph_files = mock_fetch_graph_files

        records = [rec async for rec in endpoint.stream_gfg(gfg_filter)]

        assert len(records) == 1
        assert records[0].date == datetime(2024, 1, 15, 14, 30, 0, tzinfo=UTC)


class TestNormalizeLanguages:
    """Tests for _normalize_languages helper function."""

    def test_normalize_languages_none_returns_none(self) -> None:
        """Test that None input returns None."""
        result = _normalize_languages(None)
        assert result is None

    def test_normalize_languages_lowercase(self) -> None:
        """Test that uppercase languages are converted to lowercase."""
        result = _normalize_languages(["EN", "DE", "FR"])
        assert result == {"en", "de", "fr"}

    def test_normalize_languages_already_lowercase(self) -> None:
        """Test that lowercase languages are preserved."""
        result = _normalize_languages(["en", "de", "fr"])
        assert result == {"en", "de", "fr"}

    def test_normalize_languages_mixed_case(self) -> None:
        """Test that mixed case languages are normalized."""
        result = _normalize_languages(["En", "dE", "FR", "es"])
        assert result == {"en", "de", "fr", "es"}

    def test_normalize_languages_returns_set(self) -> None:
        """Test that result is a set for efficient lookup."""
        result = _normalize_languages(["en", "en", "EN"])
        assert isinstance(result, set)
        assert result == {"en"}


class TestCaseInsensitiveLanguageFiltering:
    """Tests for case-insensitive language filtering in endpoints."""

    @pytest.mark.asyncio
    async def test_uppercase_filter_matches_lowercase_record(
        self,
        mock_file_source: MagicMock,
    ) -> None:
        """Test that filtering with uppercase ['EN'] matches records with lang='en'."""
        endpoint = GraphEndpoint(file_source=mock_file_source)

        # Record has lowercase 'en'
        record = {
            "date": "20240101120000",
            "url": "https://example.com/article",
            "lang": "en",
            "quotes": [],
        }
        data = json.dumps(record).encode("utf-8")

        async def mock_fetch_graph_files(
            _graph_type: str, _date_range: DateRange
        ) -> AsyncIterator[tuple[str, bytes]]:
            yield ("http://test.url/gqg.jsonl.gz", data)

        endpoint._fetcher.fetch_graph_files = mock_fetch_graph_files

        # Filter with uppercase 'EN'
        filter_obj = GQGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            languages=["EN"],
        )

        records = [rec async for rec in endpoint.stream_gqg(filter_obj)]
        assert len(records) == 1
        assert records[0].lang == "en"

    @pytest.mark.asyncio
    async def test_lowercase_filter_matches_uppercase_record(
        self,
        mock_file_source: MagicMock,
    ) -> None:
        """Test that filtering with lowercase ['en'] matches records with lang='EN'."""
        endpoint = GraphEndpoint(file_source=mock_file_source)

        # Record has uppercase 'EN'
        record = {
            "date": "20240101120000",
            "url": "https://example.com/article",
            "lang": "EN",
            "quotes": [],
        }
        data = json.dumps(record).encode("utf-8")

        async def mock_fetch_graph_files(
            _graph_type: str, _date_range: DateRange
        ) -> AsyncIterator[tuple[str, bytes]]:
            yield ("http://test.url/gqg.jsonl.gz", data)

        endpoint._fetcher.fetch_graph_files = mock_fetch_graph_files

        # Filter with lowercase 'en'
        filter_obj = GQGFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            languages=["en"],
        )

        records = [rec async for rec in endpoint.stream_gqg(filter_obj)]
        assert len(records) == 1
        assert records[0].lang == "EN"
