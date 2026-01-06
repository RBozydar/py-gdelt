"""Tests for streaming utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest
from pydantic import BaseModel

from py_gdelt.utils.streaming import ResultStream


if TYPE_CHECKING:
    from collections.abc import AsyncIterator


# Basic Iteration Tests
@pytest.mark.asyncio
async def test_async_iteration() -> None:
    """Test basic async iteration."""

    async def gen() -> AsyncIterator[int]:
        for i in range(3):
            yield i

    stream = ResultStream(gen())
    items = [item async for item in stream]
    assert items == [0, 1, 2]
    assert stream.exhausted


@pytest.mark.asyncio
async def test_to_list() -> None:
    """Test materialization to list."""

    async def gen() -> AsyncIterator[int]:
        for i in range(5):
            yield i

    stream = ResultStream(gen())
    result = await stream.to_list()
    assert result == [0, 1, 2, 3, 4]
    assert stream.exhausted


@pytest.mark.asyncio
async def test_to_list_empty() -> None:
    """Test to_list with empty stream."""

    async def gen() -> AsyncIterator[int]:
        return
        yield

    stream = ResultStream(gen())
    result = await stream.to_list()
    assert result == []


@pytest.mark.asyncio
async def test_to_list_after_exhausted() -> None:
    """Test to_list raises after stream exhausted."""

    async def gen() -> AsyncIterator[int]:
        yield 1

    stream = ResultStream(gen())
    await stream.to_list()

    with pytest.raises(RuntimeError, match="exhausted"):
        await stream.to_list()


# to_dataframe Tests
@pytest.mark.asyncio
async def test_to_dataframe_pydantic() -> None:
    """Test conversion of Pydantic models."""

    class Item(BaseModel):
        name: str
        value: int

    async def gen() -> AsyncIterator[Item]:
        yield Item(name="a", value=1)
        yield Item(name="b", value=2)

    stream = ResultStream(gen())
    df = await stream.to_dataframe()
    assert len(df) == 2
    assert list(df.columns) == ["name", "value"]


@pytest.mark.asyncio
async def test_to_dataframe_dataclass() -> None:
    """Test conversion of dataclasses."""

    @dataclass
    class Item:
        name: str
        value: int

    async def gen() -> AsyncIterator[Item]:
        yield Item(name="x", value=10)

    stream = ResultStream(gen())
    df = await stream.to_dataframe()
    assert len(df) == 1


@pytest.mark.asyncio
async def test_to_dataframe_dict() -> None:
    """Test conversion of dicts."""

    async def gen() -> AsyncIterator[dict[str, int]]:
        yield {"a": 1}
        yield {"a": 2}

    stream = ResultStream(gen())
    df = await stream.to_dataframe()
    assert len(df) == 2


@pytest.mark.asyncio
async def test_to_dataframe_empty() -> None:
    """Test empty stream returns empty DataFrame."""

    async def gen() -> AsyncIterator[dict[str, int]]:
        return
        yield

    stream = ResultStream(gen())
    df = await stream.to_dataframe()
    assert len(df) == 0


@pytest.mark.asyncio
async def test_to_dataframe_unsupported_type() -> None:
    """Test unsupported types raise TypeError."""

    async def gen() -> AsyncIterator[str]:
        yield "string"

    stream = ResultStream(gen())
    with pytest.raises(TypeError, match="Cannot convert"):
        await stream.to_dataframe()


# first() and take() Tests
@pytest.mark.asyncio
async def test_first() -> None:
    """Test getting first item."""

    async def gen() -> AsyncIterator[str]:
        yield "a"
        yield "b"

    stream = ResultStream(gen())
    first = await stream.first()
    assert first == "a"
    # Stream not exhausted yet
    assert not stream.exhausted


@pytest.mark.asyncio
async def test_first_empty() -> None:
    """Test first on empty stream."""

    async def gen() -> AsyncIterator[str]:
        return
        yield

    stream = ResultStream(gen())
    assert await stream.first() is None


@pytest.mark.asyncio
async def test_take() -> None:
    """Test taking n items."""

    async def gen() -> AsyncIterator[int]:
        for i in range(10):
            yield i

    stream = ResultStream(gen())
    taken = await stream.take(3)
    assert taken == [0, 1, 2]


@pytest.mark.asyncio
async def test_take_more_than_available() -> None:
    """Test take with n > stream length."""

    async def gen() -> AsyncIterator[int]:
        yield 1
        yield 2

    stream = ResultStream(gen())
    taken = await stream.take(10)
    assert taken == [1, 2]


# count() Test
@pytest.mark.asyncio
async def test_count() -> None:
    """Test counting items."""

    async def gen() -> AsyncIterator[int]:
        for i in range(5):
            yield i

    stream = ResultStream(gen())
    count = await stream.count()
    assert count == 5
    assert stream.exhausted


# Additional edge case tests
@pytest.mark.asyncio
async def test_exhausted_property_initial() -> None:
    """Test exhausted property is False initially."""

    async def gen() -> AsyncIterator[int]:
        yield 1

    stream = ResultStream(gen())
    assert not stream.exhausted


@pytest.mark.asyncio
async def test_iteration_after_first() -> None:
    """Test that iteration continues after calling first()."""

    async def gen() -> AsyncIterator[int]:
        for i in range(5):
            yield i

    stream = ResultStream(gen())
    first = await stream.first()
    assert first == 0

    remaining = [item async for item in stream]
    assert remaining == [1, 2, 3, 4]


@pytest.mark.asyncio
async def test_take_zero() -> None:
    """Test take with n=0."""

    async def gen() -> AsyncIterator[int]:
        yield 1
        yield 2

    stream = ResultStream(gen())
    taken = await stream.take(0)
    assert taken == []


@pytest.mark.asyncio
async def test_to_dataframe_with_kwargs() -> None:
    """Test to_dataframe passes kwargs to DataFrame constructor."""

    async def gen() -> AsyncIterator[dict[str, int]]:
        yield {"a": 1}
        yield {"a": 2}

    stream = ResultStream(gen())
    df = await stream.to_dataframe(index=[10, 20])
    assert list(df.index) == [10, 20]
