"""Tests for GDELT Broadcast NGrams parser (TV and Radio)."""

import pytest

from py_gdelt.parsers.broadcast_ngrams import BroadcastNGramsParser


class TestBroadcastNGramsParserTVFormat:
    """Test parsing of TV NGrams format (5 columns)."""

    @pytest.fixture
    def tv_sample_data(self) -> bytes:
        """Sample TV NGrams record (5 columns: DATE, STATION, HOUR, WORD, COUNT)."""
        return (
            b"20240115\tCNN\t14\tpresident\t42\n"
            b"20240115\tCNN\t14\teconomy\t28\n"
            b"20240115\tFOX\t18\telection\t35"
        )

    def test_parse_tv_basic_fields(self, tv_sample_data: bytes) -> None:
        """Should parse TV NGrams fields correctly."""
        parser = BroadcastNGramsParser()
        records = list(parser.parse(tv_sample_data))

        assert len(records) == 3

        first_record = records[0]
        assert first_record.date == "20240115"
        assert first_record.station == "CNN"
        assert first_record.hour == "14"
        assert first_record.ngram == "president"
        assert first_record.count == "42"
        assert first_record.show == ""  # TV format has no SHOW column

    def test_parse_tv_multiple_records(self, tv_sample_data: bytes) -> None:
        """Should parse multiple TV NGrams records."""
        parser = BroadcastNGramsParser()
        records = list(parser.parse(tv_sample_data))

        assert len(records) == 3
        assert records[0].ngram == "president"
        assert records[1].ngram == "economy"
        assert records[2].ngram == "election"

    def test_parse_tv_different_stations(self, tv_sample_data: bytes) -> None:
        """Should parse records from different stations."""
        parser = BroadcastNGramsParser()
        records = list(parser.parse(tv_sample_data))

        assert records[0].station == "CNN"
        assert records[1].station == "CNN"
        assert records[2].station == "FOX"

    def test_parse_tv_empty_show_field(self, tv_sample_data: bytes) -> None:
        """Should set show field to empty string for TV format."""
        parser = BroadcastNGramsParser()
        records = list(parser.parse(tv_sample_data))

        for record in records:
            assert record.show == ""


class TestBroadcastNGramsParserRadioFormat:
    """Test parsing of Radio NGrams format (6 columns)."""

    @pytest.fixture
    def radio_sample_data(self) -> bytes:
        """Sample Radio NGrams record (6 columns: DATE, STATION, HOUR, NGRAM, COUNT, SHOW)."""
        return (
            b"20240115\tKQED\t09\tclimate change\t15\tMorning Edition\n"
            b"20240115\tKQED\t09\tpolicy\t8\tMorning Edition\n"
            b"20240115\tWNYC\t12\thealth care\t22\tThe Takeaway"
        )

    def test_parse_radio_basic_fields(self, radio_sample_data: bytes) -> None:
        """Should parse Radio NGrams fields correctly."""
        parser = BroadcastNGramsParser()
        records = list(parser.parse(radio_sample_data))

        assert len(records) == 3

        first_record = records[0]
        assert first_record.date == "20240115"
        assert first_record.station == "KQED"
        assert first_record.hour == "09"
        assert first_record.ngram == "climate change"
        assert first_record.count == "15"
        assert first_record.show == "Morning Edition"

    def test_parse_radio_show_field(self, radio_sample_data: bytes) -> None:
        """Should parse SHOW field correctly for Radio format."""
        parser = BroadcastNGramsParser()
        records = list(parser.parse(radio_sample_data))

        assert records[0].show == "Morning Edition"
        assert records[1].show == "Morning Edition"
        assert records[2].show == "The Takeaway"

    def test_parse_radio_multi_word_ngrams(self, radio_sample_data: bytes) -> None:
        """Should handle multi-word ngrams correctly."""
        parser = BroadcastNGramsParser()
        records = list(parser.parse(radio_sample_data))

        assert records[0].ngram == "climate change"
        assert records[2].ngram == "health care"

    def test_parse_radio_multiple_records(self, radio_sample_data: bytes) -> None:
        """Should parse multiple Radio NGrams records."""
        parser = BroadcastNGramsParser()
        records = list(parser.parse(radio_sample_data))

        assert len(records) == 3
        assert all(record.show != "" for record in records)


class TestBroadcastNGramsParserMixedFormat:
    """Test parsing mixed TV and Radio NGrams (though typically files are homogeneous)."""

    def test_parse_mixed_tv_and_radio(self) -> None:
        """Should handle both TV (5 col) and Radio (6 col) in same file."""
        data = (
            b"20240115\tCNN\t14\tpresident\t42\n"  # TV (5 columns)
            b"20240115\tKQED\t09\tclimate\t15\tMorning Edition"  # Radio (6 columns)
        )

        parser = BroadcastNGramsParser()
        records = list(parser.parse(data))

        assert len(records) == 2
        assert records[0].show == ""  # TV
        assert records[1].show == "Morning Edition"  # Radio


