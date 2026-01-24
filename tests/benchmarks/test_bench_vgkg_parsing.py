"""Benchmark tests for VGKG parsing performance.

This module compares different parsing approaches for VGKG nested structures:
1. Pydantic nested models (full validation)
2. TypedDict approach (structured dicts with type hints)
3. NamedTuple approach (immutable tuples with named fields)
4. Raw string approach (no parsing of nested fields)

Based on real VGKG data with 12 columns:
- Column [3] labels: Label<FIELD>Confidence<FIELD>MID<RECORD>...
- Column [6] safe_search: score<FIELD>score<FIELD>score<FIELD>score (4 integers)
- Column [7] faces: confidence<FIELD>roll<FIELD>pan<FIELD>tilt<FIELD>detection_confidence<FIELD>bbox<RECORD>...
- Column [11] raw_json: Full Cloud Vision API JSON response (14-30KB)
"""

from __future__ import annotations

import json
import logging
import statistics
import timeit
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import NamedTuple, TypedDict

from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)


# ============================================================================
# Approach 1: Pydantic Nested Models (Full Validation)
# ============================================================================


class VisionLabel(BaseModel):
    """Google Cloud Vision label annotation."""

    description: str
    confidence: float = Field(ge=0.0, le=1.0)
    mid: str | None = None


class SafeSearchScores(BaseModel):
    """SafeSearch detection results."""

    adult: float = Field(ge=0.0, le=1.0)
    spoof: float = Field(ge=0.0, le=1.0)
    medical: float = Field(ge=0.0, le=1.0)
    violence: float = Field(ge=0.0, le=1.0)


class FaceAnnotation(BaseModel):
    """Detected face with emotion scores."""

    confidence: float
    roll: float
    pan: float
    tilt: float
    detection_confidence: float
    bounding_box: str | None = None


class VGKGRecordPydantic(BaseModel):
    """VGKG record with full Pydantic nested models."""

    date: datetime
    document_identifier: str
    image_url: str
    labels: list[VisionLabel] = Field(default_factory=list)
    logos: list[VisionLabel] = Field(default_factory=list)
    web_entities: list[VisionLabel] = Field(default_factory=list)
    safe_search: SafeSearchScores | None = None
    faces: list[FaceAnnotation] = Field(default_factory=list)
    ocr_text: str
    landmark_annotations: str
    domain: str
    raw_json: str


# ============================================================================
# Approach 2: TypedDict (Structured Dicts)
# ============================================================================


class VisionLabelDict(TypedDict):
    """Vision label as TypedDict."""

    description: str
    confidence: float
    mid: str | None


class SafeSearchDict(TypedDict):
    """SafeSearch scores as TypedDict."""

    adult: float
    spoof: float
    medical: float
    violence: float


class FaceDict(TypedDict):
    """Face annotation as TypedDict."""

    confidence: float
    roll: float
    pan: float
    tilt: float
    detection_confidence: float
    bounding_box: str | None


class VGKGRecordDict(TypedDict):
    """VGKG record using TypedDict for nested structures."""

    date: datetime
    document_identifier: str
    image_url: str
    labels: list[VisionLabelDict]
    logos: list[VisionLabelDict]
    web_entities: list[VisionLabelDict]
    safe_search: SafeSearchDict | None
    faces: list[FaceDict]
    ocr_text: str
    landmark_annotations: str
    domain: str
    raw_json: str


# ============================================================================
# Approach 3: NamedTuple (Immutable Tuples)
# ============================================================================


class VisionLabelTuple(NamedTuple):
    """Vision label as NamedTuple."""

    description: str
    confidence: float
    mid: str | None


class SafeSearchTuple(NamedTuple):
    """SafeSearch scores as NamedTuple."""

    adult: float
    spoof: float
    medical: float
    violence: float


class FaceTuple(NamedTuple):
    """Face annotation as NamedTuple."""

    confidence: float
    roll: float
    pan: float
    tilt: float
    detection_confidence: float
    bounding_box: str | None


@dataclass(slots=True)
class VGKGRecordTuple:
    """VGKG record using NamedTuple for nested structures."""

    date: datetime
    document_identifier: str
    image_url: str
    labels: list[VisionLabelTuple]
    logos: list[VisionLabelTuple]
    web_entities: list[VisionLabelTuple]
    safe_search: SafeSearchTuple | None
    faces: list[FaceTuple]
    ocr_text: str
    landmark_annotations: str
    domain: str
    raw_json: str


