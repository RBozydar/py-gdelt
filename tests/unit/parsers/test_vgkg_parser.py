"""Unit tests for VGKGParser.

Tests the VGKG parser with realistic sample data matching the actual GDELT VGKG
file format (12 columns with nested <FIELD> and <RECORD> delimiters).
"""

from __future__ import annotations

from py_gdelt.models._internal import _RawVGKG
from py_gdelt.parsers.vgkg import VGKGParser


def test_vgkg_parser_basic() -> None:
    """Test parsing a basic VGKG record with all 12 columns."""
    parser = VGKGParser()

    # Sample VGKG row with realistic data format
    sample_data = (
        "20260120120000\t"  # [0] date
        "https://www.example.com/article.html\t"  # [1] document_identifier
        "https://www.example.com/image.jpg\t"  # [2] image_url
        "Sky<FIELD>0.95<FIELD>/m/01589<RECORD>Cloud<FIELD>0.88<FIELD>/m/0csby\t"  # [3] labels
        "CNN<FIELD>0.92<FIELD>/m/019_tv\t"  # [4] logos
        "Entity1<FIELD>0.70<FIELD>/m/02000\t"  # [5] web_entities
        "0.12<FIELD>0.08<FIELD>0.05<FIELD>0.03\t"  # [6] safe_search (4 scores)
        "0.95<FIELD>0.1<FIELD>-0.2<FIELD>0.05<FIELD>0.98<FIELD>10,20,100,150\t"  # [7] faces
        "Breaking News\t"  # [8] ocr_text
        "Landmark1<FIELD>0.85<FIELD>/m/03000\t"  # [9] landmark_annotations
        "example.com\t"  # [10] domain
        '{"responses": []}'  # [11] raw_json
    )

    records = list(parser.parse(sample_data.encode("utf-8")))

    assert len(records) == 1
    record = records[0]

    assert isinstance(record, _RawVGKG)
    assert record.date == "20260120120000"
    assert record.document_identifier == "https://www.example.com/article.html"
    assert record.image_url == "https://www.example.com/image.jpg"
    assert record.labels == "Sky<FIELD>0.95<FIELD>/m/01589<RECORD>Cloud<FIELD>0.88<FIELD>/m/0csby"
    assert record.logos == "CNN<FIELD>0.92<FIELD>/m/019_tv"
    assert record.web_entities == "Entity1<FIELD>0.70<FIELD>/m/02000"
    assert record.safe_search == "0.12<FIELD>0.08<FIELD>0.05<FIELD>0.03"
    assert record.faces == "0.95<FIELD>0.1<FIELD>-0.2<FIELD>0.05<FIELD>0.98<FIELD>10,20,100,150"
    assert record.ocr_text == "Breaking News"
    assert record.landmark_annotations == "Landmark1<FIELD>0.85<FIELD>/m/03000"
    assert record.domain == "example.com"
    assert record.raw_json == '{"responses": []}'


def test_vgkg_parser_multiple_records() -> None:
    """Test parsing multiple VGKG records."""
    parser = VGKGParser()

    # Two sample records
    sample_data = (
        "20260120120000\t"
        "https://example.com/1.html\t"
        "https://example.com/1.jpg\t"
        "Label1<FIELD>0.9<FIELD>/m/01\t"
        "\t"  # Empty logos
        "\t"  # Empty web_entities
        "0.1<FIELD>0.1<FIELD>0.1<FIELD>0.1\t"
        "\t"  # Empty faces
        "OCR Text 1\t"
        "\t"  # Empty landmark_annotations
        "example.com\t"
        "{}\n"
        "20260120120001\t"
        "https://example.com/2.html\t"
        "https://example.com/2.jpg\t"
        "Label2<FIELD>0.8<FIELD>/m/02\t"
        "\t"
        "\t"
        "0.2<FIELD>0.2<FIELD>0.2<FIELD>0.2\t"
        "\t"
        "OCR Text 2\t"
        "\t"
        "example.com\t"
        "{}"
    )

    records = list(parser.parse(sample_data.encode("utf-8")))

    assert len(records) == 2
    assert records[0].date == "20260120120000"
    assert records[0].ocr_text == "OCR Text 1"
    assert records[1].date == "20260120120001"
    assert records[1].ocr_text == "OCR Text 2"


