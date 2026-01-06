"""
Unit tests for GDELT Events parser.

Tests cover:
- Version detection (v1 vs v2)
- TAB delimiter handling
- CAMEO code preservation (leading zeros)
- Empty field handling (None conversion)
- Malformed line handling
- UTF-8 encoding
- Both v1 (57 columns) and v2 (61 columns) formats
"""

import pytest

from py_gdelt.exceptions import ParseError
from py_gdelt.parsers.events import EventsParser


class TestVersionDetection:
    """Test automatic version detection from column count."""

    def test_detect_v2_format(self) -> None:
        """Test detection of v2 format (61 columns)."""
        parser = EventsParser()
        # Create a header with 61 TAB-separated columns
        header = b"\t".join([b"col"] * 61)
        version = parser.detect_version(header)
        assert version == 2

    def test_detect_v1_format(self) -> None:
        """Test detection of v1 format (57 columns)."""
        parser = EventsParser()
        # Create a header with 57 TAB-separated columns
        header = b"\t".join([b"col"] * 57)
        version = parser.detect_version(header)
        assert version == 1

    def test_detect_invalid_format(self) -> None:
        """Test error on invalid column count."""
        parser = EventsParser()
        # Create a header with 50 columns (invalid)
        header = b"\t".join([b"col"] * 50)

        with pytest.raises(ParseError) as exc_info:
            parser.detect_version(header)

        assert "expected 57 (v1) or 61 (v2)" in str(exc_info.value)
        assert "found 50" in str(exc_info.value)

    def test_detect_utf8_decode_error(self) -> None:
        """Test error on invalid UTF-8 encoding."""
        parser = EventsParser()
        # Invalid UTF-8 sequence
        header = b"\xff\xfe" + b"\t".join([b"col"] * 61)

        with pytest.raises(ParseError) as exc_info:
            parser.detect_version(header)

        assert "Failed to decode header as UTF-8" in str(exc_info.value)


