"""Comprehensive tests for GKG models."""

from __future__ import annotations

from datetime import UTC, datetime

from py_gdelt.models._internal import _RawGKG
from py_gdelt.models.common import EntityMention
from py_gdelt.models.gkg import Amount, GKGRecord, Quotation


class TestQuotation:
    """Tests for Quotation model."""

    def test_creation_with_all_fields(self) -> None:
        """Test Quotation can be created with all fields."""
        quotation = Quotation(
            offset=100,
            length=50,
            verb="said",
            quote="This is a test quote",
        )
        assert quotation.offset == 100
        assert quotation.length == 50
        assert quotation.verb == "said"
        assert quotation.quote == "This is a test quote"

    def test_serialization(self) -> None:
        """Test Quotation serialization and deserialization."""
        original = Quotation(
            offset=100,
            length=50,
            verb="declared",
            quote="A significant statement",
        )
        data = original.model_dump()
        restored = Quotation(**data)
        assert restored.offset == original.offset
        assert restored.length == original.length
        assert restored.verb == original.verb
        assert restored.quote == original.quote

    def test_json_serialization(self) -> None:
        """Test Quotation JSON serialization."""
        quotation = Quotation(offset=10, length=20, verb="announced", quote="Breaking news")
        json_str = quotation.model_dump_json()
        restored = Quotation.model_validate_json(json_str)
        assert restored.offset == 10
        assert restored.length == 20
        assert restored.verb == "announced"
        assert restored.quote == "Breaking news"


class TestAmount:
    """Tests for Amount model."""

    def test_creation_with_all_fields(self) -> None:
        """Test Amount can be created with all fields."""
        amount = Amount(amount=100.5, object="dollars", offset=50)
        assert amount.amount == 100.5
        assert amount.object == "dollars"
        assert amount.offset == 50

    def test_amount_can_be_integer(self) -> None:
        """Test Amount accepts integer values."""
        amount = Amount(amount=100, object="people", offset=200)
        assert amount.amount == 100.0
        assert isinstance(amount.amount, float)

    def test_serialization(self) -> None:
        """Test Amount serialization and deserialization."""
        original = Amount(amount=250.75, object="euros", offset=300)
        data = original.model_dump()
        restored = Amount(**data)
        assert restored.amount == original.amount
        assert restored.object == original.object
        assert restored.offset == original.offset

    def test_json_serialization(self) -> None:
        """Test Amount JSON serialization."""
        amount = Amount(amount=50.0, object="tons", offset=150)
        json_str = amount.model_dump_json()
        restored = Amount.model_validate_json(json_str)
        assert restored.amount == 50.0
        assert restored.object == "tons"
        assert restored.offset == 150


class TestGKGRecordBasicFields:
    """Tests for GKGRecord basic field handling."""

    def test_creation_with_required_fields(self) -> None:
        """Test GKGRecord can be created with required fields."""
        record = GKGRecord(
            record_id="20150101000000-1",
            date=datetime(2015, 1, 1, 0, 0, 0),
            source_url="http://example.com/article",
            source_name="Example News",
            source_collection=1,
        )
        assert record.record_id == "20150101000000-1"
        assert record.date == datetime(2015, 1, 1, 0, 0, 0)
        assert record.source_url == "http://example.com/article"
        assert record.source_name == "Example News"
        assert record.source_collection == 1

    def test_default_values(self) -> None:
        """Test default values are set correctly."""
        record = GKGRecord(
            record_id="20150101000000-1",
            date=datetime(2015, 1, 1),
            source_url="http://example.com",
            source_name="Test",
            source_collection=1,
        )
        assert record.themes == []
        assert record.persons == []
        assert record.organizations == []
        assert record.locations == []
        assert record.tone is None
        assert record.gcam == {}
        assert record.quotations == []
        assert record.amounts == []
        assert record.sharing_image is None
        assert record.all_names == []
        assert record.version == 2
        assert record.is_translated is False
        assert record.original_record_id is None
        assert record.translation_info is None

    def test_serialization(self) -> None:
        """Test GKGRecord serialization and deserialization."""
        original = GKGRecord(
            record_id="20150101000000-1",
            date=datetime(2015, 1, 1, 12, 30, 45),
            source_url="http://example.com/article",
            source_name="Example News",
            source_collection=1,
            themes=[EntityMention(entity_type="THEME", name="POLITICS", offset=10)],
            version=2,
        )
        data = original.model_dump()
        restored = GKGRecord(**data)
        assert restored.record_id == original.record_id
        assert restored.date == original.date
        assert restored.source_url == original.source_url
        assert restored.source_name == original.source_name
        assert restored.source_collection == original.source_collection
        assert len(restored.themes) == 1
        assert restored.themes[0].name == "POLITICS"


