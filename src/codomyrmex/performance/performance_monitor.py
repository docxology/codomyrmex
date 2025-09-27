"""
Performance monitoring utilities for Codomyrmex modules.

This module provides performance monitoring capabilities to track
execution times, memory usage, and other performance metrics.
"""

import time
import functools
from typing import Any, Callable, Dict, List, Optional, Union
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
import json
from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)


try:
    import psutil

    HAS_PSUTIL = True
except ImportError:
    psutil = None
    HAS_PSUTIL = False


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""

    function_name: str
    execution_time: float
    memory_usage_mb: float
    cpu_percent: float
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


class PerformanceMonitor:
    """
    A performance monitor that tracks execution times and resource usage.

    This class provides methods to monitor function performance,
    track resource usage, and generate performance reports.
    """

    def __init__(self, log_file: Optional[Union[str, Path]] = None):
        """
        Initialize the performance monitor.

        Args:
            log_file: Optional file to log performance metrics to.
        """
        self.log_file = Path(log_file) if log_file else None
        self.metrics: List[PerformanceMetrics] = []
        self._process = psutil.Process() if HAS_PSUTIL else None

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        if not HAS_PSUTIL:
            return 0.0
        return self._process.memory_info().rss / 1024 / 1024

    def _get_cpu_percent(self) -> float:
        """Get current CPU usage percentage."""
        if not HAS_PSUTIL:
            return 0.0
        return self._process.cpu_percent()

    def record_metrics(
        self,
        function_name: str,
        execution_time: float,
        memory_usage_mb: Optional[float] = None,
        cpu_percent: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Record performance metrics.

        Args:
            function_name: Name of the function being monitored
            execution_time: Execution time in seconds
            memory_usage_mb: Memory usage in MB (if None, gets current usage)
            cpu_percent: CPU usage percentage (if None, gets current usage)
            metadata: Additional metadata to store
        """
        if memory_usage_mb is None:
            memory_usage_mb = self._get_memory_usage()

        if cpu_percent is None:
            cpu_percent = self._get_cpu_percent()

        metrics = PerformanceMetrics(
            function_name=function_name,
            execution_time=execution_time,
            memory_usage_mb=memory_usage_mb,
            cpu_percent=cpu_percent,
            metadata=metadata or {},
        )

        self.metrics.append(metrics)

        # Log to file if specified
        if self.log_file:
            self._log_metrics(metrics)

    def _log_metrics(self, metrics: PerformanceMetrics) -> None:
        """Log metrics to file."""
        try:
            with open(self.log_file, "a") as f:
                json.dump(
                    {
                        "function_name": metrics.function_name,
                        "execution_time": metrics.execution_time,
                        "memory_usage_mb": metrics.memory_usage_mb,
                        "cpu_percent": metrics.cpu_percent,
                        "timestamp": metrics.timestamp,
                        "metadata": metrics.metadata,
                    },
                    f,
                )
                f.write("\n")
        except (OSError, json.JSONEncodeError):
            # If we can't write to the log file, that's okay
            pass

    def get_stats(self, function_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get performance statistics.

        Args:
            function_name: If specified, only return stats for this function

        Returns:
            Dictionary containing performance statistics
        """
        if function_name:
            filtered_metrics = [
                m for m in self.metrics if m.function_name == function_name
            ]
        else:
            filtered_metrics = self.metrics

        if not filtered_metrics:
            return {}

        execution_times = [m.execution_time for m in filtered_metrics]
        memory_usage = [m.memory_usage_mb for m in filtered_metrics]
        cpu_usage = [m.cpu_percent for m in filtered_metrics]

        return {
            "function_name": function_name or "all",
            "total_calls": len(filtered_metrics),
            "execution_time": {
                "min": min(execution_times),
                "max": max(execution_times),
                "avg": sum(execution_times) / len(execution_times),
                "total": sum(execution_times),
            },
            "memory_usage_mb": {
                "min": min(memory_usage),
                "max": max(memory_usage),
                "avg": sum(memory_usage) / len(memory_usage),
            },
            "cpu_percent": {
                "min": min(cpu_usage),
                "max": max(cpu_usage),
                "avg": sum(cpu_usage) / len(cpu_usage),
            },
        }

    def clear_metrics(self) -> None:
        """Clear all recorded metrics."""
        self.metrics.clear()

    def export_metrics(self, file_path: Union[str, Path]) -> None:
        """
        Export metrics to a JSON file.

        Args:
            file_path: Path to export metrics to
        """
        export_data = []
        for metrics in self.metrics:
            export_data.append(
                {
                    "function_name": metrics.function_name,
                    "execution_time": metrics.execution_time,
                    "memory_usage_mb": metrics.memory_usage_mb,
                    "cpu_percent": metrics.cpu_percent,
                    "timestamp": metrics.timestamp,
                    "metadata": metrics.metadata,
                }
            )

        with open(file_path, "w") as f:
            json.dump(export_data, f, indent=2)


# Global performance monitor instance
_performance_monitor = PerformanceMonitor()


def monitor_performance(
    function_name: Optional[str] = None, monitor: Optional[PerformanceMonitor] = None
) -> Callable:
    """
    Decorator for monitoring function performance.

    Args:
        function_name: Name to use for monitoring (defaults to function name)
        monitor: Performance monitor to use (defaults to global instance)

    Returns:
        Decorated function with performance monitoring enabled

    Example:
        >>> @monitor_performance()
        ... def expensive_function():
        ...     # Some expensive operation
        ...     return result
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """Wrapper.

                Returns:        The result of the operation.
                """
            monitor_instance = monitor or _performance_monitor
            name = function_name or func.__name__

            # Record initial state
            start_time = time.time()
            start_memory = monitor_instance._get_memory_usage()
            start_cpu = monitor_instance._get_cpu_percent()

            try:
                # Execute function
                result = func(*args, **kwargs)

                # Record final state
                end_time = time.time()
                end_memory = monitor_instance._get_memory_usage()
                end_cpu = monitor_instance._get_cpu_percent()

                # Calculate metrics
                execution_time = end_time - start_time
                memory_delta = end_memory - start_memory
                cpu_avg = (start_cpu + end_cpu) / 2

                # Record metrics
                monitor_instance.record_metrics(
                    function_name=name,
                    execution_time=execution_time,
                    memory_usage_mb=end_memory,
                    cpu_percent=cpu_avg,
                    metadata={"args_count": len(args), "kwargs_count": len(kwargs)},
                )

                return result

            except Exception as e:
                # Record metrics even if function fails
                end_time = time.time()
                execution_time = end_time - start_time

                monitor_instance.record_metrics(
                    function_name=name,
                    execution_time=execution_time,
                    memory_usage_mb=monitor_instance._get_memory_usage(),
                    cpu_percent=monitor_instance._get_cpu_percent(),
                    metadata={
                        "error": str(e),
                        "args_count": len(args),
                        "kwargs_count": len(kwargs),
                    },
                )

                raise

        return wrapper

    return decorator


@contextmanager
def performance_context(name: str, monitor: Optional[PerformanceMonitor] = None):
    """
    Context manager for monitoring performance of code blocks.

    Args:
        name: Name for the performance context
        monitor: Performance monitor to use (defaults to global instance)

    Example:
        >>> with performance_context("data_processing"):
        ...     # Some expensive operations
        ...     result = process_data()
    """
    monitor_instance = monitor or _performance_monitor

    start_time = time.time()
    start_memory = monitor_instance._get_memory_usage()
    start_cpu = monitor_instance._get_cpu_percent()

    try:
        yield
    finally:
        end_time = time.time()
        end_memory = monitor_instance._get_memory_usage()
        end_cpu = monitor_instance._get_cpu_percent()

        execution_time = end_time - start_time
        memory_delta = end_memory - start_memory
        cpu_avg = (start_cpu + end_cpu) / 2

        monitor_instance.record_metrics(
            function_name=name,
            execution_time=execution_time,
            memory_usage_mb=end_memory,
            cpu_percent=cpu_avg,
            metadata={"context": True},
        )


def get_performance_stats(function_name: Optional[str] = None) -> Dict[str, Any]:
    """Get performance statistics from the global monitor."""
    return _performance_monitor.get_stats(function_name)


def clear_performance_metrics() -> None:
    """Clear all performance metrics from the global monitor."""
    _performance_monitor.clear_metrics()


def export_performance_metrics(file_path: Union[str, Path]) -> None:
    """Export performance metrics to a JSON file."""
    _performance_monitor.export_metrics(file_path)
