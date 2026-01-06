"""Example usage of the GKG (Global Knowledge Graph) endpoint.

This example demonstrates how to query and stream GKG data using both
async and sync interfaces.
"""

import asyncio
from datetime import date

from py_gdelt.endpoints.gkg import GKGEndpoint
from py_gdelt.exceptions import APIError, DataError, RateLimitError
from py_gdelt.filters import DateRange, GKGFilter
from py_gdelt.sources.files import FileSource


async def async_query_example() -> None:
    """Example of async query for GKG data."""
    print("=== Async Query Example ===\n")

    # Initialize FileSource and GKGEndpoint
    async with FileSource() as file_source:
        endpoint = GKGEndpoint(file_source=file_source)

        # Create a filter for climate change articles
        filter_obj = GKGFilter(
            date_range=DateRange(start=date(2026, 1, 1), end=date(2026, 1, 1)),
            themes=["ENV_CLIMATECHANGE"],
            min_tone=0.0,  # Only positive tone articles
        )

        # Query all matching records
        try:
            result = await endpoint.query(filter_obj)

            print(f"Fetched {len(result)} GKG records")
            print(f"Query complete: {result.complete}\n")

            # Display first few records
            for i, record in enumerate(result[:5]):
                print(f"\nRecord {i + 1}:")
                print(f"  ID: {record.record_id}")
                print(f"  Source: {record.source_name}")
                print(f"  URL: {record.source_url}")
                print(f"  Primary Theme: {record.primary_theme}")
                if record.tone:
                    print(f"  Tone: {record.tone.tone:.2f}")
                print(f"  Has Quotations: {record.has_quotations}")
                print(f"  # Themes: {len(record.themes)}")
                print(f"  # Persons: {len(record.persons)}")
                print(f"  # Organizations: {len(record.organizations)}")
                print(f"  # Locations: {len(record.locations)}")
        except RateLimitError as e:
            print(f"Rate limit exceeded: {e}")
            if e.retry_after:
                print(f"Retry after {e.retry_after} seconds")
        except DataError as e:
            print(f"Data error: {e}")
        except APIError as e:
            print(f"API error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


async def async_stream_example() -> None:
    """Example of async streaming for large result sets."""
    print("\n\n=== Async Stream Example ===\n")

    async with FileSource() as file_source:
        endpoint = GKGEndpoint(file_source=file_source)

        # Filter for articles mentioning United Nations
        filter_obj = GKGFilter(
            date_range=DateRange(start=date(2026, 1, 1)),
            organizations=["United Nations"],
        )

        # Stream records one at a time
        try:
            count = 0
            async for record in endpoint.stream(filter_obj):
                count += 1
                print(f"Processing record {count}: {record.record_id}")

                # Show quotations if available
                if record.has_quotations:
                    for quote in record.quotations[:2]:  # Show first 2 quotes
                        print(f"  Quote: {quote.quote[:100]}...")

                # Process only first 10 records for demo
                if count >= 10:
                    break

            print(f"\nProcessed {count} records via streaming")
        except RateLimitError as e:
            print(f"Rate limit exceeded: {e}")
            if e.retry_after:
                print(f"Retry after {e.retry_after} seconds")
        except DataError as e:
            print(f"Data error: {e}")
        except APIError as e:
            print(f"API error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


def sync_query_example() -> None:
    """Example of synchronous query (blocking)."""
    print("\n\n=== Sync Query Example ===\n")

    # Note: FileSource needs to be created inside async context
    # For sync usage, we use asyncio.run to create the context
    async def _run() -> None:
        async with FileSource() as file_source:
            endpoint = GKGEndpoint(file_source=file_source)

            filter_obj = GKGFilter(
                date_range=DateRange(start=date(2026, 1, 1)),
                themes=["ECON_STOCKMARKET"],
            )

            # Use sync wrapper
            try:
                result = endpoint.query_sync(filter_obj)

                print(f"Fetched {len(result)} records synchronously")

                # Show themes from first record
                if result.data:
                    record = result.data[0]
                    print("\nFirst record themes:")
                    for theme in record.themes[:5]:
                        print(f"  - {theme.name} (offset: {theme.offset})")
            except RateLimitError as e:
                print(f"Rate limit exceeded: {e}")
                if e.retry_after:
                    print(f"Retry after {e.retry_after} seconds")
            except DataError as e:
                print(f"Data error: {e}")
            except APIError as e:
                print(f"API error: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")

    asyncio.run(_run())


def sync_stream_example() -> None:
    """Example of synchronous streaming."""
    print("\n\n=== Sync Stream Example ===\n")

    async def _run() -> None:
        async with FileSource() as file_source:
            endpoint = GKGEndpoint(file_source=file_source)

            filter_obj = GKGFilter(
                date_range=DateRange(start=date(2026, 1, 1)),
                country="USA",
            )

            # Use sync stream wrapper
            try:
                count = 0
                for record in endpoint.stream_sync(filter_obj):
                    count += 1
                    print(f"Record {count}: {record.source_name}")

                    if count >= 5:
                        break

                print(f"\nStreamed {count} records synchronously")
            except RateLimitError as e:
                print(f"Rate limit exceeded: {e}")
                if e.retry_after:
                    print(f"Retry after {e.retry_after} seconds")
            except DataError as e:
                print(f"Data error: {e}")
            except APIError as e:
                print(f"API error: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")

    asyncio.run(_run())


async def main() -> None:
    """Run all examples."""
    # Run async examples
    await async_query_example()
    await async_stream_example()

    # Run sync examples (these internally use asyncio.run)
    sync_query_example()
    sync_stream_example()

    print("\n\n=== All examples completed! ===")


if __name__ == "__main__":
    asyncio.run(main())
