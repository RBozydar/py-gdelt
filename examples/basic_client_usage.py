"""Basic examples demonstrating GDELTClient usage.

This script shows common usage patterns for the GDELT Python client library,
including:
- Basic client initialization
- Querying events data
- Using REST API endpoints
- Accessing lookup tables
- Custom configuration
"""

import asyncio
from datetime import date
from pathlib import Path

from py_gdelt import GDELTClient
from py_gdelt.config import GDELTSettings
from py_gdelt.exceptions import APIError, DataError, RateLimitError
from py_gdelt.filters import DateRange, DocFilter, EventFilter


async def basic_usage() -> None:
    """Demonstrate basic client usage with default settings."""
    print("=" * 60)
    print("Basic Usage Example")
    print("=" * 60)

    # Use the client as an async context manager
    async with GDELTClient() as client:
        # Query recent events from the US
        yesterday = date(2026, 1, 1)

        print(f"\nQuerying events for {yesterday}...")
        event_filter = EventFilter(
            date_range=DateRange(start=yesterday, end=yesterday),
            actor1_country="USA",
        )

        # Query a small sample
        try:
            result = await client.events.query(event_filter)
            print(f"Found {len(result)} events from the US on {yesterday}")

            if result:
                # Show first event
                first_event = result[0]
                print("\nFirst event:")
                print(f"  ID: {first_event.global_event_id}")
                print(f"  Date: {first_event.date}")
                print(f"  Event Code: {first_event.event_code}")
                print(f"  Goldstein Scale: {first_event.goldstein_scale}")
        except DataError as e:
            print(f"Data error querying events: {e}")
        except APIError as e:
            print(f"API error querying events: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


async def rest_api_usage() -> None:
    """Demonstrate REST API endpoint usage."""
    print("\n" + "=" * 60)
    print("REST API Usage Example")
    print("=" * 60)

    async with GDELTClient() as client:
        # Search for articles using DOC API
        print("\nSearching for articles about 'climate change'...")
        try:
            doc_filter = DocFilter(
                query="climate change",
                timespan="24h",
                max_results=10,
                sort_by="relevance",
            )
            articles = await client.doc.query(doc_filter)
            print(f"Found {len(articles)} articles")

            if articles:
                print("\nFirst article:")
                print(f"  Title: {articles[0].title}")
                print(f"  URL: {articles[0].url}")
                print(f"  Date: {articles[0].date}")
        except RateLimitError as e:
            print(f"Rate limit exceeded: {e}")
            if e.retry_after:
                print(f"Please retry after {e.retry_after} seconds")
        except APIError as e:
            print(f"API error searching articles: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


async def lookup_usage() -> None:
    """Demonstrate lookup table access."""
    print("\n" + "=" * 60)
    print("Lookup Tables Example")
    print("=" * 60)

    async with GDELTClient() as client:
        # Access CAMEO codes
        print("\nCAMEO Code Lookups:")
        cameo = client.lookups.cameo
        entry_01 = cameo.get("01")
        entry_14 = cameo.get("14")
        print(f"  Code '01': {entry_01.name if entry_01 else 'Unknown'}")
        print(f"  Code '14': {entry_14.name if entry_14 else 'Unknown'}")

        # Access country codes
        print("\nCountry Code Conversions:")
        countries = client.lookups.countries
        try:
            iso3 = countries.fips_to_iso3("US")
            iso2 = countries.fips_to_iso2("US")
            print(f"  FIPS 'US' -> ISO3 '{iso3}', ISO2 '{iso2}'")
        except Exception as e:
            print(f"  Lookup error: {e}")


async def custom_config_usage() -> None:
    """Demonstrate custom configuration."""
    print("\n" + "=" * 60)
    print("Custom Configuration Example")
    print("=" * 60)

    # Create custom settings
    settings = GDELTSettings(
        timeout=60,  # 60 second timeout
        max_retries=5,  # 5 retry attempts
        max_concurrent_downloads=5,  # 5 concurrent downloads
        fallback_to_bigquery=False,  # Disable BigQuery fallback
        validate_codes=True,  # Enable code validation
    )

    async with GDELTClient(settings=settings) as client:
        print("Client initialized with custom settings:")
        print(f"  Timeout: {client.settings.timeout}s")
        print(f"  Max Retries: {client.settings.max_retries}")
        print(f"  Fallback to BigQuery: {client.settings.fallback_to_bigquery}")


async def config_file_usage() -> None:
    """Demonstrate configuration from TOML file."""
    print("\n" + "=" * 60)
    print("TOML Configuration Example")
    print("=" * 60)

    # Create a sample config file with secure permissions
    import tempfile

    fd, config_path_str = tempfile.mkstemp(suffix=".toml", prefix="gdelt_")
    import os

    os.close(fd)  # Close the file descriptor
    config_path = Path(config_path_str)

    # Set secure permissions (owner read/write only)
    config_path.chmod(0o600)

    # Write config content
    config_path.write_text("""
[gdelt]
timeout = 45
max_retries = 3
cache_ttl = 7200
validate_codes = true
""")

    try:
        async with GDELTClient(config_path=config_path) as client:
            print(f"Client initialized from {config_path}")
            print(f"  Timeout: {client.settings.timeout}s")
            print(f"  Max Retries: {client.settings.max_retries}")
            print(f"  Cache TTL: {client.settings.cache_ttl}s")
    finally:
        # Cleanup
        config_path.unlink(missing_ok=True)


async def streaming_usage() -> None:
    """Demonstrate streaming large datasets."""
    print("\n" + "=" * 60)
    print("Streaming Data Example")
    print("=" * 60)

    async with GDELTClient() as client:
        yesterday = date(2026, 1, 1)

        print(f"\nStreaming events from {yesterday} (first 5)...")
        event_filter = EventFilter(
            date_range=DateRange(start=yesterday, end=yesterday),
            actor1_country="USA",
        )

        try:
            count = 0
            async for event in client.events.stream(event_filter):
                count += 1
                print(f"  Event {count}: {event.global_event_id}")
                if count >= 5:
                    break
            print(f"\nProcessed {count} events (stopped early for demo)")
        except DataError as e:
            print(f"Data error streaming events: {e}")
        except APIError as e:
            print(f"API error streaming events: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


def sync_usage() -> None:
    """Demonstrate synchronous usage."""
    print("\n" + "=" * 60)
    print("Synchronous Usage Example")
    print("=" * 60)

    # Use the client as a sync context manager
    with GDELTClient() as client:
        yesterday = date(2026, 1, 1)

        print(f"\nQuerying events for {yesterday} (synchronous)...")
        event_filter = EventFilter(
            date_range=DateRange(start=yesterday, end=yesterday),
            actor1_country="CHN",
        )

        try:
            result = client.events.query_sync(event_filter)
            print(f"Found {len(result)} events from China on {yesterday}")
        except Exception as e:
            print(f"Error querying events: {e}")


async def main() -> None:
    """Run all examples."""
    print("\n" + "=" * 60)
    print("GDELT Python Client - Usage Examples")
    print("=" * 60)

    # Run async examples
    await basic_usage()
    await rest_api_usage()
    await lookup_usage()
    await custom_config_usage()
    await config_file_usage()
    await streaming_usage()

    # Run sync example
    sync_usage()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
