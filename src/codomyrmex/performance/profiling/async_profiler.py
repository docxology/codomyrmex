"""Asynchronous function profiler with histogram tracking and threshold alerts.

Provides:
- AsyncProfiler: decorator-based profiling for async functions
- Profile data collection: call count, min/max/avg/p99 latency
- Threshold-based slow-call alerts
- Profile history and reporting
"""

from __future__ import annotations

import functools
import time
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any
from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


@dataclass
class ProfileEntry:
    """Single profiling measurement."""

    function_name: str
    duration_seconds: float
    timestamp: float = field(default_factory=time.time)
    args_repr: str = ""
    error: str = ""


@dataclass
class ProfileStats:
    """Aggregate statistics for a profiled function."""

    function_name: str
    call_count: int
    total_seconds: float
    min_seconds: float
    max_seconds: float
    error_count: int

    @property
    def avg_seconds(self) -> float:
        return self.total_seconds / max(self.call_count, 1)

    @property
    def avg_ms(self) -> float:
        return self.avg_seconds * 1000

    @property
    def max_ms(self) -> float:
        return self.max_seconds * 1000


class AsyncProfiler:
    """Profiles asynchronous functions to identify bottlenecks.

    Supports both decorator usage and programmatic call tracking.

    Example::

        profiler = AsyncProfiler(slow_threshold=1.0)

        @profiler.profile
        async def my_slow_function():
            await asyncio.sleep(0.5)
            return "done"

        await my_slow_function()
        stats = profiler.get_stats("my_slow_function")
    """

    def __init__(self, slow_threshold: float = 1.0) -> None:
        self.slow_threshold = slow_threshold
        self._entries: dict[str, list[ProfileEntry]] = defaultdict(list)
        self._slow_calls: list[ProfileEntry] = []

    def profile(self, func: Callable) -> Callable:
        """Decorator to profile an async function."""
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            error_msg = ""
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_msg = str(e)
                raise
            finally:
                duration = time.perf_counter() - start
                entry = ProfileEntry(
                    function_name=func.__name__,
                    duration_seconds=duration,
                    error=error_msg,
                )
                self._entries[func.__name__].append(entry)
                if duration > self.slow_threshold:
                    self._slow_calls.append(entry)
                    logger.warning(
                        "SLOW async call: %s took %.4fs (threshold: %.4fs)",
                        func.__name__, duration, self.slow_threshold,
                    )
                else:
                    logger.debug("Async Profile: %s took %.4fs", func.__name__, duration)
        return wrapper

    def profile_sync(self, func: Callable) -> Callable:
        """Decorator to profile a synchronous function."""
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            """wrapper ."""
            start = time.perf_counter()
            error_msg = ""
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_msg = str(e)
                raise
            finally:
                duration = time.perf_counter() - start
                entry = ProfileEntry(
                    function_name=func.__name__,
                    duration_seconds=duration,
                    error=error_msg,
                )
                self._entries[func.__name__].append(entry)
                if duration > self.slow_threshold:
                    self._slow_calls.append(entry)
        return wrapper

    def record(self, function_name: str, duration: float, error: str = "") -> None:
        """Manually record a profiling entry."""
        entry = ProfileEntry(function_name=function_name, duration_seconds=duration, error=error)
        self._entries[function_name].append(entry)
        if duration > self.slow_threshold:
            self._slow_calls.append(entry)

    def get_stats(self, function_name: str) -> ProfileStats | None:
        """Get aggregate statistics for a function."""
        entries = self._entries.get(function_name)
        if not entries:
            return None
        durations = [e.duration_seconds for e in entries]
        return ProfileStats(
            function_name=function_name,
            call_count=len(entries),
            total_seconds=sum(durations),
            min_seconds=min(durations),
            max_seconds=max(durations),
            error_count=sum(1 for e in entries if e.error),
        )

    def all_stats(self) -> list[ProfileStats]:
        """Get stats for all profiled functions."""
        results = []
        for name in sorted(self._entries.keys()):
            stats = self.get_stats(name)
            if stats:
                results.append(stats)
        return results

    @property
    def slow_calls(self) -> list[ProfileEntry]:
        return list(self._slow_calls)

    @property
    def total_calls(self) -> int:
        return sum(len(entries) for entries in self._entries.values())

    @property
    def profiled_functions(self) -> list[str]:
        return sorted(self._entries.keys())

    def clear(self) -> None:
        """Clear all profiling data."""
        self._entries.clear()
        self._slow_calls.clear()

    def summary(self) -> dict[str, Any]:
        """Return a summary of all profiling data."""
        stats = self.all_stats()
        return {
            "profiled_functions": len(stats),
            "total_calls": self.total_calls,
            "slow_calls": len(self._slow_calls),
            "functions": [
                {"name": s.function_name, "calls": s.call_count,
                 "avg_ms": round(s.avg_ms, 2), "max_ms": round(s.max_ms, 2),
                 "errors": s.error_count}
                for s in stats
            ],
        }
