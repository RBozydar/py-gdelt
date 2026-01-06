"""Unit tests for NGramsEndpoint.

Tests cover initialization, query/stream methods, filtering logic, sync wrappers,
and integration with DataFetcher for the GDELT NGrams 3.0 endpoint.
"""

from __future__ import annotations

from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from py_gdelt.endpoints.ngrams import NGramsEndpoint
from py_gdelt.filters import DateRange, NGramsFilter
from py_gdelt.models._internal import _RawNGram
from py_gdelt.models.ngrams import NGramRecord


class TestInitialization:
    """Test NGramsEndpoint initialization."""

    def test_init_default(self) -> None:
        """Test initialization with defaults."""
        endpoint = NGramsEndpoint()

        assert endpoint.settings is not None
        assert endpoint._file_source is not None
        assert endpoint._fetcher is not None
        assert endpoint._parser is not None
        assert endpoint._owns_sources is True

    def test_init_with_shared_file_source(self) -> None:
        """Test initialization with shared FileSource."""
        mock_file_source = MagicMock()

        endpoint = NGramsEndpoint(file_source=mock_file_source)

        assert endpoint._file_source is mock_file_source
        assert endpoint._owns_sources is False

    @pytest.mark.asyncio
    async def test_context_manager(self) -> None:
        """Test async context manager protocol."""
        async with NGramsEndpoint() as endpoint:
            assert endpoint is not None
            assert isinstance(endpoint, NGramsEndpoint)

    @pytest.mark.asyncio
    async def test_close_owned_sources(self) -> None:
        """Test close() closes owned resources."""
        endpoint = NGramsEndpoint()
        endpoint._file_source.__aexit__ = AsyncMock()

        await endpoint.close()

        endpoint._file_source.__aexit__.assert_called_once_with(None, None, None)

    @pytest.mark.asyncio
    async def test_close_shared_sources(self) -> None:
        """Test close() does not close shared resources."""
        mock_file_source = MagicMock()
        mock_file_source.__aexit__ = AsyncMock()

        endpoint = NGramsEndpoint(file_source=mock_file_source)
        await endpoint.close()

        mock_file_source.__aexit__.assert_not_called()


