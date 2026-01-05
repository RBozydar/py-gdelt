"""Tests for DataFetcher orchestrator module.

This module tests the DataFetcher class which orchestrates source selection
and fallback behavior between file downloads and BigQuery.
"""

from collections.abc import Iterator
from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest

from py_gdelt.exceptions import (
    APIUnavailableError,
    ConfigurationError,
    RateLimitError,
)
from py_gdelt.filters import DateRange, EventFilter, GKGFilter
from py_gdelt.sources.fetcher import DataFetcher


@pytest.fixture
def mock_file_source() -> MagicMock:
    """Create mock FileSource."""
    mock = MagicMock()
    mock.__aenter__ = AsyncMock(return_value=mock)
    mock.__aexit__ = AsyncMock(return_value=None)
    return mock


@pytest.fixture
def mock_bigquery_source() -> MagicMock:
    """Create mock BigQuerySource."""
    mock = MagicMock()
    mock.__aenter__ = AsyncMock(return_value=mock)
    mock.__aexit__ = AsyncMock(return_value=None)
    return mock


@pytest.fixture
def mock_parser() -> MagicMock:
    """Create mock Parser."""
    mock = MagicMock()
    mock.detect_version = MagicMock(return_value=2)
    return mock


@pytest.fixture
def event_filter() -> EventFilter:
    """Create test EventFilter."""
    return EventFilter(
        date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 2)),
        actor1_country="USA",
    )


@pytest.fixture
def gkg_filter() -> GKGFilter:
    """Create test GKGFilter."""
    return GKGFilter(
        date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 2)),
        themes=["ENV_CLIMATECHANGE"],
    )


class TestDataFetcherInit:
    """Test DataFetcher initialization."""

    def test_init_with_file_source_only(self, mock_file_source: MagicMock) -> None:
        """Test initialization with only file source."""
        fetcher = DataFetcher(file_source=mock_file_source)

        assert fetcher._file is mock_file_source
        assert fetcher._bq is None
        assert fetcher._fallback is False
        assert fetcher._error_policy == "warn"

    def test_init_with_both_sources(
        self,
        mock_file_source: MagicMock,
        mock_bigquery_source: MagicMock,
    ) -> None:
        """Test initialization with both file and BigQuery sources."""
        fetcher = DataFetcher(
            file_source=mock_file_source,
            bigquery_source=mock_bigquery_source,
            fallback_enabled=True,
        )

        assert fetcher._file is mock_file_source
        assert fetcher._bq is mock_bigquery_source
        assert fetcher._fallback is True

    def test_init_with_fallback_disabled(
        self,
        mock_file_source: MagicMock,
        mock_bigquery_source: MagicMock,
    ) -> None:
        """Test initialization with fallback disabled."""
        fetcher = DataFetcher(
            file_source=mock_file_source,
            bigquery_source=mock_bigquery_source,
            fallback_enabled=False,
        )

        assert fetcher._fallback is False

    def test_init_with_custom_error_policy(self, mock_file_source: MagicMock) -> None:
        """Test initialization with custom error policy."""
        fetcher = DataFetcher(
            file_source=mock_file_source,
            error_policy="raise",
        )

        assert fetcher._error_policy == "raise"


class TestDataFetcherErrorPolicy:
    """Test error handling policies."""

    def test_error_policy_raise(self, mock_file_source: MagicMock) -> None:
        """Test that 'raise' policy re-raises errors."""
        fetcher = DataFetcher(
            file_source=mock_file_source,
            error_policy="raise",
        )

        error = ValueError("test error")
        with pytest.raises(ValueError, match="test error"):
            fetcher._handle_error(error)

    def test_error_policy_warn(self, mock_file_source: MagicMock) -> None:
        """Test that 'warn' policy logs and continues."""
        fetcher = DataFetcher(
            file_source=mock_file_source,
            error_policy="warn",
        )

        error = ValueError("test error")
        # Should not raise
        fetcher._handle_error(error)

    def test_error_policy_skip(self, mock_file_source: MagicMock) -> None:
        """Test that 'skip' policy silently skips errors."""
        fetcher = DataFetcher(
            file_source=mock_file_source,
            error_policy="skip",
        )

        error = ValueError("test error")
        # Should not raise
        fetcher._handle_error(error)


