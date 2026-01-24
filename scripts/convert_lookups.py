"""Convert GDELT lookup TSV files to JSON format.

This script converts tab-delimited lookup files from gdelt_docs/ to JSON files
in src/py_gdelt/lookups/data/.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any


logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent
SOURCE_DIR = PROJECT_ROOT / "gdelt_docs"
DEST_DIR = PROJECT_ROOT / "src" / "py_gdelt" / "lookups" / "data"

ENCODINGS = ["utf-8", "latin-1", "cp1252"]


def read_tsv_with_fallback(file_path: Path) -> list[str]:
    """Read TSV file with encoding fallback.

    Tries utf-8, then latin-1, then cp1252 until successful.

    Args:
        file_path: Path to the TSV file.

    Returns:
        List of lines from the file.

    Raises:
        RuntimeError: If all encodings fail.
    """
    for encoding in ENCODINGS:
        try:
            return file_path.read_text(encoding=encoding).strip().split("\n")
        except UnicodeDecodeError:
            continue

    msg = f"Failed to read {file_path} with encodings: {ENCODINGS}"
    raise RuntimeError(msg)


def convert_image_tags() -> None:
    """Convert LOOKUP-IMAGETAGS.TXT to image_tags.json."""
    logger.info("Converting LOOKUP-IMAGETAGS.TXT...")

    source = SOURCE_DIR / "LOOKUP-IMAGETAGS.TXT"
    dest = DEST_DIR / "image_tags.json"

    lines = read_tsv_with_fallback(source)

    result: dict[str, int] = {}
    for line in lines:
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) >= 2:
            tag = parts[0].strip()
            count = int(parts[1].strip())
            result[tag] = count

    with dest.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    logger.info("  ✓ Created %s (%d entries)", dest.relative_to(PROJECT_ROOT), len(result))


def convert_image_web_tags() -> None:
    """Convert LOOKUP-IMAGEWEBTAGS.TXT to image_web_tags.json."""
    logger.info("Converting LOOKUP-IMAGEWEBTAGS.TXT...")

    source = SOURCE_DIR / "LOOKUP-IMAGEWEBTAGS.TXT"
    dest = DEST_DIR / "image_web_tags.json"

    lines = read_tsv_with_fallback(source)

    result: dict[str, int] = {}
    for line in lines:
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) >= 2:
            tag = parts[0].strip()
            count = int(parts[1].strip())
            result[tag] = count

    with dest.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    logger.info("  ✓ Created %s (%d entries)", dest.relative_to(PROJECT_ROOT), len(result))


def convert_languages() -> None:
    """Convert LOOKUP-LANGUAGES.TXT to languages.json."""
    logger.info("Converting LOOKUP-LANGUAGES.TXT...")

    source = SOURCE_DIR / "LOOKUP-LANGUAGES.TXT"
    dest = DEST_DIR / "languages.json"

    lines = read_tsv_with_fallback(source)

    result: dict[str, str] = {}
    for line in lines:
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) >= 2:
            code = parts[0].strip()
            name = parts[1].strip()
            result[code] = name

    with dest.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    logger.info("  ✓ Created %s (%d entries)", dest.relative_to(PROJECT_ROOT), len(result))


def convert_gcam_codebook() -> None:
    """Convert GCAM-MASTER-CODEBOOK.txt to gcam_codebook.json."""
    logger.info("Converting GCAM-MASTER-CODEBOOK.txt...")

    source = SOURCE_DIR / "GCAM-MASTER-CODEBOOK.txt"
    dest = DEST_DIR / "gcam_codebook.json"

    lines = read_tsv_with_fallback(source)

    result: dict[str, dict[str, Any]] = {}

    for line in lines:
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 7:
            continue

        variable = parts[0].strip()

        # Skip header row
        if variable == "Variable":
            continue

        try:
            dictionary_id = int(parts[1].strip())
            dimension_id = int(parts[2].strip())
        except ValueError:
            continue

        data_type = parts[3].strip()
        language = parts[4].strip()
        dictionary_name = parts[5].strip()
        dimension_name = parts[6].strip()
        # Skip parts[7] (Citation column)

        result[variable] = {
            "dictionary_id": dictionary_id,
            "dimension_id": dimension_id,
            "data_type": data_type,
            "language": language,
            "dictionary_name": dictionary_name,
            "dimension_name": dimension_name,
        }

    with dest.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    logger.info("  ✓ Created %s (%d entries)", dest.relative_to(PROJECT_ROOT), len(result))


def main() -> None:
    """Run all conversions."""
    logger.info("Starting GDELT lookup conversions...\n")

    # Verify directories exist
    if not SOURCE_DIR.exists():
        msg = f"Source directory not found: {SOURCE_DIR}"
        raise RuntimeError(msg)

    if not DEST_DIR.exists():
        msg = f"Destination directory not found: {DEST_DIR}"
        raise RuntimeError(msg)

    # Run conversions
    convert_image_tags()
    convert_image_web_tags()
    convert_languages()
    convert_gcam_codebook()

    logger.info("\n✅ All conversions completed successfully!")


if __name__ == "__main__":
    main()