# ============================================================================
# Approach 4: Raw Strings (No Nested Parsing)
# ============================================================================


@dataclass(slots=True)
class VGKGRecordRaw:
    """VGKG record keeping nested fields as raw strings."""

    date: datetime
    document_identifier: str
    image_url: str
    labels: str
    logos: str
    web_entities: str
    safe_search: str
    faces: str
    ocr_text: str
    landmark_annotations: str
    domain: str
    raw_json: str


# ============================================================================
# Sample Data Generation
# ============================================================================


def generate_sample_vgkg_row() -> list[str]:
    """Generate a realistic VGKG row with typical field sizes.

    Returns:
        List of 12 column values representing one VGKG row
    """
    # Column 0: date (YYYYMMDDHHMMSS)
    date = "20260120120000"

    # Column 1: document_identifier (URL)
    document_identifier = "https://www.example.com/news/article-12345.html"

    # Column 2: image_url
    image_url = "https://www.example.com/images/photo-67890.jpg"

    # Column 3: labels (10 labels, typical)
    labels_parts = [f"Label{i}<FIELD>0.{85 + i}<FIELD>/m/0{1000 + i}" for i in range(10)]
    labels = "<RECORD>".join(labels_parts)

    # Column 4: logos (2 logos, typical)
    logos_parts = [
        "CNN<FIELD>0.92<FIELD>/m/019_tv",
        "BBC<FIELD>0.88<FIELD>/m/01cd9",
    ]
    logos = "<RECORD>".join(logos_parts)

    # Column 5: web_entities (8 entities, typical)
    web_entities_parts = [f"Entity{i}<FIELD>0.{70 + i}<FIELD>/m/0{2000 + i}" for i in range(8)]
    web_entities = "<RECORD>".join(web_entities_parts)

    # Column 6: safe_search (4 scores)
    safe_search = "0.12<FIELD>0.08<FIELD>0.05<FIELD>0.03"

    # Column 7: faces (3 faces, typical)
    faces_parts = [
        "0.95<FIELD>0.1<FIELD>-0.2<FIELD>0.05<FIELD>0.98<FIELD>10,20,100,150",
        "0.87<FIELD>-0.15<FIELD>0.3<FIELD>-0.1<FIELD>0.92<FIELD>200,30,80,120",
        "0.79<FIELD>0.05<FIELD>0.1<FIELD>0.0<FIELD>0.85<FIELD>50,150,90,140",
    ]
    faces = "<RECORD>".join(faces_parts)

    # Column 8: ocr_text (typical OCR result)
    ocr_text = "Breaking News: Major event happening now. More details to follow."

    # Column 9: landmark_annotations
    landmark_annotations = "Landmark1<FIELD>0.85<FIELD>/m/03000"

    # Column 10: domain
    domain = "example.com"

    # Column 11: raw_json (simplified Cloud Vision API response, ~20KB typical)
    raw_json_obj = {
        "responses": [
            {
                "labelAnnotations": [
                    {"description": f"Label{i}", "score": 0.85 + i * 0.01, "mid": f"/m/0{1000 + i}"}
                    for i in range(10)
                ],
                "logoAnnotations": [
                    {"description": "CNN", "score": 0.92, "mid": "/m/019_tv"},
                    {"description": "BBC", "score": 0.88, "mid": "/m/01cd9"},
                ],
                "webDetection": {
                    "webEntities": [
                        {
                            "entityId": f"/m/0{2000 + i}",
                            "score": 0.70 + i * 0.01,
                            "description": f"Entity{i}",
                        }
                        for i in range(8)
                    ],
                },
                "safeSearchAnnotation": {
                    "adult": "VERY_UNLIKELY",
                    "spoof": "UNLIKELY",
                    "medical": "VERY_UNLIKELY",
                    "violence": "UNLIKELY",
                },
                "faceAnnotations": [
                    {
                        "detectionConfidence": 0.98,
                        "landmarkingConfidence": 0.95,
                        "rollAngle": 0.1,
                        "panAngle": -0.2,
                        "tiltAngle": 0.05,
                        "boundingPoly": {"vertices": [{"x": 10, "y": 20}, {"x": 100, "y": 150}]},
                    },
                    {
                        "detectionConfidence": 0.92,
                        "landmarkingConfidence": 0.87,
                        "rollAngle": -0.15,
                        "panAngle": 0.3,
                        "tiltAngle": -0.1,
                        "boundingPoly": {"vertices": [{"x": 200, "y": 30}, {"x": 80, "y": 120}]},
                    },
                    {
                        "detectionConfidence": 0.85,
                        "landmarkingConfidence": 0.79,
                        "rollAngle": 0.05,
                        "panAngle": 0.1,
                        "tiltAngle": 0.0,
                        "boundingPoly": {"vertices": [{"x": 50, "y": 150}, {"x": 90, "y": 140}]},
                    },
                ],
                "textAnnotations": [
                    {
                        "description": "Breaking News: Major event happening now. More details to follow."
                    }
                ],
                "landmarkAnnotations": [
                    {"description": "Landmark1", "score": 0.85, "mid": "/m/03000"}
                ],
            }
        ]
    }
    # Pad JSON to realistic size (~20KB)
    raw_json = json.dumps({**raw_json_obj, "padding": {"_padding": "x" * 15000}})

    return [
        date,
        document_identifier,
        image_url,
        labels,
        logos,
        web_entities,
        safe_search,
        faces,
        ocr_text,
        landmark_annotations,
        domain,
        raw_json,
    ]


