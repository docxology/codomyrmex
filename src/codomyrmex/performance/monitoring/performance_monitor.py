
import functools
import json
import time
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring.core.logger_config import get_logger

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

@dataclass
class SystemMetrics:
    """Functional component: SystemMetrics."""
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
    """Functional component: SystemMonitor."""
    def __init__(self, interval: float = 1.0):
        """Execute   Init   operations natively."""
        self.interval = interval
        self._process = psutil.Process() if HAS_PSUTIL else None
        self._monitoring = False
        self._monitor_thread = None

    def start_monitoring(self):
        """Start continuous background monitoring loop."""
        if not HAS_PSUTIL or self._monitoring:
            return

        self._monitoring = True
        import threading
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

    def _monitor_loop(self):
        """Continuously poll resources."""
        while self._monitoring:
            self.get_current_metrics()
            time.sleep(self.interval)

    def stop_monitoring(self):
        """Halt the monitoring loop."""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2.0)

    def get_current_metrics(self) -> SystemMetrics:
        """Execute Get Current Metrics operations natively."""
        if not HAS_PSUTIL:
            return SystemMetrics(0,0,0,0,0,0,0,0)

        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        net = psutil.net_io_counters()

        return SystemMetrics(
            cpu_percent=psutil.cpu_percent(),
            memory_percent=mem.percent,
            memory_used_mb=mem.used / 1024 / 1024,
            memory_total_mb=mem.total / 1024 / 1024,
            disk_usage_percent=disk.percent,
            disk_free_gb=disk.free / 1024 / 1024 / 1024,
            network_bytes_sent=net.bytes_sent,
            network_bytes_recv=net.bytes_recv
        )

class PerformanceMonitor:
    """
    A performance monitor that tracks execution times and resource usage.

    This class provides methods to monitor function performance,
    track resource usage, and generate performance reports.
    """

    def __init__(self, log_file: str | Path | None = None):
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
        memory_usage_mb: float | None = None,
        cpu_percent: float | None = None,
        metadata: dict[str, Any] | None = None,
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
        except (OSError, ValueError) as e:
            # If we can't write to the log file, that's okay
            logger.debug("Failed to write performance log: %s", e)
            pass

    def get_stats(self, function_name: str | None = None) -> dict[str, Any]:
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

    def export_metrics(self, file_path: str | Path) -> None:
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
    function_name: str | None = None, monitor: PerformanceMonitor | None = None
) -> Callable:
    """
    Decorator for monitoring function performance.

    Args:
        function_name: Name to use for monitoring (defaults to function name)
        monitor: Performance monitor to use (defaults to global instance)

    Returns:
        Decorated function with performance monitoring enabled
    """

    def decorator(func: Callable) -> Callable:
        """Execute Decorator operations natively."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """Execute Wrapper operations natively."""
            current_monitor = monitor or _performance_monitor
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                execution_time = time.time() - start_time
                current_monitor.record_metrics(
                    function_name=function_name or func.__name__,
                    execution_time=execution_time
                )
        return wrapper
    return decorator

profile_function = monitor_performance


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
        """Execute Wrapper operations natively."""

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

        # Stop not strictly needed if start didn't spawn thread, but good for completeness
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


def clear_performance_metrics() -> None:
    """Clear all metrics from the global performance monitor."""
    _performance_monitor.clear_metrics()


def get_performance_stats(function_name: str | None = None) -> dict[str, Any]:
    """Get performance statistics from the global monitor.

    Args:
        function_name: If specified, only return stats for this function.

    Returns:
        Dictionary containing performance statistics.
    """
    return _performance_monitor.get_stats(function_name)


@contextmanager
def performance_context(operation: str):
    """Context manager that records execution time of a block.

    Args:
        operation: Name of the operation being tracked.
    """
    start_time = time.time()
    try:
        yield
    finally:
        execution_time = time.time() - start_time
        _performance_monitor.record_metrics(
            function_name=operation,
            execution_time=execution_time,
        )

