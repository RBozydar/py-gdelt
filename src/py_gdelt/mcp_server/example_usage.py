"""Example usage of GDELT MCP server functionality.

This script demonstrates the core functionality without using MCP decorators.
It shows what data the MCP tools would return when called by an AI agent.
"""

from __future__ import annotations

import asyncio

from py_gdelt.lookups.cameo import CAMEOCodes


async def example_cameo_lookup() -> None:
    """Example: Look up CAMEO codes for protests."""
    print("\n=== Example: CAMEO Code Lookup (protest) ===")

    cameo = CAMEOCodes()
    matching_codes = cameo.search("protest")

    print(f"Found {len(matching_codes)} matching codes")
    print("\nFirst 3 codes:")
    for code in matching_codes[:3]:
        entry = cameo.get(code)
        goldstein = cameo.get_goldstein(code)
        if entry:
            print(f"  - {code}: {entry.name}")
            print(f"    Description: {entry.description}")
            print(f"    Goldstein: {goldstein.value if goldstein else 'N/A'}")
            print(f"    Conflict: {cameo.is_conflict(code)}")
            print()


async def example_events_query() -> None:
    """Example: Query events (requires GDELT API access)."""
    print("\n=== Example: Query Events (USA-RUS conflict) ===")
    print("(Skipped - requires API access)")
    print("Would query:")
    print("  - actor1_country: USA")
    print("  - actor2_country: RUS")
    print("  - event_type: conflict")
    print("  - days_back: 30")
    print("\nExpected output: List of events with:")
    print("  - global_event_id")
    print("  - date")
    print("  - actor details")
    print("  - event_code and name")
    print("  - goldstein_scale")
    print("  - source_url")


async def main() -> None:
    """Run examples."""
    print("GDELT MCP Server - Example Functionality")
    print("=" * 50)

    # This example works without API access (just uses lookup data)
    await example_cameo_lookup()

    # This shows what the events query would do
    await example_events_query()

    print("\n" + "=" * 50)
    print("Examples completed!")
    print("\nNote: Full examples require GDELT API access.")
    print("Run the MCP server with: python server.py")


if __name__ == "__main__":
    asyncio.run(main())
