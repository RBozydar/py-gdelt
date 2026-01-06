"""Deduplication utilities for GDELT records.

GDELT captures news reports, not unique events. ~20% redundancy exists due to:
- Multiple outlets reporting the same event
- Wire services republished across different sites
- Updates to the same story

This module provides memory-efficient deduplication using different strategies.
"""

from collections.abc import AsyncIterator, Iterable, Iterator
from enum import StrEnum
from typing import Protocol, TypeVar


class DedupeStrategy(StrEnum):
    """Deduplication strategies for GDELT events.

    Strategies range from aggressive (URL only) to granular (including event codes).
    URL_DATE_LOCATION provides a good balance for most use cases.
    """

    URL_ONLY = "url_only"
    URL_DATE = "url_date"
    URL_DATE_LOCATION = "url_date_location"  # Recommended default
    URL_DATE_LOCATION_ACTORS = "url_date_location_actors"
    AGGRESSIVE = "aggressive"


class HasDedupeFields(Protocol):
    """Protocol for objects that can be deduplicated.

    Any object with these fields can be deduplicated, regardless of its type.
    This enables duck typing for Pydantic models, dataclasses, or custom objects.

    Note: Using @property makes these covariant, so `str` matches `str | None`.
    """

    @property
    def source_url(self) -> str | None: ...
    @property
    def sql_date(self) -> str | None: ...
    @property
    def action_geo_fullname(self) -> str | None: ...
    @property
    def actor1_code(self) -> str | None: ...
    @property
    def actor2_code(self) -> str | None: ...
    @property
    def event_root_code(self) -> str | None: ...


T = TypeVar("T", bound=HasDedupeFields)


def get_dedup_key(record: HasDedupeFields, strategy: DedupeStrategy) -> tuple[str, ...]:
    """Get the deduplication key for a record based on strategy.

    Args:
        record: Record to generate key for
        strategy: Deduplication strategy to use

    Returns:
        Tuple of field values to use as deduplication key.
        None values are normalized to empty strings.
    """

    # Normalize None to empty string for consistent comparison
    def normalize(value: str | None) -> str:
        """Convert None to empty string for consistent key comparison."""
        return value if value is not None else ""

    if strategy == DedupeStrategy.URL_ONLY:
        return (normalize(record.source_url),)

    if strategy == DedupeStrategy.URL_DATE:
        return (
            normalize(record.source_url),
            normalize(record.sql_date),
        )

    if strategy == DedupeStrategy.URL_DATE_LOCATION:
        return (
            normalize(record.source_url),
            normalize(record.sql_date),
            normalize(record.action_geo_fullname),
        )

    if strategy == DedupeStrategy.URL_DATE_LOCATION_ACTORS:
        return (
            normalize(record.source_url),
            normalize(record.sql_date),
            normalize(record.action_geo_fullname),
            normalize(record.actor1_code),
            normalize(record.actor2_code),
        )

    # AGGRESSIVE strategy
    return (
        normalize(record.source_url),
        normalize(record.sql_date),
        normalize(record.action_geo_fullname),
        normalize(record.actor1_code),
        normalize(record.actor2_code),
        normalize(record.event_root_code),
    )


def deduplicate(
    records: Iterable[T],
    strategy: DedupeStrategy = DedupeStrategy.URL_DATE_LOCATION,
) -> Iterator[T]:
    """Deduplicate records using the specified strategy.

    GDELT captures news reports, not unique events. ~20% redundancy exists.
    This function yields unique records based on the strategy's key fields.

    The function is memory-efficient: it uses a generator and only stores
    seen keys in memory, not the full records.

    Args:
        records: Iterable of records to deduplicate
        strategy: Deduplication strategy to use (default: URL_DATE_LOCATION)

    Yields:
        T: Unique records based on the strategy. First occurrence is kept,
            subsequent duplicates are filtered out.

    Example:
        >>> records = fetch_events(...)
        >>> unique = deduplicate(records, DedupeStrategy.URL_DATE_LOCATION)
        >>> for event in unique:
        ...     process(event)
    """
    seen_keys: set[tuple[str, ...]] = set()

    for record in records:
        key = get_dedup_key(record, strategy)

        if key not in seen_keys:
            seen_keys.add(key)
            yield record


async def deduplicate_async(
    records: AsyncIterator[T],
    strategy: DedupeStrategy = DedupeStrategy.URL_DATE_LOCATION,
) -> AsyncIterator[T]:
    """Deduplicate async records using the specified strategy.

    Async version of deduplicate() for use with async iterators.

    GDELT captures news reports, not unique events. ~20% redundancy exists.
    This function yields unique records based on the strategy's key fields.

    The function is memory-efficient: it uses a generator and only stores
    seen keys in memory, not the full records.

    Args:
        records: Async iterable of records to deduplicate
        strategy: Deduplication strategy to use (default: URL_DATE_LOCATION)

    Yields:
        T: Unique records based on the strategy. First occurrence is kept,
            subsequent duplicates are filtered out.

    Example:
        >>> async for event in deduplicate_async(fetch_events(...)):
        ...     await process(event)
    """
    seen_keys: set[tuple[str, ...]] = set()

    async for record in records:
        key = get_dedup_key(record, strategy)

        if key not in seen_keys:
            seen_keys.add(key)
            yield record
