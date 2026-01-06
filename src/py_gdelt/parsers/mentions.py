"""Parser for GDELT Mentions files.

This module provides parsing for GDELT Mentions v2 files, which track individual
mentions of events across different news sources. Each mention record links to an
event in the Events table via GlobalEventID.

Mentions files are TAB-delimited with 16 columns (v2 only, no v1 format exists).
"""

import logging
from collections.abc import Iterator

from py_gdelt.models._internal import _RawMention


logger = logging.getLogger(__name__)

__all__ = ["MentionsParser"]


class MentionsParser:
    """Parser for GDELT Mentions files.

    Mentions files contain records of individual mentions of events in news articles,
    with metadata about the source, timing, document position, and confidence.

    Format:
        - TAB-delimited (not comma)
        - UTF-8 encoding
        - 16 columns per row
        - Empty fields represented as empty string between tabs
        - No header row
    """

    def parse(self, data: bytes, is_translated: bool = False) -> Iterator[_RawMention]:
        """Parse raw bytes into _RawMention records.

        Decodes UTF-8 data and parses each line into a _RawMention dataclass.
        Malformed lines are logged and skipped to ensure resilience.

        Args:
            data: Raw bytes from GDELT Mentions file (typically from .zip extraction)
            is_translated: Whether the file is from translated feed (not used in v2)

        Yields:
            _RawMention: Parsed mention records with all fields as strings

        Note:
            Empty fields in the TSV become None in the dataclass. Type conversion
            to int/datetime happens when converting to the public Mention model.
        """
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            logger.exception("Failed to decode mentions data as UTF-8")
            return

        for line_num, line in enumerate(text.splitlines(), start=1):
            # Skip empty lines
            if not line.strip():
                continue

            parts = line.split("\t")

            # Validate expected column count
            if len(parts) != 16:
                logger.warning(
                    "Malformed mention at line %d: expected 16 columns, got %d - skipping",
                    line_num,
                    len(parts),
                )
                continue

            # Extract fields - convert empty strings to None
            def field(idx: int, parts: list[str] = parts) -> str | None:
                """Extract field at index, returning None for empty strings."""
                val = parts[idx].strip()
                return val if val else None

            try:
                # According to GDELT v2 Mentions spec, columns 1 and 2 contain YYYYMMDDHHMMSS format
                # The _RawMention dataclass separates date (YYYYMMDD) and full (YYYYMMDDHHMMSS)
                # Since the file only has full timestamps, we extract date from the first 8 chars
                event_time_full = parts[1].strip()
                mention_time_full = parts[2].strip()

                # Extract date portions (YYYYMMDD from YYYYMMDDHHMMSS)
                event_time_date = event_time_full[:8] if event_time_full else ""
                mention_time_date = mention_time_full[:8] if mention_time_full else ""

                yield _RawMention(
                    global_event_id=parts[0].strip(),
                    event_time_date=event_time_date,
                    event_time_full=event_time_full,
                    mention_time_date=mention_time_date,
                    mention_time_full=mention_time_full,
                    mention_type=parts[3].strip(),
                    mention_source_name=parts[4].strip(),
                    mention_identifier=parts[5].strip(),
                    sentence_id=parts[6].strip(),
                    actor1_char_offset=parts[7].strip(),
                    actor2_char_offset=parts[8].strip(),
                    action_char_offset=parts[9].strip(),
                    in_raw_text=parts[10].strip(),
                    confidence=parts[11].strip(),
                    mention_doc_length=parts[12].strip(),
                    mention_doc_tone=parts[13].strip(),
                    mention_doc_translation_info=field(14),
                    extras=field(15),
                )

            except (ValueError, IndexError) as e:
                logger.warning(
                    "Failed to parse mention at line %d: %s - skipping",
                    line_num,
                    e,
                )
                continue
