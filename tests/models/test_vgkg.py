"""Tests for VGKG (Visual Global Knowledge Graph) models."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from py_gdelt.models._internal import _RawVGKG
from py_gdelt.models.vgkg import (
    FaceAnnotationDict,
    SafeSearchDict,
    VGKGRecord,
    VisionLabelDict,
)


def test_vgkg_record_from_raw_basic():
    """Test basic VGKGRecord creation from _RawVGKG."""
    raw = _RawVGKG(
        date="20260120120000",
        document_identifier="https://www.example.com/article.html",
        image_url="https://www.example.com/image.jpg",
        labels="Sky<FIELD>0.95<FIELD>/m/01589<RECORD>Cloud<FIELD>0.88<FIELD>/m/0csby",
        logos="CNN<FIELD>0.92<FIELD>/m/019_tv",
        web_entities="News<FIELD>0.85<FIELD>/m/05jbn",
        safe_search="0<FIELD>1<FIELD>0<FIELD>1",
        faces="0.95<FIELD>0.1<FIELD>-0.2<FIELD>0.05<FIELD>0.98<FIELD>10,20,100,150",
        ocr_text="Breaking News",
        landmark_annotations="Eiffel Tower<FIELD>0.90<FIELD>/m/02j81",
        domain="example.com",
        raw_json='{"test": "data"}',
    )

    record = VGKGRecord.from_raw(raw)

    assert record.date == datetime(2026, 1, 20, 12, 0, 0, tzinfo=UTC)
    assert record.document_identifier == "https://www.example.com/article.html"
    assert record.image_url == "https://www.example.com/image.jpg"
    assert record.domain == "example.com"
    assert record.ocr_text == "Breaking News"
    assert record.raw_json == '{"test": "data"}'


def test_vgkg_record_parse_labels():
    """Test parsing of labels field."""
    raw = _RawVGKG(
        date="20260120120000",
        document_identifier="https://www.example.com/article.html",
        image_url="https://www.example.com/image.jpg",
        labels="Sky<FIELD>0.95<FIELD>/m/01589<RECORD>Cloud<FIELD>0.88<FIELD>/m/0csby<RECORD>Nature<FIELD>0.75<FIELD>",
        logos="",
        web_entities="",
        safe_search="",
        faces="",
        ocr_text="",
        landmark_annotations="",
        domain="",
        raw_json="",
    )

    record = VGKGRecord.from_raw(raw)

    assert len(record.labels) == 3

    # First label
    assert record.labels[0]["description"] == "Sky"
    assert record.labels[0]["confidence"] == 0.95
    assert record.labels[0]["mid"] == "/m/01589"

    # Second label
    assert record.labels[1]["description"] == "Cloud"
    assert record.labels[1]["confidence"] == 0.88
    assert record.labels[1]["mid"] == "/m/0csby"

    # Third label (no MID)
    assert record.labels[2]["description"] == "Nature"
    assert record.labels[2]["confidence"] == 0.75
    assert record.labels[2]["mid"] is None


def test_vgkg_record_parse_safe_search():
    """Test parsing of safe_search field."""
    raw = _RawVGKG(
        date="20260120120000",
        document_identifier="https://www.example.com/article.html",
        image_url="https://www.example.com/image.jpg",
        labels="",
        logos="",
        web_entities="",
        safe_search="0<FIELD>1<FIELD>2<FIELD>3",
        faces="",
        ocr_text="",
        landmark_annotations="",
        domain="",
        raw_json="",
    )

    record = VGKGRecord.from_raw(raw)

    assert record.safe_search is not None
    assert record.safe_search["adult"] == 0
    assert record.safe_search["spoof"] == 1
    assert record.safe_search["medical"] == 2
    assert record.safe_search["violence"] == 3


def test_vgkg_record_parse_safe_search_empty():
    """Test that empty safe_search returns None."""
    raw = _RawVGKG(
        date="20260120120000",
        document_identifier="https://www.example.com/article.html",
        image_url="https://www.example.com/image.jpg",
        labels="",
        logos="",
        web_entities="",
        safe_search="",
        faces="",
        ocr_text="",
        landmark_annotations="",
        domain="",
        raw_json="",
    )

    record = VGKGRecord.from_raw(raw)
    assert record.safe_search is None


def test_vgkg_record_parse_faces():
    """Test parsing of faces field."""
    raw = _RawVGKG(
        date="20260120120000",
        document_identifier="https://www.example.com/article.html",
        image_url="https://www.example.com/image.jpg",
        labels="",
        logos="",
        web_entities="",
        safe_search="",
        faces="0.95<FIELD>0.1<FIELD>-0.2<FIELD>0.05<FIELD>0.98<FIELD>10,20,100,150<RECORD>0.87<FIELD>-0.15<FIELD>0.3<FIELD>-0.1<FIELD>0.92<FIELD>",
        ocr_text="",
        landmark_annotations="",
        domain="",
        raw_json="",
    )

    record = VGKGRecord.from_raw(raw)

    assert len(record.faces) == 2

    # First face
    assert record.faces[0]["confidence"] == 0.95
    assert record.faces[0]["roll"] == 0.1
    assert record.faces[0]["pan"] == -0.2
    assert record.faces[0]["tilt"] == 0.05
    assert record.faces[0]["detection_confidence"] == 0.98
    assert record.faces[0]["bounding_box"] == "10,20,100,150"

    # Second face (no bounding box)
    assert record.faces[1]["confidence"] == 0.87
    assert record.faces[1]["roll"] == -0.15
    assert record.faces[1]["pan"] == 0.3
    assert record.faces[1]["tilt"] == -0.1
    assert record.faces[1]["detection_confidence"] == 0.92
    assert record.faces[1]["bounding_box"] is None


def test_vgkg_record_empty_fields():
    """Test VGKGRecord with empty/None fields."""
    raw = _RawVGKG(
        date="20260120120000",
        document_identifier="https://www.example.com/article.html",
        image_url="https://www.example.com/image.jpg",
        labels="",
        logos="",
        web_entities="",
        safe_search="",
        faces="",
        ocr_text="",
        landmark_annotations="",
        domain="",
        raw_json="",
    )

    record = VGKGRecord.from_raw(raw)

    assert record.labels == []
    assert record.logos == []
    assert record.web_entities == []
    assert record.safe_search is None
    assert record.faces == []
    assert record.ocr_text == ""
    assert record.landmark_annotations == []
    assert record.domain == ""
    assert record.raw_json == ""


def test_vgkg_record_parse_malformed_labels():
    """Test that malformed labels are skipped gracefully."""
    raw = _RawVGKG(
        date="20260120120000",
        document_identifier="https://www.example.com/article.html",
        image_url="https://www.example.com/image.jpg",
        labels="Sky<FIELD>0.95<FIELD>/m/01589<RECORD>BadLabel<RECORD>Cloud<FIELD>0.88<FIELD>/m/0csby",
        logos="",
        web_entities="",
        safe_search="",
        faces="",
        ocr_text="",
        landmark_annotations="",
        domain="",
        raw_json="",
    )

    record = VGKGRecord.from_raw(raw)

    # Should only get 2 valid labels (malformed one skipped)
    assert len(record.labels) == 2
    assert record.labels[0]["description"] == "Sky"
    assert record.labels[1]["description"] == "Cloud"


def test_vgkg_record_parse_malformed_faces():
    """Test that malformed faces are skipped gracefully."""
    raw = _RawVGKG(
        date="20260120120000",
        document_identifier="https://www.example.com/article.html",
        image_url="https://www.example.com/image.jpg",
        labels="",
        logos="",
        web_entities="",
        safe_search="",
        faces="0.95<FIELD>0.1<FIELD>-0.2<RECORD>0.87<FIELD>-0.15<FIELD>0.3<FIELD>-0.1<FIELD>0.92<FIELD>",
        ocr_text="",
        landmark_annotations="",
        domain="",
        raw_json="",
    )

    record = VGKGRecord.from_raw(raw)

    # Should only get 1 valid face (first one has too few fields)
    assert len(record.faces) == 1
    assert record.faces[0]["confidence"] == 0.87


def test_vgkg_record_invalid_date():
    """Test that invalid date raises ValueError."""
    raw = _RawVGKG(
        date="INVALID",
        document_identifier="https://www.example.com/article.html",
        image_url="https://www.example.com/image.jpg",
        labels="",
        logos="",
        web_entities="",
        safe_search="",
        faces="",
        ocr_text="",
        landmark_annotations="",
        domain="",
        raw_json="",
    )

    with pytest.raises(ValueError):
        VGKGRecord.from_raw(raw)


def test_vision_label_dict_structure():
    """Test VisionLabelDict TypedDict structure."""
    label: VisionLabelDict = {
        "description": "Sky",
        "confidence": 0.95,
        "mid": "/m/01589",
    }

    assert label["description"] == "Sky"
    assert label["confidence"] == 0.95
    assert label["mid"] == "/m/01589"


def test_safe_search_dict_structure():
    """Test SafeSearchDict TypedDict structure."""
    safe_search: SafeSearchDict = {
        "adult": 0,
        "spoof": 1,
        "medical": 2,
        "violence": 3,
    }

    assert safe_search["adult"] == 0
    assert safe_search["spoof"] == 1
    assert safe_search["medical"] == 2
    assert safe_search["violence"] == 3


def test_face_annotation_dict_structure():
    """Test FaceAnnotationDict TypedDict structure."""
    face: FaceAnnotationDict = {
        "confidence": 0.95,
        "roll": 0.1,
        "pan": -0.2,
        "tilt": 0.05,
        "detection_confidence": 0.98,
        "bounding_box": "10,20,100,150",
    }

    assert face["confidence"] == 0.95
    assert face["roll"] == 0.1
    assert face["pan"] == -0.2
    assert face["tilt"] == 0.05
    assert face["detection_confidence"] == 0.98
    assert face["bounding_box"] == "10,20,100,150"
