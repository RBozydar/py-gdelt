#!/usr/bin/env python3
"""Example: Query GDELT GEO 2.0 API for geographic data.

Demonstrates:
- Basic geographic search
- Bounding box filtering
- GeoJSON output for mapping
- Location analysis
- Proper error handling with specific exceptions
"""

import asyncio

from py_gdelt import GDELTClient
from py_gdelt.exceptions import APIError, RateLimitError


async def search_locations() -> None:
    """Search for locations mentioned in news."""
    print("=" * 60)
    print("Example 1: Basic Geographic Search")
    print("=" * 60)

    async with GDELTClient() as client:
        try:
            # Search for earthquake-related locations
            result = await client.geo.search(
                "earthquake",
                timespan="7d",
                max_points=50,
            )

            print(f"\nFound {len(result.points)} locations for 'earthquake'")
            print("\nTop locations by article count:")

            # Sort by count
            sorted_points = sorted(result.points, key=lambda p: p.count, reverse=True)
            for point in sorted_points[:10]:
                print(f"  - {point.name or 'Unknown'}: {point.count} articles")
                print(f"    Coordinates: ({point.lat:.2f}, {point.lon:.2f})")
        except RateLimitError as e:
            print(f"Rate limit exceeded: {e}")
            if e.retry_after:
                print(f"Please retry after {e.retry_after} seconds")
        except APIError as e:
            print(f"API error searching locations: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


async def search_with_bounding_box() -> None:
    """Search within a geographic bounding box."""
    print("\n" + "=" * 60)
    print("Example 2: Bounding Box Search (Europe)")
    print("=" * 60)

    async with GDELTClient() as client:
        try:
            # Search within Europe bounding box (min_lat, min_lon, max_lat, max_lon)
            europe_bbox = (35.0, -10.0, 70.0, 40.0)

            result = await client.geo.search(
                "energy crisis",
                timespan="7d",
                bounding_box=europe_bbox,
                max_points=30,
            )

            print(f"\nFound {len(result.points)} locations in Europe for 'energy crisis'")
            for point in result.points[:10]:
                print(
                    f"  - {point.name}: {point.count} articles at ({point.lat:.2f}, {point.lon:.2f})",
                )
        except RateLimitError as e:
            print(f"Rate limit exceeded: {e}")
            if e.retry_after:
                print(f"Please retry after {e.retry_after} seconds")
        except APIError as e:
            print(f"API error searching with bounding box: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


async def get_geojson_output() -> None:
    """Get raw GeoJSON for mapping libraries."""
    print("\n" + "=" * 60)
    print("Example 3: GeoJSON Output")
    print("=" * 60)

    async with GDELTClient() as client:
        try:
            # Get GeoJSON format for use with mapping libraries
            geojson = await client.geo.to_geojson(
                "climate protest",
                timespan="30d",
                max_points=100,
            )

            print(f"\nGeoJSON type: {geojson.get('type')}")
            features = geojson.get("features", [])
            print(f"Number of features: {len(features)}")

            if features:
                print("\nFirst feature:")
                feat = features[0]
                print(f"  Geometry: {feat.get('geometry', {}).get('type')}")
                print(f"  Properties: {list(feat.get('properties', {}).keys())}")
        except RateLimitError as e:
            print(f"Rate limit exceeded: {e}")
            if e.retry_after:
                print(f"Please retry after {e.retry_after} seconds")
        except APIError as e:
            print(f"API error fetching GeoJSON: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


async def main() -> None:
    """Run all examples."""
    await search_locations()
    await search_with_bounding_box()
    await get_geojson_output()

    print("\n" + "=" * 60)
    print("GEO API examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