class TestMatchesFilter:
    """Test client-side filtering logic."""

    def test_matches_all_filters_pass(self) -> None:
        """Test record that matches all filter criteria."""
        endpoint = NGramsEndpoint()

        record = NGramRecord(
            date=datetime(2024, 1, 1, 12, 0, 0),
            ngram="climate change",
            language="en",
            segment_type=1,
            position=20,
            pre_context="scientists warn about",
            post_context="impacts on global",
            url="https://example.com/article",
        )

        filter_obj = NGramsFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            ngram="climate",
            language="en",
            min_position=0,
            max_position=30,
        )

        assert endpoint._matches_filter(record, filter_obj) is True

    def test_matches_ngram_case_insensitive(self) -> None:
        """Test ngram matching is case-insensitive."""
        endpoint = NGramsEndpoint()

        record = NGramRecord(
            date=datetime(2024, 1, 1),
            ngram="Climate Change",
            language="en",
            segment_type=1,
            position=20,
            pre_context="test",
            post_context="test",
            url="https://example.com",
        )

        filter_obj = NGramsFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            ngram="climate",
        )

        assert endpoint._matches_filter(record, filter_obj) is True

    def test_matches_ngram_substring(self) -> None:
        """Test ngram matching supports substring search."""
        endpoint = NGramsEndpoint()

        record = NGramRecord(
            date=datetime(2024, 1, 1),
            ngram="climate",
            language="en",
            segment_type=1,
            position=20,
            pre_context="test",
            post_context="test",
            url="https://example.com",
        )

        filter_obj = NGramsFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            ngram="lima",  # substring of "climate"
        )

        assert endpoint._matches_filter(record, filter_obj) is True

    def test_matches_ngram_fails(self) -> None:
        """Test record that fails ngram filter."""
        endpoint = NGramsEndpoint()

        record = NGramRecord(
            date=datetime(2024, 1, 1),
            ngram="weather",
            language="en",
            segment_type=1,
            position=20,
            pre_context="test",
            post_context="test",
            url="https://example.com",
        )

        filter_obj = NGramsFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            ngram="climate",
        )

        assert endpoint._matches_filter(record, filter_obj) is False

    def test_matches_language_exact(self) -> None:
        """Test language matching is exact."""
        endpoint = NGramsEndpoint()

        record = NGramRecord(
            date=datetime(2024, 1, 1),
            ngram="test",
            language="en",
            segment_type=1,
            position=20,
            pre_context="test",
            post_context="test",
            url="https://example.com",
        )

        filter_obj = NGramsFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            language="en",
        )

        assert endpoint._matches_filter(record, filter_obj) is True

    def test_matches_language_fails(self) -> None:
        """Test record that fails language filter."""
        endpoint = NGramsEndpoint()

        record = NGramRecord(
            date=datetime(2024, 1, 1),
            ngram="test",
            language="es",
            segment_type=1,
            position=20,
            pre_context="test",
            post_context="test",
            url="https://example.com",
        )

        filter_obj = NGramsFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            language="en",
        )

        assert endpoint._matches_filter(record, filter_obj) is False

    def test_matches_position_min(self) -> None:
        """Test min_position filter."""
        endpoint = NGramsEndpoint()

        record = NGramRecord(
            date=datetime(2024, 1, 1),
            ngram="test",
            language="en",
            segment_type=1,
            position=50,
            pre_context="test",
            post_context="test",
            url="https://example.com",
        )

        filter_obj = NGramsFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            min_position=30,
        )

        assert endpoint._matches_filter(record, filter_obj) is True

    def test_matches_position_min_fails(self) -> None:
        """Test record that fails min_position filter."""
        endpoint = NGramsEndpoint()

        record = NGramRecord(
            date=datetime(2024, 1, 1),
            ngram="test",
            language="en",
            segment_type=1,
            position=10,
            pre_context="test",
            post_context="test",
            url="https://example.com",
        )

        filter_obj = NGramsFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            min_position=30,
        )

        assert endpoint._matches_filter(record, filter_obj) is False

    def test_matches_position_max(self) -> None:
        """Test max_position filter."""
        endpoint = NGramsEndpoint()

        record = NGramRecord(
            date=datetime(2024, 1, 1),
            ngram="test",
            language="en",
            segment_type=1,
            position=20,
            pre_context="test",
            post_context="test",
            url="https://example.com",
        )

        filter_obj = NGramsFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            max_position=30,
        )

        assert endpoint._matches_filter(record, filter_obj) is True

    def test_matches_position_max_fails(self) -> None:
        """Test record that fails max_position filter."""
        endpoint = NGramsEndpoint()

        record = NGramRecord(
            date=datetime(2024, 1, 1),
            ngram="test",
            language="en",
            segment_type=1,
            position=80,
            pre_context="test",
            post_context="test",
            url="https://example.com",
        )

        filter_obj = NGramsFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            max_position=30,
        )

        assert endpoint._matches_filter(record, filter_obj) is False

    def test_matches_position_range(self) -> None:
        """Test min and max position together."""
        endpoint = NGramsEndpoint()

        record = NGramRecord(
            date=datetime(2024, 1, 1),
            ngram="test",
            language="en",
            segment_type=1,
            position=20,
            pre_context="test",
            post_context="test",
            url="https://example.com",
        )

        filter_obj = NGramsFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            min_position=10,
            max_position=30,
        )

        assert endpoint._matches_filter(record, filter_obj) is True

    def test_matches_no_filters(self) -> None:
        """Test record matches when no optional filters specified."""
        endpoint = NGramsEndpoint()

        record = NGramRecord(
            date=datetime(2024, 1, 1),
            ngram="anything",
            language="any",
            segment_type=1,
            position=50,
            pre_context="test",
            post_context="test",
            url="https://example.com",
        )

        filter_obj = NGramsFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
        )

        assert endpoint._matches_filter(record, filter_obj) is True


