"""Shared utilities for lookup data loading."""

from __future__ import annotations

import json
from importlib.resources import files
from typing import Any


__all__ = ["load_lookup_json"]


def load_lookup_json(filename: str) -> dict[str, Any]:
    """Load JSON data from package lookup data directory.

    Args:
        filename: Name of the JSON file in the data directory.

    Returns:
        Parsed JSON data as a dictionary.
    """
    data_path = files("py_gdelt.lookups.data").joinpath(filename)
    return json.loads(data_path.read_text())  # type: ignore[no-any-return]
