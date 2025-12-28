"""
Performance monitoring utilities for Codomyrmex modules.

This module provides performance monitoring capabilities to track
execution times, memory usage, and other performance metrics.
"""

import functools
import json
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional, Union

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
    metadata: dict[str, Any] = field(default_factory=dict)


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
        self.metrics: list[PerformanceMetrics] = []
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
        metadata: Optional[dict[str, Any]] = None,
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

    def get_stats(self, function_name: Optional[str] = None) -> dict[str, Any]:
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
                end_memory - start_memory
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
        end_memory - start_memory
        cpu_avg = (start_cpu + end_cpu) / 2

        monitor_instance.record_metrics(
            function_name=name,
            execution_time=execution_time,
            memory_usage_mb=end_memory,
            cpu_percent=cpu_avg,
            metadata={"context": True},
        )


def get_performance_stats(function_name: Optional[str] = None) -> dict[str, Any]:
    """Get performance statistics from the global monitor."""
    return _performance_monitor.get_stats(function_name)


def clear_performance_metrics() -> None:
    """Clear all performance metrics from the global monitor."""
    _performance_monitor.clear_metrics()


def export_performance_metrics(file_path: Union[str, Path]) -> None:
    """Export performance metrics to a JSON file."""
    _performance_monitor.export_metrics(file_path)


# System-wide monitoring classes and functions

import threading

@dataclass
class SystemMetrics:
    """System-wide performance metrics."""

    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_total_mb: float
    disk_usage_percent: float
    disk_free_gb: float
    network_bytes_sent: int
    network_bytes_recv: int
    timestamp: float = field(default_factory=time.time)


class SystemMonitor:
    """
    System-wide resource monitoring.

    Provides continuous monitoring of system resources including CPU, memory,
    disk, and network usage.
    """

    def __init__(self, interval: float = 1.0, history_size: int = 100):
        """
        Initialize the system monitor.

        Args:
            interval: Monitoring interval in seconds
            history_size: Maximum number of historical metrics to keep
        """
        self.interval = interval
        self.history_size = history_size
        self._monitoring = False
        self._monitor_thread = None
        self.metrics_history: list[SystemMetrics] = []
        self._lock = threading.Lock()

        if not HAS_PSUTIL:
            logger.warning("psutil not available, system monitoring will be limited")

    def start_monitoring(self) -> None:
        """Start continuous system monitoring."""
        if self._monitoring:
            logger.warning("System monitoring already running")
            return

        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        logger.info(f"Started system monitoring with {self.interval}s interval")

    def stop_monitoring(self) -> None:
        """Stop continuous system monitoring."""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2.0)
        logger.info("Stopped system monitoring")

    def get_current_metrics(self) -> SystemMetrics:
        """
        Get current system metrics.

        Returns:
            Current system metrics
        """
        if not HAS_PSUTIL:
            return SystemMetrics(
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_used_mb=0.0,
                memory_total_mb=0.0,
                disk_usage_percent=0.0,
                disk_free_gb=0.0,
                network_bytes_sent=0,
                network_bytes_recv=0
            )

        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=None)

        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used_mb = memory.used / (1024 * 1024)
        memory_total_mb = memory.total / (1024 * 1024)

        # Disk usage (root filesystem)
        disk = psutil.disk_usage('/')
        disk_usage_percent = disk.percent
        disk_free_gb = disk.free / (1024 * 1024 * 1024)

        # Network usage
        network = psutil.net_io_counters()
        network_bytes_sent = network.bytes_sent
        network_bytes_recv = network.bytes_recv

        return SystemMetrics(
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_used_mb=memory_used_mb,
            memory_total_mb=memory_total_mb,
            disk_usage_percent=disk_usage_percent,
            disk_free_gb=disk_free_gb,
            network_bytes_sent=network_bytes_sent,
            network_bytes_recv=network_bytes_recv
        )

    def get_metrics_history(self) -> list[SystemMetrics]:
        """
        Get historical metrics.

        Returns:
            List of historical system metrics
        """
        with self._lock:
            return self.metrics_history.copy()

    def get_average_metrics(self, last_n: Optional[int] = None) -> SystemMetrics:
        """
        Get average metrics over the specified number of recent measurements.

        Args:
            last_n: Number of recent measurements to average (None for all)

        Returns:
            Average system metrics
        """
        with self._lock:
            if not self.metrics_history:
                return self.get_current_metrics()

            metrics = self.metrics_history[-last_n:] if last_n else self.metrics_history

            if not metrics:
                return self.get_current_metrics()

            # Calculate averages
            avg_cpu = sum(m.cpu_percent for m in metrics) / len(metrics)
            avg_memory_percent = sum(m.memory_percent for m in metrics) / len(metrics)
            avg_memory_used = sum(m.memory_used_mb for m in metrics) / len(metrics)
            avg_disk_percent = sum(m.disk_usage_percent for m in metrics) / len(metrics)
            avg_disk_free = sum(m.disk_free_gb for m in metrics) / len(metrics)
            latest_network_sent = metrics[-1].network_bytes_sent
            latest_network_recv = metrics[-1].network_bytes_recv

            return SystemMetrics(
                cpu_percent=avg_cpu,
                memory_percent=avg_memory_percent,
                memory_used_mb=avg_memory_used,
                memory_total_mb=metrics[0].memory_total_mb,  # Total doesn't change
                disk_usage_percent=avg_disk_percent,
                disk_free_gb=avg_disk_free,
                network_bytes_sent=latest_network_sent,
                network_bytes_recv=latest_network_recv,
                timestamp=time.time()
            )

    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self._monitoring:
            try:
                metrics = self.get_current_metrics()
                with self._lock:
                    self.metrics_history.append(metrics)
                    # Maintain history size limit
                    if len(self.metrics_history) > self.history_size:
                        self.metrics_history.pop(0)

            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")

            time.sleep(self.interval)