class TestV2Parsing:
    """Test parsing of GDELT Events v2 format (61 columns)."""

    @pytest.fixture
    def sample_v2_row(self) -> list[str]:
        """Create a sample v2 row with all fields populated."""
        return [
            # Event identification (0-4)
            "1234567890",  # GLOBALEVENTID
            "20240101",  # SQLDATE
            "202401",  # MonthYear
            "2024",  # Year
            "2024.0014",  # FractionDate
            # Actor1 (5-14)
            "USA",  # Actor1Code
            "UNITED STATES",  # Actor1Name
            "USA",  # Actor1CountryCode
            "GOV",  # Actor1KnownGroupCode
            "",  # Actor1EthnicCode (empty)
            "CHR",  # Actor1Religion1Code
            "",  # Actor1Religion2Code (empty)
            "GOV",  # Actor1Type1Code
            "EXEC",  # Actor1Type2Code
            "",  # Actor1Type3Code (empty)
            # Actor2 (15-24)
            "CHN",  # Actor2Code
            "CHINA",  # Actor2Name
            "CHN",  # Actor2CountryCode
            "GOV",  # Actor2KnownGroupCode
            "",  # Actor2EthnicCode (empty)
            "",  # Actor2Religion1Code (empty)
            "",  # Actor2Religion2Code (empty)
            "GOV",  # Actor2Type1Code
            "",  # Actor2Type2Code (empty)
            "",  # Actor2Type3Code (empty)
            # Event attributes (25-34)
            "1",  # IsRootEvent
            "042",  # EventCode (CAMEO with leading zero)
            "04",  # EventBaseCode
            "04",  # EventRootCode
            "1",  # QuadClass
            "3.4",  # GoldsteinScale
            "5",  # NumMentions
            "3",  # NumSources
            "2",  # NumArticles
            "-2.5",  # AvgTone
            # Actor1Geo (35-42)
            "3",  # Actor1Geo_Type
            "Washington, District of Columbia, United States",  # Actor1Geo_Fullname
            "US",  # Actor1Geo_CountryCode
            "USDC",  # Actor1Geo_ADM1Code
            "",  # Actor1Geo_ADM2Code (empty)
            "38.8951",  # Actor1Geo_Lat
            "-77.0364",  # Actor1Geo_Long
            "531871",  # Actor1Geo_FeatureID
            # Actor2Geo (43-50)
            "3",  # Actor2Geo_Type
            "Beijing, Beijing, China",  # Actor2Geo_Fullname
            "CH",  # Actor2Geo_CountryCode
            "CH22",  # Actor2Geo_ADM1Code
            "",  # Actor2Geo_ADM2Code (empty)
            "39.9042",  # Actor2Geo_Lat
            "116.4074",  # Actor2Geo_Long
            "1816670",  # Actor2Geo_FeatureID
            # ActionGeo (51-58)
            "3",  # ActionGeo_Type
            "New York, New York, United States",  # ActionGeo_Fullname
            "US",  # ActionGeo_CountryCode
            "USNY",  # ActionGeo_ADM1Code
            "",  # ActionGeo_ADM2Code (empty)
            "40.7128",  # ActionGeo_Lat
            "-74.0060",  # ActionGeo_Long
            "5128581",  # ActionGeo_FeatureID
            # Metadata (59-60)
            "20240101120000",  # DATEADDED
            "http://example.com/article.html",  # SOURCEURL
        ]

    def test_parse_complete_v2_row(self, sample_v2_row: list[str]) -> None:
        """Test parsing a complete v2 row with all fields."""
        parser = EventsParser()
        data = "\t".join(sample_v2_row).encode("utf-8")

        events = list(parser.parse(data, is_translated=False))

        assert len(events) == 1
        event = events[0]

        # Verify event identification
        assert event.global_event_id == "1234567890"
        assert event.sql_date == "20240101"
        assert event.month_year == "202401"
        assert event.year == "2024"
        assert event.fraction_date == "2024.0014"

        # Verify Actor1
        assert event.actor1_code == "USA"
        assert event.actor1_name == "UNITED STATES"
        assert event.actor1_country_code == "USA"
        assert event.actor1_known_group_code == "GOV"
        assert event.actor1_ethnic_code is None  # Empty field
        assert event.actor1_religion1_code == "CHR"
        assert event.actor1_religion2_code is None
        assert event.actor1_type1_code == "GOV"
        assert event.actor1_type2_code == "EXEC"
        assert event.actor1_type3_code is None

        # Verify Actor2
        assert event.actor2_code == "CHN"
        assert event.actor2_name == "CHINA"

        # Verify event attributes
        assert event.is_root_event == "1"
        assert event.event_code == "042"  # CAMEO code preserved with leading zero
        assert event.event_base_code == "04"
        assert event.event_root_code == "04"
        assert event.quad_class == "1"
        assert event.goldstein_scale == "3.4"
        assert event.num_mentions == "5"
        assert event.num_sources == "3"
        assert event.num_articles == "2"
        assert event.avg_tone == "-2.5"

        # Verify Actor1Geo
        assert event.actor1_geo_type == "3"
        assert "Washington" in event.actor1_geo_fullname
        assert event.actor1_geo_country_code == "US"
        assert event.actor1_geo_adm1_code == "USDC"
        assert event.actor1_geo_adm2_code is None
        assert event.actor1_geo_lat == "38.8951"
        assert event.actor1_geo_lon == "-77.0364"
        assert event.actor1_geo_feature_id == "531871"

        # Verify metadata
        assert event.date_added == "20240101120000"
        assert event.source_url == "http://example.com/article.html"
        assert event.is_translated is False

    def test_parse_v2_with_translated_flag(self, sample_v2_row: list[str]) -> None:
        """Test that is_translated flag is properly set."""
        parser = EventsParser()
        data = "\t".join(sample_v2_row).encode("utf-8")

        events = list(parser.parse(data, is_translated=True))

        assert len(events) == 1
        assert events[0].is_translated is True

    def test_parse_v2_minimal_row(self) -> None:
        """Test parsing v2 row with only required fields."""
        parser = EventsParser()
        # Create minimal row with required fields and empty optionals
        row = [""] * 61
        # Fill required fields
        row[0] = "123"  # GLOBALEVENTID
        row[1] = "20240101"  # SQLDATE
        row[2] = "202401"  # MonthYear
        row[3] = "2024"  # Year
        row[4] = "2024.0014"  # FractionDate
        row[25] = "1"  # IsRootEvent
        row[26] = "010"  # EventCode
        row[27] = "01"  # EventBaseCode
        row[28] = "01"  # EventRootCode
        row[29] = "1"  # QuadClass
        row[30] = "0.0"  # GoldsteinScale
        row[31] = "1"  # NumMentions
        row[32] = "1"  # NumSources
        row[33] = "1"  # NumArticles
        row[34] = "0.0"  # AvgTone
        row[59] = "20240101"  # DATEADDED
        row[60] = "http://example.com/test"  # SOURCEURL (v2 specific, position 60)

        data = "\t".join(row).encode("utf-8")
        events = list(parser.parse(data))

        assert len(events) == 1
        event = events[0]

        assert event.global_event_id == "123"
        assert event.event_code == "010"  # Leading zero preserved
        assert event.actor1_code is None
        assert event.actor2_code is None
        assert event.source_url == "http://example.com/test"

    def test_parse_multiple_v2_rows(self) -> None:
        """Test parsing multiple v2 rows."""
        parser = EventsParser()
        rows = []
        for i in range(3):
            row = [""] * 61
            # Fill required fields
            row[0] = str(i)
            row[1] = "20240101"
            row[2] = "202401"
            row[3] = "2024"
            row[4] = "2024.0014"
            row[25] = "1"
            row[26] = f"0{i}0"  # 000, 010, 020
            row[27] = "01"
            row[28] = "01"
            row[29] = "1"
            row[30] = "0.0"
            row[31] = "1"
            row[32] = "1"
            row[33] = "1"
            row[34] = "0.0"
            row[59] = "20240101"
            row[60] = f"http://example.com/{i}"  # SOURCEURL
            rows.append("\t".join(row))

        data = "\n".join(rows).encode("utf-8")
        events = list(parser.parse(data))

        assert len(events) == 3
        assert events[0].global_event_id == "0"
        assert events[1].global_event_id == "1"
        assert events[2].global_event_id == "2"
        assert events[0].event_code == "000"
        assert events[1].event_code == "010"
        assert events[2].event_code == "020"


