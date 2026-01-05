"""Example: Query GDELT Mentions for a specific event.

This example demonstrates how to use the MentionsEndpoint to query mentions
of a specific event from GDELT's Mentions database.

Mentions track individual occurrences of events across different news sources.
Each mention links to an event via GlobalEventID and contains metadata about
the source, timing, document position, and confidence.

Note: Mentions queries require BigQuery as files don't support event-specific filtering.
"""

import asyncio
from datetime import date

from py_gdelt.endpoints.mentions import MentionsEndpoint
from py_gdelt.filters import DateRange, EventFilter
from py_gdelt.sources.bigquery import BigQuerySource
from py_gdelt.sources.files import FileSource


async def query_mentions_batch():
    """Query mentions for a specific event and return all results."""
    print("\n=== Batch Query: All Mentions for Event ===\n")

    async with FileSource() as file_source:
        # Initialize BigQuery source for mentions queries
        # Mentions require BigQuery as files don't support event filtering
        bq_source = BigQuerySource()

        # Create endpoint
        endpoint = MentionsEndpoint(
            file_source=file_source,
            bigquery_source=bq_source,
        )

        # Create filter with date range
        filter_obj = EventFilter(
            date_range=DateRange(
                start=date(2026, 1, 1),
                end=date(2026, 1, 7),
            )
        )

        # Query mentions for a specific event
        # Replace with an actual GlobalEventID from your data
        global_event_id = "123456789"

        result = await endpoint.query(
            global_event_id=global_event_id,
            filter_obj=filter_obj,
            use_bigquery=True,  # Required for mentions
        )

        # Display results
        print(f"Found {len(result)} mentions for event {global_event_id}")
        print(f"Query complete: {result.complete}")
        print(f"Failed requests: {result.total_failed}\n")

        # Show first 5 mentions
        for i, mention in enumerate(result[:5]):
            print(f"Mention {i+1}:")
            print(f"  Source: {mention.source_name}")
            print(f"  Identifier: {mention.identifier}")
            print(f"  Confidence: {mention.confidence}%")
            print(f"  Doc Tone: {mention.doc_tone}")
            print(f"  Mention Time: {mention.mention_time}")
            print()


async def stream_mentions():
    """Stream mentions for a specific event (memory-efficient)."""
    print("\n=== Streaming Query: Mentions with High Confidence ===\n")

    async with FileSource() as file_source:
        bq_source = BigQuerySource()

        endpoint = MentionsEndpoint(
            file_source=file_source,
            bigquery_source=bq_source,
        )

        filter_obj = EventFilter(
            date_range=DateRange(
                start=date(2026, 1, 1),
                end=date(2026, 1, 7),
            )
        )

        global_event_id = "123456789"

        # Stream mentions and filter by confidence
        count = 0
        high_confidence_count = 0

        async for mention in endpoint.stream(
            global_event_id=global_event_id,
            filter_obj=filter_obj,
            use_bigquery=True,
        ):
            count += 1

            # Only process high-confidence mentions (>= 80%)
            if mention.confidence >= 80:
                high_confidence_count += 1
                print(f"High-confidence mention #{high_confidence_count}:")
                print(f"  Source: {mention.source_name}")
                print(f"  Confidence: {mention.confidence}%")
                print(f"  Type: {mention.mention_type}")
                print()

                # Stop after 10 high-confidence mentions
                if high_confidence_count >= 10:
                    break

        print(f"\nProcessed {count} total mentions")
        print(f"Found {high_confidence_count} high-confidence mentions (>= 80%)")


def query_mentions_sync():
    """Synchronous wrapper example."""
    print("\n=== Synchronous Query Example ===\n")

    # Note: For production code, prefer async versions
    # Sync wrappers are for quick scripts and interactive use

    # Initialize sources (without async context manager)
    file_source = FileSource()
    bq_source = BigQuerySource()

    endpoint = MentionsEndpoint(
        file_source=file_source,
        bigquery_source=bq_source,
    )

    filter_obj = EventFilter(
        date_range=DateRange(start=date(2026, 1, 1), end=date(2026, 1, 3))
    )

    global_event_id = "123456789"

    # Use synchronous wrapper
    result = endpoint.query_sync(
        global_event_id=global_event_id,
        filter_obj=filter_obj,
        use_bigquery=True,
    )

    print(f"Found {len(result)} mentions (sync query)")


async def analyze_mention_sources():
    """Analyze mention sources and types."""
    print("\n=== Analysis: Mention Sources and Types ===\n")

    async with FileSource() as file_source:
        bq_source = BigQuerySource()

        endpoint = MentionsEndpoint(
            file_source=file_source,
            bigquery_source=bq_source,
        )

        filter_obj = EventFilter(
            date_range=DateRange(start=date(2026, 1, 1), end=date(2026, 1, 7))
        )

        global_event_id = "123456789"

        # Collect source statistics
        sources = {}
        types = {}

        async for mention in endpoint.stream(
            global_event_id=global_event_id,
            filter_obj=filter_obj,
            use_bigquery=True,
        ):
            # Count by source
            source = mention.source_name
            sources[source] = sources.get(source, 0) + 1

            # Count by type
            mention_type = mention.mention_type
            types[mention_type] = types.get(mention_type, 0) + 1

        # Display statistics
        print(f"Total unique sources: {len(sources)}")
        print("\nTop 10 sources:")
        for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {source}: {count} mentions")

        print("\nMention types:")
        for mention_type, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
            print(f"  Type {mention_type}: {count} mentions")


async def main():
    """Run all examples."""
    # Note: Replace global_event_id with an actual event ID from your data

    # Example 1: Batch query
    await query_mentions_batch()

    # Example 2: Streaming query
    await stream_mentions()

    # Example 4: Analysis
    await analyze_mention_sources()


if __name__ == "__main__":
    print("GDELT Mentions Query Examples")
    print("=" * 50)
    print("\nNote: These examples require:")
    print("1. Google Cloud credentials configured")
    print("2. BigQuery API enabled")
    print("3. An actual GlobalEventID from GDELT data")
    print("\nUpdate the global_event_id variable with a real event ID")
    print("from your GDELT Events data to see actual results.")
    print("=" * 50)

    asyncio.run(main())