def generate_sample_data(num_rows: int = 1000) -> list[list[str]]:
    """Generate sample VGKG data for benchmarking.

    Args:
        num_rows: Number of rows to generate

    Returns:
        List of VGKG rows (each row is list of 12 columns)
    """
    return [generate_sample_vgkg_row() for _ in range(num_rows)]


# ============================================================================
# Parsing Functions
# ============================================================================


FIELD_DELIM = "<FIELD>"
RECORD_DELIM = "<RECORD>"


def parse_pydantic(rows: list[list[str]]) -> list[VGKGRecordPydantic]:
    """Parse VGKG data using Pydantic nested models.

    Args:
        rows: List of VGKG rows

    Returns:
        List of parsed VGKGRecordPydantic objects
    """
    results = []
    for row in rows:
        # Parse labels
        labels = []
        if row[3]:
            for record in row[3].split(RECORD_DELIM):
                fields = record.split(FIELD_DELIM)
                if len(fields) >= 2:
                    labels.append(
                        VisionLabel(
                            description=fields[0],
                            confidence=float(fields[1]),
                            mid=fields[2] if len(fields) > 2 else None,
                        )
                    )

        # Parse logos
        logos = []
        if row[4]:
            for record in row[4].split(RECORD_DELIM):
                fields = record.split(FIELD_DELIM)
                if len(fields) >= 2:
                    logos.append(
                        VisionLabel(
                            description=fields[0],
                            confidence=float(fields[1]),
                            mid=fields[2] if len(fields) > 2 else None,
                        )
                    )

        # Parse web_entities
        web_entities = []
        if row[5]:
            for record in row[5].split(RECORD_DELIM):
                fields = record.split(FIELD_DELIM)
                if len(fields) >= 2:
                    web_entities.append(
                        VisionLabel(
                            description=fields[0],
                            confidence=float(fields[1]),
                            mid=fields[2] if len(fields) > 2 else None,
                        )
                    )

        # Parse safe_search
        safe_search = None
        if row[6]:
            fields = row[6].split(FIELD_DELIM)
            if len(fields) >= 4:
                safe_search = SafeSearchScores(
                    adult=float(fields[0]),
                    spoof=float(fields[1]),
                    medical=float(fields[2]),
                    violence=float(fields[3]),
                )

        # Parse faces
        faces = []
        if row[7]:
            for record in row[7].split(RECORD_DELIM):
                fields = record.split(FIELD_DELIM)
                if len(fields) >= 5:
                    faces.append(
                        FaceAnnotation(
                            confidence=float(fields[0]),
                            roll=float(fields[1]),
                            pan=float(fields[2]),
                            tilt=float(fields[3]),
                            detection_confidence=float(fields[4]),
                            bounding_box=fields[5] if len(fields) > 5 else None,
                        )
                    )

        results.append(
            VGKGRecordPydantic(
                date=datetime.strptime(row[0], "%Y%m%d%H%M%S").replace(tzinfo=UTC),
                document_identifier=row[1],
                image_url=row[2],
                labels=labels,
                logos=logos,
                web_entities=web_entities,
                safe_search=safe_search,
                faces=faces,
                ocr_text=row[8],
                landmark_annotations=row[9],
                domain=row[10],
                raw_json=row[11],
            )
        )

    return results


