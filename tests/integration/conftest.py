"""Integration test configuration.

Note: pytest markers are defined in pyproject.toml, not here.

We use pytest-asyncio (not anyio) because:
- pytest-asyncio provides better IDE support and clearer error messages
- asyncio_mode="auto" in pyproject.toml auto-detects async tests
- No need for explicit anyio_backend fixture

Run integration tests:
    pytest tests/integration/ -m integration

Skip integration tests:
    pytest tests/ -m "not integration"
"""

from collections.abc import AsyncIterator

import pytest

from py_gdelt import GDELTClient


@pytest.fixture
async def gdelt_client() -> AsyncIterator[GDELTClient]:
    """Provide initialized GDELTClient for integration tests.

    Yields:
        GDELTClient: Configured client instance for API calls.
    """
    async with GDELTClient() as client:
        yield client
