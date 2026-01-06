"""Parser for GDELT NGrams 3.0 JSON files.

This module provides parsing functionality for GDELT NGrams 3.0 data, which tracks
word and phrase occurrences across global news coverage with contextual information.

NGrams 3.0 files are newline-delimited JSON (NDJSON/JSON Lines format), where each
line is a JSON object representing a single n-gram occurrence. The parser converts
these JSON objects into _RawNGram dataclass instances for further processing.

Example JSON line:
{
  "date": "2024-01-15T10:30:00Z",
  "ngram": "climate change",
  "lang": "en",
  "type": 1,
  "pos": 20,
  "pre": "scientists warn about",
  "post": "impacts on global",
  "url": "https://example.com/article"
}
"""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

from py_gdelt.models._internal import _RawNGram


if TYPE_CHECKING:
    from collections.abc import Iterator

__all__ = ["NGramsParser"]

logger = logging.getLogger(__name__)


class NGramsParser:
    """Parser for GDELT NGrams 3.0 JSON files.

    Parses newline-delimited JSON (NDJSON) files containing n-gram occurrences
    from GDELT NGrams 3.0 dataset. Each line is a JSON object that gets converted
    to a _RawNGram dataclass instance.

    The parser handles:
    - Newline-delimited JSON (NDJSON/JSON Lines format)
    - Malformed JSON lines (logs warning and skips)
    - Type conversion of all values to strings
    - Missing optional fields

    Note:
        The parser receives decompressed bytes. Gzip decompression is handled
        by the FileSource before data reaches the parser.
    """

    def parse(self, data: bytes) -> Iterator[_RawNGram]:
        """Parse raw bytes containing NDJSON into _RawNGram records.

        Args:
            data: Raw bytes containing newline-delimited JSON. May be the result
                of gzip decompression, but decompression happens upstream.

        Yields:
            _RawNGram: _RawNGram instances, one per valid JSON line.

        Note:
            Malformed JSON lines are logged as warnings and skipped. The parser
            continues processing subsequent lines to maximize data recovery.
        """
        # Decode bytes to string
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            logger.exception("Failed to decode NGrams data as UTF-8")
            return

        # Process each line
        for line_num, raw_line in enumerate(text.splitlines(), start=1):
            # Skip empty lines
            line = raw_line.strip()
            if not line:
                continue

            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                logger.warning(
                    "Skipping malformed JSON at line %d: %s - Line content: %s",
                    line_num,
                    e,
                    line[:100],  # Log first 100 chars for debugging
                )
                continue

            # Map JSON fields to _RawNGram fields, converting all to strings
            try:
                raw_ngram = _RawNGram(
                    date=str(obj.get("date", "")),
                    ngram=str(obj.get("ngram", "")),
                    language=str(obj.get("lang", "")),
                    segment_type=str(obj.get("type", "")),
                    position=str(obj.get("pos", "")),
                    pre_context=str(obj.get("pre", "")),
                    post_context=str(obj.get("post", "")),
                    url=str(obj.get("url", "")),
                )
                yield raw_ngram
            except Exception as e:  # noqa: BLE001
                # Error boundary: log and skip malformed records
                logger.warning(
                    "Failed to create _RawNGram from line %d: %s - Data: %s",
                    line_num,
                    e,
                    obj,
                )
                continue