class TestV1Parsing:
    """Test parsing of GDELT Events v1 format (57 columns)."""

    @pytest.fixture
    def sample_v1_row(self) -> list[str]:
        """Create a sample v1 row with all fields populated."""
        return [
            # Event identification (0-4)
            "1234567890",  # GLOBALEVENTID
            "20240101",  # SQLDATE
            "202401",  # MonthYear
            "2024",  # Year
            "2024.0014",  # FractionDate
            # Actor1 (5-14)
            "USA",  # Actor1Code
            "UNITED STATES",  # Actor1Name
            "USA",  # Actor1CountryCode
            "GOV",  # Actor1KnownGroupCode
            "",  # Actor1EthnicCode (empty)
            "CHR",  # Actor1Religion1Code
            "",  # Actor1Religion2Code (empty)
            "GOV",  # Actor1Type1Code
            "EXEC",  # Actor1Type2Code
            "",  # Actor1Type3Code (empty)
            # Actor2 (15-24)
            "CHN",  # Actor2Code
            "CHINA",  # Actor2Name
            "CHN",  # Actor2CountryCode
            "GOV",  # Actor2KnownGroupCode
            "",  # Actor2EthnicCode (empty)
            "",  # Actor2Religion1Code (empty)
            "",  # Actor2Religion2Code (empty)
            "GOV",  # Actor2Type1Code
            "",  # Actor2Type2Code (empty)
            "",  # Actor2Type3Code (empty)
            # Event attributes (25-34)
            "1",  # IsRootEvent
            "042",  # EventCode (CAMEO with leading zero)
            "04",  # EventBaseCode
            "04",  # EventRootCode
            "1",  # QuadClass
            "3.4",  # GoldsteinScale
            "5",  # NumMentions
            "3",  # NumSources
            "2",  # NumArticles
            "-2.5",  # AvgTone
            # Actor1Geo (35-41) - v1 has no FeatureID
            "3",  # Actor1Geo_Type
            "Washington, District of Columbia, United States",  # Actor1Geo_Fullname
            "US",  # Actor1Geo_CountryCode
            "USDC",  # Actor1Geo_ADM1Code
            "",  # Actor1Geo_ADM2Code (empty)
            "38.8951",  # Actor1Geo_Lat
            "-77.0364",  # Actor1Geo_Long
            # Actor2Geo (42-48) - v1 has no FeatureID
            "3",  # Actor2Geo_Type
            "Beijing, Beijing, China",  # Actor2Geo_Fullname
            "CH",  # Actor2Geo_CountryCode
            "CH22",  # Actor2Geo_ADM1Code
            "",  # Actor2Geo_ADM2Code (empty)
            "39.9042",  # Actor2Geo_Lat
            "116.4074",  # Actor2Geo_Long
            # ActionGeo (49-55) - v1 has no FeatureID
            "3",  # ActionGeo_Type
            "New York, New York, United States",  # ActionGeo_Fullname
            "US",  # ActionGeo_CountryCode
            "USNY",  # ActionGeo_ADM1Code
            "",  # ActionGeo_ADM2Code (empty)
            "40.7128",  # ActionGeo_Lat
            "-74.0060",  # ActionGeo_Long
            # Metadata (56)
            "20240101",  # DATEADDED (v1: YYYYMMDD at position 56, no timestamp)
        ]

    def test_parse_complete_v1_row(self, sample_v1_row: list[str]) -> None:
        """Test parsing a complete v1 row with all fields."""
        parser = EventsParser()
        data = "\t".join(sample_v1_row).encode("utf-8")

        events = list(parser.parse(data, is_translated=False))

        assert len(events) == 1
        event = events[0]

        # Verify event identification
        assert event.global_event_id == "1234567890"
        assert event.sql_date == "20240101"

        # Verify event attributes
        assert event.event_code == "042"  # CAMEO code preserved with leading zero

        # Verify metadata (v1 specific)
        assert event.date_added == "20240101"  # v1: YYYYMMDD only
        assert event.source_url is None  # v1: no SOURCEURL field

    def test_parse_v1_minimal_row(self) -> None:
        """Test parsing v1 row with only required fields."""
        parser = EventsParser()
        # Create minimal row with required fields and empty optionals
        row = [""] * 57
        # Fill required fields (v1 format)
        row[0] = "123"  # GLOBALEVENTID
        row[1] = "20240101"  # SQLDATE
        row[2] = "202401"  # MonthYear
        row[3] = "2024"  # Year
        row[4] = "2024.0014"  # FractionDate
        row[25] = "1"  # IsRootEvent
        row[26] = "010"  # EventCode
        row[27] = "01"  # EventBaseCode
        row[28] = "01"  # EventRootCode
        row[29] = "1"  # QuadClass
        row[30] = "0.0"  # GoldsteinScale
        row[31] = "1"  # NumMentions
        row[32] = "1"  # NumSources
        row[33] = "1"  # NumArticles
        row[34] = "0.0"  # AvgTone
        row[56] = "20240101"  # DATEADDED (v1 position: 56)

        data = "\t".join(row).encode("utf-8")
        events = list(parser.parse(data))

        assert len(events) == 1
        event = events[0]

        assert event.global_event_id == "123"
        assert event.event_code == "010"  # Leading zero preserved
        assert event.date_added == "20240101"
        assert event.source_url is None  # v1 has no SOURCEURL
        assert event.actor1_geo_feature_id is None  # v1 has no FeatureID fields
        assert event.actor2_geo_feature_id is None
        assert event.action_geo_feature_id is None


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_parse_empty_data(self) -> None:
        """Test parsing empty data."""
        parser = EventsParser()
        events = list(parser.parse(b""))
        assert events == []

    def test_parse_whitespace_only(self) -> None:
        """Test parsing whitespace-only data."""
        parser = EventsParser()
        events = list(parser.parse(b"   \n\n   \n"))
        assert events == []

    def test_parse_with_empty_lines(self) -> None:
        """Test parsing data with empty lines interspersed."""
        parser = EventsParser()
        # Create valid v2 row
        row = [""] * 61
        row[0] = "123"
        row[1] = "20240101"
        row[2] = "202401"
        row[3] = "2024"
        row[4] = "2024.0014"
        row[25] = "1"
        row[26] = "010"
        row[27] = "01"
        row[28] = "01"
        row[29] = "1"
        row[30] = "0.0"
        row[31] = "1"
        row[32] = "1"
        row[33] = "1"
        row[34] = "0.0"
        row[59] = "20240101"
        row[60] = "http://example.com/test"  # SOURCEURL

        row_str = "\t".join(row)
        # Test with empty lines interspersed (but not leading, as parser checks first line)
        data = f"{row_str}\n\n{row_str}\n".encode()
        events = list(parser.parse(data))

        assert len(events) == 2

    def test_parse_invalid_utf8(self) -> None:
        """Test error on invalid UTF-8 encoding."""
        parser = EventsParser()
        # Invalid UTF-8 sequence
        data = b"\xff\xfe\x00\x00"

        with pytest.raises(ParseError) as exc_info:
            list(parser.parse(data))

        assert "Failed to decode data as UTF-8" in str(exc_info.value)

    def test_parse_malformed_row_skipped(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test that malformed rows are logged and skipped."""
        parser = EventsParser()
        # Create one valid row and one malformed row (missing required fields)
        valid_row = [""] * 61
        valid_row[0] = "123"
        valid_row[1] = "20240101"
        valid_row[2] = "202401"
        valid_row[3] = "2024"
        valid_row[4] = "2024.0014"
        valid_row[25] = "1"
        valid_row[26] = "010"
        valid_row[27] = "01"
        valid_row[28] = "01"
        valid_row[29] = "1"
        valid_row[30] = "0.0"
        valid_row[31] = "1"
        valid_row[32] = "1"
        valid_row[33] = "1"
        valid_row[34] = "0.0"
        valid_row[59] = "20240101"
        valid_row[60] = "http://example.com/test"  # SOURCEURL

        # Malformed row: wrong column count (only 10 columns instead of 61)
        malformed_row = ["malformed"] * 10

        data = ("\t".join(valid_row) + "\n" + "\t".join(malformed_row)).encode("utf-8")

        events = list(parser.parse(data))

        # Should only get the valid row
        assert len(events) == 1
        assert events[0].global_event_id == "123"

        # Check that warning was logged for the malformed row
        assert "Skipping malformed line" in caplog.text

    def test_cameo_code_leading_zeros_preserved(self) -> None:
        """Test that CAMEO codes with leading zeros are preserved as strings."""
        parser = EventsParser()
        row = [""] * 61
        row[0] = "123"
        row[1] = "20240101"
        row[2] = "202401"
        row[3] = "2024"
        row[4] = "2024.0014"
        row[25] = "1"
        row[26] = "010"  # Leading zero
        row[27] = "01"  # Leading zero
        row[28] = "0"  # Single digit
        row[29] = "1"
        row[30] = "0.0"
        row[31] = "1"
        row[32] = "1"
        row[33] = "1"
        row[34] = "0.0"
        row[59] = "20240101"
        row[60] = "http://example.com/test"  # SOURCEURL

        data = "\t".join(row).encode("utf-8")
        events = list(parser.parse(data))

        assert len(events) == 1
        event = events[0]
        assert event.event_code == "010"
        assert event.event_base_code == "01"
        assert event.event_root_code == "0"


class TestColumnMapping:
    """Test correct column mapping for different versions."""

    def test_v2_column_positions(self) -> None:
        """Test that v2 columns are in correct positions."""
        parser = EventsParser()

        # Verify key column positions
        assert parser.V2_COLUMNS["GLOBALEVENTID"] == 0
        assert parser.V2_COLUMNS["SQLDATE"] == 1
        assert parser.V2_COLUMNS["Actor1Code"] == 5
        assert parser.V2_COLUMNS["Actor2Code"] == 15
        assert parser.V2_COLUMNS["IsRootEvent"] == 25
        assert parser.V2_COLUMNS["EventCode"] == 26
        assert parser.V2_COLUMNS["Actor1Geo_Type"] == 35
        assert parser.V2_COLUMNS["Actor2Geo_Type"] == 43
        assert parser.V2_COLUMNS["ActionGeo_Type"] == 51
        assert parser.V2_COLUMNS["DATEADDED"] == 59
        assert parser.V2_COLUMNS["SOURCEURL"] == 60

    def test_v1_column_positions(self) -> None:
        """Test that v1 columns are in correct positions."""
        parser = EventsParser()

        # Verify key column positions
        assert parser.V1_COLUMNS["GLOBALEVENTID"] == 0
        assert parser.V1_COLUMNS["SQLDATE"] == 1
        assert parser.V1_COLUMNS["Actor1Code"] == 5
        assert parser.V1_COLUMNS["Actor2Code"] == 15
        assert parser.V1_COLUMNS["IsRootEvent"] == 25
        assert parser.V1_COLUMNS["EventCode"] == 26
        # v1 geo fields have different positions (no FeatureID)
        assert parser.V1_COLUMNS["Actor1Geo_Type"] == 35
        assert parser.V1_COLUMNS["Actor1Geo_Long"] == 41  # Last Actor1Geo field
        assert parser.V1_COLUMNS["Actor2Geo_Type"] == 42
        assert parser.V1_COLUMNS["Actor2Geo_Long"] == 48  # Last Actor2Geo field
        assert parser.V1_COLUMNS["ActionGeo_Type"] == 49
        assert parser.V1_COLUMNS["ActionGeo_Long"] == 55  # Last ActionGeo field
        assert parser.V1_COLUMNS["DATEADDED"] == 56  # Last column in v1
        assert "SOURCEURL" not in parser.V1_COLUMNS  # v1 has no SOURCEURL
        assert "Actor1Geo_FeatureID" not in parser.V1_COLUMNS  # v1 has no FeatureID
        assert "Actor2Geo_FeatureID" not in parser.V1_COLUMNS
        assert "ActionGeo_FeatureID" not in parser.V1_COLUMNS
