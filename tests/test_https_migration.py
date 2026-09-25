"""Regression coverage for GDELT's data server HTTPS migration."""

from __future__ import annotations

import io
import zipfile
from typing import TYPE_CHECKING

import httpx
import pytest

from py_gdelt.config import GDELTSettings
from py_gdelt.sources.files import FileSource
from py_gdelt.utils.urls import normalize_data_url


if TYPE_CHECKING:
    from pathlib import Path


async def test_legacy_master_links_download_without_redirects(tmp_path: Path) -> None:
    """Fetch HTTPS manifests and upgrade old links before download and caching."""
    legacy_url = "http://data.gdeltproject.org/gdeltv2/20240101000000.export.CSV.zip"
    secure_url = legacy_url.replace("http:", "https:", 1)
    requests: list[httpx.Request] = []
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w") as zipped:
        zipped.writestr("data.csv", "event data")

    def respond(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.scheme == "http":
            return httpx.Response(
                301, headers={"location": str(request.url.copy_with(scheme="https"))}
            )
        if request.url.path.endswith(".txt"):
            return httpx.Response(200, text=f"1 hash {legacy_url}\n{legacy_url}\n")
        return httpx.Response(200, content=archive.getvalue())

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        source = FileSource(settings=GDELTSettings(cache_dir=tmp_path), client=client)
        assert await source.get_master_file_list(include_translation=True) == [secure_url] * 4
        assert await source.download_and_extract(legacy_url) == b"event data"
        assert await source.download_and_extract(secure_url) == b"event data"
        assert await source.get_master_file_list(include_translation=True) == [secure_url] * 4
        assert len(requests) == 3
        assert all(request.url.scheme == "https" for request in requests)


@pytest.mark.parametrize(
    "url",
    [
        "https://data.gdeltproject.org/gdeltv2/file.zip",
        "http://example.com/file.zip",
        "http://data.gdeltproject.org.evil.example/file.zip",
        "http://data.gdeltproject.org@evil.example/file.zip",
        "ftp://data.gdeltproject.org/file.zip",
    ],
)
def test_normalization_preserves_other_urls(url: str) -> None:
    """Canonicalization must not broaden URL trust to other hosts or schemes."""
    assert normalize_data_url(url) == url
