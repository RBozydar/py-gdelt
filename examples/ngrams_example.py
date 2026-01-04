#!/usr/bin/env python3
"""Example: Query GDELT NGrams 3.0 data.

This example demonstrates how to use NGramsEndpoint to query word and phrase
occurrences from GDELT NGrams 3.0 dataset, with filtering by language, position,
and ngram text.
"""

import asyncio
import logging
from datetime import date

from py_gdelt.config import GDELTSettings
from py_gdelt.endpoints import NGramsEndpoint
from py_gdelt.filters import DateRange, NGramsFilter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def query_climate_mentions() -> None:
    """Query NGrams for mentions of 'climate' in English articles.

    Demonstrates basic filtering by ngram text and language, focusing on
    early article mentions (position 0-30, i.e., first 30% of article).
    """
    logger.info("Querying NGrams for 'climate' mentions in English articles")

    # Configure settings with caching
    settings = GDELTSettings(
        cache_ttl=3600,  # Cache for 1 hour
        max_concurrent_downloads=5,
    )

    async with NGramsEndpoint(settings=settings) as endpoint:
        # Create filter for recent data
        filter_obj = NGramsFilter(
            date_range=DateRange(
                start=date(2026, 1, 1),
                end=date(2026, 1, 2),
            ),
            ngram="climate",
            language="en",
            min_position=0,
            max_position=30,  # Focus on early article mentions
        )

        # Query and collect all results
        result = await endpoint.query(filter_obj)

        logger.info("Found %d climate mentions in article headlines", len(result))

        # Display top 5 mentions
        for i, record in enumerate(result.data[:5], 1):
            logger.info(
                "Record %d: '%s' at position %d",
                i,
                record.context[:80],  # First 80 chars of context
                record.position,
            )
            logger.info("  URL: %s", record.url)


async def stream_language_diversity() -> None:
    """Stream NGrams to analyze language diversity for a term.

    Demonstrates streaming for memory efficiency and collecting statistics
    across multiple languages.
    """
    logger.info("Analyzing language diversity for 'peace' mentions")

    async with NGramsEndpoint() as endpoint:
        # Create filter for broad search
        filter_obj = NGramsFilter(
            date_range=DateRange(start=date(2026, 1, 1)),
            ngram="peace",
        )

        # Track language statistics
        language_counts: dict[str, int] = {}
        total_records = 0

        # Stream records for memory efficiency
        async for record in endpoint.stream(filter_obj):
            total_records += 1
            language_counts[record.language] = (
                language_counts.get(record.language, 0) + 1
            )

            # Limit to first 1000 records for this example
            if total_records >= 1000:
                break

        logger.info("Processed %d records across %d languages", total_records, len(language_counts))

        # Display top languages
        sorted_languages = sorted(
            language_counts.items(), key=lambda x: x[1], reverse=True
        )
        for lang, count in sorted_languages[:5]:
            logger.info("  %s: %d mentions (%.1f%%)", lang, count, 100 * count / total_records)


async def analyze_position_distribution() -> None:
    """Analyze where in articles a term appears.

    Demonstrates position-based filtering to understand if a term appears
    in headlines, body, or conclusions.
    """
    logger.info("Analyzing position distribution for 'election' mentions")

    async with NGramsEndpoint() as endpoint:
        filter_obj = NGramsFilter(
            date_range=DateRange(start=date(2026, 1, 1)),
            ngram="election",
            language="en",
        )

        # Track position distribution
        early_count = 0  # Position 0-30 (first 30%)
        middle_count = 0  # Position 30-70
        late_count = 0  # Position 70-90 (last 30%)
        total = 0

        async for record in endpoint.stream(filter_obj):
            total += 1

            if record.is_early_in_article:
                early_count += 1
            elif record.is_late_in_article:
                late_count += 1
            else:
                middle_count += 1

            # Limit for example
            if total >= 500:
                break

        logger.info("Position distribution across %d records:", total)
        logger.info("  Early (0-30): %d (%.1f%%)", early_count, 100 * early_count / total)
        logger.info("  Middle (30-70): %d (%.1f%%)", middle_count, 100 * middle_count / total)
        logger.info("  Late (70-90): %d (%.1f%%)", late_count, 100 * late_count / total)


async def sync_example() -> None:
    """Example using synchronous wrappers.

    Demonstrates sync methods for use in non-async code, though async
    methods are preferred when possible.
    """
    logger.info("Running synchronous example")

    endpoint = NGramsEndpoint()

    filter_obj = NGramsFilter(
        date_range=DateRange(start=date(2026, 1, 1)),
        ngram="technology",
        language="en",
        max_position=20,  # Headlines only
    )

    # Use sync wrapper
    result = endpoint.query_sync(filter_obj)

    logger.info("Found %d technology mentions in headlines", len(result))

    # Display first few
    for record in result.data[:3]:
        logger.info("  '%s' in %s", record.ngram, record.url)

    # Clean up
    asyncio.run(endpoint.close())


async def main() -> None:
    """Run all examples."""
    logger.info("=" * 60)
    logger.info("GDELT NGrams 3.0 Examples")
    logger.info("=" * 60)

    # Example 1: Basic query with filtering
    await query_climate_mentions()
    logger.info("")

    # Example 2: Streaming for language diversity
    await stream_language_diversity()
    logger.info("")

    # Example 3: Position distribution analysis
    await analyze_position_distribution()
    logger.info("")

    # Example 4: Synchronous wrapper
    await asyncio.to_thread(sync_example)
    logger.info("")

    logger.info("All examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