def test_vgkg_parser_empty_fields() -> None:
    """Test parsing VGKG record with empty optional fields."""
    parser = VGKGParser()

    # Record with all empty optional fields
    sample_data = (
        "20260120120000\t"
        "https://example.com/article.html\t"
        "https://example.com/image.jpg\t"
        "\t"  # Empty labels
        "\t"  # Empty logos
        "\t"  # Empty web_entities
        "\t"  # Empty safe_search
        "\t"  # Empty faces
        "\t"  # Empty ocr_text
        "\t"  # Empty landmark_annotations
        "example.com\t"
        "{}"
    )

    records = list(parser.parse(sample_data.encode("utf-8")))

    assert len(records) == 1
    record = records[0]

    assert record.labels == ""
    assert record.logos == ""
    assert record.web_entities == ""
    assert record.safe_search == ""
    assert record.faces == ""
    assert record.ocr_text == ""
    assert record.landmark_annotations == ""


def test_vgkg_parser_malformed_line() -> None:
    """Test that malformed lines are skipped with a warning."""
    parser = VGKGParser()

    # First line is valid, second has only 5 columns, third is valid
    sample_data = (
        "20260120120000\t" + "\t" * 10 + "{}\n"
        "INVALID\tLINE\tWITH\tTOO\tFEW\n"  # Only 5 columns
        "20260120120001\t" + "\t" * 10 + "{}"
    )

    records = list(parser.parse(sample_data.encode("utf-8")))

    # Should skip malformed line and return only 2 valid records
    assert len(records) == 2
    assert records[0].date == "20260120120000"
    assert records[1].date == "20260120120001"


def test_vgkg_parser_empty_input() -> None:
    """Test parsing empty input."""
    parser = VGKGParser()

    records = list(parser.parse(b""))
    assert len(records) == 0


def test_vgkg_parser_whitespace_handling() -> None:
    """Test that leading/trailing whitespace is stripped from fields."""
    parser = VGKGParser()

    sample_data = (
        "  20260120120000  \t"
        "  https://example.com/article.html  \t"
        "  https://example.com/image.jpg  \t"
        "  Label1<FIELD>0.9<FIELD>/m/01  \t"
        "\t\t\t\t\t\t"
        "  example.com  \t"
        "  {}  "
    )

    records = list(parser.parse(sample_data.encode("utf-8")))

    assert len(records) == 1
    record = records[0]

    assert record.date == "20260120120000"
    assert record.document_identifier == "https://example.com/article.html"
    assert record.image_url == "https://example.com/image.jpg"
    assert record.labels == "Label1<FIELD>0.9<FIELD>/m/01"
    assert record.domain == "example.com"
    assert record.raw_json == "{}"


def test_vgkg_parser_unicode_handling() -> None:
    """Test parsing with Unicode characters in text fields."""
    parser = VGKGParser()

    sample_data = (
        "20260120120000\t"
        "https://example.com/article.html\t"
        "https://example.com/image.jpg\t"
        "天空<FIELD>0.95<FIELD>/m/01589\t"  # Chinese characters in label
        "\t\t\t\t"
        "突発ニュース: 日本語テキスト\t"  # Japanese OCR text
        "\t"
        "example.com\t"
        "{}"
    )

    records = list(parser.parse(sample_data.encode("utf-8")))

    assert len(records) == 1
    record = records[0]

    assert "天空" in record.labels
    assert record.ocr_text == "突発ニュース: 日本語テキスト"


def test_vgkg_parser_nested_delimiters() -> None:
    """Test parsing complex nested structures with multiple RECORD and FIELD delimiters."""
    parser = VGKGParser()

    sample_data = (
        "20260120120000\t"
        "https://example.com/article.html\t"
        "https://example.com/image.jpg\t"
        # Multiple labels with RECORD delimiter
        "Sky<FIELD>0.95<FIELD>/m/01589<RECORD>Cloud<FIELD>0.88<FIELD>/m/0csby<RECORD>Tree<FIELD>0.75<FIELD>/m/07j7r\t"
        # Multiple logos
        "CNN<FIELD>0.92<FIELD>/m/019_tv<RECORD>BBC<FIELD>0.88<FIELD>/m/01cd9\t"
        "\t\t"
        # Multiple faces
        "0.95<FIELD>0.1<FIELD>-0.2<FIELD>0.05<FIELD>0.98<FIELD>10,20,100,150<RECORD>0.87<FIELD>-0.15<FIELD>0.3<FIELD>-0.1<FIELD>0.92<FIELD>200,30,80,120\t"
        "\t\t"
        "example.com\t"
        "{}"
    )

    records = list(parser.parse(sample_data.encode("utf-8")))

    assert len(records) == 1
    record = records[0]

    # Verify nested delimiters are preserved
    assert record.labels.count("<RECORD>") == 2  # 3 labels = 2 record delimiters
    assert record.labels.count("<FIELD>") == 6  # 3 labels * 2 fields each = 6 field delimiters
    assert record.logos.count("<RECORD>") == 1  # 2 logos = 1 record delimiter
    assert record.faces.count("<RECORD>") == 1  # 2 faces = 1 record delimiter