class TestDataFetcherFetchFromFiles:
    """Test fetching from file source."""

    @pytest.mark.asyncio
    async def test_fetch_from_files_events(
        self,
        mock_file_source: MagicMock,
        mock_parser: MagicMock,
        event_filter: EventFilter,
    ) -> None:
        """Test fetching events from file source."""
        # Mock file source methods
        mock_file_source.get_files_for_date_range = AsyncMock(
            return_value=["http://example.com/file1.zip"],
        )

        # Mock stream_files to yield URL and data
        async def mock_stream_files(urls):  # type: ignore[no-untyped-def]
            yield "http://example.com/file1.zip", b"test data"

        mock_file_source.stream_files = mock_stream_files

        # Mock parser to yield events (using dict for simplicity)
        mock_event = {
            "global_event_id": "123",
            "sql_date": "20240101",
            "event_code": "010",
        }

        def mock_parse(data: bytes, is_translated: bool = False) -> Iterator[dict]:  # type: ignore[type-arg]
            yield mock_event

        mock_parser.parse = mock_parse

        # Create fetcher and fetch
        fetcher = DataFetcher(file_source=mock_file_source)

        events = []
        async for event in fetcher._fetch_from_files(event_filter, mock_parser):
            events.append(event)

        assert len(events) == 1
        assert events[0]["global_event_id"] == "123"

        # Verify file source was called correctly
        mock_file_source.get_files_for_date_range.assert_called_once_with(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 2),
            file_type="export",
            include_translation=True,
        )

    @pytest.mark.asyncio
    async def test_fetch_from_files_gkg(
        self,
        mock_file_source: MagicMock,
        mock_parser: MagicMock,
        gkg_filter: GKGFilter,
    ) -> None:
        """Test fetching GKG from file source."""
        # Mock file source methods
        mock_file_source.get_files_for_date_range = AsyncMock(
            return_value=["http://example.com/file1.zip"],
        )

        # Mock stream_files
        async def mock_stream_files(urls):  # type: ignore[no-untyped-def]
            yield "http://example.com/file1.zip", b"test data"

        mock_file_source.stream_files = mock_stream_files

        # Mock parser to yield GKG records (using dict for simplicity)
        mock_gkg = {
            "gkg_record_id": "123",
            "date": "20240101",
            "themes": "ENV_CLIMATECHANGE",
        }

        def mock_parse(data: bytes, is_translated: bool = False) -> Iterator[dict]:  # type: ignore[type-arg]
            yield mock_gkg

        mock_parser.parse = mock_parse

        # Create fetcher and fetch
        fetcher = DataFetcher(file_source=mock_file_source)

        gkgs = []
        async for gkg in fetcher._fetch_from_files(gkg_filter, mock_parser):
            gkgs.append(gkg)

        assert len(gkgs) == 1
        assert gkgs[0]["gkg_record_id"] == "123"

        # Verify file source was called correctly
        mock_file_source.get_files_for_date_range.assert_called_once_with(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 2),
            file_type="gkg",
            include_translation=True,
        )


