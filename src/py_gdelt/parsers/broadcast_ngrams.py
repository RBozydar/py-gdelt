"""Parser for GDELT Broadcast NGrams files (TV and Radio).

Broadcast NGrams provides word and phrase frequency data from TV and Radio transcripts.
This parser handles both TV NGrams (5 columns) and Radio NGrams (6 columns) formats,
unifying them into a single dataclass structure.

TV NGrams: DATE, STATION, HOUR, WORD, COUNT
Radio NGrams: DATE, STATION, HOUR, NGRAM, COUNT, SHOW

The parser converts raw TAB-delimited bytes into _RawBroadcastNGram dataclass instances.
"""

import logging
from collections.abc import Iterator

from py_gdelt.models._internal import _RawBroadcastNGram


__all__ = ["BroadcastNGramsParser"]

logger = logging.getLogger(__name__)


class BroadcastNGramsParser:
    """Parser for GDELT Broadcast NGrams files (TV and Radio).

    Handles tab-delimited broadcast NGrams files, automatically detecting format
    from column count (5 for TV, 6 for Radio) and parsing records into internal
    _RawBroadcastNGram dataclass instances.

    The parser is lenient with malformed lines (logs warning and skips) to
    ensure processing continues even with occasional data quality issues.

    Example:
        >>> parser = BroadcastNGramsParser()
        >>> for record in parser.parse(raw_bytes):
        ...     print(record.date, record.station, record.ngram, record.count)
    """

    def parse(self, data: bytes) -> Iterator[_RawBroadcastNGram]:
        """Parse raw bytes into _RawBroadcastNGram records.

        Args:
            data: Raw broadcast NGrams file content as bytes (TAB-delimited).

        Yields:
            _RawBroadcastNGram: Parsed broadcast ngram records.

        Notes:
            - Automatically detects TV (5 columns) vs Radio (6 columns) format
            - Empty fields are converted to empty strings
            - Malformed lines are logged and skipped
            - UTF-8 encoding with replacement for invalid characters
        """
        lines = data.decode("utf-8", errors="replace").strip().split("\n")
        if not lines:
            logger.warning("Empty broadcast NGrams data provided")
            return

        for line_num, raw_line in enumerate(lines, start=1):
            line = raw_line.strip()
            if not line:
                continue

            parts = line.split("\t")
            column_count = len(parts)

            # TV NGrams: 5 columns (DATE, STATION, HOUR, WORD, COUNT)
            # Radio NGrams: 6 columns (DATE, STATION, HOUR, NGRAM, COUNT, SHOW)
            if column_count not in {5, 6}:
                logger.warning(
                    "Skipping malformed broadcast NGrams line %d: expected 5 (TV) or 6 (Radio) columns, got %d",
                    line_num,
                    column_count,
                )
                continue

            try:
                # Common fields for both TV and Radio
                date = parts[0].strip()
                station = parts[1].strip()
                hour = parts[2].strip()
                ngram = parts[3].strip()
                count = parts[4].strip()

                # Radio has an extra SHOW column
                show = parts[5].strip() if column_count == 6 else ""

                yield _RawBroadcastNGram(
                    date=date,
                    station=station,
                    hour=hour,
                    ngram=ngram,
                    count=count,
                    show=show,
                )
            except Exception as e:  # noqa: BLE001
                # Error boundary: log and skip malformed lines
                logger.warning(
                    "Error parsing broadcast NGrams line %d: %s",
                    line_num,
                    e,
                )
                continue
