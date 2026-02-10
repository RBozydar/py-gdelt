"""Result models for analytics queries.

Each result type is a standalone Pydantic BaseModel carrying query results,
metadata, and the generated SQL for debugging.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from py_gdelt.sources.metadata import QueryMetadata  # noqa: TC001 - Pydantic needs runtime access


__all__ = [
    "ComparisonResult",
    "DyadResult",
    "ExtremeEventsResult",
    "PartitionedTopNResult",
    "TimeSeriesResult",
    "TrendResult",
]


class TimeSeriesResult(BaseModel):
    """Result of a time-series analytics query.

    Args:
        buckets: Time buckets with metric values. Keys: ``"bucket"`` (ISO date),
            one key per metric, optional ``"{metric}_ma{window}"`` for moving averages.
        granularity: Time bucketing granularity used.
        metrics: Metric names included in each bucket.
        moving_average_window: Window size if moving averages were computed.
        meta: Query metadata from BigQuery.
        sql: Generated SQL for debugging.
    """

    buckets: list[dict[str, Any]]
    granularity: str
    metrics: list[str]
    moving_average_window: int | None = None
    meta: QueryMetadata | None = None
    sql: str | None = None

    def to_compact(self) -> str:
        """Return a brief one-line summary suitable for LLM consumption.

        Returns:
            str: Compact summary string.
        """
        return (
            f"{len(self.buckets)} buckets ({self.granularity}), metrics: {', '.join(self.metrics)}"
        )

    def __str__(self) -> str:
        """Return compact string representation.

        Returns:
            str: Compact summary string.
        """
        return self.to_compact()


class ExtremeEventsResult(BaseModel):
    """Result of an extremes analytics query.

    Args:
        most_negative: Event rows with lowest criterion values.
        most_positive: Event rows with highest criterion values.
        criterion: Column used to rank events.
        requested_negative: Number of negative extremes requested.
        requested_positive: Number of positive extremes requested.
        meta: Query metadata from BigQuery.
        sql: Generated SQL for debugging.
    """

    most_negative: list[dict[str, Any]]
    most_positive: list[dict[str, Any]]
    criterion: str
    requested_negative: int
    requested_positive: int
    meta: QueryMetadata | None = None
    sql: str | None = None

    def to_compact(self) -> str:
        """Return a brief one-line summary suitable for LLM consumption.

        Returns:
            str: Compact summary string.
        """
        return (
            f"{len(self.most_negative)} negative, "
            f"{len(self.most_positive)} positive extremes by {self.criterion}"
        )

    def __str__(self) -> str:
        """Return compact string representation.

        Returns:
            str: Compact summary string.
        """
        return self.to_compact()


class ComparisonResult(BaseModel):
    """Result of a comparison analytics query.

    Args:
        rows: Time buckets with per-value metric columns.
        compare_by: Column used to compare (e.g., Actor1CountryCode).
        values: Values being compared.
        metric: Metric computed for each value.
        granularity: Time bucketing granularity used.
        meta: Query metadata from BigQuery.
        sql: Generated SQL for debugging.
    """

    rows: list[dict[str, Any]]
    compare_by: str
    values: list[str]
    metric: str
    granularity: str
    meta: QueryMetadata | None = None
    sql: str | None = None

    def to_compact(self) -> str:
        """Return a brief one-line summary suitable for LLM consumption.

        Returns:
            str: Compact summary string.
        """
        return (
            f"Comparing {', '.join(self.values)} by {self.compare_by} "
            f"({len(self.rows)} buckets, {self.metric})"
        )

    def __str__(self) -> str:
        """Return compact string representation.

        Returns:
            str: Compact summary string.
        """
        return self.to_compact()


class TrendResult(BaseModel):
    """Result of a trend detection analytics query.

    Args:
        slope: Linear regression slope (metric units per time unit).
        r_squared: Coefficient of determination (0-1).
        direction: Trend direction: ``"escalating"``, ``"de-escalating"``, or ``"stable"``.
        p_value: Approximate p-value, or None if insufficient data.
        data_points: Number of time buckets used for regression.
        metric: Metric analyzed.
        granularity: Time bucketing granularity used.
        meta: Query metadata from BigQuery.
        sql: Generated SQL for debugging.
    """

    slope: float
    r_squared: float
    direction: str
    p_value: float | None = None
    data_points: int = 0
    metric: str = ""
    granularity: str = ""
    meta: QueryMetadata | None = None
    sql: str | None = None

    def to_compact(self) -> str:
        """Return a brief one-line summary suitable for LLM consumption.

        Returns:
            str: Compact summary string.
        """
        return (
            f"{self.direction} (slope={self.slope:.4f}, "
            f"R\u00b2={self.r_squared:.3f}, n={self.data_points})"
        )

    def __str__(self) -> str:
        """Return compact string representation.

        Returns:
            str: Compact summary string.
        """
        return self.to_compact()


class DyadResult(BaseModel):
    """Result of a dyadic (actor pair) analytics query.

    Args:
        a_to_b: Time-series buckets for Actor1=a, Actor2=b direction.
        b_to_a: Time-series buckets for Actor1=b, Actor2=a direction.
        actor_a: First actor code.
        actor_b: Second actor code.
        granularity: Time bucketing granularity used.
        metrics: Metric names included in each bucket.
        meta: Query metadata from BigQuery.
        sql: Generated SQL for debugging.
    """

    a_to_b: list[dict[str, Any]]
    b_to_a: list[dict[str, Any]]
    actor_a: str
    actor_b: str
    granularity: str
    metrics: list[str]
    meta: QueryMetadata | None = None
    sql: str | None = None

    def to_compact(self) -> str:
        """Return a brief one-line summary suitable for LLM consumption.

        Returns:
            str: Compact summary string.
        """
        return (
            f"{self.actor_a}\u2192{self.actor_b}: {len(self.a_to_b)} buckets, "
            f"{self.actor_b}\u2192{self.actor_a}: {len(self.b_to_a)} buckets"
        )

    def __str__(self) -> str:
        """Return compact string representation.

        Returns:
            str: Compact summary string.
        """
        return self.to_compact()


class PartitionedTopNResult(BaseModel):
    """Result of a top-N per group analytics query.

    Args:
        groups: Mapping from group key to top-N rows for that group.
        partition_by: Column used to partition groups.
        order_by: Column used to rank within each group.
        n: Maximum items per group.
        ascending: Whether ranking is ascending.
        meta: Query metadata from BigQuery.
        sql: Generated SQL for debugging.
    """

    groups: dict[str, list[dict[str, Any]]]
    partition_by: str
    order_by: str
    n: int
    ascending: bool = False
    meta: QueryMetadata | None = None
    sql: str | None = None

    def to_compact(self) -> str:
        """Return a brief one-line summary suitable for LLM consumption.

        Returns:
            str: Compact summary string.
        """
        return f"{len(self.groups)} groups, top {self.n} by {self.order_by} per {self.partition_by}"

    def __str__(self) -> str:
        """Return compact string representation.

        Returns:
            str: Compact summary string.
        """
        return self.to_compact()
