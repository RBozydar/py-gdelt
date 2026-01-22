"""Parser for GDELT VGKG (Visual Global Knowledge Graph) files.

VGKG provides Google Cloud Vision API analysis of images extracted from news
articles, including labels, logos, web entities, safe search scores, face
detection, OCR text, and landmark annotations.

The parser converts raw TAB-delimited bytes into _RawVGKG dataclass instances.
Complex nested fields (labels, logos, faces) use <FIELD> and <RECORD> delimiters
and are stored as strings for parsing during Pydantic model conversion.

Nested delimiter format:
    - <FIELD> separates fields within a record
    - <RECORD> separates multiple records in a column

Example nested fields:
    labels: "Sky<FIELD>0.95<FIELD>/m/01589<RECORD>Cloud<FIELD>0.88<FIELD>/m/0csby"
    safe_search: "0.12<FIELD>0.08<FIELD>0.05<FIELD>0.03"
    faces: "0.95<FIELD>0.1<FIELD>-0.2<FIELD>0.05<FIELD>0.98<FIELD>10,20,100,150<RECORD>..."
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from collections.abc import Iterator

from py_gdelt.models._internal import _RawVGKG


__all__ = ["VGKGParser"]

logger = logging.getLogger(__name__)


class VGKGParser:
    """Parser for GDELT VGKG files with nested delimiters.

    Handles tab-delimited VGKG files with 12 columns. The VGKG files use nested
    delimiters (<FIELD> and <RECORD>) for complex fields like labels, logos, and
    face annotations.

    This parser keeps nested fields as raw strings; parsing of nested structures
    happens in the Pydantic model layer for performance.

    The parser is lenient with malformed lines (logs warning and skips) to ensure
    processing continues even with occasional data quality issues.

    Attributes:
        EXPECTED_COLUMNS: Number of columns expected in VGKG files (12).

    Example:
        >>> parser = VGKGParser()
        >>> for record in parser.parse(raw_bytes):
        ...     print(record.date, record.image_url)
    """

    EXPECTED_COLUMNS = 12

    def parse(self, data: bytes) -> Iterator[_RawVGKG]:
        """Parse raw bytes into _RawVGKG records.

        Args:
            data: Raw VGKG file content as bytes (TAB-delimited).

        Yields:
            _RawVGKG: _RawVGKG instances for each valid record.

        Notes:
            - VGKG files have 12 columns with nested <FIELD> and <RECORD> delimiters
            - Empty fields are converted to empty strings
            - Malformed lines are logged and skipped
            - UTF-8 encoding with replacement for invalid characters
            - Complex delimited fields (labels, logos, faces) remain as strings
              for downstream parsing
        """
        lines = data.decode("utf-8", errors="replace").strip().split("\n")
        if not lines:
            logger.warning("Empty VGKG data provided")
            return

        logger.debug("Parsing %d VGKG lines", len(lines))

        for line_num, raw_line in enumerate(lines, start=1):
            line = raw_line.strip()
            if not line:
                continue

            parts = line.split("\t")
            if len(parts) != self.EXPECTED_COLUMNS:
                logger.warning(
                    "Skipping malformed VGKG line %d: expected %d columns, got %d",
                    line_num,
                    self.EXPECTED_COLUMNS,
                    len(parts),
                )
                continue

            try:
                # Helper to convert None values to empty strings
                def field(idx: int, parts: list[str] = parts) -> str:
                    val = parts[idx].strip() if idx < len(parts) else ""
                    return val if val else ""

                yield _RawVGKG(
                    date=field(0),
                    document_identifier=field(1),
                    image_url=field(2),
                    labels=field(3),
                    logos=field(4),
                    web_entities=field(5),
                    safe_search=field(6),
                    faces=field(7),
                    ocr_text=field(8),
                    landmark_annotations=field(9),
                    domain=field(10),
                    raw_json=field(11),
                )
            except Exception as e:  # noqa: BLE001
                # Error boundary: log and skip malformed lines
                logger.warning("Error parsing VGKG line %d: %s", line_num, e)
                continue
