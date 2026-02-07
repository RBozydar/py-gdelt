"""BigQuery query metadata and cost estimation models.

This module provides Pydantic models for capturing metadata from BigQuery
query execution and pre-execution cost estimates via dry runs:

- **QueryMetadata**: Metadata from a completed BigQuery query job.
- **QueryEstimate**: Pre-execution cost estimate from a dry run.
"""

from __future__ import annotations

from datetime import datetime  # noqa: TC003 - Pydantic needs runtime access

from pydantic import BaseModel


__all__ = ["QueryEstimate", "QueryMetadata"]


class QueryMetadata(BaseModel):
    """Metadata from a completed BigQuery query job.

    All fields are optional because BigQuery may not populate every
    statistic for all query types or execution modes.

    Args:
        bytes_processed: Total bytes scanned during query execution.
        bytes_billed: Total bytes charged, rounded up to 10 MB minimum by BigQuery.
        cache_hit: Whether results were served from the BigQuery cache.
        slot_millis: Compute slot-milliseconds consumed by the query.
        total_rows: Number of rows in the query result.
        started: Timestamp when query execution started.
        ended: Timestamp when query execution completed.
        statement_type: SQL statement type (e.g., SELECT).
    """

    bytes_processed: int | None = None
    bytes_billed: int | None = None
    cache_hit: bool | None = None
    slot_millis: int | None = None
    total_rows: int | None = None
    started: datetime | None = None
    ended: datetime | None = None
    statement_type: str | None = None


class QueryEstimate(BaseModel):
    """Pre-execution cost estimate from a BigQuery dry run.

    Args:
        bytes_processed: Estimated bytes that would be scanned.
        query: The SQL query that would be executed.
    """

    bytes_processed: int
    query: str
