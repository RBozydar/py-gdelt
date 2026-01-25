#!/usr/bin/env python3
"""One-time script to extract examples and usage_notes from CAMEO verb codebook.

This script parses the markdown file at gdelt_docs/cameo_docs/chapter_2_verb_codebook.md
and enriches the existing cameo_codes.json with usage_notes and examples fields.

Usage:
    python scripts/enrich_cameo_codes.py
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Paths relative to repository root
REPO_ROOT = Path(__file__).parent.parent
MARKDOWN_PATH = REPO_ROOT / "gdelt_docs" / "cameo_docs" / "chapter_2_verb_codebook.md"
JSON_PATH = REPO_ROOT / "src" / "py_gdelt" / "lookups" / "data" / "cameo_codes.json"


def parse_markdown_entries(content: str) -> dict[str, dict[str, Any]]:
    """Parse CAMEO code entries from markdown content.

    Args:
        content: Raw markdown content from the verb codebook.

    Returns:
        Dictionary mapping CAMEO codes to their extracted data.
    """
    entries: dict[str, dict[str, Any]] = {}
    current_code: str | None = None
    current_usage_notes: list[str] = []
    current_examples: list[str] = []

    # Pattern to match table rows: | Field | Value |
    row_pattern = re.compile(r"^\|\s*([^|]+?)\s*\|\s*(.+?)\s*\|$")
    # Pattern to detect table separator rows (|---|---|)
    separator_pattern = re.compile(r"^\|[\s-]+\|[\s-]+\|$")

    lines = content.splitlines()
    for i, line in enumerate(lines):
        # Check if this line is a separator row
        if separator_pattern.match(line):
            # Look at the previous line to see if it starts a new entry
            if i > 0:
                prev_match = row_pattern.match(lines[i - 1])
                if prev_match:
                    prev_field = prev_match.group(1).strip().lower()
                    prev_value = prev_match.group(2).strip()
                    # If previous row was CAMEO/NAME with a numeric value,
                    # we've already started a new entry when processing that row.
                    # If it was NAME with a non-numeric value (entry without code),
                    # save the previous entry now.
                    if (
                        prev_field in ("cameo", "name")
                        and not re.match(r"^\d+$", prev_value)
                        and current_code is not None
                    ):
                        _save_entry(
                            entries,
                            current_code,
                            current_usage_notes,
                            current_examples,
                        )
                        current_code = None
                        current_usage_notes = []
                        current_examples = []
            continue

        match = row_pattern.match(line)
        if not match:
            continue

        field = match.group(1).strip()
        value = match.group(2).strip()

        # Skip separator-like content
        if field.startswith("-") or value.startswith("-"):
            continue

        field_lower = field.lower()

        # Check for code field (CAMEO or NAME with a numeric value)
        if field_lower in ("cameo", "name"):
            # Check if value looks like a code (digits only)
            if re.match(r"^\d+$", value):
                # Save previous entry if exists
                if current_code is not None:
                    _save_entry(entries, current_code, current_usage_notes, current_examples)

                current_code = value
                current_usage_notes = []
                current_examples = []
                continue

            # Check for all-caps "NAME" with non-numeric value
            # This indicates a new entry header without explicit code number
            # (e.g., "| NAME | Engage in symbolic act |" for code 017)
            # "Name" (mixed case) is just the code name field, not a new entry
            if field == "NAME" and current_code is not None:
                _save_entry(entries, current_code, current_usage_notes, current_examples)
                current_code = None
                current_usage_notes = []
                current_examples = []
            continue

        # Extract usage notes
        if field_lower == "usage notes" and current_code is not None and value:
            current_usage_notes.append(value)

        # Extract examples (skip Example Note rows)
        if field_lower == "example" and current_code is not None and value:
            current_examples.append(value)

    # Save the last entry
    if current_code is not None:
        _save_entry(entries, current_code, current_usage_notes, current_examples)

    return entries


def _save_entry(
    entries: dict[str, dict[str, Any]],
    code: str,
    usage_notes: list[str],
    examples: list[str],
) -> None:
    """Save a parsed entry to the entries dictionary.

    Args:
        entries: Dictionary to store entries in.
        code: The CAMEO code.
        usage_notes: List of usage note strings.
        examples: List of example strings.
    """
    entry: dict[str, Any] = {}

    if usage_notes:
        # Concatenate multiple usage notes with space
        entry["usage_notes"] = " ".join(usage_notes)
    else:
        entry["usage_notes"] = None

    if examples:
        entry["examples"] = examples

    if entry:
        entries[code] = entry


def merge_enrichment(
    existing: dict[str, dict[str, Any]], enrichment: dict[str, dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    """Merge enrichment data into existing JSON data.

    Args:
        existing: Existing cameo_codes.json data.
        enrichment: Parsed enrichment data from markdown.

    Returns:
        Merged data with enrichment fields added.
    """
    merged = {}
    codes_enriched = 0

    for code, data in existing.items():
        merged[code] = dict(data)  # Copy existing data

        if code in enrichment:
            enrich_data = enrichment[code]

            # Add usage_notes if present
            if enrich_data.get("usage_notes") is not None:
                merged[code]["usage_notes"] = enrich_data["usage_notes"]

            # Add examples if present
            if "examples" in enrich_data:
                merged[code]["examples"] = enrich_data["examples"]

            codes_enriched += 1

    # Check for codes in enrichment not in existing (potential mismatches)
    codes_not_found = [code for code in enrichment if code not in existing]

    logger.info("Enriched %d codes", codes_enriched)
    if codes_not_found:
        logger.warning(
            "Found %d codes in markdown not in JSON: %s",
            len(codes_not_found),
            codes_not_found[:10],
        )

    return merged


def main() -> None:
    """Main entry point for the enrichment script."""
    logger.info("Reading markdown file: %s", MARKDOWN_PATH)
    if not MARKDOWN_PATH.exists():
        logger.error("Markdown file not found: %s", MARKDOWN_PATH)
        return

    content = MARKDOWN_PATH.read_text(encoding="utf-8")
    logger.info("Parsing CAMEO entries from markdown...")
    enrichment = parse_markdown_entries(content)
    logger.info("Parsed %d entries from markdown", len(enrichment))

    logger.info("Reading existing JSON: %s", JSON_PATH)
    if not JSON_PATH.exists():
        logger.error("JSON file not found: %s", JSON_PATH)
        return

    with JSON_PATH.open(encoding="utf-8") as f:
        existing = json.load(f)
    logger.info("Loaded %d codes from JSON", len(existing))

    logger.info("Merging enrichment data...")
    merged = merge_enrichment(existing, enrichment)

    logger.info("Writing updated JSON...")
    with JSON_PATH.open("w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)
        f.write("\n")  # Add trailing newline

    logger.info("Done! Updated %s", JSON_PATH)


if __name__ == "__main__":
    main()
