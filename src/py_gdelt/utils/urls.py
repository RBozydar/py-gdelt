"""URL compatibility for GDELT data manifests."""

from __future__ import annotations


def normalize_data_url(url: str) -> str:
    """Upgrade legacy GDELT data URLs without rewriting other hosts.

    Args:
        url: URL from a manifest or caller.

    Returns:
        HTTPS URL for the GDELT data host, otherwise the original URL.
    """
    if url.startswith("http://data.gdeltproject.org/"):
        return "https://" + url.removeprefix("http://")
    return url
