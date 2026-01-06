"""Streaming utilities for memory-efficient iteration over large datasets."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar


if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    import pandas as pd

T = TypeVar("T")


class ResultStream(Generic[T]):
    """
    Wrapper around async iterator with terminal methods for convenience.

    Provides memory-efficient streaming with optional materialization.

    Args:
        iterator: Async iterator to wrap

    Example:
        stream = ResultStream(async_generator())

        # Stream one at a time (memory efficient)
        async for item in stream:
            process(item)

        # Or materialize all at once
        items = await stream.to_list()

        # Or convert to DataFrame (requires pandas)
        df = await stream.to_dataframe()
    """

    def __init__(self, iterator: AsyncIterator[T]) -> None:
        self._iterator = iterator
        self._exhausted = False

    def __aiter__(self) -> AsyncIterator[T]:
        """Return self for async iteration."""
        return self

    async def __anext__(self) -> T:
        """Get next item from underlying iterator."""
        if self._exhausted:
            raise StopAsyncIteration
        try:
            return await self._iterator.__anext__()
        except StopAsyncIteration:
            self._exhausted = True
            raise

    async def to_list(self) -> list[T]:
        """
        Materialize all items into a list.

        Warning: This loads all items into memory. For large datasets,
        prefer streaming iteration.

        Returns:
            List of all items from the stream.

        Raises:
            RuntimeError: If stream has already been partially consumed.
        """
        if self._exhausted:
            msg = "Stream has been exhausted"
            raise RuntimeError(msg)

        items: list[T] = [item async for item in self]
        return items

    async def to_dataframe(self, **kwargs: Any) -> pd.DataFrame:
        """
        Convert stream items to a pandas DataFrame.

        Requires pandas to be installed. Items should be Pydantic models
        or dataclasses with a dict representation.

        Args:
            **kwargs: Additional arguments passed to pd.DataFrame constructor.

        Returns:
            DataFrame containing all items.

        Raises:
            ImportError: If pandas is not installed.
            RuntimeError: If stream has been exhausted.
        """
        try:
            import pandas as pd
        except ImportError:
            msg = "pandas is required for to_dataframe(). Install with: pip install pandas"
            raise ImportError(msg) from None

        items = await self.to_list()
        if not items:
            return pd.DataFrame()

        # Handle Pydantic models
        first = items[0]
        if hasattr(first, "model_dump"):
            records = [item.model_dump() for item in items]  # type: ignore[attr-defined]
        # Handle dataclasses
        elif hasattr(first, "__dataclass_fields__"):
            from dataclasses import asdict

            records = [asdict(item) for item in items]  # type: ignore[call-overload]
        # Handle dicts
        elif isinstance(first, dict):
            records = items
        else:
            msg = (
                f"Cannot convert {type(first).__name__} to DataFrame. "
                "Items must be Pydantic models, dataclasses, or dicts."
            )
            raise TypeError(msg)

        return pd.DataFrame(records, **kwargs)

    async def first(self) -> T | None:
        """
        Get the first item from the stream.

        Returns:
            First item, or None if stream is empty.

        Note:
            The stream can still be iterated after calling first(),
            but the first item will not be included.
        """
        try:
            return await self.__anext__()
        except StopAsyncIteration:
            return None

    async def take(self, n: int) -> list[T]:
        """
        Take up to n items from the stream.

        Args:
            n: Maximum number of items to take.

        Returns:
            List of up to n items.
        """
        items: list[T] = []
        count = 0
        async for item in self:
            if count >= n:
                break
            items.append(item)
            count += 1
        return items

    async def count(self) -> int:
        """
        Count items in the stream.

        Warning: This exhausts the stream.

        Returns:
            Total number of items.
        """
        count = 0
        async for _ in self:
            count += 1
        return count

    @property
    def exhausted(self) -> bool:
        """Check if stream has been fully consumed."""
        return self._exhausted


__all__ = [
    "ResultStream",
]