def parse_typeddict(rows: list[list[str]]) -> list[VGKGRecordDict]:
    """Parse VGKG data using TypedDict for nested structures.

    Args:
        rows: List of VGKG rows

    Returns:
        List of parsed VGKGRecordDict objects
    """
    results: list[VGKGRecordDict] = []
    for row in rows:
        # Parse labels
        labels: list[VisionLabelDict] = []
        if row[3]:
            for label_str in row[3].split(RECORD_DELIM):
                fields = label_str.split(FIELD_DELIM)
                if len(fields) >= 2:
                    labels.append(
                        {
                            "description": fields[0],
                            "confidence": float(fields[1]),
                            "mid": fields[2] if len(fields) > 2 else None,
                        }
                    )

        # Parse logos
        logos: list[VisionLabelDict] = []
        if row[4]:
            for logo_str in row[4].split(RECORD_DELIM):
                fields = logo_str.split(FIELD_DELIM)
                if len(fields) >= 2:
                    logos.append(
                        {
                            "description": fields[0],
                            "confidence": float(fields[1]),
                            "mid": fields[2] if len(fields) > 2 else None,
                        }
                    )

        # Parse web_entities
        web_entities: list[VisionLabelDict] = []
        if row[5]:
            for entity_str in row[5].split(RECORD_DELIM):
                fields = entity_str.split(FIELD_DELIM)
                if len(fields) >= 2:
                    web_entities.append(
                        {
                            "description": fields[0],
                            "confidence": float(fields[1]),
                            "mid": fields[2] if len(fields) > 2 else None,
                        }
                    )

        # Parse safe_search
        safe_search: SafeSearchDict | None = None
        if row[6]:
            fields = row[6].split(FIELD_DELIM)
            if len(fields) >= 4:
                safe_search = {
                    "adult": float(fields[0]),
                    "spoof": float(fields[1]),
                    "medical": float(fields[2]),
                    "violence": float(fields[3]),
                }

        # Parse faces
        faces: list[FaceDict] = []
        if row[7]:
            for face_str in row[7].split(RECORD_DELIM):
                fields = face_str.split(FIELD_DELIM)
                if len(fields) >= 5:
                    faces.append(
                        {
                            "confidence": float(fields[0]),
                            "roll": float(fields[1]),
                            "pan": float(fields[2]),
                            "tilt": float(fields[3]),
                            "detection_confidence": float(fields[4]),
                            "bounding_box": fields[5] if len(fields) > 5 else None,
                        }
                    )

        record: VGKGRecordDict = {
            "date": datetime.strptime(row[0], "%Y%m%d%H%M%S").replace(tzinfo=UTC),
            "document_identifier": row[1],
            "image_url": row[2],
            "labels": labels,
            "logos": logos,
            "web_entities": web_entities,
            "safe_search": safe_search,
            "faces": faces,
            "ocr_text": row[8],
            "landmark_annotations": row[9],
            "domain": row[10],
            "raw_json": row[11],
        }
        results.append(record)

    return results


