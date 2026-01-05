"""Async best practices: concurrent API calls with asyncio.gather().

This example demonstrates how to leverage the async design of py-gdelt
to make concurrent API calls, significantly improving performance when
you need data from multiple endpoints or queries.

Key concepts demonstrated:
- Using asyncio.gather() for concurrent requests
- Comparing sequential vs concurrent execution times
- Proper error handling with return_exceptions=True
- Batching requests to avoid overwhelming the API
"""

import asyncio
import time
from datetime import date, timedelta

from py_gdelt import GDELTClient
from py_gdelt.exceptions import APIError, DataError, RateLimitError
from py_gdelt.filters import DateRange, DocFilter, EventFilter


async def sequential_example() -> None:
    """Demonstrate sequential API calls (slower approach)."""
    print("=" * 60)
    print("Sequential API Calls (One at a Time)")
    print("=" * 60)

    async with GDELTClient() as client:
        queries = ["climate change", "artificial intelligence", "renewable energy"]

        start_time = time.perf_counter()

        results = []
        for query in queries:
            try:
                doc_filter = DocFilter(
                    query=query,
                    timespan="24h",
                    max_results=5,
                )
                articles = await client.doc.query(doc_filter)
                results.append((query, len(articles)))
                print(f"  '{query}': {len(articles)} articles")
            except APIError as e:
                print(f"  '{query}': API error - {e}")
                results.append((query, 0))

        elapsed = time.perf_counter() - start_time
        print(f"\nSequential execution time: {elapsed:.2f}s")
        return elapsed


async def concurrent_example() -> float:
    """Demonstrate concurrent API calls using asyncio.gather()."""
    print("\n" + "=" * 60)
    print("Concurrent API Calls (Using asyncio.gather)")
    print("=" * 60)

    async with GDELTClient() as client:
        queries = ["climate change", "artificial intelligence", "renewable energy"]

        async def search_articles(query: str) -> tuple[str, int]:
            """Search for articles with a specific query."""
            try:
                doc_filter = DocFilter(
                    query=query,
                    timespan="24h",
                    max_results=5,
                )
                articles = await client.doc.query(doc_filter)
                return (query, len(articles))
            except APIError as e:
                print(f"  API error for '{query}': {e}")
                return (query, 0)

        start_time = time.perf_counter()

        # Run all searches concurrently
        results = await asyncio.gather(
            *[search_articles(q) for q in queries],
            return_exceptions=True,  # Don't let one failure cancel others
        )

        elapsed = time.perf_counter() - start_time

        # Process results
        for result in results:
            if isinstance(result, Exception):
                print(f"  Error: {result}")
            else:
                query, count = result
                print(f"  '{query}': {count} articles")

        print(f"\nConcurrent execution time: {elapsed:.2f}s")
        return elapsed


async def multi_endpoint_concurrent() -> None:
    """Demonstrate concurrent calls to different endpoints."""
    print("\n" + "=" * 60)
    print("Concurrent Multi-Endpoint Queries")
    print("=" * 60)

    async with GDELTClient() as client:
        yesterday = date(2026, 1, 1)

        async def get_events() -> str:
            """Query events endpoint."""
            try:
                event_filter = EventFilter(
                    date_range=DateRange(start=yesterday, end=yesterday),
                    actor1_country="USA",
                )
                events = await client.events.query(event_filter)
                return f"Events: {len(events)} records"
            except (DataError, APIError) as e:
                return f"Events: Error - {e}"

        async def get_doc_articles() -> str:
            """Query DOC API for articles."""
            try:
                doc_filter = DocFilter(
                    query="international relations",
                    timespan="24h",
                    max_results=10,
                )
                articles = await client.doc.query(doc_filter)
                return f"Articles: {len(articles)} results"
            except (RateLimitError, APIError) as e:
                return f"Articles: Error - {e}"

        async def get_geo_points() -> str:
            """Query GEO API for geographic data."""
            try:
                geo_result = await client.geo.search(
                    query="earthquake",
                    max_points=50,
                )
                points = geo_result.features if hasattr(geo_result, "features") else []
                return f"Geo points: {len(points)} locations"
            except (RateLimitError, APIError) as e:
                return f"Geo: Error - {e}"

        start_time = time.perf_counter()

        # Query multiple endpoints concurrently
        results = await asyncio.gather(
            get_events(),
            get_doc_articles(),
            get_geo_points(),
            return_exceptions=True,
        )

        elapsed = time.perf_counter() - start_time

        print("\nResults from concurrent endpoint queries:")
        for result in results:
            if isinstance(result, Exception):
                print(f"  Error: {result}")
            else:
                print(f"  {result}")

        print(f"\nTotal time for 3 endpoints: {elapsed:.2f}s")