class TestStreamMethod:
    """Test stream() method."""

    @pytest.mark.asyncio
    async def test_stream_basic(self) -> None:
        """Test basic streaming with no filtering."""
        endpoint = NGramsEndpoint()

        # Mock raw records from DataFetcher
        raw_records = [
            _RawNGram(
                date="20240101120000",
                ngram="climate",
                language="en",
                segment_type="1",
                position="20",
                pre_context="scientists warn about",
                post_context="impacts on global",
                url="https://example.com/1",
            ),
            _RawNGram(
                date="20240101130000",
                ngram="weather",
                language="en",
                segment_type="1",
                position="30",
                pre_context="today's forecast shows",
                post_context="patterns across region",
                url="https://example.com/2",
            ),
        ]

        async def mock_fetch_ngrams(filter_obj):
            for record in raw_records:
                yield record

        endpoint._fetcher.fetch_ngrams = mock_fetch_ngrams

        filter_obj = NGramsFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
        )

        records = [record async for record in endpoint.stream(filter_obj)]

        assert len(records) == 2
        assert records[0].ngram == "climate"
        assert records[1].ngram == "weather"

    @pytest.mark.asyncio
    async def test_stream_with_filtering(self) -> None:
        """Test streaming with client-side filtering."""
        endpoint = NGramsEndpoint()

        raw_records = [
            _RawNGram(
                date="20240101120000",
                ngram="climate change",
                language="en",
                segment_type="1",
                position="20",
                pre_context="test",
                post_context="test",
                url="https://example.com/1",
            ),
            _RawNGram(
                date="20240101130000",
                ngram="weather",
                language="es",
                segment_type="1",
                position="30",
                pre_context="test",
                post_context="test",
                url="https://example.com/2",
            ),
            _RawNGram(
                date="20240101140000",
                ngram="climate policy",
                language="en",
                segment_type="1",
                position="80",
                pre_context="test",
                post_context="test",
                url="https://example.com/3",
            ),
        ]

        async def mock_fetch_ngrams(filter_obj):
            for record in raw_records:
                yield record

        endpoint._fetcher.fetch_ngrams = mock_fetch_ngrams

        filter_obj = NGramsFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
            ngram="climate",
            language="en",
            max_position=50,
        )

        records = [record async for record in endpoint.stream(filter_obj)]

        # Should only get first record (has "climate", language="en", position=20)
        assert len(records) == 1
        assert records[0].ngram == "climate change"

    @pytest.mark.asyncio
    async def test_stream_conversion_error_handling(self) -> None:
        """Test stream handles conversion errors gracefully."""
        endpoint = NGramsEndpoint()

        # Invalid raw record (bad date format)
        raw_records = [
            _RawNGram(
                date="invalid_date",
                ngram="test",
                language="en",
                segment_type="1",
                position="20",
                pre_context="test",
                post_context="test",
                url="https://example.com",
            ),
        ]

        async def mock_fetch_ngrams(filter_obj):
            for record in raw_records:
                yield record

        endpoint._fetcher.fetch_ngrams = mock_fetch_ngrams

        filter_obj = NGramsFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
        )

        records = [record async for record in endpoint.stream(filter_obj)]

        # Should skip invalid record
        assert len(records) == 0


class TestQueryMethod:
    """Test query() method."""

    @pytest.mark.asyncio
    async def test_query_collects_all_records(self) -> None:
        """Test query() collects all records from stream."""
        endpoint = NGramsEndpoint()

        raw_records = [
            _RawNGram(
                date="20240101120000",
                ngram="test1",
                language="en",
                segment_type="1",
                position="20",
                pre_context="test",
                post_context="test",
                url="https://example.com/1",
            ),
            _RawNGram(
                date="20240101130000",
                ngram="test2",
                language="en",
                segment_type="1",
                position="30",
                pre_context="test",
                post_context="test",
                url="https://example.com/2",
            ),
        ]

        async def mock_fetch_ngrams(filter_obj):
            for record in raw_records:
                yield record

        endpoint._fetcher.fetch_ngrams = mock_fetch_ngrams

        filter_obj = NGramsFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
        )

        result = await endpoint.query(filter_obj)

        assert len(result) == 2
        assert result.data[0].ngram == "test1"
        assert result.data[1].ngram == "test2"
        assert result.complete is True
        assert result.total_failed == 0

    @pytest.mark.asyncio
    async def test_query_empty_results(self) -> None:
        """Test query() with no matching records."""
        endpoint = NGramsEndpoint()

        async def mock_fetch_ngrams(filter_obj):
            # Yield nothing
            if False:
                yield

        endpoint._fetcher.fetch_ngrams = mock_fetch_ngrams

        filter_obj = NGramsFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
        )

        result = await endpoint.query(filter_obj)

        assert len(result) == 0
        assert result.complete is True


class TestSyncWrappers:
    """Test synchronous wrapper methods."""

    def test_query_sync(self) -> None:
        """Test query_sync() wrapper."""
        with patch("asyncio.run") as mock_run:
            mock_result = MagicMock()
            mock_run.return_value = mock_result

            endpoint = NGramsEndpoint()
            filter_obj = NGramsFilter(
                date_range=DateRange(start=date(2024, 1, 1)),
            )

            result = endpoint.query_sync(filter_obj)

            mock_run.assert_called_once()
            assert result is mock_result

    def test_stream_sync(self) -> None:
        """Test stream_sync() wrapper yields records."""
        endpoint = NGramsEndpoint()

        # Create mock async generator
        raw_records = [
            _RawNGram(
                date="20240101120000",
                ngram="test",
                language="en",
                segment_type="1",
                position="20",
                pre_context="test",
                post_context="test",
                url="https://example.com",
            ),
        ]

        async def mock_fetch_ngrams(filter_obj):
            for record in raw_records:
                yield record

        endpoint._fetcher.fetch_ngrams = mock_fetch_ngrams

        filter_obj = NGramsFilter(
            date_range=DateRange(start=date(2024, 1, 1)),
        )

        records = list(endpoint.stream_sync(filter_obj))

        assert len(records) == 1
        assert records[0].ngram == "test"