def parse_namedtuple(rows: list[list[str]]) -> list[VGKGRecordTuple]:
    """Parse VGKG data using NamedTuple for nested structures.

    Args:
        rows: List of VGKG rows

    Returns:
        List of parsed VGKGRecordTuple objects
    """
    results = []
    for row in rows:
        # Parse labels
        labels: list[VisionLabelTuple] = []
        if row[3]:
            for record in row[3].split(RECORD_DELIM):
                fields = record.split(FIELD_DELIM)
                if len(fields) >= 2:
                    labels.append(
                        VisionLabelTuple(
                            description=fields[0],
                            confidence=float(fields[1]),
                            mid=fields[2] if len(fields) > 2 else None,
                        )
                    )

        # Parse logos
        logos: list[VisionLabelTuple] = []
        if row[4]:
            for record in row[4].split(RECORD_DELIM):
                fields = record.split(FIELD_DELIM)
                if len(fields) >= 2:
                    logos.append(
                        VisionLabelTuple(
                            description=fields[0],
                            confidence=float(fields[1]),
                            mid=fields[2] if len(fields) > 2 else None,
                        )
                    )

        # Parse web_entities
        web_entities: list[VisionLabelTuple] = []
        if row[5]:
            for record in row[5].split(RECORD_DELIM):
                fields = record.split(FIELD_DELIM)
                if len(fields) >= 2:
                    web_entities.append(
                        VisionLabelTuple(
                            description=fields[0],
                            confidence=float(fields[1]),
                            mid=fields[2] if len(fields) > 2 else None,
                        )
                    )

        # Parse safe_search
        safe_search: SafeSearchTuple | None = None
        if row[6]:
            fields = row[6].split(FIELD_DELIM)
            if len(fields) >= 4:
                safe_search = SafeSearchTuple(
                    adult=float(fields[0]),
                    spoof=float(fields[1]),
                    medical=float(fields[2]),
                    violence=float(fields[3]),
                )

        # Parse faces
        faces: list[FaceTuple] = []
        if row[7]:
            for record in row[7].split(RECORD_DELIM):
                fields = record.split(FIELD_DELIM)
                if len(fields) >= 5:
                    faces.append(
                        FaceTuple(
                            confidence=float(fields[0]),
                            roll=float(fields[1]),
                            pan=float(fields[2]),
                            tilt=float(fields[3]),
                            detection_confidence=float(fields[4]),
                            bounding_box=fields[5] if len(fields) > 5 else None,
                        )
                    )

        results.append(
            VGKGRecordTuple(
                date=datetime.strptime(row[0], "%Y%m%d%H%M%S").replace(tzinfo=UTC),
                document_identifier=row[1],
                image_url=row[2],
                labels=labels,
                logos=logos,
                web_entities=web_entities,
                safe_search=safe_search,
                faces=faces,
                ocr_text=row[8],
                landmark_annotations=row[9],
                domain=row[10],
                raw_json=row[11],
            )
        )

    return results


def parse_raw(rows: list[list[str]]) -> list[VGKGRecordRaw]:
    """Parse VGKG data keeping nested fields as raw strings.

    Args:
        rows: List of VGKG rows

    Returns:
        List of parsed VGKGRecordRaw objects
    """
    return [
        VGKGRecordRaw(
            date=datetime.strptime(row[0], "%Y%m%d%H%M%S").replace(tzinfo=UTC),
            document_identifier=row[1],
            image_url=row[2],
            labels=row[3],
            logos=row[4],
            web_entities=row[5],
            safe_search=row[6],
            faces=row[7],
            ocr_text=row[8],
            landmark_annotations=row[9],
            domain=row[10],
            raw_json=row[11],
        )
        for row in rows
    ]


# ============================================================================
# Benchmark Execution
# ============================================================================


def run_benchmark(
    num_rows: int = 1000,
    num_iterations: int = 5,
) -> dict[str, dict[str, float]]:
    """Run benchmark comparing all parsing approaches.

    Args:
        num_rows: Number of rows to parse in each iteration
        num_iterations: Number of times to run each approach

    Returns:
        Dictionary mapping approach name to performance metrics
    """
    sample_data = generate_sample_data(num_rows)

    results: dict[str, dict[str, float]] = {}

    # Benchmark 1: Pydantic nested models
    times = []
    for _ in range(num_iterations):
        start = timeit.default_timer()
        parse_pydantic(sample_data)
        end = timeit.default_timer()
        times.append(end - start)

    results["pydantic"] = {
        "mean": statistics.mean(times),
        "median": statistics.median(times),
        "stdev": statistics.stdev(times) if len(times) > 1 else 0.0,
        "min": min(times),
        "max": max(times),
    }

    # Benchmark 2: TypedDict approach
    times = []
    for _ in range(num_iterations):
        start = timeit.default_timer()
        parse_typeddict(sample_data)
        end = timeit.default_timer()
        times.append(end - start)

    results["typeddict"] = {
        "mean": statistics.mean(times),
        "median": statistics.median(times),
        "stdev": statistics.stdev(times) if len(times) > 1 else 0.0,
        "min": min(times),
        "max": max(times),
    }

    # Benchmark 3: NamedTuple approach
    times = []
    for _ in range(num_iterations):
        start = timeit.default_timer()
        parse_namedtuple(sample_data)
        end = timeit.default_timer()
        times.append(end - start)

    results["namedtuple"] = {
        "mean": statistics.mean(times),
        "median": statistics.median(times),
        "stdev": statistics.stdev(times) if len(times) > 1 else 0.0,
        "min": min(times),
        "max": max(times),
    }

    # Benchmark 4: Raw string approach
    times = []
    for _ in range(num_iterations):
        start = timeit.default_timer()
        parse_raw(sample_data)
        end = timeit.default_timer()
        times.append(end - start)

    results["raw"] = {
        "mean": statistics.mean(times),
        "median": statistics.median(times),
        "stdev": statistics.stdev(times) if len(times) > 1 else 0.0,
        "min": min(times),
        "max": max(times),
    }

    return results


