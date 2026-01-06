"""
Parser for GDELT Events files (v1 and v2).

This module provides the EventsParser class for parsing TAB-delimited GDELT Events
files into internal _RawEvent dataclasses. The parser automatically detects the
format version (v1 with 57 columns or v2 with 61 columns) and handles differences
in column positions between versions.

Key features:
- Automatic version detection (v1: 57 columns, v2: 61 columns)
- TAB delimiter handling (despite .CSV file extension)
- CAMEO code preservation (keeps leading zeros as strings)
- UTF-8 encoding support
- Graceful error handling for malformed lines

Column mapping reference:
- v2 (61 columns): Full feature set with DATEADDED timestamp and SOURCEURL
- v1 (57 columns): Legacy format with some fields in different positions
"""

import csv
import io
import logging
from collections.abc import Iterator
from typing import ClassVar

from py_gdelt.exceptions import ParseError
from py_gdelt.models._internal import _RawEvent


__all__ = ["EventsParser"]

logger = logging.getLogger(__name__)


class EventsParser:
    """
    Parser for GDELT Events files (v1/v2).

    This parser handles both GDELT Events v1 (57 columns) and v2 (61 columns)
    formats, automatically detecting the version from the column count and
    mapping columns appropriately.

    Attributes:
        V2_COLUMNS: Column name to index mapping for v2 format (61 columns)
        V1_COLUMNS: Column name to index mapping for v1 format (57 columns)

    Example:
        >>> parser = EventsParser()
        >>> data = b"123\\t20240101\\t..."  # Raw event data
        >>> for event in parser.parse(data, is_translated=False):
        ...     print(event.global_event_id)
    """

    # Column indices for v2 (61 columns) - the canonical format
    V2_COLUMNS: ClassVar[dict[str, int]] = {
        "GLOBALEVENTID": 0,
        "SQLDATE": 1,
        "MonthYear": 2,
        "Year": 3,
        "FractionDate": 4,
        # Actor1 fields (5-14)
        "Actor1Code": 5,
        "Actor1Name": 6,
        "Actor1CountryCode": 7,
        "Actor1KnownGroupCode": 8,
        "Actor1EthnicCode": 9,
        "Actor1Religion1Code": 10,
        "Actor1Religion2Code": 11,
        "Actor1Type1Code": 12,
        "Actor1Type2Code": 13,
        "Actor1Type3Code": 14,
        # Actor2 fields (15-24)
        "Actor2Code": 15,
        "Actor2Name": 16,
        "Actor2CountryCode": 17,
        "Actor2KnownGroupCode": 18,
        "Actor2EthnicCode": 19,
        "Actor2Religion1Code": 20,
        "Actor2Religion2Code": 21,
        "Actor2Type1Code": 22,
        "Actor2Type2Code": 23,
        "Actor2Type3Code": 24,
        # Event fields (25-34)
        "IsRootEvent": 25,
        "EventCode": 26,
        "EventBaseCode": 27,
        "EventRootCode": 28,
        "QuadClass": 29,
        "GoldsteinScale": 30,
        "NumMentions": 31,
        "NumSources": 32,
        "NumArticles": 33,
        "AvgTone": 34,
        # Actor1Geo fields (35-42)
        "Actor1Geo_Type": 35,
        "Actor1Geo_Fullname": 36,
        "Actor1Geo_CountryCode": 37,
        "Actor1Geo_ADM1Code": 38,
        "Actor1Geo_ADM2Code": 39,
        "Actor1Geo_Lat": 40,
        "Actor1Geo_Long": 41,
        "Actor1Geo_FeatureID": 42,
        # Actor2Geo fields (43-50)
        "Actor2Geo_Type": 43,
        "Actor2Geo_Fullname": 44,
        "Actor2Geo_CountryCode": 45,
        "Actor2Geo_ADM1Code": 46,
        "Actor2Geo_ADM2Code": 47,
        "Actor2Geo_Lat": 48,
        "Actor2Geo_Long": 49,
        "Actor2Geo_FeatureID": 50,
        # ActionGeo fields (51-58)
        "ActionGeo_Type": 51,
        "ActionGeo_Fullname": 52,
        "ActionGeo_CountryCode": 53,
        "ActionGeo_ADM1Code": 54,
        "ActionGeo_ADM2Code": 55,
        "ActionGeo_Lat": 56,
        "ActionGeo_Long": 57,
        "ActionGeo_FeatureID": 58,
        # Metadata columns start at 59
        "DATEADDED": 59,
        "SOURCEURL": 60,
    }

    # Column indices for v1 (57 columns, 0-56)
    # Main differences from v2:
    # - v1 ends at column 56 (57 total: 0-56)
    # - v2 ends at column 60 (61 total: 0-60)
    # - Difference is 4 columns: v1 lacks DATEADDED (59) and SOURCEURL (60)
    # - v1 also lacks FeatureID fields for all three Geo sections (3 fields)
    # - That accounts for 3 columns, but we need 4... checking actual format
    # - For now, implementing based on specification: 57 vs 61 columns
    V1_COLUMNS: ClassVar[dict[str, int]] = {
        "GLOBALEVENTID": 0,
        "SQLDATE": 1,
        "MonthYear": 2,
        "Year": 3,
        "FractionDate": 4,
        # Actor1 fields (5-14)
        "Actor1Code": 5,
        "Actor1Name": 6,
        "Actor1CountryCode": 7,
        "Actor1KnownGroupCode": 8,
        "Actor1EthnicCode": 9,
        "Actor1Religion1Code": 10,
        "Actor1Religion2Code": 11,
        "Actor1Type1Code": 12,
        "Actor1Type2Code": 13,
        "Actor1Type3Code": 14,
        # Actor2 fields (15-24)
        "Actor2Code": 15,
        "Actor2Name": 16,
        "Actor2CountryCode": 17,
        "Actor2KnownGroupCode": 18,
        "Actor2EthnicCode": 19,
        "Actor2Religion1Code": 20,
        "Actor2Religion2Code": 21,
        "Actor2Type1Code": 22,
        "Actor2Type2Code": 23,
        "Actor2Type3Code": 24,
        # Event fields (25-34)
        "IsRootEvent": 25,
        "EventCode": 26,
        "EventBaseCode": 27,
        "EventRootCode": 28,
        "QuadClass": 29,
        "GoldsteinScale": 30,
        "NumMentions": 31,
        "NumSources": 32,
        "NumArticles": 33,
        "AvgTone": 34,
        # Actor1Geo fields (35-41) - no FeatureID in v1
        "Actor1Geo_Type": 35,
        "Actor1Geo_Fullname": 36,
        "Actor1Geo_CountryCode": 37,
        "Actor1Geo_ADM1Code": 38,
        "Actor1Geo_ADM2Code": 39,
        "Actor1Geo_Lat": 40,
        "Actor1Geo_Long": 41,
        # Actor2Geo fields (42-48) - no FeatureID in v1
        "Actor2Geo_Type": 42,
        "Actor2Geo_Fullname": 43,
        "Actor2Geo_CountryCode": 44,
        "Actor2Geo_ADM1Code": 45,
        "Actor2Geo_ADM2Code": 46,
        "Actor2Geo_Lat": 47,
        "Actor2Geo_Long": 48,
        # ActionGeo fields (49-55) - no FeatureID in v1
        "ActionGeo_Type": 49,
        "ActionGeo_Fullname": 50,
        "ActionGeo_CountryCode": 51,
        "ActionGeo_ADM1Code": 52,
        "ActionGeo_ADM2Code": 53,
        "ActionGeo_Lat": 54,
        "ActionGeo_Long": 55,
        # v1 ends at column 56 with DATEADDED (YYYYMMDD format)
        "DATEADDED": 56,
        # No SOURCEURL in v1
    }

    def detect_version(self, header: bytes) -> int:
        """
        Detect format version from first line.

        Args:
            header: First line of the file (raw bytes)

        Returns:
            Version number (1 or 2)

        Raises:
            ParseError: If version cannot be detected or format is invalid
        """
        try:
            # Decode and count TAB-delimited columns
            line = header.decode("utf-8").strip()
            column_count = len(line.split("\t"))

            if column_count == 61:
                return 2
            if column_count == 57:
                return 1

            msg = (
                f"Invalid GDELT Events format: expected 57 (v1) or 61 (v2) "
                f"columns, found {column_count}"
            )
            raise ParseError(msg, raw_data=line[:200])

        except UnicodeDecodeError as e:
            err_msg = f"Failed to decode header as UTF-8: {e}"
            raise ParseError(err_msg) from e

    def parse(self, data: bytes, is_translated: bool = False) -> Iterator[_RawEvent]:
        """
        Parse raw bytes into _RawEvent records.

        This method automatically detects the GDELT Events version (v1 or v2)
        from the column count and parses accordingly. Empty fields are converted
        to None. Malformed lines are logged and skipped.

        Args:
            data: Raw file content as bytes (TAB-delimited)
            is_translated: Whether this is from the translated feed

        Yields:
            _RawEvent: _RawEvent instances for each valid row

        Raises:
            ParseError: If the file format is completely invalid or unreadable
        """
        if not data:
            return

        try:
            # Decode to string
            text = data.decode("utf-8")
        except UnicodeDecodeError as e:
            err_msg = f"Failed to decode data as UTF-8: {e}"
            raise ParseError(err_msg) from e

        # Detect version from first line
        lines = text.split("\n", 1)
        if not lines or not lines[0].strip():
            return

        version = self.detect_version(lines[0].encode("utf-8"))
        column_map = self.V2_COLUMNS if version == 2 else self.V1_COLUMNS

        logger.info("Parsing GDELT Events v%d file", version)

        # Parse using csv module for proper TAB handling
        reader = csv.reader(io.StringIO(text), delimiter="\t")

        for line_num, row in enumerate(reader, start=1):
            if not row or not row[0].strip():
                # Skip empty lines
                continue

            try:
                event = self._parse_row(row, column_map, is_translated, version)
                yield event
            except Exception as e:  # noqa: BLE001
                # Error boundary: log and skip malformed lines, continue processing
                logger.warning(
                    "Skipping malformed line %d: %s",
                    line_num,
                    str(e),
                    exc_info=True,
                )
                continue

    def _parse_row(
        self,
        row: list[str],
        column_map: dict[str, int],
        is_translated: bool,
        version: int,
    ) -> _RawEvent:
        """
        Parse a single row into a _RawEvent.

        Args:
            row: List of column values
            column_map: Column name to index mapping
            is_translated: Whether this is from the translated feed
            version: GDELT version (1 or 2)

        Returns:
            Populated _RawEvent instance

        Raises:
            ValueError: If required fields are missing or invalid
        """

        # Helper to get value or None for empty strings
        def get(column_name: str) -> str | None:
            idx = column_map.get(column_name)
            if idx is None or idx >= len(row):
                return None
            value = row[idx].strip()
            return value if value else None

        # Helper to get required value
        def get_required(column_name: str) -> str:
            value = get(column_name)
            if value is None:
                msg = f"Required field '{column_name}' is missing or empty"
                raise ValueError(msg)
            return value

        # Build _RawEvent
        # Note: For v1, SOURCEURL doesn't exist, so it will be None
        return _RawEvent(
            # Event identification (required)
            global_event_id=get_required("GLOBALEVENTID"),
            sql_date=get_required("SQLDATE"),
            month_year=get_required("MonthYear"),
            year=get_required("Year"),
            fraction_date=get_required("FractionDate"),
            # Actor1 attributes
            actor1_code=get("Actor1Code"),
            actor1_name=get("Actor1Name"),
            actor1_country_code=get("Actor1CountryCode"),
            actor1_known_group_code=get("Actor1KnownGroupCode"),
            actor1_ethnic_code=get("Actor1EthnicCode"),
            actor1_religion1_code=get("Actor1Religion1Code"),
            actor1_religion2_code=get("Actor1Religion2Code"),
            actor1_type1_code=get("Actor1Type1Code"),
            actor1_type2_code=get("Actor1Type2Code"),
            actor1_type3_code=get("Actor1Type3Code"),
            # Actor2 attributes
            actor2_code=get("Actor2Code"),
            actor2_name=get("Actor2Name"),
            actor2_country_code=get("Actor2CountryCode"),
            actor2_known_group_code=get("Actor2KnownGroupCode"),
            actor2_ethnic_code=get("Actor2EthnicCode"),
            actor2_religion1_code=get("Actor2Religion1Code"),
            actor2_religion2_code=get("Actor2Religion2Code"),
            actor2_type1_code=get("Actor2Type1Code"),
            actor2_type2_code=get("Actor2Type2Code"),
            actor2_type3_code=get("Actor2Type3Code"),
            # Event attributes (required)
            is_root_event=get_required("IsRootEvent"),
            event_code=get_required("EventCode"),
            event_base_code=get_required("EventBaseCode"),
            event_root_code=get_required("EventRootCode"),
            quad_class=get_required("QuadClass"),
            goldstein_scale=get_required("GoldsteinScale"),
            num_mentions=get_required("NumMentions"),
            num_sources=get_required("NumSources"),
            num_articles=get_required("NumArticles"),
            avg_tone=get_required("AvgTone"),
            # Actor1 Geography
            actor1_geo_type=get("Actor1Geo_Type"),
            actor1_geo_fullname=get("Actor1Geo_Fullname"),
            actor1_geo_country_code=get("Actor1Geo_CountryCode"),
            actor1_geo_adm1_code=get("Actor1Geo_ADM1Code"),
            actor1_geo_adm2_code=get("Actor1Geo_ADM2Code"),
            actor1_geo_lat=get("Actor1Geo_Lat"),
            actor1_geo_lon=get("Actor1Geo_Long"),
            actor1_geo_feature_id=get("Actor1Geo_FeatureID"),
            # Actor2 Geography
            actor2_geo_type=get("Actor2Geo_Type"),
            actor2_geo_fullname=get("Actor2Geo_Fullname"),
            actor2_geo_country_code=get("Actor2Geo_CountryCode"),
            actor2_geo_adm1_code=get("Actor2Geo_ADM1Code"),
            actor2_geo_adm2_code=get("Actor2Geo_ADM2Code"),
            actor2_geo_lat=get("Actor2Geo_Lat"),
            actor2_geo_lon=get("Actor2Geo_Long"),
            actor2_geo_feature_id=get("Actor2Geo_FeatureID"),
            # Action Geography
            action_geo_type=get("ActionGeo_Type"),
            action_geo_fullname=get("ActionGeo_Fullname"),
            action_geo_country_code=get("ActionGeo_CountryCode"),
            action_geo_adm1_code=get("ActionGeo_ADM1Code"),
            action_geo_adm2_code=get("ActionGeo_ADM2Code"),
            action_geo_lat=get("ActionGeo_Lat"),
            action_geo_lon=get("ActionGeo_Long"),
            action_geo_feature_id=get("ActionGeo_FeatureID"),
            # Metadata fields
            date_added=get_required("DATEADDED"),
            source_url=get("SOURCEURL") if version == 2 else None,
            is_translated=is_translated,
        )
