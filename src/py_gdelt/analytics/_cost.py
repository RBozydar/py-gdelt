"""Session-level BigQuery cost tracker.

Tracks cumulative bytes processed across analytics queries within a session,
with optional budget enforcement.
"""

from __future__ import annotations

import threading


class SessionCostTracker:
    """Cumulative BigQuery cost tracker for analytics sessions.

    Tracks bytes processed across queries and optionally enforces a byte
    budget. Thread-safe for forward compatibility with free-threaded Python.

    Args:
        budget_bytes: Maximum cumulative bytes to process. None for no limit.
    """

    def __init__(self, budget_bytes: int | None = None) -> None:
        self._budget_bytes = budget_bytes
        self._cumulative_bytes: int = 0
        self._query_count: int = 0
        self._lock = threading.Lock()

    @property
    def cumulative_bytes(self) -> int:
        """Total bytes processed across all recorded queries."""
        return self._cumulative_bytes

    @property
    def remaining_bytes(self) -> int | None:
        """Bytes remaining in budget, or None if no budget set."""
        if self._budget_bytes is None:
            return None
        return max(0, self._budget_bytes - self._cumulative_bytes)

    @property
    def query_count(self) -> int:
        """Number of queries recorded."""
        return self._query_count

    def record(self, bytes_processed: int) -> None:
        """Record bytes from a completed query.

        Args:
            bytes_processed: Bytes processed by the query.

        Raises:
            BudgetExceededError: If cumulative bytes exceed the budget.
        """
        from py_gdelt.exceptions import BudgetExceededError  # noqa: PLC0415

        with self._lock:
            self._cumulative_bytes += bytes_processed
            self._query_count += 1
            if self._budget_bytes is not None and self._cumulative_bytes > self._budget_bytes:
                msg = (
                    f"Session budget exceeded: {self._cumulative_bytes:,} bytes processed "
                    f"vs {self._budget_bytes:,} byte budget"
                )
                raise BudgetExceededError(msg)

    def check_budget(self, estimated_bytes: int) -> None:
        """Pre-flight check before executing a query.

        Args:
            estimated_bytes: Estimated bytes the query will process.

        Raises:
            BudgetExceededError: If the estimate would exceed the remaining budget.
        """
        from py_gdelt.exceptions import BudgetExceededError  # noqa: PLC0415

        if self._budget_bytes is None:
            return
        with self._lock:
            if self._cumulative_bytes + estimated_bytes > self._budget_bytes:
                msg = (
                    f"Query would exceed session budget: "
                    f"{self._cumulative_bytes:,} + {estimated_bytes:,} estimated "
                    f"> {self._budget_bytes:,} budget"
                )
                raise BudgetExceededError(msg)

    def reset(self) -> None:
        """Reset tracker to zero."""
        with self._lock:
            self._cumulative_bytes = 0
            self._query_count = 0
