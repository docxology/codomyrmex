"""Performance logging utilities.

This module provides the PerformanceLogger class for timing operations,
tracking durations, and logging performance metrics. Thread-safe for
concurrent timing operations.

Example:
    >>> from codomyrmex.logging_monitoring.handlers import PerformanceLogger
    >>> perf_logger = PerformanceLogger("my_service")
    >>> with perf_logger.time_operation("database_query"):
    ...     result = db.query("SELECT * FROM users")
    >>> perf_logger.log_metric("query_results", len(result), unit="rows")
"""

import logging
import time
from contextlib import contextmanager
from typing import Any
from collections.abc import Iterator


class PerformanceLogger:
    """Logger specialized for performance metrics and timing operations.

    Provides utilities for timing code blocks, tracking operation durations,
    and logging performance metrics. Thread-safe for concurrent timing operations.

    Attributes:
        logger: The underlying logger instance.
        _timers: Dictionary tracking active timing operations.

    Example:
        >>> perf_logger = PerformanceLogger("my_service")
        >>> with perf_logger.time_operation("database_query"):
        ...     result = db.query("SELECT * FROM users")
        >>> perf_logger.log_metric("query_results", len(result), unit="rows")
    """

    def __init__(self, logger_name: str = "performance"):
        """Initialize a PerformanceLogger.

        Args:
            logger_name: Name for the underlying logger. Defaults to "performance".
        """
        self.logger = logging.getLogger(logger_name)
        self._timers: dict[str, float] = {}

    def start_timer(self, operation: str, context: dict[str, Any] | None = None) -> None:
        """Start timing an operation.

        Records the start time for the named operation. Use end_timer() to
        complete the timing and log the duration.

        Args:
            operation: A unique name identifying the operation being timed.
            context: Optional dictionary of additional context for the log.

        Returns:
            None

        Example:
            >>> perf_logger.start_timer("api_call", {"endpoint": "/users"})
            >>> # ... perform operation ...
            >>> duration = perf_logger.end_timer("api_call")
        """
        self._timers[operation] = time.time()
        self.logger.debug(f"Started timing: {operation}", extra={"operation": operation, "context": context or {}})

    def end_timer(self, operation: str, context: dict[str, Any] | None = None) -> float:
        """End timing an operation and log the duration.

        Calculates and logs the elapsed time since start_timer() was called
        for this operation.

        Args:
            operation: The name of the operation that was started.
            context: Optional dictionary of additional context for the log.

        Returns:
            The duration in seconds, or 0.0 if the operation was not started.

        Example:
            >>> perf_logger.start_timer("file_upload")
            >>> # ... perform upload ...
            >>> duration = perf_logger.end_timer("file_upload", {"file_size": 1024})
            >>> print(f"Upload took {duration:.2f} seconds")
        """
        if operation not in self._timers:
            return 0.0
        start_time = self._timers.pop(operation)
        duration = time.time() - start_time
        self.logger.info(f"Operation completed: {operation}", extra={"operation": operation, "duration_seconds": duration, "context": context or {}})
        return duration

    @contextmanager
    def time_operation(self, operation: str, context: dict[str, Any] | None = None) -> Iterator[None]:
        """Context manager for timing a code block.

        Automatically starts and ends timing around the enclosed code block.
        Logs the duration when the block exits, even if an exception occurs.

        Args:
            operation: A unique name identifying the operation being timed.
            context: Optional dictionary of additional context for the log.

        Yields:
            None

        Example:
            >>> with perf_logger.time_operation("data_processing", {"batch_id": 42}):
            ...     process_data(batch)
            # Logs: "Operation completed: data_processing" with duration
        """
        self.start_timer(operation, context)
        try:
            yield
        finally:
            self.end_timer(operation, context)

    def log_metric(self, name: str, value: Any, unit: str | None = None, context: dict[str, Any] | None = None) -> None:
        """Log a performance metric.

        Records a named metric value with optional unit and context. Useful
        for tracking counters, gauges, and other measurements.

        Args:
            name: The name of the metric (e.g., "requests_per_second").
            value: The metric value (numeric or any serializable type).
            unit: Optional unit of measurement (e.g., "ms", "bytes", "count").
            context: Optional dictionary of additional context for the log.

        Returns:
            None

        Example:
            >>> perf_logger.log_metric("response_time", 150, unit="ms")
            >>> perf_logger.log_metric("cache_hit_ratio", 0.95, context={"cache": "redis"})
        """
        extra = {"metric_name": name, "metric_value": value, "context": context or {}}
        if unit:
            extra["metric_unit"] = unit
        self.logger.info(f"Metric: {name} = {value}", extra=extra)
