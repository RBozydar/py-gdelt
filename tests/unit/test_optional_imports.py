"""Regression tests for optional BigQuery import boundaries."""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from pathlib import Path


SRC_DIR = Path(__file__).resolve().parents[2] / "src"

BLOCK_GOOGLE_IMPORTS = """
import importlib.abc
import sys

for module_name in list(sys.modules):
    if module_name == "google" or module_name.startswith("google."):
        del sys.modules[module_name]


class BlockGoogleImports(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "google" or fullname.startswith("google."):
            raise ImportError(f"blocked optional Google import: {fullname}")
        return None


sys.meta_path.insert(0, BlockGoogleImports())
"""


def _run_python_with_google_blocked(code: str) -> subprocess.CompletedProcess[str]:
    """Run a clean Python subprocess that rejects Google SDK imports."""
    env = os.environ.copy()
    python_path = str(SRC_DIR)
    if env.get("PYTHONPATH"):
        python_path = f"{python_path}{os.pathsep}{env['PYTHONPATH']}"
    env["PYTHONPATH"] = python_path
    env.pop("GDELT_BIGQUERY_PROJECT", None)
    env.pop("GDELT_BIGQUERY_CREDENTIALS", None)
    command = f"{textwrap.dedent(BLOCK_GOOGLE_IMPORTS)}\n{textwrap.dedent(code)}"

    return subprocess.run(  # noqa: S603
        [sys.executable, "-c", command],
        capture_output=True,
        check=False,
        env=env,
        text=True,
        timeout=20,
    )


def test_base_imports_and_doc_client_do_not_require_google() -> None:
    """Base package imports and DOC client access work without Google SDK imports."""
    completed = _run_python_with_google_blocked(
        """
        import asyncio
        import py_gdelt
        from py_gdelt import GDELTClient, GDELTSettings
        from py_gdelt.endpoints import DocEndpoint
        from py_gdelt.sources import DataFetcher, FileSource

        async def main():
            async with GDELTClient(settings=GDELTSettings()) as client:
                doc = client.doc
                assert isinstance(doc, DocEndpoint)

        asyncio.run(main())
        assert py_gdelt is not None
        assert GDELTClient is not None
        assert GDELTSettings is not None
        assert DataFetcher is not None
        assert FileSource is not None
        """,
    )

    assert completed.returncode == 0, completed.stderr + completed.stdout


def test_bigquery_source_lazy_export_requires_bigquery_extra() -> None:
    """Explicit BigQuery import fails with an actionable optional-extra message."""
    completed = _run_python_with_google_blocked(
        """
        for statement in (
            "from py_gdelt.sources import BigQuerySource",
            "from py_gdelt.sources.bigquery import BigQuerySource",
        ):
            try:
                exec(statement)
            except ImportError as exc:
                message = str(exc)
                assert "gdelt-py[bigquery]" in message
                assert "pip install" in message
            else:
                raise AssertionError(f"expected ImportError from {statement!r}")
        """,
    )

    assert completed.returncode == 0, completed.stderr + completed.stdout
