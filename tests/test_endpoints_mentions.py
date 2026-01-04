"""Tests for MentionsEndpoint module.

This module tests the MentionsEndpoint class which provides access to GDELT Mentions data
using DataFetcher for source orchestration.
"""

from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from py_gdelt.endpoints.mentions import MentionsEndpoint
from py_gdelt.exceptions import ConfigurationError
from py_gdelt.filters import DateRange, EventFilter
from py_gdelt.models._internal import _RawMention
from py_gdelt.models.common import FetchResult
from py_gdelt.models.events import Mention


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
def event_filter() -> EventFilter:
    """Create test EventFilter."""
    return EventFilter(
        date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 7)),
    )


@pytest.fixture
def sample_raw_mention() -> _RawMention:
    """Create sample _RawMention for testing."""
    return _RawMention(
        global_event_id="123456789",
        event_time_date="20240101",
        event_time_full="20240101120000",
        mention_time_date="20240101",
        mention_time_full="20240101130000",
        mention_type="1",
        mention_source_name="BBC News",
        mention_identifier="https://www.bbc.com/news/article",
        sentence_id="5",
        actor1_char_offset="123",
        actor2_char_offset="456",
        action_char_offset="789",
        in_raw_text="1",
        confidence="85",
        mention_doc_length="2500",
        mention_doc_tone="-2.5",
        mention_doc_translation_info=None,
        extras=None,
    )


@pytest.fixture
def sample_bigquery_row() -> dict:
    """Create sample BigQuery row dict for testing."""
    return {
        "GlobalEventID": 123456789,
        "EventTimeDate": 20240101,
        "EventTimeFullDate": 20240101120000,
        "MentionTimeDate": 20240101,
        "MentionTimeFullDate": 20240101130000,
        "MentionType": 1,
        "MentionSourceName": "BBC News",
        "MentionIdentifier": "https://www.bbc.com/news/article",
        "SentenceID": 5,
        "Actor1CharOffset": 123,
        "Actor2CharOffset": 456,
        "ActionCharOffset": 789,
        "InRawText": 1,
        "Confidence": 85,
        "MentionDocLen": 2500,
        "MentionDocTone": -2.5,
        "MentionDocTranslationInfo": None,
        "Extras": None,
    }


class TestMentionsEndpointInit:
    """Test MentionsEndpoint initialization."""

    def test_init_with_file_source_only(self, mock_file_source: MagicMock) -> None:
        """Test initialization with only file source."""
        endpoint = MentionsEndpoint(file_source=mock_file_source)

        assert hasattr(endpoint, "_fetcher")
        assert endpoint._fetcher is not None

    def test_init_with_both_sources(
        self,
        mock_file_source: MagicMock,
        mock_bigquery_source: MagicMock,
    ) -> None:
        """Test initialization with both file and BigQuery sources."""
        endpoint = MentionsEndpoint(
            file_source=mock_file_source,
            bigquery_source=mock_bigquery_source,
            fallback_enabled=True,
        )

        assert hasattr(endpoint, "_fetcher")
        assert endpoint._fetcher._fallback is True

    def test_init_with_fallback_disabled(
        self,
        mock_file_source: MagicMock,
        mock_bigquery_source: MagicMock,
    ) -> None:
        """Test initialization with fallback disabled."""
        endpoint = MentionsEndpoint(
            file_source=mock_file_source,
            bigquery_source=mock_bigquery_source,
            fallback_enabled=False,
        )

        assert endpoint._fetcher._fallback is False

    def test_init_with_error_policy(
        self,
        mock_file_source: MagicMock,
    ) -> None:
        """Test initialization with custom error policy."""
        endpoint = MentionsEndpoint(
            file_source=mock_file_source,
            error_policy="raise",
        )

        assert endpoint._fetcher._error_policy == "raise"


