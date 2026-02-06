"""Predefined column subsets for GDELT BigQuery queries.

Column profiles reduce BigQuery scan costs by selecting only needed columns.
BigQuery is columnar -- you only pay for columns you SELECT.

Example:
    >>> from py_gdelt.sources.columns import EventColumns
    >>> # Use CORE profile for ~75% cost reduction
    >>> async for row in client.events.stream(f, columns=EventColumns.CORE, use_bigquery=True):
    ...     print(row["GLOBALEVENTID"])
"""

from __future__ import annotations

from typing import Final


class EventColumns:
    """Predefined column subsets for GDELT Events BigQuery queries.

    Each attribute is a frozenset of BigQuery column names that can be passed
    to ``columns`` parameter of endpoint query/stream methods.
    """

    CORE: Final[frozenset[str]] = frozenset(
        {
            "GLOBALEVENTID",
            "SQLDATE",
            "Actor1Name",
            "Actor1CountryCode",
            "Actor2Name",
            "Actor2CountryCode",
            "IsRootEvent",
            "EventCode",
            "EventRootCode",
            "QuadClass",
            "GoldsteinScale",
            "NumMentions",
            "AvgTone",
            "ActionGeo_CountryCode",
            "SOURCEURL",
        }
    )

    ACTORS: Final[frozenset[str]] = frozenset(
        {
            "GLOBALEVENTID",
            "SQLDATE",
            "Actor1Code",
            "Actor1Name",
            "Actor1CountryCode",
            "Actor1KnownGroupCode",
            "Actor1Type1Code",
            "Actor2Code",
            "Actor2Name",
            "Actor2CountryCode",
            "Actor2KnownGroupCode",
            "Actor2Type1Code",
        }
    )

    GEOGRAPHY: Final[frozenset[str]] = frozenset(
        {
            "GLOBALEVENTID",
            "SQLDATE",
            "Actor1Geo_Type",
            "Actor1Geo_FullName",
            "Actor1Geo_CountryCode",
            "Actor1Geo_Lat",
            "Actor1Geo_Long",
            "Actor2Geo_Type",
            "Actor2Geo_FullName",
            "Actor2Geo_CountryCode",
            "Actor2Geo_Lat",
            "Actor2Geo_Long",
            "ActionGeo_Type",
            "ActionGeo_FullName",
            "ActionGeo_CountryCode",
            "ActionGeo_Lat",
            "ActionGeo_Long",
        }
    )

    METRICS: Final[frozenset[str]] = frozenset(
        {
            "GLOBALEVENTID",
            "SQLDATE",
            "EventCode",
            "EventRootCode",
            "QuadClass",
            "GoldsteinScale",
            "NumMentions",
            "NumSources",
            "NumArticles",
            "AvgTone",
        }
    )


class GKGColumns:
    """Predefined column subsets for GDELT GKG BigQuery queries.

    Each attribute is a frozenset of BigQuery column names that can be passed
    to ``columns`` parameter of endpoint query/stream methods.
    """

    CORE: Final[frozenset[str]] = frozenset(
        {
            "GKGRECORDID",
            "DATE",
            "V2Themes",
            "V2Persons",
            "V2Organizations",
            "V2Tone",
            "V2Locations",
            "DocumentIdentifier",
        }
    )

    ENTITIES: Final[frozenset[str]] = frozenset(
        {
            "GKGRECORDID",
            "DATE",
            "DocumentIdentifier",
            "V2Persons",
            "V2Organizations",
            "AllNames",
        }
    )

    FULL_TEXT: Final[frozenset[str]] = frozenset(
        {
            "GKGRECORDID",
            "DATE",
            "SourceCommonName",
            "DocumentIdentifier",
            "V2Themes",
            "V2Persons",
            "V2Organizations",
            "V2Tone",
            "V2Locations",
            "Quotations",
            "AllNames",
            "Amounts",
        }
    )


class MentionColumns:
    """Predefined column subsets for GDELT Mentions BigQuery queries.

    Each attribute is a frozenset of BigQuery column names that can be passed
    to ``columns`` parameter of endpoint query/stream methods.
    """

    CORE: Final[frozenset[str]] = frozenset(
        {
            "GLOBALEVENTID",
            "MentionTimeDate",
            "MentionSourceName",
            "MentionIdentifier",
            "Confidence",
            "MentionDocTone",
        }
    )