class TestGKGRecordProperties:
    """Tests for GKGRecord properties."""

    def test_primary_theme_with_themes(self) -> None:
        """Test primary_theme returns first theme name."""
        record = GKGRecord(
            record_id="20150101000000-1",
            date=datetime(2015, 1, 1),
            source_url="http://example.com",
            source_name="Test",
            source_collection=1,
            themes=[
                EntityMention(entity_type="THEME", name="POLITICS"),
                EntityMention(entity_type="THEME", name="ECONOMY"),
            ],
        )
        assert record.primary_theme == "POLITICS"

    def test_primary_theme_with_no_themes(self) -> None:
        """Test primary_theme returns None when no themes exist."""
        record = GKGRecord(
            record_id="20150101000000-1",
            date=datetime(2015, 1, 1),
            source_url="http://example.com",
            source_name="Test",
            source_collection=1,
        )
        assert record.primary_theme is None

    def test_has_quotations_true(self) -> None:
        """Test has_quotations returns True when quotations exist."""
        record = GKGRecord(
            record_id="20150101000000-1",
            date=datetime(2015, 1, 1),
            source_url="http://example.com",
            source_name="Test",
            source_collection=1,
            quotations=[Quotation(offset=10, length=20, verb="said", quote="test")],
        )
        assert record.has_quotations is True

    def test_has_quotations_false(self) -> None:
        """Test has_quotations returns False when no quotations exist."""
        record = GKGRecord(
            record_id="20150101000000-1",
            date=datetime(2015, 1, 1),
            source_url="http://example.com",
            source_name="Test",
            source_collection=1,
        )
        assert record.has_quotations is False