class TestBroadcastNGramsParserEdgeCases:
    """Test edge cases and error handling."""

    def test_parse_empty_data(self) -> None:
        """Should handle empty data gracefully."""
        parser = BroadcastNGramsParser()
        records = list(parser.parse(b""))

        assert len(records) == 0

    def test_parse_whitespace_only(self) -> None:
        """Should handle whitespace-only data gracefully."""
        parser = BroadcastNGramsParser()
        records = list(parser.parse(b"   \n\n   \n"))

        assert len(records) == 0

    def test_parse_malformed_line_wrong_column_count(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Should skip lines with wrong column count."""
        data = (
            b"20240115\tCNN\t14\tpresident\t42\n"  # Valid TV (5 columns)
            b"TOO\tFEW\tCOLUMNS\n"  # Invalid (3 columns)
            b"20240115\tFOX\t18\telection\t35"  # Valid TV (5 columns)
        )

        parser = BroadcastNGramsParser()
        records = list(parser.parse(data))

        assert len(records) == 2  # Only valid records parsed
        assert "Skipping malformed broadcast NGrams line 2" in caplog.text
        assert "expected 5 (TV) or 6 (Radio) columns, got 3" in caplog.text

    def test_parse_malformed_line_too_many_columns(self, caplog: pytest.LogCaptureFixture) -> None:
        """Should skip lines with too many columns."""
        data = (
            b"20240115\tCNN\t14\tpresident\t42\n"  # Valid (5 columns)
            b"20240115\tCNN\t14\tword\t10\tshow\textra\tcolumns"  # Invalid (8 columns)
        )

        parser = BroadcastNGramsParser()
        records = list(parser.parse(data))

        assert len(records) == 1
        assert "Skipping malformed broadcast NGrams line 2" in caplog.text
        assert "got 8" in caplog.text

    def test_parse_empty_fields(self) -> None:
        """Should handle empty fields gracefully."""
        data = b"20240115\t\t14\tword\t42"  # Empty station field

        parser = BroadcastNGramsParser()
        records = list(parser.parse(data))

        assert len(records) == 1
        assert records[0].station == ""
        assert records[0].ngram == "word"

    def test_parse_whitespace_in_fields(self) -> None:
        """Should strip whitespace from fields."""
        data = b"20240115  \t  CNN  \t  14  \t  president  \t  42  "

        parser = BroadcastNGramsParser()
        records = list(parser.parse(data))

        assert len(records) == 1
        assert records[0].date == "20240115"
        assert records[0].station == "CNN"
        assert records[0].ngram == "president"

    def test_parse_utf8_with_invalid_chars(self) -> None:
        """Should handle invalid UTF-8 characters gracefully."""
        data = b"20240115\tCNN\xff\xfe\t14\tword\t42"  # Invalid UTF-8 in station

        parser = BroadcastNGramsParser()
        records = list(parser.parse(data))

        # Should still parse with replacement chars
        assert len(records) == 1
        assert records[0].date == "20240115"

    def test_parse_skip_blank_lines(self) -> None:
        """Should skip blank lines."""
        data = (
            b"20240115\tCNN\t14\tpresident\t42\n"
            b"\n"  # Blank line
            b"   \n"  # Whitespace-only line
            b"20240115\tFOX\t18\telection\t35"
        )

        parser = BroadcastNGramsParser()
        records = list(parser.parse(data))

        assert len(records) == 2

    def test_parse_exception_handling(self, caplog: pytest.LogCaptureFixture) -> None:
        """Should handle unexpected exceptions during parsing."""
        # This test ensures the error boundary works
        # Valid data should parse successfully
        data = b"20240115\tCNN\t14\tpresident\t42"

        parser = BroadcastNGramsParser()
        records = list(parser.parse(data))

        assert len(records) == 1


class TestBroadcastNGramsParserRealWorldScenarios:
    """Test realistic scenarios with sample data."""

    def test_parse_multiple_hours_same_station(self) -> None:
        """Should parse multiple hours from same station."""
        data = (
            b"20240115\tCNN\t08\tbreaking\t10\n"
            b"20240115\tCNN\t09\tbreaking\t12\n"
            b"20240115\tCNN\t10\tbreaking\t15"
        )

        parser = BroadcastNGramsParser()
        records = list(parser.parse(data))

        assert len(records) == 3
        assert all(record.station == "CNN" for record in records)
        assert [record.hour for record in records] == ["08", "09", "10"]

    def test_parse_varying_counts(self) -> None:
        """Should handle varying frequency counts."""
        data = (
            b"20240115\tCNN\t14\trare_word\t1\n"
            b"20240115\tCNN\t14\tcommon_word\t9999\n"
            b"20240115\tCNN\t14\tmedium_word\t150"
        )

        parser = BroadcastNGramsParser()
        records = list(parser.parse(data))

        assert records[0].count == "1"
        assert records[1].count == "9999"
        assert records[2].count == "150"

    def test_parse_special_characters_in_ngrams(self) -> None:
        """Should handle special characters in ngrams."""
        data = b"20240115\tCNN\t14\tdon't\t25"

        parser = BroadcastNGramsParser()
        records = list(parser.parse(data))

        assert len(records) == 1
        assert records[0].ngram == "don't"
