"""Log aggregation and search utilities.

Provides in-memory log aggregation, filtering by level/module/time
range, and basic log analytics (rate, error ratio, top modules).
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class LogRecord:
    """A stored log record.

    Attributes:
        level: Log level string (e.g. "info", "error").
        message: Log message.
        module: Source module.
        timestamp: Unix timestamp.
        correlation_id: Request/workflow correlation ID.
        fields: Additional structured fields.
    """

    level: str
    message: str
    module: str = ""
    timestamp: float = field(default_factory=time.time)
    correlation_id: str = ""
    fields: dict[str, Any] = field(default_factory=dict)


@dataclass
class LogQuery:
    """Query parameters for log search.

    Attributes:
        levels: Filter by log levels (empty = all).
        modules: Filter by module names (empty = all).
        start_time: Only include logs after this timestamp.
        end_time: Only include logs before this timestamp.
        correlation_id: Filter by correlation ID.
        message_contains: Substring search in messages.
        limit: Maximum number of results.
    """

    levels: list[str] = field(default_factory=list)
    modules: list[str] = field(default_factory=list)
    start_time: float = 0.0
    end_time: float = 0.0
    correlation_id: str = ""
    message_contains: str = ""
    limit: int = 100


@dataclass
class LogStats:
    """Aggregate statistics for log records.

    Attributes:
        total_count: Total number of records.
        level_counts: Count per log level.
        module_counts: Count per module.
        error_rate: Fraction of error/critical logs.
        records_per_second: Average log rate.
        time_range_seconds: Span between first and last log.
        top_modules: Top modules by log count.
    """

    total_count: int = 0
    level_counts: dict[str, int] = field(default_factory=dict)
    module_counts: dict[str, int] = field(default_factory=dict)
    error_rate: float = 0.0
    records_per_second: float = 0.0
    time_range_seconds: float = 0.0
    top_modules: list[tuple[str, int]] = field(default_factory=list)


class LogAggregator:
    """In-memory log aggregation, search, and analytics.

    Stores log records and provides filtering, search, and
    statistical analysis capabilities.

    Example::

        agg = LogAggregator()
        agg.add(LogRecord(level="info", message="Started", module="main"))
        agg.add(LogRecord(level="error", message="Failed", module="db"))
        results = agg.search(LogQuery(levels=["error"]))
        stats = agg.stats()
    """

    def __init__(self, max_records: int = 100_000) -> None:
        self._records: list[LogRecord] = []
        self._max_records = max_records

    @property
    def count(self) -> int:
        """Number of stored records."""
        return len(self._records)

    def add(self, record: LogRecord) -> None:
        """Add a log record."""
        if len(self._records) >= self._max_records:
            self._records.pop(0)
        self._records.append(record)

    def add_many(self, records: list[LogRecord]) -> None:
        """Add multiple log records."""
        for r in records:
            self.add(r)

    def search(self, query: LogQuery) -> list[LogRecord]:
        """Search logs matching the query criteria.

        Args:
            query: Search parameters.

        Returns:
            List of matching records, most recent first.
        """
        results = []
        for record in reversed(self._records):
            if query.levels and record.level not in query.levels:
                continue
            if query.modules and record.module not in query.modules:
                continue
            if query.start_time and record.timestamp < query.start_time:
                continue
            if query.end_time and record.timestamp > query.end_time:
                continue
            if query.correlation_id and record.correlation_id != query.correlation_id:
                continue
            if query.message_contains and query.message_contains not in record.message:
                continue

            results.append(record)
            if len(results) >= query.limit:
                break

        return results

    def stats(self) -> LogStats:
        """Compute aggregate statistics over all stored records.

        Returns:
            LogStats with counts, rates, and top modules.
        """
        if not self._records:
            return LogStats()

        level_counts: dict[str, int] = defaultdict(int)
        module_counts: dict[str, int] = defaultdict(int)

        for r in self._records:
            level_counts[r.level] += 1
            if r.module:
                module_counts[r.module] += 1

        total = len(self._records)
        error_count = level_counts.get("error", 0) + level_counts.get("critical", 0)
        error_rate = error_count / total if total > 0 else 0.0

        timestamps = [r.timestamp for r in self._records]
        time_range = max(timestamps) - min(timestamps) if len(timestamps) > 1 else 0.0
        rps = total / time_range if time_range > 0 else 0.0

        top_modules = sorted(module_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        return LogStats(
            total_count=total,
            level_counts=dict(level_counts),
            module_counts=dict(module_counts),
            error_rate=error_rate,
            records_per_second=rps,
            time_range_seconds=time_range,
            top_modules=top_modules,
        )

    def tail(self, n: int = 20) -> list[LogRecord]:
        """Return the most recent n records."""
        return list(self._records[-n:])

    def clear(self) -> None:
        """Remove all stored records."""
        self._records.clear()
