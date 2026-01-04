#!/usr/bin/env python3
"""Real-life integration test: What did Trump do related to Venezuela this week?

This script queries GDELT's DOC API to find recent news articles about
Trump and Venezuela, demonstrating real API usage.
"""

import asyncio
from datetime import date, timedelta

from py_gdelt import GDELTClient
from py_gdelt.filters import DocFilter


async def search_trump_venezuela() -> None:
    """Search for recent Trump + Venezuela news."""
    print("=" * 70)
    print("GDELT Integration Test: Trump + Venezuela (This Week)")
    print("=" * 70)

    async with GDELTClient() as client:
        # Search DOC API for articles
        print("\nSearching GDELT DOC API for 'Trump Venezuela'...")

        doc_filter = DocFilter(
            query="Trump Venezuela",
            timespan="7d",  # Last 7 days
            max_results=50,
            sort_by="date",  # Most recent first
            source_language="english",  # English articles only
        )

        try:
            articles = await client.doc.query(doc_filter)

            # Filter for English articles client-side (GDELT sometimes ignores language filter)
            non_english_domains = ('.ru', '.kr', '.cn', '.jp', '.ua', '.il', '.fi', '.uk.co',
                                   'qianlong.com', 'vetogate.com', 'alquds.co', 'youm7.com',
                                   'webdunia.com', 'centralasia.media', 'israelinfo.co',
                                   'liga.net', 'iltalehti.fi', 'unian.net', 'glavred.info',
                                   'heraldcorp.com', 'hankookilbo.com', 'koreatimes.com', 'fnnews.com')
            english_articles = [a for a in articles if a.is_english or
                               (a.domain and not any(d in a.domain for d in non_english_domains))]

            print(f"\nFound {len(articles)} total articles, {len(english_articles)} likely English\n")
            print("-" * 70)

            for i, article in enumerate(english_articles[:20], 1):  # Show top 20
                print(f"\n{i}. {article.title}")
                # Parse the date - handle various formats
                date_str = article.seendate or "Unknown"
                if date_str and "T" in date_str:
                    # Format: 20260103T174500Z -> 2026-01-03 17:45
                    try:
                        date_str = f"{date_str[0:4]}-{date_str[4:6]}-{date_str[6:8]} {date_str[9:11]}:{date_str[11:13]}"
                    except (IndexError, ValueError):
                        pass
                print(f"   Date: {date_str}")
                print(f"   Source: {article.domain}")
                print(f"   URL: {article.url[:80]}...")

                # Show tone if available
                if article.tone is not None:
                    tone_label = "positive" if article.tone > 0 else "negative" if article.tone < 0 else "neutral"
                    print(f"   Tone: {article.tone:.2f} ({tone_label})")

            print("\n" + "-" * 70)
            print(f"\nTotal English articles: {len(english_articles)}")

            # Summary
            if english_articles:
                print("\n" + "=" * 70)
                print("SUMMARY: Key topics from headlines")
                print("=" * 70)

                # Extract common themes from titles
                keywords = {}
                for article in english_articles:
                    title_lower = article.title.lower()
                    for word in ["tariff", "oil", "sanction", "maduro", "guaido",
                                 "military", "invasion", "threat", "economy", "crisis",
                                 "panama", "canal", "deportation", "immigration"]:
                        if word in title_lower:
                            keywords[word] = keywords.get(word, 0) + 1

                if keywords:
                    print("\nKeywords found in headlines:")
                    for word, count in sorted(keywords.items(), key=lambda x: -x[1]):
                        print(f"  - {word}: {count} mentions")

        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()


async def search_events_venezuela() -> None:
    """Search for events involving Venezuela."""
    print("\n" + "=" * 70)
    print("Searching GDELT Events for Venezuela (if files available)")
    print("=" * 70)

    async with GDELTClient() as client:
        # Try GEO API for geographic context
        print("\nSearching GEO API for Venezuela-related coverage...")

        try:
            from py_gdelt.filters import GeoFilter

            geo_filter = GeoFilter(
                query="Venezuela Trump",
                timespan="7d",
            )

            geo_results = await client.geo.query(geo_filter)

            if geo_results:
                print(f"Found {len(geo_results)} geographic features")
                for feat in geo_results[:5]:
                    print(f"  - {feat}")
            else:
                print("No geographic results")

        except Exception as e:
            print(f"GEO API error (expected if no results): {e}")


def main() -> None:
    """Run the integration test."""
    asyncio.run(search_trump_venezuela())
    # asyncio.run(search_events_venezuela())  # Optional


if __name__ == "__main__":
    main()
