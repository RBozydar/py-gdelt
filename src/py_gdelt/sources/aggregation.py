"""Aggregation types for BigQuery aggregate queries.

This module provides the data types needed for building BigQuery aggregation
queries against GDELT tables. It includes:

- **AggFunc**: Supported aggregation functions (COUNT, SUM, AVG, etc.)
- **Aggregation**: Specification for a single aggregation column
- **AggregationResult**: Container for aggregation query results
- **GKGUnnestField**: GKG fields that require UNNEST(SPLIT(...)) for aggregation

Example:
    >>> from py_gdelt.sources.aggregation import AggFunc, Aggregation
    >>> agg = Aggregation(func=AggFunc.COUNT, column="*", alias="event_count")
    >>> agg = Aggregation(func=AggFunc.AVG, column="AvgTone", alias="mean_tone")
"""

from __future__ import annotations

import re
from enum import StrEnum
from typing import Any, Final

from pydantic import BaseModel, model_validator


class AggFunc(StrEnum):
    """BigQuery aggregation functions.

    Each member maps directly to a SQL aggregation function. COUNT_DISTINCT
    is rendered as ``COUNT(DISTINCT column)``.
    """

    COUNT = "COUNT"
    SUM = "SUM"
    AVG = "AVG"
    MIN = "MIN"
    MAX = "MAX"
    COUNT_DISTINCT = "COUNT_DISTINCT"


class Aggregation(BaseModel):
    """Single aggregation specification.

    Args:
        func: Aggregation function to apply.
        column: Column to aggregate. Use ``"*"`` only with COUNT.
        alias: Output column name. Auto-generated if None.
    """

    func: AggFunc
    column: str = "*"
    alias: str | None = None

    @model_validator(mode="after")
    def _validate_star_only_with_count(self) -> Aggregation:
        """Ensure ``column='*'`` is only used with COUNT."""
        if self.column == "*" and self.func != AggFunc.COUNT:
            msg = "column='*' is only valid with AggFunc.COUNT"
            raise ValueError(msg)
        return self


class GKGUnnestField(StrEnum):
    """GKG fields that require UNNEST(SPLIT(...)) for aggregation.

    These fields are semicolon-delimited in BigQuery and must be unnested
    before they can be grouped on. Each entry within the delimited list
    is itself comma-delimited, where the first element is the name.
    """

    THEMES = "themes"
    PERSONS = "persons"
    ORGANIZATIONS = "organizations"


# Maps GKGUnnestField -> (BQ column, SPLIT expression for extracting the name)
GKG_UNNEST_CONFIG: Final[dict[GKGUnnestField, tuple[str, str]]] = {
    GKGUnnestField.THEMES: ("V2Themes", "SPLIT(item, ',')[SAFE_OFFSET(0)]"),
    GKGUnnestField.PERSONS: ("V2Persons", "SPLIT(item, ',')[SAFE_OFFSET(0)]"),
    GKGUnnestField.ORGANIZATIONS: ("V2Organizations", "SPLIT(item, ',')[SAFE_OFFSET(0)]"),
}

# Regex for validating alias names (alphanumeric + underscore only)
_ALIAS_PATTERN: Final[re.Pattern[str]] = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


class AggregationResult(BaseModel):
    """Result of an aggregation query.

    Args:
        rows: Result rows as list of dicts.
        group_by: Column names used for grouping.
        total_rows: Number of result rows.
        bytes_processed: Bytes scanned by BigQuery (for cost tracking).
    """

    rows: list[dict[str, Any]]
    group_by: list[str]
    total_rows: int
    bytes_processed: int | None = None
