#!/usr/bin/env python3
"""Example: Query GDELT Context 2.0 API for contextual analysis.

Demonstrates:
- Basic contextual analysis with themes and entities
- Getting top themes for a search term
- Filtering entities by type (PERSON, ORG, LOCATION)
- Tone/sentiment analysis
- Proper error handling with specific exceptions
"""

import asyncio

from py_gdelt import GDELTClient
from py_gdelt.exceptions import APIError, RateLimitError


async def analyze_topic_context() -> None:
    """Analyze contextual information for a topic."""
    print("=" * 60)
    print("Example 1: Basic Contextual Analysis")
    print("=" * 60)

    async with GDELTClient() as client:
        # Analyze context for "artificial intelligence"
        try:
            result = await client.context.analyze(
                "artificial intelligence",
                timespan="7d",
            )

            print("\nQuery: 'artificial intelligence'")
            print(f"Articles analyzed: {result.article_count}")

            if result.themes:
                print("\nTop Themes:")
                for theme in result.themes[:5]:
                    print(f"  - {theme.theme}: {theme.count} mentions")

            if result.entities:
                print("\nTop Entities:")
                for entity in result.entities[:5]:
                    print(f"  - {entity.name} ({entity.entity_type}): {entity.count}")

            if result.tone:
                print("\nTone Analysis:")
                print(f"  Average tone: {result.tone.average_tone:.2f}")
                print(f"  Positive: {result.tone.positive_count}")
                print(f"  Negative: {result.tone.negative_count}")
                print(f"  Neutral: {result.tone.neutral_count}")
        except RateLimitError as e:
            print(f"Rate limit exceeded: {e}")
            if e.retry_after:
                print(f"Please retry after {e.retry_after} seconds")
        except APIError as e:
            print(f"API error analyzing topic: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


async def get_entities_by_type() -> None:
    """Get entities filtered by type."""
    print("\n" + "=" * 60)
    print("Example 2: Entities by Type")
    print("=" * 60)

    async with GDELTClient() as client:
        try:
            # Get people mentioned in climate change coverage
            people = await client.context.get_entities(
                "climate change",
                entity_type="PERSON",
                timespan="30d",
                limit=10,
            )

            print("\nTop people mentioned in 'climate change' coverage:")
            for person in people:
                print(f"  - {person.name}: {person.count} mentions")

            # Get organizations
            orgs = await client.context.get_entities(
                "climate change",
                entity_type="ORG",
                timespan="30d",
                limit=10,
            )

            print("\nTop organizations:")
            for org in orgs:
                print(f"  - {org.name}: {org.count} mentions")
        except RateLimitError as e:
            print(f"Rate limit exceeded: {e}")
            if e.retry_after:
                print(f"Please retry after {e.retry_after} seconds")
        except APIError as e:
            print(f"API error fetching entities: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


async def compare_topic_themes() -> None:
    """Compare themes across different topics."""
    print("\n" + "=" * 60)
    print("Example 3: Compare Topic Themes")
    print("=" * 60)

    async with GDELTClient() as client:
        topics = ["technology", "healthcare", "economy"]

        for topic in topics:
            try:
                themes = await client.context.get_themes(topic, limit=3)
                print(f"\n'{topic}' top themes:")
                for theme in themes:
                    print(f"  - {theme.theme}: {theme.count}")
            except RateLimitError as e:
                print(f"Rate limit exceeded for '{topic}': {e}")
            except APIError as e:
                print(f"API error fetching themes for '{topic}': {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")


async def main() -> None:
    """Run all examples."""
    await analyze_topic_context()
    await get_entities_by_type()
    await compare_topic_themes()

    print("\n" + "=" * 60)
    print("Context API examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
