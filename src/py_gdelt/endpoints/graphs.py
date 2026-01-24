"""Graph datasets endpoint for GDELT data.

This module provides the GraphEndpoint class for querying GDELT's graph datasets
including GQG (Quotation Graph), GEG (Entity Graph), GFG (Frontpage Graph),
GGG (Geographic Graph), GEMG (Embedded Metadata Graph), and GAL (Article List).
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Literal

from py_gdelt.models.common import FetchResult
from py_gdelt.parsers import graphs as graph_parsers


if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from py_gdelt.filters import (
        GALFilter,
        GEGFilter,
        GEMGFilter,
        GFGFilter,
        GGGFilter,
        GQGFilter,
    )
    from py_gdelt.models.graphs import (
        GALRecord,
        GEGRecord,
        GEMGRecord,
        GFGRecord,
        GGGRecord,
        GQGRecord,
    )
    from py_gdelt.sources.fetcher import DataFetcher
    from py_gdelt.sources.files import FileSource

__all__ = ["GraphEndpoint"]

logger = logging.getLogger(__name__)


class GraphEndpoint:
    """Endpoint for GDELT Graph datasets.

    Provides type-safe access to all six graph datasets with per-dataset
    query and stream methods that preserve return types. Graph datasets are
    sourced exclusively from files (no BigQuery fallback available).

    Args:
        file_source: FileSource instance for downloading GDELT graph files.
        error_policy: How to handle errors - 'raise', 'warn', or 'skip'.

    Example:
        Query Global Quotation Graph records:

        >>> from datetime import date
        >>> from py_gdelt.filters import GQGFilter, DateRange
        >>> from py_gdelt.endpoints.graphs import GraphEndpoint
        >>> from py_gdelt.sources.files import FileSource
        >>>
        >>> async def main():
        ...     async with FileSource() as file_source:
        ...         endpoint = GraphEndpoint(file_source=file_source)
        ...         filter_obj = GQGFilter(
        ...             date_range=DateRange(start=date(2025, 1, 20))
        ...         )
        ...         result = await endpoint.query_gqg(filter_obj)
        ...         for record in result:
        ...             print(record.quotes)

        Stream Entity Graph records:

        >>> async def stream_example():
        ...     async with FileSource() as file_source:
        ...         endpoint = GraphEndpoint(file_source=file_source)
        ...         filter_obj = GEGFilter(
        ...             date_range=DateRange(start=date(2025, 1, 20))
        ...         )
        ...         async for record in endpoint.stream_geg(filter_obj):
        ...             for entity in record.entities:
        ...                 print(entity.name, entity.entity_type)
    """

    def __init__(
        self,
        file_source: FileSource,
        *,
        error_policy: Literal["raise", "warn", "skip"] = "warn",
    ) -> None:
        from py_gdelt.sources.fetcher import DataFetcher

        self._fetcher: DataFetcher = DataFetcher(
            file_source=file_source,
            bigquery_source=None,
            fallback_enabled=False,
            error_policy=error_policy,
        )
        self._error_policy = error_policy

        logger.debug(
            "GraphEndpoint initialized (error_policy=%s)",
            error_policy,
        )

    def _handle_parse_error(self, url: str, error: Exception) -> None:
        """Handle parsing errors according to error policy.

        Args:
            url: The URL being parsed when the error occurred.
            error: The exception that was raised.

        Raises:
            Exception: Re-raises the error if error_policy is 'raise'.
        """
        if self._error_policy == "raise":
            raise error
        if self._error_policy == "warn":
            logger.warning("Error parsing %s: %s", url, error)
        # skip: continue silently

    # --- GQG (Global Quotation Graph) ---

    async def query_gqg(
        self,
        filter_obj: GQGFilter,
    ) -> FetchResult[GQGRecord]:
        """Query Global Quotation Graph records.

        Args:
            filter_obj: Filter specifying date range and optional language filter.

        Returns:
            FetchResult containing GQGRecord instances.
        """
        records = [record async for record in self.stream_gqg(filter_obj)]
        return FetchResult(data=records, failed=[])

    async def stream_gqg(
        self,
        filter_obj: GQGFilter,
    ) -> AsyncIterator[GQGRecord]:
        """Stream Global Quotation Graph records.

        Args:
            filter_obj: Filter specifying date range and optional language filter.

        Yields:
            GQGRecord: Individual quotation graph records.
        """
        async for url, data in self._fetcher.fetch_graph_files("gqg", filter_obj.date_range):
            try:
                for record in graph_parsers.parse_gqg(data):
                    if filter_obj.languages and record.lang not in filter_obj.languages:
                        continue
                    yield record
            except Exception as e:  # noqa: BLE001
                self._handle_parse_error(url, e)

    # --- GEG (Global Entity Graph) ---

    async def query_geg(
        self,
        filter_obj: GEGFilter,
    ) -> FetchResult[GEGRecord]:
        """Query Global Entity Graph records.

        Args:
            filter_obj: Filter specifying date range and optional language filter.

        Returns:
            FetchResult containing GEGRecord instances.
        """
        records = [record async for record in self.stream_geg(filter_obj)]
        return FetchResult(data=records, failed=[])

    async def stream_geg(
        self,
        filter_obj: GEGFilter,
    ) -> AsyncIterator[GEGRecord]:
        """Stream Global Entity Graph records.

        Args:
            filter_obj: Filter specifying date range and optional language filter.

        Yields:
            GEGRecord: Individual entity graph records.
        """
        async for url, data in self._fetcher.fetch_graph_files("geg", filter_obj.date_range):
            try:
                for record in graph_parsers.parse_geg(data):
                    if filter_obj.languages and record.lang not in filter_obj.languages:
                        continue
                    yield record
            except Exception as e:  # noqa: BLE001
                self._handle_parse_error(url, e)

    # --- GFG (Global Frontpage Graph) ---

    async def query_gfg(
        self,
        filter_obj: GFGFilter,
    ) -> FetchResult[GFGRecord]:
        """Query Global Frontpage Graph records.

        Args:
            filter_obj: Filter specifying date range and optional language filter.

        Returns:
            FetchResult containing GFGRecord instances.
        """
        records = [record async for record in self.stream_gfg(filter_obj)]
        return FetchResult(data=records, failed=[])

    async def stream_gfg(
        self,
        filter_obj: GFGFilter,
    ) -> AsyncIterator[GFGRecord]:
        """Stream Global Frontpage Graph records.

        Args:
            filter_obj: Filter specifying date range and optional language filter.

        Yields:
            GFGRecord: Individual Frontpage graph records.
        """
        async for url, data in self._fetcher.fetch_graph_files("gfg", filter_obj.date_range):
            try:
                for record in graph_parsers.parse_gfg(data):
                    if filter_obj.languages and record.lang not in filter_obj.languages:
                        continue
                    yield record
            except Exception as e:  # noqa: BLE001
                self._handle_parse_error(url, e)

    # --- GGG (Global Geographic Graph) ---

    async def query_ggg(
        self,
        filter_obj: GGGFilter,
    ) -> FetchResult[GGGRecord]:
        """Query Global Geographic Graph records.

        Args:
            filter_obj: Filter specifying date range.

        Returns:
            FetchResult containing GGGRecord instances.
        """
        records = [record async for record in self.stream_ggg(filter_obj)]
        return FetchResult(data=records, failed=[])

    async def stream_ggg(
        self,
        filter_obj: GGGFilter,
    ) -> AsyncIterator[GGGRecord]:
        """Stream Global Geographic Graph records.

        Args:
            filter_obj: Filter specifying date range.

        Yields:
            GGGRecord: Individual Geographic graph records.
        """
        async for url, data in self._fetcher.fetch_graph_files("ggg", filter_obj.date_range):
            try:
                for record in graph_parsers.parse_ggg(data):
                    yield record
            except Exception as e:  # noqa: BLE001
                self._handle_parse_error(url, e)

    # --- GEMG (Global Embedded Metadata Graph) ---

    async def query_gemg(
        self,
        filter_obj: GEMGFilter,
    ) -> FetchResult[GEMGRecord]:
        """Query Global Embedded Metadata Graph records.

        Args:
            filter_obj: Filter specifying date range and optional language filter.

        Returns:
            FetchResult containing GEMGRecord instances.
        """
        records = [record async for record in self.stream_gemg(filter_obj)]
        return FetchResult(data=records, failed=[])

    async def stream_gemg(
        self,
        filter_obj: GEMGFilter,
    ) -> AsyncIterator[GEMGRecord]:
        """Stream Global Embedded Metadata Graph records.

        Args:
            filter_obj: Filter specifying date range and optional language filter.

        Yields:
            GEMGRecord: Individual embedded metadata graph records.
        """
        async for url, data in self._fetcher.fetch_graph_files("gemg", filter_obj.date_range):
            try:
                for record in graph_parsers.parse_gemg(data):
                    if filter_obj.languages and record.lang not in filter_obj.languages:
                        continue
                    yield record
            except Exception as e:  # noqa: BLE001
                self._handle_parse_error(url, e)

    # --- GAL (Global Article List) ---

    async def query_gal(
        self,
        filter_obj: GALFilter,
    ) -> FetchResult[GALRecord]:
        """Query Global Article List records.

        Args:
            filter_obj: Filter specifying date range and optional language filter.

        Returns:
            FetchResult containing GALRecord instances.
        """
        records = [record async for record in self.stream_gal(filter_obj)]
        return FetchResult(data=records, failed=[])

    async def stream_gal(
        self,
        filter_obj: GALFilter,
    ) -> AsyncIterator[GALRecord]:
        """Stream Global Article List records.

        Args:
            filter_obj: Filter specifying date range and optional language filter.

        Yields:
            GALRecord: Individual article list records.
        """
        async for url, data in self._fetcher.fetch_graph_files("gal", filter_obj.date_range):
            try:
                for record in graph_parsers.parse_gal(data):
                    if filter_obj.languages and record.lang not in filter_obj.languages:
                        continue
                    yield record
            except Exception as e:  # noqa: BLE001
                self._handle_parse_error(url, e)
