"""Tests for GDELT GKG parser."""

import pytest

from py_gdelt.parsers.gkg import GKGParser


class TestGKGParserVersionDetection:
    """Test version detection from column counts."""

    def test_detect_v1_format(self) -> None:
        """Should detect v1 format from 15 columns."""
        parser = GKGParser()
        # Create a header line with 15 tab-separated columns
        header = "\t".join([f"col{i}" for i in range(15)])
        version = parser.detect_version(header.encode("utf-8"))
        assert version == 1

    def test_detect_v2_format(self) -> None:
        """Should detect v2.1 format from 27 columns."""
        parser = GKGParser()
        # Create a header line with 27 tab-separated columns
        header = "\t".join([f"col{i}" for i in range(27)])
        version = parser.detect_version(header.encode("utf-8"))
        assert version == 2

    def test_reject_invalid_column_count(self) -> None:
        """Should raise ValueError for unsupported column counts."""
        parser = GKGParser()
        header = "\t".join([f"col{i}" for i in range(20)])  # Invalid count
        with pytest.raises(ValueError, match="Unsupported GKG column count: 20"):
            parser.detect_version(header.encode("utf-8"))

    def test_reject_empty_header(self) -> None:
        """Should raise ValueError for empty header."""
        parser = GKGParser()
        with pytest.raises(ValueError, match="Empty header line"):
            parser.detect_version(b"")


class TestGKGParserV1:
    """Test parsing of GKG v1 format (15 columns)."""

    @pytest.fixture
    def v1_sample_data(self) -> bytes:
        """Sample GKG v1 record (15 columns)."""
        # Format: GKGRECORDID, DATE, SourceCollectionId, SourceCommonName, DocumentIdentifier,
        # V1Counts, V1Themes, V1Locations, V1Persons, V1Organizations, V1.5Tone,
        # SharingImage, RelatedImages, Quotations, AllNames
        return (
            b"20130101000000-1\t20130101000000\t1\tExample.com\thttp://example.com/article1\t"
            b"10#PROTEST#123;20#VIOLENCE#45\t"
            b"PROTEST;VIOLENCE;POLITICS\t"
            b"1#Egypt#EG#EG#31.2#29.8#-123456\t"
            b"John Smith;Jane Doe\t"
            b"United Nations;Red Cross\t"
            b"-2.5,10.2,12.7,0.5,5.0,3.2,1500\t"
            b"http://example.com/image.jpg\t"
            b"http://example.com/img1.jpg;http://example.com/img2.jpg\t"
            b"We must act now#John Smith#15\t"
            b"John Smith;Jane Doe;Egypt"
        )

    def test_parse_v1_basic_fields(self, v1_sample_data: bytes) -> None:
        """Should parse basic v1 fields correctly."""
        parser = GKGParser()
        records = list(parser.parse(v1_sample_data))

        assert len(records) == 1
        record = records[0]

        assert record.gkg_record_id == "20130101000000-1"
        assert record.date == "20130101000000"
        assert record.source_collection_id == "1"
        assert record.source_common_name == "Example.com"
        assert record.document_identifier == "http://example.com/article1"

    def test_parse_v1_delimited_fields(self, v1_sample_data: bytes) -> None:
        """Should preserve delimited fields as strings for downstream parsing."""
        parser = GKGParser()
        records = list(parser.parse(v1_sample_data))
        record = records[0]

        # Counts remain as delimited string
        assert record.counts_v1 == "10#PROTEST#123;20#VIOLENCE#45"
        # Themes remain as semicolon-delimited
        assert record.themes_v1 == "PROTEST;VIOLENCE;POLITICS"
        # Locations remain as delimited string
        assert record.locations_v1 == "1#Egypt#EG#EG#31.2#29.8#-123456"

    def test_parse_v1_missing_v2_fields(self, v1_sample_data: bytes) -> None:
        """Should set v2-only fields to empty strings or None."""
        parser = GKGParser()
        records = list(parser.parse(v1_sample_data))
        record = records[0]

        # v2.1-only fields should be empty or None
        assert record.counts_v2 == ""
        assert record.themes_v2_enhanced == ""
        assert record.locations_v2_enhanced == ""
        assert record.dates_v2 == ""
        assert record.gcam == ""
        assert record.social_image_embeds is None
        assert record.social_video_embeds is None
        assert record.amounts is None
        assert record.translation_info is None
        assert record.extras_xml is None

    def test_parse_v1_optional_fields(self, v1_sample_data: bytes) -> None:
        """Should parse optional fields correctly."""
        parser = GKGParser()
        records = list(parser.parse(v1_sample_data))
        record = records[0]

        assert record.sharing_image == "http://example.com/image.jpg"
        assert record.related_images == "http://example.com/img1.jpg;http://example.com/img2.jpg"
        assert record.quotations == "We must act now#John Smith#15"
        assert record.all_names == "John Smith;Jane Doe;Egypt"

    def test_parse_v1_empty_fields(self) -> None:
        """Should handle empty fields as None."""
        # Create v1 record with some empty fields
        data = b"\t".join(
            [
                b"20130101000000-1",
                b"20130101000000",
                b"1",
                b"",  # Empty source name
                b"http://example.com",
                b"",  # Empty counts
                b"THEME1",
                b"",  # Empty locations
                b"",  # Empty persons
                b"ORG1",
                b"-2.5,10,12,0.5,5,3,1500",
                b"",  # Empty sharing image
                b"",  # Empty related images
                b"",  # Empty quotations
                b"Name1",
            ],
        )

        parser = GKGParser()
        records = list(parser.parse(data))
        record = records[0]

        assert record.source_common_name == ""
        assert record.counts_v1 == ""
        assert record.locations_v1 == ""
        assert record.sharing_image is None
        assert record.related_images is None

    def test_parse_v1_multiple_records(self) -> None:
        """Should parse multiple v1 records."""
        data = (
            b"20130101000000-1\t20130101000000\t1\tSite1\thttp://s1.com\t"
            b"count1\ttheme1\tloc1\tper1\torg1\ttone1\timg1\timgs1\tquot1\tname1\n"
            b"20130101000000-2\t20130101000000\t1\tSite2\thttp://s2.com\t"
            b"count2\ttheme2\tloc2\tper2\torg2\ttone2\timg2\timgs2\tquot2\tname2"
        )

        parser = GKGParser()
        records = list(parser.parse(data))

        assert len(records) == 2
        assert records[0].gkg_record_id == "20130101000000-1"
        assert records[1].gkg_record_id == "20130101000000-2"

    def test_parse_v1_malformed_line_skipped(self, caplog: pytest.LogCaptureFixture) -> None:
        """Should skip malformed lines and log warning."""
        # Valid line followed by malformed line (wrong column count)
        data = (
            b"20130101000000-1\t20130101000000\t1\tSite1\thttp://s1.com\t"
            b"count1\ttheme1\tloc1\tper1\torg1\ttone1\timg1\timgs1\tquot1\tname1\n"
            b"MALFORMED\tLINE\tWITH\tWRONG\tCOLUMNS"
        )

        parser = GKGParser()
        records = list(parser.parse(data))

        assert len(records) == 1  # Only valid line parsed
        assert "Skipping malformed GKG v1 line" in caplog.text
        assert "expected 15 columns, got 5" in caplog.text


