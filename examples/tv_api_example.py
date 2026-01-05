#!/usr/bin/env python3
"""Example: Query GDELT TV and TVAI APIs for television news monitoring.

Demonstrates:
- Searching TV transcripts for clips
- Timeline of TV mentions
- Station comparison charts
- AI-enhanced TV search
"""

import asyncio

from py_gdelt import GDELTClient


async def search_tv_clips() -> None:
    """Search for TV clips mentioning a topic."""
    print("=" * 60)
    print("Example 1: TV Clip Search")
    print("=" * 60)

    async with GDELTClient() as client:
        try:
            # Search for clips about "economy"
            clips = await client.tv.search(
                "economy",
                timespan="24h",
                max_results=10,
            )

            print(f"\nFound {len(clips)} clips about 'economy'")
            for clip in clips[:5]:
                print(f"\n  Station: {clip.station}")
                print(f"  Show: {clip.show_name}")
                if clip.date:
                    print(f"  Date: {clip.date}")
                if clip.snippet:
                    print(f"  Snippet: {clip.snippet[:100]}...")
        except Exception as e:
            print(f"Error searching TV clips: {e}")


async def search_by_station() -> None:
    """Search clips on a specific station."""
    print("\n" + "=" * 60)
    print("Example 2: Station-Specific Search")
    print("=" * 60)

    async with GDELTClient() as client:
        stations = ["CNN", "FOXNEWS", "MSNBC"]

        for station in stations:
            try:
                clips = await client.tv.search(
                    "election",
                    timespan="7d",
                    station=station,
                    max_results=5,
                )
                print(f"\n{station}: {len(clips)} clips about 'election'")
                if clips:
                    print(f"  First clip show: {clips[0].show_name}")
            except Exception as e:
                print(f"Error searching {station}: {e}")


async def get_timeline() -> None:
    """Get timeline of TV mentions."""
    print("\n" + "=" * 60)
    print("Example 3: TV Mention Timeline")
    print("=" * 60)

    async with GDELTClient() as client:
        try:
            timeline = await client.tv.timeline(
                "immigration",
                timespan="7d",
            )

            print("\nTimeline for 'immigration' (last 7 days):")
            print(f"Number of data points: {len(timeline.points)}")

            if timeline.points:
                # Show last 5 data points
                for point in timeline.points[-5:]:
                    print(f"  {point.date}: {point.count} mentions")
        except Exception as e:
            print(f"Error fetching timeline: {e}")


async def compare_stations() -> None:
    """Compare coverage across stations."""
    print("\n" + "=" * 60)
    print("Example 4: Station Comparison")
    print("=" * 60)

    async with GDELTClient() as client:
        try:
            chart = await client.tv.station_chart(
                "healthcare",
                timespan="7d",
            )

            print("\nStation coverage for 'healthcare':")
            for station in chart.stations[:10]:
                pct = f"{station.percentage:.1f}%" if station.percentage else "N/A"
                print(f"  {station.station}: {station.count} mentions ({pct})")
        except Exception as e:
            print(f"Error fetching station chart: {e}")


async def ai_enhanced_search() -> None:
    """Use AI-enhanced TV search."""
    print("\n" + "=" * 60)
    print("Example 5: AI-Enhanced Search")
    print("=" * 60)

    async with GDELTClient() as client:
        try:
            # TVAI provides AI-enhanced search capabilities
            clips = await client.tv_ai.search(
                "artificial intelligence impact on jobs",
                timespan="7d",
                max_results=5,
            )

            print(f"\nAI-enhanced search found {len(clips)} clips")
            for clip in clips[:3]:
                print(f"\n  Station: {clip.station}")
                print(f"  Show: {clip.show_name}")
                if clip.snippet:
                    print(f"  Snippet: {clip.snippet[:150]}...")
        except Exception as e:
            print(f"Error with AI-enhanced search: {e}")


async def main() -> None:
    """Run all examples."""
    await search_tv_clips()
    await search_by_station()
    await get_timeline()
    await compare_stations()
    await ai_enhanced_search()

    print("\n" + "=" * 60)
    print("TV API examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