class TestGKGRecordFromRaw:
    """Tests for GKGRecord.from_raw() conversion method."""

    def test_from_raw_basic_fields(self) -> None:
        """Test from_raw converts basic fields correctly."""
        raw = _RawGKG(
            gkg_record_id="20150101120000-1",
            date="20150101120000",
            source_collection_id="1",
            source_common_name="Test News",
            document_identifier="http://example.com/article",
            counts_v1="",
            counts_v2="",
            themes_v1="",
            themes_v2_enhanced="POLITICS,10;ECONOMY,50",
            locations_v1="",
            locations_v2_enhanced="",
            persons_v1="",
            persons_v2_enhanced="",
            organizations_v1="",
            organizations_v2_enhanced="",
            tone="",
            dates_v2="",
            gcam="",
        )
        record = GKGRecord.from_raw(raw)
        assert record.record_id == "20150101120000-1"
        assert record.date == datetime(2015, 1, 1, 12, 0, 0, tzinfo=UTC)
        assert record.source_url == "http://example.com/article"
        assert record.source_name == "Test News"
        assert record.source_collection == 1

    def test_from_raw_translation_detection_with_suffix(self) -> None:
        """Test from_raw detects translation from -T suffix."""
        raw = _RawGKG(
            gkg_record_id="20150101120000-T",
            date="20150101120000",
            source_collection_id="1",
            source_common_name="Test",
            document_identifier="http://example.com",
            counts_v1="",
            counts_v2="",
            themes_v1="",
            themes_v2_enhanced="",
            locations_v1="",
            locations_v2_enhanced="",
            persons_v1="",
            persons_v2_enhanced="",
            organizations_v1="",
            organizations_v2_enhanced="",
            tone="",
            dates_v2="",
            gcam="",
        )
        record = GKGRecord.from_raw(raw)
        assert record.is_translated is True
        assert record.original_record_id == "20150101120000"

    def test_from_raw_no_translation(self) -> None:
        """Test from_raw handles non-translated records."""
        raw = _RawGKG(
            gkg_record_id="20150101120000-1",
            date="20150101120000",
            source_collection_id="1",
            source_common_name="Test",
            document_identifier="http://example.com",
            counts_v1="",
            counts_v2="",
            themes_v1="",
            themes_v2_enhanced="",
            locations_v1="",
            locations_v2_enhanced="",
            persons_v1="",
            persons_v2_enhanced="",
            organizations_v1="",
            organizations_v2_enhanced="",
            tone="",
            dates_v2="",
            gcam="",
        )
        record = GKGRecord.from_raw(raw)
        assert record.is_translated is False
        assert record.original_record_id is None

    def test_from_raw_themes_v2_enhanced(self) -> None:
        """Test from_raw parses V2 enhanced themes."""
        raw = _RawGKG(
            gkg_record_id="20150101120000-1",
            date="20150101120000",
            source_collection_id="1",
            source_common_name="Test",
            document_identifier="http://example.com",
            counts_v1="",
            counts_v2="",
            themes_v1="",
            themes_v2_enhanced="PROTEST,100;VIOLENCE,200;POLITICS,50",
            locations_v1="",
            locations_v2_enhanced="",
            persons_v1="",
            persons_v2_enhanced="",
            organizations_v1="",
            organizations_v2_enhanced="",
            tone="",
            dates_v2="",
            gcam="",
        )
        record = GKGRecord.from_raw(raw)
        assert len(record.themes) == 3
        assert record.themes[0].name == "PROTEST"
        assert record.themes[0].offset == 100
        assert record.themes[1].name == "VIOLENCE"
        assert record.themes[1].offset == 200
        assert record.themes[2].name == "POLITICS"
        assert record.themes[2].offset == 50

    def test_from_raw_themes_v1_fallback(self) -> None:
        """Test from_raw falls back to V1 themes when V2 is empty."""
        raw = _RawGKG(
            gkg_record_id="20150101120000-1",
            date="20150101120000",
            source_collection_id="1",
            source_common_name="Test",
            document_identifier="http://example.com",
            counts_v1="",
            counts_v2="",
            themes_v1="THEME1;THEME2",
            themes_v2_enhanced="",
            locations_v1="",
            locations_v2_enhanced="",
            persons_v1="",
            persons_v2_enhanced="",
            organizations_v1="",
            organizations_v2_enhanced="",
            tone="",
            dates_v2="",
            gcam="",
        )
        record = GKGRecord.from_raw(raw)
        assert len(record.themes) == 2
        assert record.themes[0].name == "THEME1"
        assert record.themes[1].name == "THEME2"

    def test_from_raw_persons_parsing(self) -> None:
        """Test from_raw parses persons correctly."""
        raw = _RawGKG(
            gkg_record_id="20150101120000-1",
            date="20150101120000",
            source_collection_id="1",
            source_common_name="Test",
            document_identifier="http://example.com",
            counts_v1="",
            counts_v2="",
            themes_v1="",
            themes_v2_enhanced="",
            locations_v1="",
            locations_v2_enhanced="",
            persons_v1="",
            persons_v2_enhanced="John Doe,50;Jane Smith,150",
            organizations_v1="",
            organizations_v2_enhanced="",
            tone="",
            dates_v2="",
            gcam="",
        )
        record = GKGRecord.from_raw(raw)
        assert len(record.persons) == 2
        assert record.persons[0].entity_type == "PERSON"
        assert record.persons[0].name == "John Doe"
        assert record.persons[0].offset == 50
        assert record.persons[1].name == "Jane Smith"
        assert record.persons[1].offset == 150

    def test_from_raw_organizations_parsing(self) -> None:
        """Test from_raw parses organizations correctly."""
        raw = _RawGKG(
            gkg_record_id="20150101120000-1",
            date="20150101120000",
            source_collection_id="1",
            source_common_name="Test",
            document_identifier="http://example.com",
            counts_v1="",
            counts_v2="",
            themes_v1="",
            themes_v2_enhanced="",
            locations_v1="",
            locations_v2_enhanced="",
            persons_v1="",
            persons_v2_enhanced="",
            organizations_v1="",
            organizations_v2_enhanced="United Nations,100;Red Cross,250",
            tone="",
            dates_v2="",
            gcam="",
        )
        record = GKGRecord.from_raw(raw)
        assert len(record.organizations) == 2
        assert record.organizations[0].entity_type == "ORG"
        assert record.organizations[0].name == "United Nations"
        assert record.organizations[0].offset == 100

    def test_from_raw_locations_parsing(self) -> None:
        """Test from_raw parses locations correctly."""
        raw = _RawGKG(
            gkg_record_id="20150101120000-1",
            date="20150101120000",
            source_collection_id="1",
            source_common_name="Test",
            document_identifier="http://example.com",
            counts_v1="",
            counts_v2="",
            themes_v1="",
            themes_v2_enhanced="",
            locations_v1="",
            locations_v2_enhanced="3#Paris#FR#A8#75#48.8566#2.3522#123456;2#London#UK#ENG##51.5074#-0.1278#789012",
            persons_v1="",
            persons_v2_enhanced="",
            organizations_v1="",
            organizations_v2_enhanced="",
            tone="",
            dates_v2="",
            gcam="",
        )
        record = GKGRecord.from_raw(raw)
        assert len(record.locations) == 2
        assert record.locations[0].geo_type == 3
        assert record.locations[0].name == "Paris"
        assert record.locations[0].country_code == "FR"
        assert record.locations[0].lat == 48.8566
        assert record.locations[0].lon == 2.3522
        assert record.locations[1].name == "London"
        assert record.locations[1].lat == 51.5074
        assert record.locations[1].lon == -0.1278

    def test_from_raw_tone_parsing(self) -> None:
        """Test from_raw parses tone correctly."""
        raw = _RawGKG(
            gkg_record_id="20150101120000-1",
            date="20150101120000",
            source_collection_id="1",
            source_common_name="Test",
            document_identifier="http://example.com",
            counts_v1="",
            counts_v2="",
            themes_v1="",
            themes_v2_enhanced="",
            locations_v1="",
            locations_v2_enhanced="",
            persons_v1="",
            persons_v2_enhanced="",
            organizations_v1="",
            organizations_v2_enhanced="",
            tone="-5.5,10.2,15.7,8.3,3.5,2.1,1500",
            dates_v2="",
            gcam="",
        )
        record = GKGRecord.from_raw(raw)
        assert record.tone is not None
        assert record.tone.tone == -5.5
        assert record.tone.positive_score == 10.2
        assert record.tone.negative_score == 15.7
        assert record.tone.polarity == 8.3
        assert record.tone.activity_reference_density == 3.5
        assert record.tone.self_group_reference_density == 2.1
        assert record.tone.word_count == 1500

    def test_from_raw_gcam_parsing(self) -> None:
        """Test from_raw parses GCAM correctly."""
        raw = _RawGKG(
            gkg_record_id="20150101120000-1",
            date="20150101120000",
            source_collection_id="1",
            source_common_name="Test",
            document_identifier="http://example.com",
            counts_v1="",
            counts_v2="",
            themes_v1="",
            themes_v2_enhanced="",
            locations_v1="",
            locations_v2_enhanced="",
            persons_v1="",
            persons_v2_enhanced="",
            organizations_v1="",
            organizations_v2_enhanced="",
            tone="",
            dates_v2="",
            gcam="c2.14:3.2;c5.1:0.85;c10.3:-1.5",
        )
        record = GKGRecord.from_raw(raw)
        assert len(record.gcam) == 3
        assert record.gcam["c2.14"] == 3.2
        assert record.gcam["c5.1"] == 0.85
        assert record.gcam["c10.3"] == -1.5

    def test_from_raw_quotations_parsing(self) -> None:
        """Test from_raw parses quotations correctly."""
        raw = _RawGKG(
            gkg_record_id="20150101120000-1",
            date="20150101120000",
            source_collection_id="1",
            source_common_name="Test",
            document_identifier="http://example.com",
            counts_v1="",
            counts_v2="",
            themes_v1="",
            themes_v2_enhanced="",
            locations_v1="",
            locations_v2_enhanced="",
            persons_v1="",
            persons_v2_enhanced="",
            organizations_v1="",
            organizations_v2_enhanced="",
            tone="",
            dates_v2="",
            gcam="",
            quotations="100|50|said|This is a quote#200|30|declared|Another quote here",
        )
        record = GKGRecord.from_raw(raw)
        assert len(record.quotations) == 2
        assert record.quotations[0].offset == 100
        assert record.quotations[0].length == 50
        assert record.quotations[0].verb == "said"
        assert record.quotations[0].quote == "This is a quote"
        assert record.quotations[1].offset == 200
        assert record.quotations[1].length == 30
        assert record.quotations[1].verb == "declared"

    def test_from_raw_amounts_parsing(self) -> None:
        """Test from_raw parses amounts correctly."""
        raw = _RawGKG(
            gkg_record_id="20150101120000-1",
            date="20150101120000",
            source_collection_id="1",
            source_common_name="Test",
            document_identifier="http://example.com",
            counts_v1="",
            counts_v2="",
            themes_v1="",
            themes_v2_enhanced="",
            locations_v1="",
            locations_v2_enhanced="",
            persons_v1="",
            persons_v2_enhanced="",
            organizations_v1="",
            organizations_v2_enhanced="",
            tone="",
            dates_v2="",
            gcam="",
            amounts="100.5,dollars,50;25,people,150",
        )
        record = GKGRecord.from_raw(raw)
        assert len(record.amounts) == 2
        assert record.amounts[0].amount == 100.5
        assert record.amounts[0].object == "dollars"
        assert record.amounts[0].offset == 50
        assert record.amounts[1].amount == 25.0
        assert record.amounts[1].object == "people"

    def test_from_raw_all_names_parsing(self) -> None:
        """Test from_raw parses all_names correctly."""
        raw = _RawGKG(
            gkg_record_id="20150101120000-1",
            date="20150101120000",
            source_collection_id="1",
            source_common_name="Test",
            document_identifier="http://example.com",
            counts_v1="",
            counts_v2="",
            themes_v1="",
            themes_v2_enhanced="",
            locations_v1="",
            locations_v2_enhanced="",
            persons_v1="",
            persons_v2_enhanced="",
            organizations_v1="",
            organizations_v2_enhanced="",
            tone="",
            dates_v2="",
            gcam="",
            all_names="John Doe;Jane Smith;Paris;United Nations",
        )
        record = GKGRecord.from_raw(raw)
        assert len(record.all_names) == 4
        assert "John Doe" in record.all_names
        assert "Jane Smith" in record.all_names
        assert "Paris" in record.all_names
        assert "United Nations" in record.all_names

    def test_from_raw_version_detection_v2(self) -> None:
        """Test from_raw detects version 2 from enhanced fields."""
        raw = _RawGKG(
            gkg_record_id="20150101120000-1",
            date="20150101120000",
            source_collection_id="1",
            source_common_name="Test",
            document_identifier="http://example.com",
            counts_v1="",
            counts_v2="",
            themes_v1="",
            themes_v2_enhanced="THEME1,10",
            locations_v1="",
            locations_v2_enhanced="",
            persons_v1="",
            persons_v2_enhanced="",
            organizations_v1="",
            organizations_v2_enhanced="",
            tone="",
            dates_v2="",
            gcam="",
        )
        record = GKGRecord.from_raw(raw)
        assert record.version == 2

    def test_from_raw_version_detection_v1(self) -> None:
        """Test from_raw detects version 1 from absence of enhanced fields."""
        raw = _RawGKG(
            gkg_record_id="20150101120000-1",
            date="20150101120000",
            source_collection_id="1",
            source_common_name="Test",
            document_identifier="http://example.com",
            counts_v1="",
            counts_v2="",
            themes_v1="THEME1",
            themes_v2_enhanced="",
            locations_v1="",
            locations_v2_enhanced="",
            persons_v1="",
            persons_v2_enhanced="",
            organizations_v1="",
            organizations_v2_enhanced="",
            tone="",
            dates_v2="",
            gcam="",
        )
        record = GKGRecord.from_raw(raw)
        assert record.version == 1

    def test_from_raw_with_translation_info(self) -> None:
        """Test from_raw preserves translation_info."""
        raw = _RawGKG(
            gkg_record_id="20150101120000-1",
            date="20150101120000",
            source_collection_id="1",
            source_common_name="Test",
            document_identifier="http://example.com",
            counts_v1="",
            counts_v2="",
            themes_v1="",
            themes_v2_enhanced="",
            locations_v1="",
            locations_v2_enhanced="",
            persons_v1="",
            persons_v2_enhanced="",
            organizations_v1="",
            organizations_v2_enhanced="",
            tone="",
            dates_v2="",
            gcam="",
            translation_info="srclc:fra;fra:0.95",
        )
        record = GKGRecord.from_raw(raw)
        assert record.translation_info == "srclc:fra;fra:0.95"

    def test_from_raw_with_sharing_image(self) -> None:
        """Test from_raw preserves sharing_image."""
        raw = _RawGKG(
            gkg_record_id="20150101120000-1",
            date="20150101120000",
            source_collection_id="1",
            source_common_name="Test",
            document_identifier="http://example.com",
            counts_v1="",
            counts_v2="",
            themes_v1="",
            themes_v2_enhanced="",
            locations_v1="",
            locations_v2_enhanced="",
            persons_v1="",
            persons_v2_enhanced="",
            organizations_v1="",
            organizations_v2_enhanced="",
            tone="",
            dates_v2="",
            gcam="",
            sharing_image="http://example.com/image.jpg",
        )
        record = GKGRecord.from_raw(raw)
        assert record.sharing_image == "http://example.com/image.jpg"


