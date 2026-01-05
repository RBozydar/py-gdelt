"""Utility functions for the py-gdelt library."""

from py_gdelt.utils.dedup import DedupeStrategy, deduplicate
from py_gdelt.utils.streaming import ResultStream


__all__ = [
    "DedupeStrategy",
    "ResultStream",
    "deduplicate",
]
