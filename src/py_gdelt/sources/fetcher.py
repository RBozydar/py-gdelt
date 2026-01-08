"""DataFetcher orchestrator for GDELT data sources.

This module provides the DataFetcher class, which orchestrates source selection and
fallback behavior between file downloads (primary) and BigQuery (fallback).

Key Design Principles:
- Files are ALWAYS primary (free, no credentials needed)
- BigQuery is FALLBACK ONLY (on 429/error, if credentials configured)
- Fallback logged at WARNING level (not silent)
- Configurable error policy (raise/warn/skip)

The DataFetcher uses dependency injection to receive source instances and parsers,
making it easy to test and configure.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Literal, Protocol, TypeVar

from py_gdelt.exceptions import (
    APIError,
    APIUnavailableError,
    ConfigurationError,
    RateLimitError,
)
from py_gdelt.filters import EventFilter, GKGFilter, NGramsFilter


if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator

    from py_gdelt.models._internal import _RawEvent, _RawGKG, _RawMention, _RawNGram
    from py_gdelt.sources.bigquery import BigQuerySource
    from py_gdelt.sources.files import FileSource, FileType

__all__ = ["DataFetcher", "ErrorPolicy", "Parser"]

logger = logging.getLogger(__name__)

# Type variable for parser output (covariant since only used in return position)
T_co = TypeVar("T_co", covariant=True)

# Type variable for generic fetch methods
R = TypeVar("R")

# Error handling policy
ErrorPolicy = Literal["raise", "warn", "skip"]


class Parser(Protocol[T_co]):
    """Interface for file format parsers.

    All GDELT parsers must implement this protocol to be used with DataFetcher.
    The parser is responsible for converting raw bytes into typed records.
    """

    def parse(self, data: bytes, is_translated: bool = False) -> Iterator[T_co]:
        """Parse raw bytes into typed records.

        Args:
            data: Raw file content as bytes
            is_translated: Whether this is from the translated feed

        Returns:
            Iterator of parsed records

        Raises:
            ParseError: If parsing fails
        """
        ...

    def detect_version(self, header: bytes) -> int:
        """Detect format version from header (1 or 2).

        Args:
            header: First line of the file (raw bytes)

        Returns:
            Version number (1 or 2)

        Raises:
            ParseError: If version cannot be detected
        """
        ...


class DataFetcher:
    """Orchestrates source selection and fallback for GDELT data fetching.

    This class implements the primary/fallback pattern where file downloads are
    always the primary source (free, no credentials) and BigQuery is the fallback
    (on rate limit/error, if credentials configured).

    The DataFetcher uses dependency injection to receive source instances, making
    it easy to test and configure. It supports configurable error handling policies
    and structured logging for all fallback events.

    Args:
        file_source: FileSource instance for downloading GDELT files
        bigquery_source: Optional BigQuerySource instance for fallback queries
        fallback_enabled: Whether to fallback to BigQuery on errors (default: True)
        error_policy: How to handle errors - 'raise', 'warn', or 'skip' (default: 'warn')

    Note:
        BigQuery fallback only activates if both fallback_enabled=True AND
        bigquery_source is provided AND credentials are configured.

    Example:
        >>> async with FileSource() as file_source:
        ...     fetcher = DataFetcher(
        ...         file_source=file_source,
        ...         fallback_enabled=True,
        ...     )
        ...     filter_obj = EventFilter(
        ...         date_range=DateRange(start=date(2024, 1, 1))
        ...     )
        ...     async for event in fetcher.fetch_events(filter_obj):
        ...         print(event.global_event_id)
    """

    def __init__(
        self,
        file_source: FileSource,
        bigquery_source: BigQuerySource | None = None,
        *,
        fallback_enabled: bool = True,
        error_policy: ErrorPolicy = "warn",
    ) -> None:
        self._file = file_source
        self._bq = bigquery_source
        self._fallback = fallback_enabled and bigquery_source is not None
        self._error_policy = error_policy

        logger.debug(
            "DataFetcher initialized (fallback_enabled=%s, error_policy=%s)",
            self._fallback,
            error_policy,
        )

    async def fetch(
        self,
        filter_obj: EventFilter | GKGFilter,
        parser: Parser[R],
        *,
        use_bigquery: bool = False,
    ) -> AsyncIterator[R]:
        """Generic fetch method with automatic fallback.

        This is a low-level method that powers all the high-level fetch methods.
        It tries file downloads first, then falls back to BigQuery on rate limit/error.

        Args:
            filter_obj: Filter with date range and query parameters
            parser: Parser instance to convert raw bytes into typed records
            use_bigquery: If True, skip file downloads and use BigQuery directly

        Yields:
            R: Parsed records

        Raises:
            RateLimitError: If rate limited and fallback not available/enabled
            APIError: If download fails and fallback not available/enabled
            ConfigurationError: If BigQuery requested but not configured
        """
        # If explicitly requested to use BigQuery, skip file source
        if use_bigquery:
            if self._bq is None:
                msg = "BigQuery requested but not configured"
                logger.error(msg)
                raise ConfigurationError(msg)

            logger.info("Using BigQuery directly (use_bigquery=True)")
            async for record in self._fetch_from_bigquery(filter_obj, parser):
                yield record
            return

        # Try file source first (primary source)
        try:
            async for record in self._fetch_from_files(filter_obj, parser):
                yield record

        except RateLimitError as e:
            # Rate limited - fallback to BigQuery if available
            if self._fallback:
                logger.warning(
                    "Rate limited on file source (retry_after=%s), falling back to BigQuery",
                    e.retry_after,
                )
                async for record in self._fetch_from_bigquery(filter_obj, parser):
                    yield record
            else:
                # No fallback available
                logger.exception("Rate limited and fallback not enabled")
                self._handle_error(e)

        except (APIError, APIUnavailableError) as e:
            # API error - fallback to BigQuery if available
            if self._fallback:
                logger.warning(
                    "File source failed (%s: %s), falling back to BigQuery",
                    type(e).__name__,
                    e,
                )
                async for record in self._fetch_from_bigquery(filter_obj, parser):
                    yield record
            else:
                # No fallback available
                logger.exception("File source failed and fallback not enabled")
                self._handle_error(e)

    async def _fetch_from_files(
        self,
        filter_obj: EventFilter | GKGFilter,
        parser: Parser[R],
    ) -> AsyncIterator[R]:
        """Fetch data from file source and parse.

        Args:
            filter_obj: Filter with date range and query parameters
            parser: Parser instance to convert raw bytes into typed records

        Yields:
            R: Parsed records

        Raises:
            RateLimitError: If rate limited by file server
            APIError: If download fails
        """
        # Determine file type from filter
        file_type: FileType
        if isinstance(filter_obj, EventFilter):
            file_type = "export"
        elif isinstance(filter_obj, GKGFilter):
            file_type = "gkg"
        else:  # pragma: no cover
            # Defensive: unreachable given current type union, but protects against future changes
            msg = f"Unsupported filter type: {type(filter_obj).__name__}"  # type: ignore[unreachable]
            logger.error(msg)
            raise TypeError(msg)

        # Convert dates to datetimes (at midnight)
        start_dt = datetime.combine(filter_obj.date_range.start, datetime.min.time())
        end_date = filter_obj.date_range.end or filter_obj.date_range.start
        end_dt = datetime.combine(end_date, datetime.min.time())

        # Get file URLs for date range
        urls = await self._file.get_files_for_date_range(
            start_date=start_dt,
            end_date=end_dt,
            file_type=file_type,
            include_translation=filter_obj.include_translated,
        )

        logger.info(
            "Fetching %d %s files for date range %s to %s",
            len(urls),
            file_type,
            filter_obj.date_range.start,
            filter_obj.date_range.end or filter_obj.date_range.start,
        )

        # Download and parse files
        records_yielded = 0
        async for url, data in self._file.stream_files(urls):
            # Determine if this is a translated file
            is_translated = ".translation" in url

            # Parse the file data
            try:
                # Handle both sync and async parsers
                parse_result = parser.parse(data, is_translated=is_translated)

                # Check if result is async iterator
                if hasattr(parse_result, "__aiter__"):
                    # Async parser
                    async for record in parse_result:
                        yield record
                        records_yielded += 1
                else:
                    # Sync parser (most common)
                    for record in parse_result:
                        yield record
                        records_yielded += 1

            except Exception as e:
                # Error boundary: handle parsing errors according to error policy
                logger.exception("Failed to parse file %s", url)
                self._handle_error(e)

        logger.info("Fetched %d records from file source", records_yielded)

    async def _fetch_from_bigquery(
        self,
        filter_obj: EventFilter | GKGFilter,
        parser: Parser[R],
    ) -> AsyncIterator[R]:
        """Fetch data from BigQuery source.

        Note: BigQuery returns data in a different format than files, so we don't
        use the parser here. Instead, we yield BigQuery row dictionaries directly.
        The caller is responsible for converting them to the appropriate type.

        Args:
            filter_obj: Filter with date range and query parameters
            parser: Parser instance (not used for BigQuery, kept for interface consistency)

        Yields:
            R: Records from BigQuery (as dictionaries)

        Raises:
            ConfigurationError: If BigQuery not configured
        """
        if self._bq is None:
            msg = "BigQuery fallback requested but not configured"
            logger.error(msg)
            raise ConfigurationError(msg)

        # Query BigQuery based on filter type
        if isinstance(filter_obj, EventFilter):
            logger.debug("Querying BigQuery events table")
            async for row in self._bq.query_events(filter_obj):
                # BigQuery returns dict, yield as-is
                # Note: Type T might not match dict, caller should handle conversion
                yield row  # type: ignore[misc]

        elif isinstance(filter_obj, GKGFilter):
            logger.debug("Querying BigQuery GKG table")
            async for row in self._bq.query_gkg(filter_obj):
                # BigQuery returns dict, yield as-is
                yield row  # type: ignore[misc]

        else:  # pragma: no cover
            # Defensive: unreachable given current type union
            msg = f"Unsupported filter type for BigQuery: {type(filter_obj).__name__}"  # type: ignore[unreachable]
            logger.error(msg)
            raise TypeError(msg)

    def _handle_error(self, error: Exception) -> None:
        """Handle errors according to the configured error policy.

        Args:
            error: The exception that occurred

        Raises:
            Exception: If error_policy is 'raise', re-raises the error
        """
        if self._error_policy == "raise":
            raise error
        if self._error_policy == "warn":
            logger.warning("Error occurred: %s (error_policy=warn, continuing)", error)
        elif self._error_policy == "skip":
            logger.debug("Error occurred: %s (error_policy=skip, skipping)", error)
        else:  # pragma: no cover
            # Defensive: unreachable given Literal type
            logger.error("Unknown error_policy: %s, raising error", self._error_policy)  # type: ignore[unreachable]
            raise error

    async def fetch_events(
        self,
        filter_obj: EventFilter,
        *,
        use_bigquery: bool = False,
    ) -> AsyncIterator[_RawEvent]:
        """Fetch GDELT Events with automatic fallback.

        This is a convenience method that creates an EventsParser and calls fetch().
        Files are always tried first (free, no credentials), with automatic fallback
        to BigQuery on rate limit/error if credentials are configured.

        Args:
            filter_obj: Event filter with date range and query parameters
            use_bigquery: If True, skip files and use BigQuery directly

        Yields:
            _RawEvent: Event instances

        Raises:
            RateLimitError: If rate limited and fallback not available
            APIError: If download fails and fallback not available
            ConfigurationError: If BigQuery requested but not configured

        Example:
            >>> filter_obj = EventFilter(
            ...     date_range=DateRange(start=date(2024, 1, 1)),
            ...     actor1_country="USA",
            ... )
            >>> async for event in fetcher.fetch_events(filter_obj):
            ...     print(event.global_event_id)
        """
        from py_gdelt.parsers import EventsParser

        parser = EventsParser()
        async for event in self.fetch(filter_obj, parser, use_bigquery=use_bigquery):
            yield event

    async def fetch_mentions(
        self,
        global_event_id: int,
        filter_obj: EventFilter,
        *,
        use_bigquery: bool = False,
    ) -> AsyncIterator[_RawMention]:
        """Fetch GDELT Mentions for a specific event.

        This method fetches all mentions of a specific event from the Mentions table.
        Note that mentions require a date range filter for efficient querying.

        Args:
            global_event_id: Global event ID to fetch mentions for (integer)
            filter_obj: Filter with date range (other fields ignored for mentions)
            use_bigquery: If True, skip files and use BigQuery directly

        Yields:
            _RawMention: Mention instances

        Raises:
            RateLimitError: If rate limited and fallback not available
            APIError: If download fails and fallback not available
            ConfigurationError: If BigQuery requested but not configured

        Example:
            >>> filter_obj = EventFilter(
            ...     date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 7))
            ... )
            >>> async for mention in fetcher.fetch_mentions(123456789, filter_obj):
            ...     print(mention.mention_source_name)
        """
        # For mentions, we need to use BigQuery as files don't support event-specific queries
        if not use_bigquery and self._bq is None:
            msg = (
                "Mentions queries require BigQuery (files don't support event-specific filtering). "
                "Please configure BigQuery credentials or set use_bigquery=True."
            )
            logger.error(msg)
            raise ConfigurationError(msg)

        if self._bq is None:
            msg = "BigQuery required for mentions but not configured"
            logger.error(msg)
            raise ConfigurationError(msg)

        # Query BigQuery mentions table
        logger.info("Querying mentions for event %s", global_event_id)
        async for row in self._bq.query_mentions(
            global_event_id=global_event_id,
            date_range=filter_obj.date_range,
        ):
            # BigQuery returns dict, we need to convert to _RawMention
            # For now, yield the dict directly - conversion will happen at API boundary
            yield row  # type: ignore[misc]

    async def fetch_gkg(
        self,
        filter_obj: GKGFilter,
        *,
        use_bigquery: bool = False,
    ) -> AsyncIterator[_RawGKG]:
        """Fetch GDELT GKG (Global Knowledge Graph) records with automatic fallback.

        This is a convenience method that creates a GKGParser and calls fetch().
        Files are always tried first (free, no credentials), with automatic fallback
        to BigQuery on rate limit/error if credentials are configured.

        Args:
            filter_obj: GKG filter with date range and query parameters
            use_bigquery: If True, skip files and use BigQuery directly

        Yields:
            _RawGKG: GKG record instances

        Raises:
            RateLimitError: If rate limited and fallback not available
            APIError: If download fails and fallback not available
            ConfigurationError: If BigQuery requested but not configured

        Example:
            >>> filter_obj = GKGFilter(
            ...     date_range=DateRange(start=date(2024, 1, 1)),
            ...     themes=["ENV_CLIMATECHANGE"],
            ... )
            >>> async for gkg in fetcher.fetch_gkg(filter_obj):
            ...     print(gkg.gkg_record_id)
        """
        from py_gdelt.parsers import GKGParser

        parser = GKGParser()
        async for gkg in self.fetch(filter_obj, parser, use_bigquery=use_bigquery):
            yield gkg

    async def fetch_ngrams(
        self,
        filter_obj: NGramsFilter,
    ) -> AsyncIterator[_RawNGram]:
        """Fetch GDELT NGrams records.

        Note: NGrams are only available via file downloads, not BigQuery.
        If file downloads fail, this method will raise an error.

        Args:
            filter_obj: NGramsFilter with date range (ngram/language/position filters
                       applied client-side in NGramsEndpoint)

        Yields:
            _RawNGram: NGram record instances

        Raises:
            RateLimitError: If rate limited
            APIError: If download fails
            ConfigurationError: If BigQuery fallback attempted (not supported for ngrams)

        Example:
            >>> from py_gdelt.filters import NGramsFilter, DateRange
            >>> from datetime import date
            >>> filter_obj = NGramsFilter(
            ...     date_range=DateRange(start=date(2024, 1, 1))
            ... )
            >>> async for ngram in fetcher.fetch_ngrams(filter_obj):
            ...     print(ngram.ngram, ngram.language)
        """
        from py_gdelt.parsers import NGramsParser

        parser = NGramsParser()

        # Convert dates to datetimes (at midnight)
        start_dt = datetime.combine(filter_obj.date_range.start, datetime.min.time())
        end_date = filter_obj.date_range.end or filter_obj.date_range.start
        end_dt = datetime.combine(end_date, datetime.min.time())

        # Get ngrams file URLs
        urls = await self._file.get_files_for_date_range(
            start_date=start_dt,
            end_date=end_dt,
            file_type="ngrams",
            include_translation=False,  # NGrams don't have translations
        )

        logger.info(
            "Fetching %d ngrams files for date range %s to %s",
            len(urls),
            filter_obj.date_range.start,
            filter_obj.date_range.end or filter_obj.date_range.start,
        )

        # Download and parse files
        records_yielded = 0
        async for url, data in self._file.stream_files(urls):
            # Parse the file data
            try:
                # NGramsParser returns sync iterator
                for record in parser.parse(data):
                    yield record
                    records_yielded += 1

            except Exception as e:
                # Error boundary: handle parsing errors according to error policy
                logger.exception("Failed to parse ngrams file %s", url)
                self._handle_error(e)

        logger.info("Fetched %d ngrams records from file source", records_yielded)