class TestMentionsEndpointQuery:
    """Test MentionsEndpoint.query() method."""

    @pytest.mark.asyncio
    async def test_query_returns_fetch_result(
        self,
        mock_file_source: MagicMock,
        event_filter: EventFilter,
        sample_raw_mention: _RawMention,
    ) -> None:
        """Test that query() returns FetchResult."""
        # Setup mock to return async iterator
        async def mock_fetch_mentions(*args, **kwargs):
            yield sample_raw_mention

        endpoint = MentionsEndpoint(file_source=mock_file_source)
        # Mock the fetcher's fetch_mentions method
        endpoint._fetcher.fetch_mentions = mock_fetch_mentions

        result = await endpoint.query(
            global_event_id="123456789",
            filter_obj=event_filter,
        )

        assert isinstance(result, FetchResult)
        assert len(result) == 1
        assert result.complete

    @pytest.mark.asyncio
    async def test_query_converts_raw_to_mention(
        self,
        mock_file_source: MagicMock,
        event_filter: EventFilter,
        sample_raw_mention: _RawMention,
    ) -> None:
        """Test that query() converts _RawMention to Mention."""

        async def mock_fetch_mentions(*args, **kwargs):
            yield sample_raw_mention

        endpoint = MentionsEndpoint(file_source=mock_file_source)
        endpoint._fetcher.fetch_mentions = mock_fetch_mentions

        result = await endpoint.query(
            global_event_id="123456789",
            filter_obj=event_filter,
        )

        assert len(result.data) == 1
        mention = result.data[0]
        assert isinstance(mention, Mention)
        assert mention.global_event_id == 123456789
        assert mention.source_name == "BBC News"
        assert mention.confidence == 85

    @pytest.mark.asyncio
    async def test_query_with_multiple_mentions(
        self,
        mock_file_source: MagicMock,
        event_filter: EventFilter,
        sample_raw_mention: _RawMention,
    ) -> None:
        """Test query() with multiple mentions."""

        async def mock_fetch_mentions(*args, **kwargs):
            for i in range(3):
                mention = _RawMention(
                    global_event_id="123456789",
                    event_time_date="20240101",
                    event_time_full="20240101120000",
                    mention_time_date="20240101",
                    mention_time_full="20240101130000",
                    mention_type="1",
                    mention_source_name=f"Source {i}",
                    mention_identifier=f"https://example.com/{i}",
                    sentence_id=str(i),
                    actor1_char_offset="0",
                    actor2_char_offset="0",
                    action_char_offset="0",
                    in_raw_text="1",
                    confidence="75",
                    mention_doc_length="1000",
                    mention_doc_tone="0.0",
                    mention_doc_translation_info=None,
                    extras=None,
                )
                yield mention

        endpoint = MentionsEndpoint(file_source=mock_file_source)
        endpoint._fetcher.fetch_mentions = mock_fetch_mentions
        result = await endpoint.query(
            global_event_id="123456789",
            filter_obj=event_filter,
        )

        assert len(result) == 3
        assert all(isinstance(m, Mention) for m in result.data)
        assert [m.source_name for m in result.data] == ["Source 0", "Source 1", "Source 2"]

    @pytest.mark.asyncio
    async def test_query_with_bigquery_dict(
        self,
        mock_file_source: MagicMock,
        event_filter: EventFilter,
        sample_bigquery_row: dict,
    ) -> None:
        """Test query() handles BigQuery dict results."""

        async def mock_fetch_mentions(*args, **kwargs):
            yield sample_bigquery_row

        endpoint = MentionsEndpoint(file_source=mock_file_source)
        endpoint._fetcher.fetch_mentions = mock_fetch_mentions
        result = await endpoint.query(
            global_event_id="123456789",
            filter_obj=event_filter,
        )

        assert len(result) == 1
        mention = result.data[0]
        assert isinstance(mention, Mention)
        assert mention.global_event_id == 123456789
        assert mention.source_name == "BBC News"

    @pytest.mark.asyncio
    async def test_query_passes_parameters_to_fetcher(
        self,
        mock_file_source: MagicMock,
        event_filter: EventFilter,
    ) -> None:
        """Test that query() passes correct parameters to fetcher."""
        call_args_captured = {}

        async def mock_fetch_mentions(*args, **kwargs):
            call_args_captured.update(kwargs)
            # Return empty iterator
            return
            yield  # Make it a generator

        endpoint = MentionsEndpoint(file_source=mock_file_source)
        endpoint._fetcher.fetch_mentions = mock_fetch_mentions
        await endpoint.query(
            global_event_id="123456789",
            filter_obj=event_filter,
            use_bigquery=True,
        )

        assert call_args_captured["global_event_id"] == "123456789"
        assert call_args_captured["filter_obj"] is event_filter
        assert call_args_captured["use_bigquery"] is True


