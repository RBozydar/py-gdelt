"""Pydantic models for GDELT VGKG (Visual Global Knowledge Graph) data.

VGKG contains Google Cloud Vision API analysis of images from news articles.
Nested structures use TypedDict for performance (see tests/benchmarks/test_bench_vgkg_parsing.py).

Based on schema discovery from real GDELT VGKG data (2026-01-20).
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, TypedDict

from pydantic import BaseModel, Field


if TYPE_CHECKING:
    from py_gdelt.models._internal import _RawVGKG


__all__ = [
    "FaceAnnotationDict",
    "SafeSearchDict",
    "VGKGRecord",
    "VisionLabelDict",
]


# Delimiters for parsing nested VGKG fields
_FIELD_DELIM = "<FIELD>"
_RECORD_DELIM = "<RECORD>"


class VisionLabelDict(TypedDict):
    """Google Cloud Vision label annotation (lightweight).

    Used for labels, logos, web_entities, and landmark_annotations fields.
    TypedDict avoids Pydantic validation overhead for nested structures.
    """

    description: str
    confidence: float
    mid: str | None  # Knowledge Graph MID - useful for entity linking


class SafeSearchDict(TypedDict):
    """SafeSearch detection results.

    Values are integers from Cloud Vision API:
    - UNKNOWN = -1
    - VERY_UNLIKELY = 0
    - UNLIKELY = 1
    - POSSIBLE = 2
    - LIKELY = 3
    - VERY_LIKELY = 4
    """

    adult: int
    spoof: int
    medical: int
    violence: int


class FaceAnnotationDict(TypedDict):
    """Detected face with pose angles.

    Contains pose information (roll/pan/tilt angles), NOT emotion scores.
    Angles are in degrees relative to the camera.
    """

    confidence: float
    roll: float  # Head roll angle in degrees
    pan: float  # Head pan angle in degrees
    tilt: float  # Head tilt angle in degrees
    detection_confidence: float
    bounding_box: str | None  # Format: "x1,y1,x2,y2"


class VGKGRecord(BaseModel):
    """Visual GKG record with Cloud Vision annotations.

    Nested structures (labels, faces, etc.) use TypedDict for performance.
    See tests/benchmarks/test_bench_vgkg_parsing.py for rationale.

    Attributes:
        date: Timestamp of the analysis.
        document_identifier: Source article URL.
        image_url: URL of the analyzed image.
        labels: List of detected labels with confidence scores.
        logos: List of detected logos.
        web_entities: List of web entities matched to the image.
        safe_search: SafeSearch annotation scores.
        faces: List of detected faces with pose information.
        ocr_text: Text extracted via OCR.
        landmark_annotations: List of detected landmarks.
        domain: Domain of the source article.
        raw_json: Full Cloud Vision API JSON response.
    """

    date: datetime
    document_identifier: str
    image_url: str
    labels: list[VisionLabelDict] = Field(default_factory=list)
    logos: list[VisionLabelDict] = Field(default_factory=list)
    web_entities: list[VisionLabelDict] = Field(default_factory=list)
    safe_search: SafeSearchDict | None = None
    faces: list[FaceAnnotationDict] = Field(default_factory=list)
    ocr_text: str = ""
    landmark_annotations: list[VisionLabelDict] = Field(default_factory=list)
    domain: str = ""
    raw_json: str = ""  # Keep as string - users can parse with json.loads() if needed

    @classmethod
    def from_raw(cls, raw: _RawVGKG) -> VGKGRecord:
        """Convert internal _RawVGKG to validated VGKGRecord model.

        Args:
            raw: Internal raw VGKG representation with string fields.

        Returns:
            Validated VGKGRecord instance.

        Raises:
            ValueError: If date parsing or type conversion fails.
        """
        return cls(
            date=datetime.strptime(raw.date, "%Y%m%d%H%M%S").replace(tzinfo=UTC),
            document_identifier=raw.document_identifier,
            image_url=raw.image_url,
            labels=cls._parse_labels(raw.labels),
            logos=cls._parse_labels(raw.logos),
            web_entities=cls._parse_labels(raw.web_entities),
            safe_search=cls._parse_safe_search(raw.safe_search),
            faces=cls._parse_faces(raw.faces),
            ocr_text=raw.ocr_text or "",
            landmark_annotations=cls._parse_labels(raw.landmark_annotations),
            domain=raw.domain or "",
            raw_json=raw.raw_json or "",
        )

    @classmethod
    def _parse_labels(cls, raw: str) -> list[VisionLabelDict]:
        """Parse Label<FIELD>Confidence<FIELD>MID<RECORD>... format.

        Args:
            raw: Delimited string with label records.

        Returns:
            List of VisionLabelDict objects.
        """
        if not raw:
            return []
        labels: list[VisionLabelDict] = []
        for record in raw.split(_RECORD_DELIM):
            if not record.strip():
                continue
            fields = record.split(_FIELD_DELIM)
            if len(fields) >= 2:
                try:
                    labels.append(
                        {
                            "description": fields[0],
                            "confidence": float(fields[1]) if fields[1] else 0.0,
                            "mid": fields[2] if len(fields) > 2 and fields[2] else None,
                        }
                    )
                except (ValueError, IndexError):
                    continue
        return labels

    @classmethod
    def _parse_safe_search(cls, raw: str) -> SafeSearchDict | None:
        """Parse safe_search field (4 integers).

        Args:
            raw: Delimited string with 4 safe search scores.

        Returns:
            SafeSearchDict or None if parsing fails.
        """
        if not raw:
            return None
        fields = raw.split(_FIELD_DELIM)
        if len(fields) < 4:
            return None
        try:
            return {
                "adult": int(fields[0]) if fields[0] else -1,
                "spoof": int(fields[1]) if fields[1] else -1,
                "medical": int(fields[2]) if fields[2] else -1,
                "violence": int(fields[3]) if fields[3] else -1,
            }
        except (ValueError, IndexError):
            return None

    @classmethod
    def _parse_faces(cls, raw: str) -> list[FaceAnnotationDict]:
        """Parse faces field (roll/pan/tilt angles, NOT emotions).

        Args:
            raw: Delimited string with face records.

        Returns:
            List of FaceAnnotationDict objects.
        """
        if not raw:
            return []
        faces: list[FaceAnnotationDict] = []
        for record in raw.split(_RECORD_DELIM):
            if not record.strip():
                continue
            fields = record.split(_FIELD_DELIM)
            if len(fields) >= 5:
                try:
                    faces.append(
                        {
                            "confidence": float(fields[0]) if fields[0] else 0.0,
                            "roll": float(fields[1]) if fields[1] else 0.0,
                            "pan": float(fields[2]) if fields[2] else 0.0,
                            "tilt": float(fields[3]) if fields[3] else 0.0,
                            "detection_confidence": float(fields[4]) if fields[4] else 0.0,
                            "bounding_box": fields[5] if len(fields) > 5 and fields[5] else None,
                        }
                    )
                except (ValueError, IndexError):
                    continue
        return faces