async def batched_concurrent_queries() -> None:
    """Demonstrate batched concurrent queries to avoid rate limits."""
    print("\n" + "=" * 60)
    print("Batched Concurrent Queries (Rate-Limit Friendly)")
    print("=" * 60)

    async with GDELTClient() as client:
        # Query multiple days of data
        base_date = date(2026, 1, 1)
        dates = [base_date - timedelta(days=i) for i in range(6)]

        async def get_events_for_date(query_date: date) -> tuple[date, int]:
            """Get event count for a specific date."""
            try:
                event_filter = EventFilter(
                    date_range=DateRange(start=query_date, end=query_date),
                    actor1_country="RUS",
                )
                events = await client.events.query(event_filter)
                return (query_date, len(events))
            except (DataError, APIError) as e:
                print(f"  {query_date}: Error - {e}")
                return (query_date, 0)

        # Process in batches of 3 to be rate-limit friendly
        batch_size = 3
        all_results = []

        start_time = time.perf_counter()

        for i in range(0, len(dates), batch_size):
            batch = dates[i : i + batch_size]
            print(f"\nProcessing batch {i // batch_size + 1}...")

            batch_results = await asyncio.gather(
                *[get_events_for_date(d) for d in batch],
                return_exceptions=True,
            )

            for result in batch_results:
                if isinstance(result, Exception):
                    print(f"  Error: {result}")
                else:
                    query_date, count = result
                    print(f"  {query_date}: {count} events")
                    all_results.append(result)

            # Small delay between batches to be respectful to the API
            if i + batch_size < len(dates):
                await asyncio.sleep(0.5)

        elapsed = time.perf_counter() - start_time

        total_events = sum(count for _, count in all_results if isinstance(count, int))
        print(f"\nTotal events across {len(dates)} days: {total_events}")
        print(f"Batched execution time: {elapsed:.2f}s")


async def error_handling_patterns() -> None:
    """Demonstrate proper error handling with concurrent calls."""
    print("\n" + "=" * 60)
    print("Error Handling in Concurrent Calls")
    print("=" * 60)

    async with GDELTClient() as client:

        async def safe_query(query: str) -> dict:
            """Wrap query in comprehensive error handling."""
            try:
                doc_filter = DocFilter(
                    query=query,
                    timespan="24h",
                    max_results=5,
                )
                articles = await client.doc.query(doc_filter)
                return {"query": query, "status": "success", "count": len(articles)}
            except RateLimitError as e:
                return {
                    "query": query,
                    "status": "rate_limited",
                    "retry_after": e.retry_after,
                }
            except APIError as e:
                return {"query": query, "status": "api_error", "error": str(e)}
            except Exception as e:
                return {"query": query, "status": "unexpected_error", "error": str(e)}

        queries = ["technology", "politics", "science", "sports"]

        results = await asyncio.gather(*[safe_query(q) for q in queries])

        print("\nResults with structured error handling:")
        for result in results:
            status = result["status"]
            query = result["query"]
            if status == "success":
                print(f"  '{query}': {result['count']} articles")
            elif status == "rate_limited":
                print(f"  '{query}': Rate limited (retry after {result.get('retry_after')}s)")
            else:
                print(f"  '{query}': {status} - {result.get('error', 'Unknown')}")


async def main() -> None:
    """Run all async best practices examples."""
    print("\n" + "=" * 60)
    print("GDELT Python Client - Async Best Practices")
    print("=" * 60)
    print("\nThis example demonstrates how to use asyncio.gather() for")
    print("concurrent API calls, significantly improving performance.\n")

    # Compare sequential vs concurrent
    seq_time = await sequential_example()
    conc_time = await concurrent_example()

    if seq_time > 0 and conc_time > 0:
        speedup = seq_time / conc_time
        print(f"\nSpeedup from concurrency: {speedup:.1f}x faster")

    # Multi-endpoint concurrent queries
    await multi_endpoint_concurrent()

    # Batched queries for rate-limit friendliness
    await batched_concurrent_queries()

    # Error handling patterns
    await error_handling_patterns()

    print("\n" + "=" * 60)
    print("Key Takeaways:")
    print("=" * 60)
    print("1. Use asyncio.gather() to run independent queries concurrently")
    print("2. Use return_exceptions=True to prevent one failure from canceling all")
    print("3. Batch requests to avoid overwhelming the API with rate limits")
    print("4. Wrap queries in try/except to handle errors gracefully")
    print("5. Consider adding small delays between batches for API friendliness")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