class TestMentionsEndpointStream:
    """Test MentionsEndpoint.stream() method."""

    @pytest.mark.asyncio
    async def test_stream_yields_mentions(
        self,
        mock_file_source: MagicMock,
        event_filter: EventFilter,
        sample_raw_mention: _RawMention,
    ) -> None:
        """Test that stream() yields Mention objects."""

        async def mock_fetch_mentions(*args, **kwargs):
            yield sample_raw_mention

        endpoint = MentionsEndpoint(file_source=mock_file_source)
        endpoint._fetcher.fetch_mentions = mock_fetch_mentions
        mentions = []
        async for mention in endpoint.stream(
            global_event_id="123456789",
            filter_obj=event_filter,
        ):
            mentions.append(mention)

        assert len(mentions) == 1
        assert isinstance(mentions[0], Mention)
        assert mentions[0].global_event_id == 123456789

    @pytest.mark.asyncio
    async def test_stream_converts_raw_to_mention(
        self,
        mock_file_source: MagicMock,
        event_filter: EventFilter,
        sample_raw_mention: _RawMention,
    ) -> None:
        """Test that stream() converts _RawMention to Mention at yield boundary."""

        async def mock_fetch_mentions(*args, **kwargs):
            yield sample_raw_mention

        endpoint = MentionsEndpoint(file_source=mock_file_source)
        endpoint._fetcher.fetch_mentions = mock_fetch_mentions
        async for mention in endpoint.stream(
            global_event_id="123456789",
            filter_obj=event_filter,
        ):
            assert isinstance(mention, Mention)
            assert mention.source_name == "BBC News"
            assert mention.confidence == 85
            break

    @pytest.mark.asyncio
    async def test_stream_handles_bigquery_dicts(
        self,
        mock_file_source: MagicMock,
        event_filter: EventFilter,
        sample_bigquery_row: dict,
    ) -> None:
        """Test that stream() handles BigQuery dict results."""

        async def mock_fetch_mentions(*args, **kwargs):
            yield sample_bigquery_row

        endpoint = MentionsEndpoint(file_source=mock_file_source)
        endpoint._fetcher.fetch_mentions = mock_fetch_mentions
        mentions = []
        async for mention in endpoint.stream(
            global_event_id="123456789",
            filter_obj=event_filter,
        ):
            mentions.append(mention)

        assert len(mentions) == 1
        assert isinstance(mentions[0], Mention)

    @pytest.mark.asyncio
    async def test_stream_memory_efficient(
        self,
        mock_file_source: MagicMock,
        event_filter: EventFilter,
    ) -> None:
        """Test that stream() yields one at a time (memory efficient)."""
        yield_count = 0

        async def mock_fetch_mentions(*args, **kwargs):
            for i in range(100):
                mention = _RawMention(
                    global_event_id="123456789",
                    event_time_date="20240101",
                    event_time_full="20240101120000",
                    mention_time_date="20240101",
                    mention_time_full="20240101130000",
                    mention_type="1",
                    mention_source_name=f"Source {i}",
                    mention_identifier=f"https://example.com/{i}",
                    sentence_id=str(i),
                    actor1_char_offset="0",
                    actor2_char_offset="0",
                    action_char_offset="0",
                    in_raw_text="1",
                    confidence="75",
                    mention_doc_length="1000",
                    mention_doc_tone="0.0",
                    mention_doc_translation_info=None,
                    extras=None,
                )
                yield mention

        endpoint = MentionsEndpoint(file_source=mock_file_source)
        endpoint._fetcher.fetch_mentions = mock_fetch_mentions

        # Only consume first 10 items
        consumed = 0
        async for mention in endpoint.stream(
            global_event_id="123456789",
            filter_obj=event_filter,
        ):
            consumed += 1
            if consumed >= 10:
                break

        # Should have only consumed 10, not all 100
        assert consumed == 10


class TestMentionsEndpointSyncWrappers:
    """Test synchronous wrapper methods."""

    def test_query_sync_returns_fetch_result(
        self,
        mock_file_source: MagicMock,
        event_filter: EventFilter,
        sample_raw_mention: _RawMention,
    ) -> None:
        """Test that query_sync() returns FetchResult."""

        async def mock_fetch_mentions(*args, **kwargs):
            yield sample_raw_mention

        endpoint = MentionsEndpoint(file_source=mock_file_source)
        endpoint._fetcher.fetch_mentions = mock_fetch_mentions
        result = endpoint.query_sync(
            global_event_id="123456789",
            filter_obj=event_filter,
        )

        assert isinstance(result, FetchResult)
        assert len(result) == 1

    def test_stream_sync_yields_mentions(
        self,
        mock_file_source: MagicMock,
        event_filter: EventFilter,
        sample_raw_mention: _RawMention,
    ) -> None:
        """Test that stream_sync() yields Mention objects."""

        async def mock_fetch_mentions(*args, **kwargs):
            for i in range(3):
                mention = _RawMention(
                    global_event_id="123456789",
                    event_time_date="20240101",
                    event_time_full="20240101120000",
                    mention_time_date="20240101",
                    mention_time_full="20240101130000",
                    mention_type="1",
                    mention_source_name=f"Source {i}",
                    mention_identifier=f"https://example.com/{i}",
                    sentence_id=str(i),
                    actor1_char_offset="0",
                    actor2_char_offset="0",
                    action_char_offset="0",
                    in_raw_text="1",
                    confidence="75",
                    mention_doc_length="1000",
                    mention_doc_tone="0.0",
                    mention_doc_translation_info=None,
                    extras=None,
                )
                yield mention

        endpoint = MentionsEndpoint(file_source=mock_file_source)
        endpoint._fetcher.fetch_mentions = mock_fetch_mentions
        mentions = list(
            endpoint.stream_sync(
                global_event_id="123456789",
                filter_obj=event_filter,
            )
        )

        assert len(mentions) == 3
        assert all(isinstance(m, Mention) for m in mentions)