def print_results(results: dict[str, dict[str, float]], num_rows: int) -> None:
    """Print benchmark results in a formatted table.

    Args:
        results: Benchmark results from run_benchmark
        num_rows: Number of rows processed
    """
    print("\n" + "=" * 80)
    print("VGKG PARSING BENCHMARK RESULTS")
    print("=" * 80)
    print(f"Rows processed: {num_rows:,}")
    print("Iterations: 5")
    print()

    # Calculate relative performance
    baseline = results["pydantic"]["mean"]

    # Print header
    print(
        f"{'Approach':<15} {'Mean (s)':<12} {'Median (s)':<12} {'StdDev':<10} {'vs Pydantic':<12}"
    )
    print("-" * 80)

    # Print each approach
    for approach in ["pydantic", "typeddict", "namedtuple", "raw"]:
        metrics = results[approach]
        speedup = baseline / metrics["mean"]
        speedup_str = f"{speedup:.2f}x" if speedup >= 1 else f"{1 / speedup:.2f}x slower"

        print(
            f"{approach:<15} "
            f"{metrics['mean']:>10.4f}  "
            f"{metrics['median']:>10.4f}  "
            f"{metrics['stdev']:>8.4f}  "
            f"{speedup_str:>12}"
        )

    print("-" * 80)
    print()

    # Print throughput
    print("Throughput (rows/second):")
    print("-" * 80)
    for approach in ["pydantic", "typeddict", "namedtuple", "raw"]:
        metrics = results[approach]
        throughput = num_rows / metrics["mean"]
        print(f"{approach:<15} {throughput:>12,.0f} rows/sec")

    print("=" * 80)
    print()

    # Print recommendations
    print("RECOMMENDATIONS:")
    print("-" * 80)

    fastest = min(results.items(), key=lambda x: x[1]["mean"])
    print(f"Fastest approach: {fastest[0]} ({fastest[1]['mean']:.4f}s mean)")

    pydantic_mean = results["pydantic"]["mean"]
    raw_mean = results["raw"]["mean"]
    parsing_overhead = ((pydantic_mean - raw_mean) / raw_mean) * 100

    print(f"Parsing overhead: {parsing_overhead:.1f}% (Pydantic vs Raw)")
    print()

    if parsing_overhead < 50:
        print("✓ Use Pydantic: Low overhead, full validation worth it")
    elif parsing_overhead < 150:
        print("⚠ Consider NamedTuple: Moderate overhead, good middle ground")
    else:
        print("⚠ Consider Raw or TypedDict: High overhead, parse on-demand")

    print("=" * 80)


# ============================================================================
# Test Entry Point
# ============================================================================


def test_vgkg_parsing_benchmark() -> None:
    """Run VGKG parsing benchmark test.

    This test compares parsing performance of different approaches.
    Can be run standalone or via pytest.
    """
    results = run_benchmark(num_rows=1000, num_iterations=5)
    print_results(results, num_rows=1000)

    # Basic assertions to ensure benchmark ran successfully
    for approach in ["pydantic", "typeddict", "namedtuple", "raw"]:
        mean_time = results[approach]["mean"]
        if mean_time <= 0:
            msg = f"{approach} benchmark failed: invalid time {mean_time}"
            raise ValueError(msg)
        if mean_time > 60:
            logger.warning("%s took longer than expected: %s seconds", approach, mean_time)


if __name__ == "__main__":
    test_vgkg_parsing_benchmark()