# Additional monitoring functions

def monitor_system_resources(interval: float = 1.0):
    """
    Context manager for monitoring system resources during execution.

    Args:
        interval: Monitoring interval in seconds

    Returns:
        Context manager that yields a SystemMonitor instance
    """
    def _context_manager():
        monitor = SystemMonitor(interval=interval)
        monitor.start_monitoring()
        try:
            yield monitor
        finally:
            monitor.stop_monitoring()

    return _context_manager()


def profile_memory_usage(func: Callable) -> Callable:
    """
    Decorator to profile memory usage of a function.

    Args:
        func: Function to profile

    Returns:
        Decorated function that tracks memory usage
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not HAS_PSUTIL:
            logger.warning("psutil not available, memory profiling disabled")
            return func(*args, **kwargs)

        process = psutil.Process()
        memory_before = process.memory_info().rss / (1024 * 1024)

        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            memory_after = process.memory_info().rss / (1024 * 1024)
            memory_delta = memory_after - memory_before

            logger.info(
                f"Memory profile for {func.__name__}: "
                f"before={memory_before:.1f}MB, "
                f"after={memory_after:.1f}MB, "
                f"delta={memory_delta:+.1f}MB, "
                f"duration={end_time - start_time:.3f}s"
            )

    return wrapper


def get_system_metrics() -> dict[str, Any]:
    """
    Get comprehensive system metrics.

    Returns:
        Dictionary containing current system metrics
    """
    monitor = SystemMonitor()
    metrics = monitor.get_current_metrics()

    return {
        "cpu_percent": metrics.cpu_percent,
        "memory_percent": metrics.memory_percent,
        "memory_used_mb": metrics.memory_used_mb,
        "memory_total_mb": metrics.memory_total_mb,
        "disk_usage_percent": metrics.disk_usage_percent,
        "disk_free_gb": metrics.disk_free_gb,
        "network_bytes_sent": metrics.network_bytes_sent,
        "network_bytes_recv": metrics.network_bytes_recv,
        "timestamp": metrics.timestamp
    }


@contextmanager
def track_resource_usage(operation: str):
    """
    Context manager to track resource usage for an operation.

    Args:
        operation: Name of the operation being tracked
    """
    if not HAS_PSUTIL:
        logger.warning("psutil not available, resource tracking disabled")
        yield
        return

    monitor = SystemMonitor(interval=0.5)  # Frequent sampling
    monitor.start_monitoring()

    start_time = time.time()
    start_metrics = monitor.get_current_metrics()

    try:
        yield
    finally:
        end_time = time.time()
        end_metrics = monitor.get_current_metrics()

        monitor.stop_monitoring()

        duration = end_time - start_time
        cpu_used = end_metrics.cpu_percent - start_metrics.cpu_percent
        memory_delta = end_metrics.memory_used_mb - start_metrics.memory_used_mb

        logger.info(
            f"Resource tracking for '{operation}': "
            f"duration={duration:.3f}s, "
            f"cpu_delta={cpu_used:+.1f}%, "
            f"memory_delta={memory_delta:+.1f}MB"
        )