class TestDataFetcherFallback:
    """Test fallback behavior from files to BigQuery."""

    @pytest.mark.asyncio
    async def test_fallback_on_rate_limit(
        self,
        mock_file_source: MagicMock,
        mock_bigquery_source: MagicMock,
        mock_parser: MagicMock,
        event_filter: EventFilter,
    ) -> None:
        """Test fallback to BigQuery on rate limit error."""
        # Mock file source to raise RateLimitError
        mock_file_source.get_files_for_date_range = AsyncMock(
            side_effect=RateLimitError("Rate limited", retry_after=60),
        )

        # Mock BigQuery to return data
        async def mock_query_events(filter_obj, columns=None, limit=None):  # type: ignore[no-untyped-def]
            yield {"GLOBALEVENTID": "123", "EventCode": "010"}

        mock_bigquery_source.query_events = mock_query_events

        # Create fetcher with fallback enabled
        fetcher = DataFetcher(
            file_source=mock_file_source,
            bigquery_source=mock_bigquery_source,
            fallback_enabled=True,
        )

        # Fetch events - should fallback to BigQuery
        events = []
        async for event in fetcher.fetch(event_filter, mock_parser):
            events.append(event)

        assert len(events) == 1
        assert events[0]["GLOBALEVENTID"] == "123"

    @pytest.mark.asyncio
    async def test_fallback_on_api_error(
        self,
        mock_file_source: MagicMock,
        mock_bigquery_source: MagicMock,
        mock_parser: MagicMock,
        event_filter: EventFilter,
    ) -> None:
        """Test fallback to BigQuery on API error."""
        # Mock file source to raise APIError
        mock_file_source.get_files_for_date_range = AsyncMock(
            side_effect=APIUnavailableError("Service unavailable"),
        )

        # Mock BigQuery to return data
        async def mock_query_events(filter_obj, columns=None, limit=None):  # type: ignore[no-untyped-def]
            yield {"GLOBALEVENTID": "456", "EventCode": "020"}

        mock_bigquery_source.query_events = mock_query_events

        # Create fetcher with fallback enabled
        fetcher = DataFetcher(
            file_source=mock_file_source,
            bigquery_source=mock_bigquery_source,
            fallback_enabled=True,
        )

        # Fetch events - should fallback to BigQuery
        events = []
        async for event in fetcher.fetch(event_filter, mock_parser):
            events.append(event)

        assert len(events) == 1
        assert events[0]["GLOBALEVENTID"] == "456"

    @pytest.mark.asyncio
    async def test_no_fallback_when_disabled(
        self,
        mock_file_source: MagicMock,
        mock_bigquery_source: MagicMock,
        mock_parser: MagicMock,
        event_filter: EventFilter,
    ) -> None:
        """Test that fallback is disabled when fallback_enabled=False."""
        # Mock file source to raise RateLimitError
        mock_file_source.get_files_for_date_range = AsyncMock(
            side_effect=RateLimitError("Rate limited"),
        )

        # Create fetcher with fallback DISABLED
        fetcher = DataFetcher(
            file_source=mock_file_source,
            bigquery_source=mock_bigquery_source,
            fallback_enabled=False,
            error_policy="raise",
        )

        # Fetch events - should raise error (no fallback)
        with pytest.raises(RateLimitError):
            async for _ in fetcher.fetch(event_filter, mock_parser):
                pass

    @pytest.mark.asyncio
    async def test_no_fallback_when_bigquery_not_configured(
        self,
        mock_file_source: MagicMock,
        mock_parser: MagicMock,
        event_filter: EventFilter,
    ) -> None:
        """Test that fallback doesn't happen when BigQuery not configured."""
        # Mock file source to raise RateLimitError
        mock_file_source.get_files_for_date_range = AsyncMock(
            side_effect=RateLimitError("Rate limited"),
        )

        # Create fetcher WITHOUT BigQuery source
        fetcher = DataFetcher(
            file_source=mock_file_source,
            fallback_enabled=True,
            error_policy="raise",
        )

        # Fetch events - should raise error (no fallback available)
        with pytest.raises(RateLimitError):
            async for _ in fetcher.fetch(event_filter, mock_parser):
                pass


