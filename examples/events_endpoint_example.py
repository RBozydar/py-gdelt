#!/usr/bin/env python3
"""Example usage of EventsEndpoint.

This example demonstrates how to use the EventsEndpoint to query GDELT Events data
with various filtering, deduplication, and streaming options.
"""

import asyncio
from datetime import date

from py_gdelt.endpoints import EventsEndpoint
from py_gdelt.filters import DateRange, EventFilter
from py_gdelt.sources import FileSource
from py_gdelt.utils.dedup import DedupeStrategy


async def example_basic_query() -> None:
    """Example: Basic event query."""
    print("=" * 60)
    print("Example 1: Basic Event Query")
    print("=" * 60)

    async with FileSource() as file_source:
        endpoint = EventsEndpoint(file_source=file_source)

        # Create filter for USA events on January 1, 2026
        filter_obj = EventFilter(
            date_range=DateRange(start=date(2026, 1, 1)),
            actor1_country="USA",
        )

        # Query events
        result = await endpoint.query(filter_obj)

        print(f"Found {len(result)} events")
        if result.data:
            event = result.data[0]
            print(f"\nFirst event:")
            print(f"  ID: {event.global_event_id}")
            print(f"  Date: {event.date}")
            print(f"  Event Code: {event.event_code}")
            if event.actor1:
                print(f"  Actor1: {event.actor1.name} ({event.actor1.code})")
            if event.actor2:
                print(f"  Actor2: {event.actor2.name} ({event.actor2.code})")
            if event.action_geo:
                print(f"  Location: {event.action_geo.name}")


async def example_streaming() -> None:
    """Example: Stream events for memory efficiency."""
    print("\n" + "=" * 60)
    print("Example 2: Streaming Events")
    print("=" * 60)

    async with FileSource() as file_source:
        endpoint = EventsEndpoint(file_source=file_source)

        # Create filter for a week of events
        filter_obj = EventFilter(
            date_range=DateRange(
                start=date(2026, 1, 1),
                end=date(2026, 1, 7),
            ),
        )

        # Stream events one at a time
        count = 0
        async for event in endpoint.stream(filter_obj):
            count += 1
            if count <= 5:  # Print first 5
                print(f"Event {count}: {event.global_event_id}")

        print(f"Streamed {count} total events")


async def example_deduplication() -> None:
    """Example: Query with deduplication."""
    print("\n" + "=" * 60)
    print("Example 3: Deduplication")
    print("=" * 60)

    async with FileSource() as file_source:
        endpoint = EventsEndpoint(file_source=file_source)

        # Create filter
        filter_obj = EventFilter(
            date_range=DateRange(start=date(2026, 1, 1)),
        )

        # Query with deduplication
        result = await endpoint.query(
            filter_obj,
            deduplicate=True,
            dedupe_strategy=DedupeStrategy.URL_DATE_LOCATION,
        )

        print(f"Found {len(result)} unique events")
        print(f"Deduplication strategy: {DedupeStrategy.URL_DATE_LOCATION}")


async def example_filtered_query() -> None:
    """Example: Query with multiple filters."""
    print("\n" + "=" * 60)
    print("Example 4: Advanced Filtering")
    print("=" * 60)

    async with FileSource() as file_source:
        endpoint = EventsEndpoint(file_source=file_source)

        # Create filter with multiple criteria
        filter_obj = EventFilter(
            date_range=DateRange(start=date(2026, 1, 1)),
            actor1_country="USA",
            actor2_country="RUS",
            min_tone=-5.0,  # Negative tone events only
            max_tone=0.0,
        )

        # Query events
        result = await endpoint.query(filter_obj)

        print(f"Found {len(result)} events matching criteria:")
        print("  - Actor1: USA")
        print("  - Actor2: RUS")
        print("  - Tone: -5.0 to 0.0 (negative)")


async def example_sync_usage() -> None:
    """Example: Synchronous usage (blocking)."""
    print("\n" + "=" * 60)
    print("Example 5: Synchronous Usage")
    print("=" * 60)

    # Note: This is a demonstration. In real async code, use async methods.
    file_source = FileSource()
    endpoint = EventsEndpoint(file_source=file_source)

    # Create filter
    filter_obj = EventFilter(
        date_range=DateRange(start=date(2026, 1, 1)),
    )

    # Synchronous query (blocks until complete)
    result = endpoint.query_sync(filter_obj)

    print(f"Found {len(result)} events (synchronous query)")


async def main() -> None:
    """Run all examples."""
    try:
        await example_basic_query()
        await example_streaming()
        await example_deduplication()
        await example_filtered_query()
        # Note: Skipping sync example in async context
        # await example_sync_usage()  # Would raise RuntimeError

        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # Run all examples
    asyncio.run(main())
