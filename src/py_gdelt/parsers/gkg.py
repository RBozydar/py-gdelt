"""Parser for GDELT GKG (Global Knowledge Graph) files.

GKG provides rich content analysis from news articles including themes, people,
organizations, locations, counts, and sentiment analysis. This parser handles
both v1 (15 columns, pre-2015) and v2.1 (27 columns, 2015+) formats.

The parser converts raw TAB-delimited bytes into _RawGKG dataclass instances.
Complex nested fields (GCAM, themes, locations, etc.) are stored as strings
and parsed into structured objects during Pydantic model conversion.

Security Note:
    The V2EXTRASXML field contains untrusted XML that MUST be parsed using
    defusedxml to prevent XML entity expansion attacks. This parsing happens
    downstream in the Pydantic model layer, not here.
"""

import logging
from collections.abc import Iterator

from py_gdelt.exceptions import ParseError
from py_gdelt.models._internal import _RawGKG


__all__ = ["GKGParser"]

logger = logging.getLogger(__name__)


class GKGParser:
    """Parser for GDELT GKG files (v1/v2.1).

    Handles tab-delimited GKG files, automatically detecting format version
    from column count and parsing records into internal _RawGKG dataclass
    instances.

    The parser is lenient with malformed lines (logs warning and skips) to
    ensure processing continues even with occasional data quality issues.

    Example:
        >>> parser = GKGParser()
        >>> for record in parser.parse(raw_bytes):
        ...     print(record.gkg_record_id, record.document_identifier)
    """

    def detect_version(self, header: bytes) -> int:
        """Detect GKG format version from first line.

        Args:
            header: First line of the GKG file as raw bytes.

        Returns:
            Format version: 1 for v1 (15 columns), 2 for v2.1 (27 columns).

        Raises:
            ParseError: If column count doesn't match v1 (15) or v2.1 (27).
        """
        line = header.decode("utf-8", errors="replace").strip()
        if not line:
            err_msg = "Empty header line, cannot detect GKG version"
            raise ParseError(err_msg)

        column_count = len(line.split("\t"))

        if column_count == 15:
            return 1
        if column_count == 27:
            return 2

        msg = f"Unsupported GKG column count: {column_count} (expected 15 for v1 or 27 for v2.1)"
        raise ParseError(msg)

    def parse(self, data: bytes, is_translated: bool = False) -> Iterator[_RawGKG]:
        """Parse raw bytes into _RawGKG records.

        Args:
            data: Raw GKG file content as bytes (TAB-delimited).
            is_translated: Whether this is a translated document set (indicated
                by "-T" suffix in record IDs). Defaults to False.

        Yields:
            _RawGKG: _RawGKG instances for each valid record.

        Notes:
            - Automatically detects v1 vs v2.1 format from first line
            - Empty fields are converted to None
            - Malformed lines are logged and skipped
            - UTF-8 encoding with replacement for invalid characters
            - Complex delimited fields (themes, locations, etc.) remain as
              strings for downstream parsing
        """
        lines = data.decode("utf-8", errors="replace").strip().split("\n")
        if not lines:
            logger.warning("Empty GKG data provided")
            return

        # Detect version from first line
        version = self.detect_version(lines[0].encode("utf-8"))
        logger.debug("Detected GKG version: %d", version)

        if version == 1:
            yield from self._parse_v1(lines, is_translated)
        else:
            yield from self._parse_v2(lines, is_translated)

    def _parse_v1(self, lines: list[str], is_translated: bool) -> Iterator[_RawGKG]:
        """Parse GKG v1 format (15 columns).

        Args:
            lines: List of text lines from the GKG file.
            is_translated: Whether records are translated.

        Yields:
            _RawGKG: _RawGKG instances with v1-specific field mapping.

        Notes:
            v1 lacks many v2.1 fields (dates, GCAM, social embeds, etc.).
            These are set to empty strings to maintain consistent schema.
        """
        for line_num, raw_line in enumerate(lines, start=1):
            line = raw_line.strip()
            if not line:
                continue

            parts = line.split("\t")
            if len(parts) != 15:
                logger.warning(
                    "Skipping malformed GKG v1 line %d: expected 15 columns, got %d",
                    line_num,
                    len(parts),
                )
                continue

            # Helper to convert empty strings to None
            def field(idx: int, parts: list[str] = parts) -> str | None:
                val = parts[idx].strip()
                return val if val else None

            try:
                yield _RawGKG(
                    gkg_record_id=parts[0],
                    date=parts[1],
                    source_collection_id=field(2) or "",
                    source_common_name=field(3) or "",
                    document_identifier=field(4) or "",
                    counts_v1=field(5) or "",
                    counts_v2="",  # v1 has no v2 counts
                    themes_v1=field(6) or "",
                    themes_v2_enhanced="",  # v1 has no enhanced themes
                    locations_v1=field(7) or "",
                    locations_v2_enhanced="",  # v1 has no enhanced locations
                    persons_v1=field(8) or "",
                    persons_v2_enhanced="",
                    organizations_v1=field(9) or "",
                    organizations_v2_enhanced="",
                    tone=field(10) or "",
                    dates_v2="",  # v1 has no v2 dates
                    gcam="",  # v1 has no GCAM
                    sharing_image=field(11),
                    related_images=field(12),
                    social_image_embeds=None,  # v1 has no social embeds
                    social_video_embeds=None,
                    quotations=field(13),
                    all_names=field(14),
                    amounts=None,  # v1 has no amounts
                    translation_info=None,  # v1 has no translation info
                    extras_xml=None,  # v1 has no extras XML
                    is_translated=is_translated,
                )
            except Exception as e:  # noqa: BLE001
                # Error boundary: log and skip malformed lines
                logger.warning("Error parsing GKG v1 line %d: %s", line_num, e)
                continue

    def _parse_v2(self, lines: list[str], is_translated: bool) -> Iterator[_RawGKG]:
        """Parse GKG v2.1 format (27 columns).

        Args:
            lines: List of text lines from the GKG file.
            is_translated: Whether records are translated (can also be detected
                from "-T" suffix in GKGRECORDID).

        Yields:
            _RawGKG: _RawGKG instances with full v2.1 field mapping.

        Notes:
            - Record ID format: YYYYMMDDHHMMSS-XXXXX or YYYYMMDDHHMMSS-T-XXXXX
            - V2EXTRASXML contains untrusted XML - must use defusedxml downstream
            - Complex fields (GCAM, quotations) use nested delimiters
        """
        for line_num, raw_line in enumerate(lines, start=1):
            line = raw_line.strip()
            if not line:
                continue

            parts = line.split("\t")
            if len(parts) != 27:
                logger.warning(
                    "Skipping malformed GKG v2.1 line %d: expected 27 columns, got %d",
                    line_num,
                    len(parts),
                )
                continue

            # Helper to convert empty strings to None
            def field(idx: int, parts: list[str] = parts) -> str | None:
                val = parts[idx].strip()
                return val if val else None

            try:
                # Detect translation from record ID (ends with -T)
                record_id = parts[0]
                detected_translated = is_translated or record_id.endswith("-T")

                yield _RawGKG(
                    gkg_record_id=record_id,
                    date=parts[1],
                    source_collection_id=field(2) or "",
                    source_common_name=field(3) or "",
                    document_identifier=field(4) or "",
                    counts_v1=field(5) or "",
                    counts_v2=field(6) or "",
                    themes_v1=field(7) or "",
                    themes_v2_enhanced=field(8) or "",
                    locations_v1=field(9) or "",
                    locations_v2_enhanced=field(10) or "",
                    persons_v1=field(11) or "",
                    persons_v2_enhanced=field(12) or "",
                    organizations_v1=field(13) or "",
                    organizations_v2_enhanced=field(14) or "",
                    tone=field(15) or "",
                    dates_v2=field(16) or "",
                    gcam=field(17) or "",
                    sharing_image=field(18),
                    related_images=field(19),
                    social_image_embeds=field(20),
                    social_video_embeds=field(21),
                    quotations=field(22),
                    all_names=field(23),
                    amounts=field(24),
                    translation_info=field(25),
                    extras_xml=field(26),
                    is_translated=detected_translated,
                )
            except Exception as e:  # noqa: BLE001
                # Error boundary: log and skip malformed lines
                logger.warning("Error parsing GKG v2.1 line %d: %s", line_num, e)
                continue