class TestDataFetcherUseBigQuery:
    """Test direct BigQuery usage (skip files)."""

    @pytest.mark.asyncio
    async def test_use_bigquery_directly(
        self,
        mock_file_source: MagicMock,
        mock_bigquery_source: MagicMock,
        mock_parser: MagicMock,
        event_filter: EventFilter,
    ) -> None:
        """Test using BigQuery directly when use_bigquery=True."""

        # Mock BigQuery to return data
        async def mock_query_events(filter_obj, columns=None, limit=None):  # type: ignore[no-untyped-def]
            yield {"GLOBALEVENTID": "789", "EventCode": "030"}

        mock_bigquery_source.query_events = mock_query_events

        # Create fetcher
        fetcher = DataFetcher(
            file_source=mock_file_source,
            bigquery_source=mock_bigquery_source,
        )

        # Fetch with use_bigquery=True
        events = []
        async for event in fetcher.fetch(event_filter, mock_parser, use_bigquery=True):
            events.append(event)

        assert len(events) == 1
        assert events[0]["GLOBALEVENTID"] == "789"

        # Verify file source was NOT called
        mock_file_source.get_files_for_date_range.assert_not_called()

    @pytest.mark.asyncio
    async def test_use_bigquery_without_source(
        self,
        mock_file_source: MagicMock,
        mock_parser: MagicMock,
        event_filter: EventFilter,
    ) -> None:
        """Test that use_bigquery=True raises error if BigQuery not configured."""
        # Create fetcher WITHOUT BigQuery source
        fetcher = DataFetcher(file_source=mock_file_source)

        # Try to fetch with use_bigquery=True - should raise ConfigurationError
        with pytest.raises(ConfigurationError, match="not configured"):
            async for _ in fetcher.fetch(event_filter, mock_parser, use_bigquery=True):
                pass


class TestDataFetcherConvenienceMethods:
    """Test convenience methods (fetch_events, fetch_gkg, etc.)."""

    @pytest.mark.asyncio
    async def test_fetch_events(
        self,
        mock_file_source: MagicMock,
        event_filter: EventFilter,
    ) -> None:
        """Test fetch_events convenience method."""
        # Mock file source
        mock_file_source.get_files_for_date_range = AsyncMock(
            return_value=["http://example.com/file1.zip"],
        )

        async def mock_stream_files(urls):  # type: ignore[no-untyped-def]
            # Async generator that yields nothing (to avoid parser errors)
            if False:
                yield

        mock_file_source.stream_files = mock_stream_files

        # Create fetcher
        fetcher = DataFetcher(file_source=mock_file_source)

        # Fetch events
        events = []
        async for event in fetcher.fetch_events(event_filter):
            events.append(event)

        # Verify file source was called
        mock_file_source.get_files_for_date_range.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_gkg(
        self,
        mock_file_source: MagicMock,
        gkg_filter: GKGFilter,
    ) -> None:
        """Test fetch_gkg convenience method."""
        # Mock file source
        mock_file_source.get_files_for_date_range = AsyncMock(
            return_value=["http://example.com/file1.zip"],
        )

        async def mock_stream_files(urls):  # type: ignore[no-untyped-def]
            # Async generator that yields nothing (to avoid parser errors)
            if False:
                yield

        mock_file_source.stream_files = mock_stream_files

        # Create fetcher
        fetcher = DataFetcher(file_source=mock_file_source)

        # Fetch GKG
        gkgs = []
        async for gkg in fetcher.fetch_gkg(gkg_filter):
            gkgs.append(gkg)

        # Verify file source was called
        mock_file_source.get_files_for_date_range.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_mentions_requires_bigquery(
        self,
        mock_file_source: MagicMock,
        event_filter: EventFilter,
    ) -> None:
        """Test that fetch_mentions requires BigQuery."""
        # Create fetcher WITHOUT BigQuery source
        fetcher = DataFetcher(file_source=mock_file_source)

        # Try to fetch mentions - should raise ConfigurationError
        with pytest.raises(ConfigurationError, match="BigQuery"):
            async for _ in fetcher.fetch_mentions("123", event_filter):
                pass

    @pytest.mark.asyncio
    async def test_fetch_mentions_with_bigquery(
        self,
        mock_file_source: MagicMock,
        mock_bigquery_source: MagicMock,
        event_filter: EventFilter,
    ) -> None:
        """Test fetch_mentions with BigQuery configured."""

        # Mock BigQuery to return mentions
        async def mock_query_mentions(global_event_id, columns=None, date_range=None):  # type: ignore[no-untyped-def]
            yield {
                "GLOBALEVENTID": global_event_id,
                "MentionTimeDate": "20240101",
                "MentionSourceName": "test source",
            }

        mock_bigquery_source.query_mentions = mock_query_mentions

        # Create fetcher with BigQuery
        fetcher = DataFetcher(
            file_source=mock_file_source,
            bigquery_source=mock_bigquery_source,
        )

        # Fetch mentions
        mentions = []
        async for mention in fetcher.fetch_mentions("123", event_filter):
            mentions.append(mention)

        assert len(mentions) == 1
        assert mentions[0]["GLOBALEVENTID"] == "123"

    @pytest.mark.asyncio
    async def test_fetch_ngrams(
        self,
        mock_file_source: MagicMock,
        event_filter: EventFilter,
    ) -> None:
        """Test fetch_ngrams convenience method."""
        # Mock file source
        mock_file_source.get_files_for_date_range = AsyncMock(
            return_value=["http://example.com/file1.gz"],
        )

        async def mock_stream_files(urls):  # type: ignore[no-untyped-def]
            # Async generator that yields nothing (to avoid parser errors)
            if False:
                yield

        mock_file_source.stream_files = mock_stream_files

        # Create fetcher
        fetcher = DataFetcher(file_source=mock_file_source)

        # Fetch ngrams
        ngrams = []
        async for ngram in fetcher.fetch_ngrams(event_filter):
            ngrams.append(ngram)

        # Verify file source was called with ngrams file type
        mock_file_source.get_files_for_date_range.assert_called_once_with(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 2),
            file_type="ngrams",
            include_translation=False,
        )


