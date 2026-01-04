"""Tests for GDELT Mentions parser."""

import pytest

from py_gdelt.models._internal import _RawMention
from py_gdelt.parsers.mentions import MentionsParser


class TestMentionsParser:
    """Test suite for MentionsParser."""

    @pytest.fixture
    def parser(self) -> MentionsParser:
        """Create a MentionsParser instance."""
        return MentionsParser()

    def test_parse_single_mention_full_fields(self, parser: MentionsParser) -> None:
        """Test parsing a single mention with all fields populated."""
        data = (
            "123456789\t"  # GlobalEventID
            "20240104120000\t"  # EventTimeDate (YYYYMMDDHHMMSS)
            "20240104121500\t"  # MentionTimeDate (YYYYMMDDHHMMSS)
            "1\t"  # MentionType (1=Web)
            "CNN\t"  # MentionSourceName
            "https://cnn.com/article/123\t"  # MentionIdentifier
            "5\t"  # SentenceID
            "45\t"  # Actor1CharOffset
            "78\t"  # Actor2CharOffset
            "100\t"  # ActionCharOffset
            "1\t"  # InRawText (1=in raw)
            "95\t"  # Confidence (1-100)
            "5000\t"  # MentionDocLen
            "-2.5\t"  # MentionDocTone
            "eng;spa\t"  # MentionDocTranslationInfo
            ""  # Extras (empty)
        ).encode("utf-8")

        mentions = list(parser.parse(data))

        assert len(mentions) == 1
        mention = mentions[0]

        assert isinstance(mention, _RawMention)
        assert mention.global_event_id == "123456789"
        assert mention.event_time_date == "20240104"
        assert mention.event_time_full == "20240104120000"
        assert mention.mention_time_date == "20240104"
        assert mention.mention_time_full == "20240104121500"
        assert mention.mention_type == "1"
        assert mention.mention_source_name == "CNN"
        assert mention.mention_identifier == "https://cnn.com/article/123"
        assert mention.sentence_id == "5"
        assert mention.actor1_char_offset == "45"
        assert mention.actor2_char_offset == "78"
        assert mention.action_char_offset == "100"
        assert mention.in_raw_text == "1"
        assert mention.confidence == "95"
        assert mention.mention_doc_length == "5000"
        assert mention.mention_doc_tone == "-2.5"
        assert mention.mention_doc_translation_info == "eng;spa"
        assert mention.extras is None

    def test_parse_mention_with_empty_optional_fields(self, parser: MentionsParser) -> None:
        """Test parsing mention with empty optional fields."""
        data = (
            "987654321\t"
            "20240104130000\t"
            "20240104130500\t"
            "2\t"  # MentionType (2=Citation)
            "BBC\t"
            "https://bbc.com/news/456\t"
            "1\t"
            "0\t"
            "0\t"
            "0\t"
            "0\t"
            "80\t"
            "3000\t"
            "1.2\t"
            "\t"  # Empty translation info
            ""  # Empty extras
        ).encode("utf-8")

        mentions = list(parser.parse(data))

        assert len(mentions) == 1
        mention = mentions[0]
        assert mention.global_event_id == "987654321"
        assert mention.mention_doc_translation_info is None
        assert mention.extras is None

    def test_parse_multiple_mentions(self, parser: MentionsParser) -> None:
        """Test parsing multiple mentions in one file."""
        data = (
            "111\t20240104100000\t20240104100500\t1\tCNN\thttp://a.com\t1\t10\t20\t30\t1\t90\t1000\t-1.0\t\t\n"
            "222\t20240104110000\t20240104110500\t2\tBBC\thttp://b.com\t2\t15\t25\t35\t0\t85\t2000\t0.5\t\t\n"
            "333\t20240104120000\t20240104120500\t3\tNYT\thttp://c.com\t3\t20\t30\t40\t1\t95\t3000\t2.0\t\t"
        ).encode("utf-8")

        mentions = list(parser.parse(data))

        assert len(mentions) == 3
        assert mentions[0].global_event_id == "111"
        assert mentions[1].global_event_id == "222"
        assert mentions[2].global_event_id == "333"

    def test_parse_empty_data(self, parser: MentionsParser) -> None:
        """Test parsing empty data returns no mentions."""
        data = b""
        mentions = list(parser.parse(data))
        assert len(mentions) == 0

    def test_parse_only_whitespace(self, parser: MentionsParser) -> None:
        """Test parsing whitespace-only data returns no mentions."""
        data = b"\n\n   \n\t\t\n"
        mentions = list(parser.parse(data))
        assert len(mentions) == 0

    def test_parse_malformed_line_wrong_column_count(
        self, parser: MentionsParser, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test that malformed lines with wrong column count are skipped."""
        data = (
            "111\t20240104100000\t20240104100500\t1\tCNN\thttp://a.com\t1\t10\t20\t30\t1\t90\t1000\t-1.0\t\t\n"
            "222\t20240104110000\t20240104110500\t2\tBBC\n"  # Only 5 columns (should be 16)
            "333\t20240104120000\t20240104120500\t3\tNYT\thttp://c.com\t3\t20\t30\t40\t1\t95\t3000\t2.0\t\t"
        ).encode("utf-8")

        with caplog.at_level("WARNING"):
            mentions = list(parser.parse(data))

        # Should only parse the valid lines
        assert len(mentions) == 2
        assert mentions[0].global_event_id == "111"
        assert mentions[1].global_event_id == "333"

        # Should log warning about malformed line
        assert "Malformed mention at line 2" in caplog.text
        assert "expected 16 columns, got 5" in caplog.text

    def test_parse_invalid_utf8(
        self, parser: MentionsParser, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test that invalid UTF-8 data is handled gracefully."""
        # Invalid UTF-8 sequence
        data = b"\xff\xfe\x00\x00"

        with caplog.at_level("ERROR"):
            mentions = list(parser.parse(data))

        assert len(mentions) == 0
        assert "Failed to decode mentions data as UTF-8" in caplog.text

    def test_parse_mention_types(self, parser: MentionsParser) -> None:
        """Test parsing different mention types (1=Web, 2=Citation, 3=Core, 4=Dtic, 5=Translation)."""
        data = (
            "1\t20240104100000\t20240104100500\t1\tCNN\thttp://a.com\t1\t0\t0\t0\t1\t90\t1000\t0\t\t\n"
            "2\t20240104100000\t20240104100500\t2\tBBC\thttp://b.com\t1\t0\t0\t0\t1\t90\t1000\t0\t\t\n"
            "3\t20240104100000\t20240104100500\t3\tNYT\thttp://c.com\t1\t0\t0\t0\t1\t90\t1000\t0\t\t\n"
            "4\t20240104100000\t20240104100500\t4\tDTIC\thttp://d.com\t1\t0\t0\t0\t1\t90\t1000\t0\t\t\n"
            "5\t20240104100000\t20240104100500\t5\tTranslated\thttp://e.com\t1\t0\t0\t0\t1\t90\t1000\t0\teng;fra\t"
        ).encode("utf-8")

        mentions = list(parser.parse(data))

        assert len(mentions) == 5
        assert mentions[0].mention_type == "1"  # Web
        assert mentions[1].mention_type == "2"  # Citation
        assert mentions[2].mention_type == "3"  # Core
        assert mentions[3].mention_type == "4"  # Dtic
        assert mentions[4].mention_type == "5"  # Translation
        assert mentions[4].mention_doc_translation_info == "eng;fra"

    def test_parse_confidence_range(self, parser: MentionsParser) -> None:
        """Test parsing confidence values (1-100 range)."""
        data = (
            "1\t20240104100000\t20240104100500\t1\tA\thttp://a.com\t1\t0\t0\t0\t1\t1\t1000\t0\t\t\n"
            "2\t20240104100000\t20240104100500\t1\tB\thttp://b.com\t1\t0\t0\t0\t1\t50\t1000\t0\t\t\n"
            "3\t20240104100000\t20240104100500\t1\tC\thttp://c.com\t1\t0\t0\t0\t1\t100\t1000\t0\t\t"
        ).encode("utf-8")

        mentions = list(parser.parse(data))

        assert len(mentions) == 3
        assert mentions[0].confidence == "1"
        assert mentions[1].confidence == "50"
        assert mentions[2].confidence == "100"

    def test_parse_negative_tone(self, parser: MentionsParser) -> None:
        """Test parsing negative tone values."""
        data = (
            "1\t20240104100000\t20240104100500\t1\tA\thttp://a.com\t1\t0\t0\t0\t1\t90\t1000\t-10.5\t\t"
        ).encode("utf-8")

        mentions = list(parser.parse(data))

        assert len(mentions) == 1
        assert mentions[0].mention_doc_tone == "-10.5"

    def test_parse_in_raw_text_flag(self, parser: MentionsParser) -> None:
        """Test parsing InRawText flag (0=extracted, 1=in raw)."""
        data = (
            "1\t20240104100000\t20240104100500\t1\tA\thttp://a.com\t1\t0\t0\t0\t0\t90\t1000\t0\t\t\n"
            "2\t20240104100000\t20240104100500\t1\tB\thttp://b.com\t1\t0\t0\t0\t1\t90\t1000\t0\t\t"
        ).encode("utf-8")

        mentions = list(parser.parse(data))

        assert len(mentions) == 2
        assert mentions[0].in_raw_text == "0"  # Extracted
        assert mentions[1].in_raw_text == "1"  # In raw text

    def test_parse_character_offsets(self, parser: MentionsParser) -> None:
        """Test parsing character offset fields."""
        data = (
            "1\t20240104100000\t20240104100500\t1\tA\thttp://a.com\t1\t100\t200\t300\t1\t90\t1000\t0\t\t"
        ).encode("utf-8")

        mentions = list(parser.parse(data))

        assert len(mentions) == 1
        assert mentions[0].actor1_char_offset == "100"
        assert mentions[0].actor2_char_offset == "200"
        assert mentions[0].action_char_offset == "300"

    def test_parse_preserves_string_types(self, parser: MentionsParser) -> None:
        """Test that all fields remain as strings for later type conversion."""
        data = (
            "123\t20240104100000\t20240104100500\t1\tCNN\thttp://a.com\t5\t10\t20\t30\t1\t95\t5000\t-2.5\t\t"
        ).encode("utf-8")

        mentions = list(parser.parse(data))

        mention = mentions[0]
        # All numeric fields should still be strings
        assert isinstance(mention.global_event_id, str)
        assert isinstance(mention.sentence_id, str)
        assert isinstance(mention.actor1_char_offset, str)
        assert isinstance(mention.confidence, str)
        assert isinstance(mention.mention_doc_length, str)
        assert isinstance(mention.mention_doc_tone, str)

    def test_parse_date_extraction_from_timestamp(self, parser: MentionsParser) -> None:
        """Test that date portion is correctly extracted from full timestamp."""
        data = (
            "1\t20240104235959\t20240105010203\t1\tA\thttp://a.com\t1\t0\t0\t0\t1\t90\t1000\t0\t\t"
        ).encode("utf-8")

        mentions = list(parser.parse(data))

        assert len(mentions) == 1
        mention = mentions[0]

        # Full timestamps
        assert mention.event_time_full == "20240104235959"
        assert mention.mention_time_full == "20240105010203"

        # Date portions (first 8 chars)
        assert mention.event_time_date == "20240104"
        assert mention.mention_time_date == "20240105"
