#!/usr/bin/env python3
"""Regenerate countries.json from geonamescache data.

This script fetches country data from geonamescache and generates
the countries.json lookup file with FIPS codes, ISO codes, names,
and regional classifications.

Usage:
    uv run python scripts/regenerate_countries.py
"""

from __future__ import annotations

import json
from pathlib import Path

from geonamescache import GeonamesCache


LOOKUPS_DATA = Path("src/py_gdelt/lookups/data")

# Map continent codes to region names
CONTINENT_TO_REGION: dict[str, str] = {
    "AF": "Africa",
    "AS": "Asia",
    "EU": "Europe",
    "NA": "North America",
    "SA": "South America",
    "OC": "Oceania",
    "AN": "Antarctica",
}

# FIPS codes for Middle East countries (override continent-based region)
MIDDLE_EAST_FIPS: list[str] = [
    "IR",  # Iran
    "IZ",  # Iraq
    "IS",  # Israel
    "SA",  # Saudi Arabia
    "AE",  # United Arab Emirates
    "KU",  # Kuwait
    "BA",  # Bahrain
    "QA",  # Qatar
    "LE",  # Lebanon
    "SY",  # Syria
    "JO",  # Jordan
    "YM",  # Yemen
    "MU",  # Oman
]


def regenerate_countries() -> None:
    """Regenerate countries.json from geonamescache data."""
    gc = GeonamesCache()
    countries = gc.get_countries()

    output: dict[str, dict[str, str | None]] = {}

    for data in countries.values():
        fips = data.get("fips")
        if not fips:
            continue

        # Determine region from continent, with Middle East override
        region = CONTINENT_TO_REGION.get(data.get("continentcode", ""), "Other")
        if fips in MIDDLE_EAST_FIPS:
            region = "Middle East"

        output[fips] = {
            "iso3": data.get("iso3"),
            "iso2": data.get("iso"),
            "name": data.get("name"),
            "full_name": None,
            "region": region,
        }

    # Sort by FIPS code for consistent output
    output = dict(sorted(output.items()))

    # Write to file
    output_path = LOOKUPS_DATA / "countries.json"
    output_path.write_text(json.dumps(output, indent=2) + "\n")
    print(f"Wrote {len(output)} countries to {output_path}")


if __name__ == "__main__":
    regenerate_countries()