class TestDataFetcherEdgeCases:
    """Test edge cases and error scenarios."""

    @pytest.mark.asyncio
    async def test_unsupported_filter_type(
        self,
        mock_file_source: MagicMock,
        mock_parser: MagicMock,
    ) -> None:
        """Test that unsupported filter types raise ValueError."""

        # Create a mock filter that's not EventFilter or GKGFilter
        class UnsupportedFilter:
            pass

        unsupported_filter = UnsupportedFilter()

        # Create fetcher
        fetcher = DataFetcher(file_source=mock_file_source)

        # Try to fetch - should raise ValueError
        with pytest.raises(ValueError, match="Unsupported filter type"):
            async for _ in fetcher._fetch_from_files(unsupported_filter, mock_parser):  # type: ignore[arg-type]
                pass

    @pytest.mark.asyncio
    async def test_parsing_error_with_skip_policy(
        self,
        mock_file_source: MagicMock,
        mock_parser: MagicMock,
        event_filter: EventFilter,
    ) -> None:
        """Test that parsing errors are handled according to error policy."""
        # Mock file source
        mock_file_source.get_files_for_date_range = AsyncMock(
            return_value=["http://example.com/file1.zip"],
        )

        async def mock_stream_files(urls):  # type: ignore[no-untyped-def]
            yield "http://example.com/file1.zip", b"bad data"

        mock_file_source.stream_files = mock_stream_files

        # Mock parser to raise error
        def mock_parse(data: bytes, is_translated: bool = False) -> Iterator[dict]:  # type: ignore[type-arg]
            raise ValueError("Parse error")

        mock_parser.parse = mock_parse

        # Create fetcher with skip policy
        fetcher = DataFetcher(
            file_source=mock_file_source,
            error_policy="skip",
        )

        # Fetch events - should skip errors and continue
        events = []
        async for event in fetcher._fetch_from_files(event_filter, mock_parser):
            events.append(event)

        # Should have no events (all failed)
        assert len(events) == 0