class TestMentionsEndpointDictConversion:
    """Test _dict_to_mention() helper method."""

    def test_dict_to_mention_converts_bigquery_row(
        self,
        mock_file_source: MagicMock,
        sample_bigquery_row: dict,
    ) -> None:
        """Test that _dict_to_mention() converts BigQuery row correctly."""
        endpoint = MentionsEndpoint(file_source=mock_file_source)
        mention = endpoint._dict_to_mention(sample_bigquery_row)

        assert isinstance(mention, Mention)
        assert mention.global_event_id == 123456789
        assert mention.source_name == "BBC News"
        assert mention.confidence == 85
        assert mention.doc_tone == -2.5

    def test_dict_to_mention_handles_missing_fields(
        self,
        mock_file_source: MagicMock,
    ) -> None:
        """Test that _dict_to_mention() handles missing fields gracefully."""
        minimal_row = {
            "GlobalEventID": 123,
            "EventTimeFullDate": 20240101120000,
            "MentionTimeFullDate": 20240101130000,
            "MentionSourceName": "Test Source",
            "MentionIdentifier": "https://test.com",
        }

        endpoint = MentionsEndpoint(file_source=mock_file_source)
        mention = endpoint._dict_to_mention(minimal_row)

        assert isinstance(mention, Mention)
        assert mention.global_event_id == 123
        assert mention.source_name == "Test Source"

    def test_dict_to_mention_converts_types(
        self,
        mock_file_source: MagicMock,
    ) -> None:
        """Test that _dict_to_mention() converts types correctly."""
        row = {
            "GlobalEventID": 123,
            "EventTimeDate": 20240101,
            "EventTimeFullDate": 20240101120000,
            "MentionTimeDate": 20240101,
            "MentionTimeFullDate": 20240101130000,
            "MentionType": 1,
            "MentionSourceName": "Test",
            "MentionIdentifier": "https://test.com",
            "SentenceID": 5,
            "Actor1CharOffset": 100,
            "Actor2CharOffset": 200,
            "ActionCharOffset": 300,
            "InRawText": 1,
            "Confidence": 90,
            "MentionDocLen": 3000,
            "MentionDocTone": 5.5,
        }

        endpoint = MentionsEndpoint(file_source=mock_file_source)
        mention = endpoint._dict_to_mention(row)

        assert mention.global_event_id == 123
        assert mention.mention_type == 1
        assert mention.sentence_id == 5
        assert mention.actor1_char_offset == 100
        assert mention.actor2_char_offset == 200
        assert mention.action_char_offset == 300
        assert mention.confidence == 90
        assert mention.doc_length == 3000
        assert mention.doc_tone == 5.5
        assert mention.in_raw_text is True


class TestMentionsEndpointEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.mark.asyncio
    async def test_query_with_empty_results(
        self,
        mock_file_source: MagicMock,
        event_filter: EventFilter,
    ) -> None:
        """Test query() with no mentions returned."""

        async def mock_fetch_mentions(*args, **kwargs):
            return
            yield  # Make it a generator

        endpoint = MentionsEndpoint(file_source=mock_file_source)
        endpoint._fetcher.fetch_mentions = mock_fetch_mentions
        result = await endpoint.query(
            global_event_id="123456789",
            filter_obj=event_filter,
        )

        assert len(result) == 0
        assert result.complete
        assert isinstance(result, FetchResult)

    @pytest.mark.asyncio
    async def test_stream_with_empty_results(
        self,
        mock_file_source: MagicMock,
        event_filter: EventFilter,
    ) -> None:
        """Test stream() with no mentions returned."""

        async def mock_fetch_mentions(*args, **kwargs):
            return
            yield  # Make it a generator

        endpoint = MentionsEndpoint(file_source=mock_file_source)
        endpoint._fetcher.fetch_mentions = mock_fetch_mentions
        mentions = []
        async for mention in endpoint.stream(
            global_event_id="123456789",
            filter_obj=event_filter,
        ):
            mentions.append(mention)

        assert len(mentions) == 0

    @pytest.mark.asyncio
    async def test_query_with_use_bigquery_false(
        self,
        mock_file_source: MagicMock,
        event_filter: EventFilter,
        sample_raw_mention: _RawMention,
    ) -> None:
        """Test query() with use_bigquery=False (files)."""

        async def mock_fetch_mentions(*args, **kwargs):
            yield sample_raw_mention

        endpoint = MentionsEndpoint(file_source=mock_file_source)
        endpoint._fetcher.fetch_mentions = mock_fetch_mentions
        result = await endpoint.query(
            global_event_id="123456789",
            filter_obj=event_filter,
            use_bigquery=False,
        )

        assert len(result) == 1