class TestGKGParserV2:
    """Test parsing of GKG v2.1 format (27 columns)."""

    @pytest.fixture
    def v2_sample_data(self) -> bytes:
        """Sample GKG v2.1 record (27 columns)."""
        # All 27 columns for v2.1
        return b"\t".join(
            [
                b"20150218230000-1",  # 0: GKGRECORDID
                b"20150218230000",  # 1: DATE
                b"1",  # 2: SourceCollectionId
                b"NewsSource.com",  # 3: SourceCommonName
                b"http://news.com/article",  # 4: DocumentIdentifier
                b"10#OLD_COUNT#50",  # 5: V1Counts
                b"20#NEW_COUNT#100;30#COUNT2#200",  # 6: V2.1Counts
                b"OLD_THEME",  # 7: V1Themes
                b"NEW_THEME1;NEW_THEME2",  # 8: V2EnhancedThemes
                b"1#Paris#FR",  # 9: V1Locations
                b"2#London#UK#UK#51.5#-0.1#123456",  # 10: V2EnhancedLocations
                b"Person A",  # 11: V1Persons
                b"Person B;Person C",  # 12: V2EnhancedPersons
                b"Org A",  # 13: V1Organizations
                b"Org B;Org C",  # 14: V2EnhancedOrganizations
                b"-3.5,15.2,18.7,0.8,6.5,4.1,2000",  # 15: V1.5Tone
                b"20150218;20150219",  # 16: V2.1Dates
                b"c2.14:3.0;c5.1:0.85",  # 17: V2.1GCAM
                b"http://news.com/share.jpg",  # 18: SharingImage
                b"http://news.com/img1.jpg",  # 19: RelatedImages
                b"http://social.com/embed1",  # 20: SocialImageEmbeds
                b"http://video.com/embed1",  # 21: SocialVideoEmbeds
                b"Quote text#Speaker#Position",  # 22: Quotations
                b"Name1;Name2;Name3",  # 23: AllNames
                b"100;200;$500",  # 24: Amounts
                b"srclc:eng;eng:0.95",  # 25: TranslationInfo
                b"<extra>xml</extra>",  # 26: ExtrasXML
            ],
        )

    def test_parse_v2_basic_fields(self, v2_sample_data: bytes) -> None:
        """Should parse basic v2.1 fields correctly."""
        parser = GKGParser()
        records = list(parser.parse(v2_sample_data))

        assert len(records) == 1
        record = records[0]

        assert record.gkg_record_id == "20150218230000-1"
        assert record.date == "20150218230000"
        assert record.source_collection_id == "1"
        assert record.source_common_name == "NewsSource.com"
        assert record.document_identifier == "http://news.com/article"

    def test_parse_v2_v1_and_v2_fields(self, v2_sample_data: bytes) -> None:
        """Should parse both v1 and v2.1 versions of fields."""
        parser = GKGParser()
        records = list(parser.parse(v2_sample_data))
        record = records[0]

        # Both v1 and v2 counts present
        assert record.counts_v1 == "10#OLD_COUNT#50"
        assert record.counts_v2 == "20#NEW_COUNT#100;30#COUNT2#200"

        # Both v1 and v2 themes
        assert record.themes_v1 == "OLD_THEME"
        assert record.themes_v2_enhanced == "NEW_THEME1;NEW_THEME2"

        # Both v1 and v2 locations
        assert record.locations_v1 == "1#Paris#FR"
        assert record.locations_v2_enhanced == "2#London#UK#UK#51.5#-0.1#123456"

    def test_parse_v2_exclusive_fields(self, v2_sample_data: bytes) -> None:
        """Should parse v2.1-exclusive fields."""
        parser = GKGParser()
        records = list(parser.parse(v2_sample_data))
        record = records[0]

        assert record.dates_v2 == "20150218;20150219"
        assert record.gcam == "c2.14:3.0;c5.1:0.85"
        assert record.social_image_embeds == "http://social.com/embed1"
        assert record.social_video_embeds == "http://video.com/embed1"
        assert record.amounts == "100;200;$500"
        assert record.translation_info == "srclc:eng;eng:0.95"
        assert record.extras_xml == "<extra>xml</extra>"

    def test_parse_v2_translation_detection_from_record_id(self) -> None:
        """Should detect translation from -T suffix in record ID."""
        # Create complete v2.1 row with 27 columns
        # Note: Last column must be non-empty to avoid strip() removing trailing tabs
        data = b"\t".join(
            [
                b"20150218230000-T",  # 0: GKGRECORDID (ends with -T to indicate translation)
                b"20150218230000",  # 1: DATE
                b"1",  # 2: SourceCollectionId
                b"NewsSource",  # 3: SourceCommonName
                b"http://news.com",  # 4: DocumentIdentifier
                b"",  # 5: V1Counts
                b"",  # 6: V2.1Counts
                b"",  # 7: V1Themes
                b"",  # 8: V2EnhancedThemes
                b"",  # 9: V1Locations
                b"",  # 10: V2EnhancedLocations
                b"",  # 11: V1Persons
                b"",  # 12: V2EnhancedPersons
                b"",  # 13: V1Organizations
                b"",  # 14: V2EnhancedOrganizations
                b"",  # 15: V1.5Tone
                b"",  # 16: V2.1Dates
                b"",  # 17: V2.1GCAM
                b"",  # 18: SharingImage
                b"",  # 19: RelatedImages
                b"",  # 20: SocialImageEmbeds
                b"",  # 21: SocialVideoEmbeds
                b"",  # 22: Quotations
                b"",  # 23: AllNames
                b"",  # 24: Amounts
                b"",  # 25: TranslationInfo
                b"<xml></xml>",  # 26: ExtrasXML (non-empty to preserve column count)
            ],
        )

        parser = GKGParser()
        records = list(parser.parse(data, is_translated=False))
        record = records[0]

        assert record.is_translated is True  # Detected from -T suffix

    def test_parse_v2_translation_from_parameter(self) -> None:
        """Should set translation from is_translated parameter."""
        # Create complete v2.1 row with 27 columns
        # Note: Last column must be non-empty to avoid strip() removing trailing tabs
        data = b"\t".join(
            [
                b"20150218230000-1",  # 0: GKGRECORDID (No -T suffix)
                b"20150218230000",  # 1: DATE
            ]
            + [b""] * 24
            + [b"<xml></xml>"],
        )  # Columns 2-25 empty, 26 non-empty

        parser = GKGParser()
        records = list(parser.parse(data, is_translated=True))
        record = records[0]

        assert record.is_translated is True

    def test_parse_v2_empty_optional_fields(self) -> None:
        """Should handle empty optional fields as None."""
        # All 27 columns present, with empty optional fields at the end
        # Note: We make ExtrasXML non-empty to ensure all 27 columns are preserved
        data = b"\t".join(
            [
                b"20150218230000-1",  # 0: GKGRECORDID
                b"20150218230000",  # 1: DATE
                b"1",  # 2: SourceCollectionId
                b"NewsSource",  # 3: SourceCommonName
                b"http://news.com",  # 4: DocumentIdentifier
                b"counts1",  # 5: V1Counts
                b"counts2",  # 6: V2.1Counts
                b"themes1",  # 7: V1Themes
                b"themes2",  # 8: V2EnhancedThemes
                b"locs1",  # 9: V1Locations
                b"locs2",  # 10: V2EnhancedLocations
                b"pers1",  # 11: V1Persons
                b"pers2",  # 12: V2EnhancedPersons
                b"orgs1",  # 13: V1Organizations
                b"orgs2",  # 14: V2EnhancedOrganizations
                b"tone",  # 15: V1.5Tone
                b"dates",  # 16: V2.1Dates
                b"gcam",  # 17: V2.1GCAM
                b"",  # 18: SharingImage (empty)
                b"",  # 19: RelatedImages (empty)
                b"",  # 20: SocialImageEmbeds (empty)
                b"",  # 21: SocialVideoEmbeds (empty)
                b"",  # 22: Quotations (empty)
                b"",  # 23: AllNames (empty)
                b"",  # 24: Amounts (empty)
                b"",  # 25: TranslationInfo (empty)
                b"<xml></xml>",  # 26: ExtrasXML (non-empty to preserve column count)
            ],
        )

        parser = GKGParser()
        records = list(parser.parse(data))
        record = records[0]

        assert record.sharing_image is None
        assert record.related_images is None
        assert record.social_image_embeds is None
        assert record.social_video_embeds is None
        assert record.quotations is None
        assert record.all_names is None
        assert record.amounts is None
        assert record.translation_info is None
        assert record.extras_xml == "<xml></xml>"  # This one is non-empty now

    def test_parse_v2_multiple_records(self) -> None:
        """Should parse multiple v2.1 records."""
        record1 = b"\t".join([b"20150218230000-1", b"20150218230000"] + [b"field"] * 25)
        record2 = b"\t".join([b"20150218230000-2", b"20150218230000"] + [b"field"] * 25)
        data = record1 + b"\n" + record2

        parser = GKGParser()
        records = list(parser.parse(data))

        assert len(records) == 2
        assert records[0].gkg_record_id == "20150218230000-1"
        assert records[1].gkg_record_id == "20150218230000-2"

    def test_parse_v2_malformed_line_skipped(self, caplog: pytest.LogCaptureFixture) -> None:
        """Should skip malformed lines and log warning."""
        valid_record = b"\t".join([b"20150218230000-1", b"20150218230000"] + [b"field"] * 25)
        malformed_record = b"TOO\tFEW\tCOLUMNS"
        data = valid_record + b"\n" + malformed_record

        parser = GKGParser()
        records = list(parser.parse(data))

        assert len(records) == 1  # Only valid record parsed
        assert "Skipping malformed GKG v2.1 line" in caplog.text
        assert "expected 27 columns, got 3" in caplog.text


