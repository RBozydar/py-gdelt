"""Shared utilities for lookup data loading."""

from __future__ import annotations

import functools
import json
from importlib.resources import files
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from collections.abc import Sequence


__all__ = ["fuzzy_search", "is_fuzzy_available", "load_lookup_json", "resolve_fuzzy_mode"]


def resolve_fuzzy_mode(fuzzy: bool | None) -> bool:
    """Resolve fuzzy matching mode and validate availability.

    Args:
        fuzzy: Fuzzy mode. None auto-detects, True forces fuzzy, False forces substring.

    Returns:
        True if fuzzy matching should be used, False otherwise.

    Raises:
        ImportError: If fuzzy=True but rapidfuzz is not installed.
    """
    use_fuzzy = fuzzy if fuzzy is not None else is_fuzzy_available()
    if use_fuzzy and not is_fuzzy_available():
        msg = "Fuzzy matching requires rapidfuzz. Install with: pip install py-gdelt[fuzzy]"
        raise ImportError(msg)
    return use_fuzzy


@functools.lru_cache(maxsize=1)
def is_fuzzy_available() -> bool:
    """Check if rapidfuzz is installed.

    The result is cached for performance.

    Returns:
        True if rapidfuzz is installed, False otherwise.
    """
    try:
        import rapidfuzz

        _ = rapidfuzz  # Avoid unused import warning
    except ImportError:
        return False
    else:
        return True


def fuzzy_search(
    query: str,
    candidates: Sequence[str],
    threshold: int = 60,
    limit: int | None = None,
) -> list[tuple[str, float, int]]:
    """Perform fuzzy search using rapidfuzz.

    Uses rapidfuzz.fuzz.WRatio for weighted ratio matching.

    Args:
        query: Search query string.
        candidates: Sequence of candidate strings to match against.
        threshold: Minimum score (0-100) for a match to be included.
        limit: Maximum number of results to return. None for unlimited.

    Returns:
        List of (candidate, score, index) tuples sorted by score descending.
        The index is the position of the match in the original candidates sequence,
        allowing callers to map results back to codes without reverse-mapping text.

    Raises:
        ImportError: If rapidfuzz is not installed.
    """
    from rapidfuzz import fuzz, process

    results = process.extract(
        query,
        candidates,
        scorer=fuzz.WRatio,
        score_cutoff=threshold,
        limit=limit,
    )

    # process.extract returns list of (match, score, index) tuples
    return [(match, score, idx) for match, score, idx in results]


def load_lookup_json(filename: str) -> dict[str, Any]:
    """Load JSON data from package lookup data directory.

    Args:
        filename: Name of the JSON file in the data directory.

    Returns:
        Parsed JSON data as a dictionary.
    """
    data_path = files("py_gdelt.lookups.data").joinpath(filename)
    return json.loads(data_path.read_text())  # type: ignore[no-any-return]