class TestGKGRecordEdgeCases:
    """Tests for edge cases in GKG parsing."""

    def test_from_raw_empty_themes(self) -> None:
        """Test from_raw handles empty themes string."""
        raw = _RawGKG(
            gkg_record_id="20150101120000-1",
            date="20150101120000",
            source_collection_id="1",
            source_common_name="Test",
            document_identifier="http://example.com",
            counts_v1="",
            counts_v2="",
            themes_v1="",
            themes_v2_enhanced="",
            locations_v1="",
            locations_v2_enhanced="",
            persons_v1="",
            persons_v2_enhanced="",
            organizations_v1="",
            organizations_v2_enhanced="",
            tone="",
            dates_v2="",
            gcam="",
        )
        record = GKGRecord.from_raw(raw)
        assert record.themes == []

    def test_from_raw_themes_with_missing_offset(self) -> None:
        """Test from_raw handles themes without offset gracefully."""
        raw = _RawGKG(
            gkg_record_id="20150101120000-1",
            date="20150101120000",
            source_collection_id="1",
            source_common_name="Test",
            document_identifier="http://example.com",
            counts_v1="",
            counts_v2="",
            themes_v1="",
            themes_v2_enhanced="THEME1",
            locations_v1="",
            locations_v2_enhanced="",
            persons_v1="",
            persons_v2_enhanced="",
            organizations_v1="",
            organizations_v2_enhanced="",
            tone="",
            dates_v2="",
            gcam="",
        )
        record = GKGRecord.from_raw(raw)
        assert len(record.themes) == 1
        assert record.themes[0].name == "THEME1"
        assert record.themes[0].offset is None

    def test_from_raw_quotation_with_hash_in_text(self) -> None:
        """Test from_raw handles quotations with # in quote text."""
        raw = _RawGKG(
            gkg_record_id="20150101120000-1",
            date="20150101120000",
            source_collection_id="1",
            source_common_name="Test",
            document_identifier="http://example.com",
            counts_v1="",
            counts_v2="",
            themes_v1="",
            themes_v2_enhanced="",
            locations_v1="",
            locations_v2_enhanced="",
            persons_v1="",
            persons_v2_enhanced="",
            organizations_v1="",
            organizations_v2_enhanced="",
            tone="",
            dates_v2="",
            gcam="",
            quotations="100|50|said|This has a pipe | in it",
        )
        record = GKGRecord.from_raw(raw)
        assert len(record.quotations) == 1
        # Note: The parser uses # as record separator and | as field separator
        # with max 4 splits, so pipe in quote text is preserved
        assert record.quotations[0].quote == "This has a pipe | in it"

    def test_from_raw_empty_quotations(self) -> None:
        """Test from_raw handles empty quotations field."""
        raw = _RawGKG(
            gkg_record_id="20150101120000-1",
            date="20150101120000",
            source_collection_id="1",
            source_common_name="Test",
            document_identifier="http://example.com",
            counts_v1="",
            counts_v2="",
            themes_v1="",
            themes_v2_enhanced="",
            locations_v1="",
            locations_v2_enhanced="",
            persons_v1="",
            persons_v2_enhanced="",
            organizations_v1="",
            organizations_v2_enhanced="",
            tone="",
            dates_v2="",
            gcam="",
            quotations=None,
        )
        record = GKGRecord.from_raw(raw)
        assert record.quotations == []

    def test_from_raw_empty_amounts(self) -> None:
        """Test from_raw handles empty amounts field."""
        raw = _RawGKG(
            gkg_record_id="20150101120000-1",
            date="20150101120000",
            source_collection_id="1",
            source_common_name="Test",
            document_identifier="http://example.com",
            counts_v1="",
            counts_v2="",
            themes_v1="",
            themes_v2_enhanced="",
            locations_v1="",
            locations_v2_enhanced="",
            persons_v1="",
            persons_v2_enhanced="",
            organizations_v1="",
            organizations_v2_enhanced="",
            tone="",
            dates_v2="",
            gcam="",
            amounts=None,
        )
        record = GKGRecord.from_raw(raw)
        assert record.amounts == []
