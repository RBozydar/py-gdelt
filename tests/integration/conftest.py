"""Integration test configuration.

Note: pytest markers are defined in pyproject.toml, not here.
The anyio_backend fixture is NOT used - we use pytest-asyncio with asyncio_mode="auto".
"""

import pytest

from py_gdelt import GDELTClient


@pytest.fixture
async def gdelt_client():
    """Provide initialized GDELTClient for integration tests.

    Usage:
        async def test_something(gdelt_client):
            result = await gdelt_client.doc.search("test")
    """
    async with GDELTClient() as client:
        yield client