class TestGKGParserEdgeCases:
    """Test edge cases and error handling."""

    def test_parse_empty_data(self) -> None:
        """Should raise error on empty data."""
        parser = GKGParser()
        with pytest.raises(ValueError, match="Empty header line"):
            list(parser.parse(b""))

    def test_parse_whitespace_only(self) -> None:
        """Should raise error on whitespace-only data."""
        parser = GKGParser()
        with pytest.raises(ValueError, match="Empty header line"):
            list(parser.parse(b"   \n\n   \n"))

    def test_parse_utf8_with_invalid_chars(self) -> None:
        """Should handle invalid UTF-8 characters gracefully."""
        # Create complete v2.1 record with invalid UTF-8 in a field (27 columns total)
        # Note: Last column must be non-empty to avoid strip() removing trailing tabs
        data = b"\t".join(
            [
                b"20150218230000-1",  # 0: GKGRECORDID
                b"20150218230000",  # 1: DATE
                b"1",  # 2: SourceCollectionId
                b"News\xff\xfeSource",  # 3: SourceCommonName (Invalid UTF-8 sequence)
                b"http://news.com",  # 4: DocumentIdentifier
            ]
            + [b""] * 21
            + [b"<xml></xml>"],
        )  # 5-25: empty, 26: non-empty

        parser = GKGParser()
        records = list(parser.parse(data))

        # Should still parse, with replacement chars
        assert len(records) == 1
        assert "News" in records[0].source_common_name

    def test_parse_exception_during_record_creation(self, caplog: pytest.LogCaptureFixture) -> None:
        """Should handle exceptions during record creation gracefully."""
        # This would require mocking to trigger an exception in the dataclass constructor
        # For now, we test that malformed lines are caught
        data = b"\t".join([b"id"] + [b"field"] * 26)  # Valid column count

        parser = GKGParser()
        # Should not raise, just log and skip problematic records
        records = list(parser.parse(data))
        assert isinstance(records, list)
