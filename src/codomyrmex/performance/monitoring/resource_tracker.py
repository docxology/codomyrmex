import logging
import threading
import time
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any

import psutil

from codomyrmex.logging_monitoring import get_logger

"""
# Resource Tracker for Codomyrmex Performance Monitoring

This module provides detailed resource tracking capabilities for monitoring
memory usage, CPU consumption, and other system resources during operations.
"""

# Import logging
try:
    logger = get_logger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)

# Import psutil for system monitoring
try:
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


@dataclass
class ResourceSnapshot:
    """Snapshot of resource usage at a point in time."""

    timestamp: float
    memory_rss_mb: float
    memory_vms_mb: float
    cpu_percent: float
    cpu_times_user: float
    cpu_times_system: float
    num_threads: int
    num_fds: int = 0  # File descriptors (Unix only)
    context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "memory_rss_mb": self.memory_rss_mb,
            "memory_vms_mb": self.memory_vms_mb,
            "cpu_percent": self.cpu_percent,
            "cpu_times_user": self.cpu_times_user,
            "cpu_times_system": self.cpu_times_system,
            "num_threads": self.num_threads,
            "num_fds": self.num_fds,
            "context": self.context,
        }


@dataclass
class ResourceTrackingResult:
    """Result of resource tracking for an operation."""

    operation: str
    start_time: float
    end_time: float
    duration: float
    snapshots: list[ResourceSnapshot]
    peak_memory_rss_mb: float
    peak_memory_vms_mb: float
    average_cpu_percent: float
    total_cpu_time: float
    memory_delta_mb: float
    summary: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "operation": self.operation,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "peak_memory_rss_mb": self.peak_memory_rss_mb,
            "peak_memory_vms_mb": self.peak_memory_vms_mb,
            "average_cpu_percent": self.average_cpu_percent,
            "total_cpu_time": self.total_cpu_time,
            "memory_delta_mb": self.memory_delta_mb,
            "snapshot_count": len(self.snapshots),
            "summary": self.summary,
        }


class ResourceTracker:
    """
    Advanced resource tracker for monitoring system resource usage.

    Provides detailed tracking of memory, CPU, threads, and other system
    resources during operation execution with configurable sampling rates.
    """

    def __init__(self, sample_interval: float = 0.1, max_snapshots: int = 1000):
        """
        Initialize the resource tracker.

        Args:
            sample_interval: Time between resource samples in seconds
            max_snapshots: Maximum number of snapshots to keep
        """
        self.sample_interval = sample_interval
        self.max_snapshots = max_snapshots
        self._tracking = False
        self._snapshots: list[ResourceSnapshot] = []
        self._lock = threading.Lock()

        if not HAS_PSUTIL:
            logger.warning("psutil not available, resource tracking will be limited")

    def start_tracking(
        self, operation: str, context: dict[str, Any] | None = None
    ) -> None:
        """
        Start tracking resources for an operation.

        Args:
            operation: Name of the operation being tracked
            context: Additional context information
        """
        if self._tracking:
            logger.warning("Resource tracking already in progress")
            return

        self._tracking = True
        self._snapshots.clear()
        self._operation = operation
        self._context = context or {}
        self._start_time = time.time()

        logger.info("Started resource tracking for operation: %s", operation)

        # Take initial snapshot
        self._take_snapshot("start")

    def stop_tracking(self, operation: str) -> ResourceTrackingResult:
        """
        Stop tracking and return results.

        Args:
            operation: Name of the operation (for validation)

        Returns:
            ResourceTrackingResult with complete tracking data
        """
        if not self._tracking:
            logger.warning("Resource tracking not in progress")
            return self._create_empty_result(operation)

        if operation != self._operation:
            logger.warning(
                "Operation name mismatch: expected %s, got %s",
                self._operation,
                operation,
            )

        self._tracking = False
        end_time = time.time()

        # Take final snapshot
        self._take_snapshot("end")

        # Calculate results
        result = self._calculate_results(operation, end_time)

        logger.info("Stopped resource tracking for operation: %s", operation)
        logger.info(
            "Tracking summary: %.3fs, peak memory: %.1fMB, avg CPU: %.1f%%",
            result.duration,
            result.peak_memory_rss_mb,
            result.average_cpu_percent,
        )

        return result

    def _take_snapshot(self, phase: str = "") -> None:
        """Take a resource usage snapshot."""
        if not HAS_PSUTIL:
            return

        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            cpu_times = process.cpu_times()
            cpu_percent = process.cpu_percent(interval=None)

            snapshot = ResourceSnapshot(
                timestamp=time.time(),
                memory_rss_mb=memory_info.rss / (1024 * 1024),
                memory_vms_mb=memory_info.vms / (1024 * 1024),
                cpu_percent=cpu_percent,
                cpu_times_user=cpu_times.user,
                cpu_times_system=cpu_times.system,
                num_threads=process.num_threads(),
                context={"phase": phase, **self._context},
            )

            # Try to get file descriptor count (Unix only)
            try:
                snapshot.num_fds = len(process.open_files())
            except (psutil.AccessDenied, AttributeError):
                snapshot.num_fds = 0

            with self._lock:
                self._snapshots.append(snapshot)

                # Maintain snapshot limit
                if len(self._snapshots) > self.max_snapshots:
                    # Remove oldest snapshots, keeping at least the first and last
                    if len(self._snapshots) > 2:
                        self._snapshots.pop(1)

        except Exception as e:
            logger.error("Error taking resource snapshot: %s", e)

    def _snapshot_stats(self) -> tuple[float, float, float, float, float]:
        """Return (peak_rss, peak_vms, avg_cpu, total_cpu_time, memory_delta) from snapshots."""
        snaps = self._snapshots
        rss = [s.memory_rss_mb for s in snaps]
        vms = [s.memory_vms_mb for s in snaps]
        cpu = [s.cpu_percent for s in snaps]
        peak_rss = max(rss) if rss else 0.0
        peak_vms = max(vms) if vms else 0.0
        avg_cpu = sum(cpu) / len(cpu) if cpu else 0.0
        time_span = snaps[-1].timestamp - snaps[0].timestamp if len(snaps) > 1 else 0.0
        total_cpu_time = avg_cpu * time_span / 100.0
        memory_delta = snaps[-1].memory_rss_mb - snaps[0].memory_rss_mb
        return peak_rss, peak_vms, avg_cpu, total_cpu_time, memory_delta

    def _build_result_summary(
        self, avg_cpu: float, memory_delta: float, end_snapshot: object
    ) -> dict:
        """Build the summary dict for a ResourceTrackingResult."""
        return {
            "total_snapshots": len(self._snapshots),
            "sample_interval": self.sample_interval,
            "memory_trend": "increasing"
            if memory_delta > 1.0
            else "stable"
            if abs(memory_delta) < 1.0
            else "decreasing",
            "cpu_intensity": "high"
            if avg_cpu > 50
            else "medium"
            if avg_cpu > 20
            else "low",
            "thread_count": end_snapshot.num_threads,
            "tracking_quality": "good" if len(self._snapshots) > 10 else "limited",
        }

    def _calculate_results(
        self, operation: str, end_time: float
    ) -> ResourceTrackingResult:
        """Calculate tracking results from snapshots."""
        if not self._snapshots:
            return self._create_empty_result(operation)
        start_snapshot = self._snapshots[0]
        end_snapshot = self._snapshots[-1]
        peak_rss, peak_vms, avg_cpu, total_cpu_time, memory_delta = (
            self._snapshot_stats()
        )
        summary = self._build_result_summary(avg_cpu, memory_delta, end_snapshot)
        return ResourceTrackingResult(
            operation=operation,
            start_time=start_snapshot.timestamp,
            end_time=end_time,
            duration=end_time - start_snapshot.timestamp,
            snapshots=self._snapshots.copy(),
            peak_memory_rss_mb=peak_rss,
            peak_memory_vms_mb=peak_vms,
            average_cpu_percent=avg_cpu,
            total_cpu_time=total_cpu_time,
            memory_delta_mb=memory_delta,
            summary=summary,
        )

    def _create_empty_result(self, operation: str) -> ResourceTrackingResult:
        """Create an empty result for error cases."""
        return ResourceTrackingResult(
            operation=operation,
            start_time=time.time(),
            end_time=time.time(),
            duration=0.0,
            snapshots=[],
            peak_memory_rss_mb=0.0,
            peak_memory_vms_mb=0.0,
            average_cpu_percent=0.0,
            total_cpu_time=0.0,
            memory_delta_mb=0.0,
            summary={"error": "No tracking data available"},
        )

    def get_current_snapshot(self) -> ResourceSnapshot | None:
        """Get the most recent snapshot."""
        with self._lock:
            return self._snapshots[-1] if self._snapshots else None

    def get_snapshot_count(self) -> int:
        """Get the number of snapshots taken."""
        with self._lock:
            return len(self._snapshots)

    def is_tracking(self) -> bool:
        """Check if tracking is currently active."""
        return self._tracking


@contextmanager
def track_memory_usage(func: Callable):
    """
    Context manager decorator to track memory usage of a function.

    Args:
        func: Function to track

    Yields:
        Function result
    """
    tracker = ResourceTracker()

    def wrapper(*args, **kwargs):
        """Wrapper."""
        tracker.start_tracking(
            func.__name__, {"args_count": len(args), "kwargs_count": len(kwargs)}
        )

        try:
            result = func(*args, **kwargs)
            return result
        finally:
            tracking_result = tracker.stop_tracking(func.__name__)

            logger.info(
                "Memory tracking for %s: duration=%.3fs, peak_memory=%.1fMB, memory_delta=%+.1fMB",
                func.__name__,
                tracking_result.duration,
                tracking_result.peak_memory_rss_mb,
                tracking_result.memory_delta_mb,
            )

    yield wrapper


def _report_summary(results: list[ResourceTrackingResult]) -> dict[str, Any]:
    """Compute aggregate summary stats for a resource report."""
    n = len(results)
    total_duration = sum(r.duration for r in results)
    peak_memories = [r.peak_memory_rss_mb for r in results]
    cpu_usages = [r.average_cpu_percent for r in results]
    return {
        "total_operations": n,
        "total_duration_seconds": total_duration,
        "average_duration_seconds": total_duration / n if n else 0,
        "max_peak_memory_mb": max(peak_memories) if peak_memories else 0,
        "average_peak_memory_mb": sum(peak_memories) / len(peak_memories)
        if peak_memories
        else 0,
        "max_cpu_usage_percent": max(cpu_usages) if cpu_usages else 0,
        "average_cpu_usage_percent": sum(cpu_usages) / len(cpu_usages)
        if cpu_usages
        else 0,
    }


def _report_top_consumers(results: list[ResourceTrackingResult]) -> dict[str, Any]:
    """Return top-5 memory/cpu/slow consumers for a resource report."""
    return {
        "memory_hogs": [
            {"operation": r.operation, "peak_memory_mb": r.peak_memory_rss_mb}
            for r in sorted(results, key=lambda r: r.peak_memory_rss_mb, reverse=True)[
                :5
            ]
        ],
        "cpu_hogs": [
            {"operation": r.operation, "avg_cpu_percent": r.average_cpu_percent}
            for r in sorted(results, key=lambda r: r.average_cpu_percent, reverse=True)[
                :5
            ]
        ],
        "slow_operations": [
            {"operation": r.operation, "duration_seconds": r.duration}
            for r in sorted(results, key=lambda r: r.duration, reverse=True)[:5]
        ],
    }


def create_resource_report(results: list[ResourceTrackingResult]) -> dict[str, Any]:
    """Create a comprehensive resource usage report from multiple tracking results."""
    if not results:
        return {"status": "no_data", "message": "No resource tracking results provided"}
    return {
        "summary": _report_summary(results),
        "top_consumers": _report_top_consumers(results),
        "detailed_results": [r.to_dict() for r in results],
        "generated_at": time.time(),
    }


def _benchmark_metrics(
    results: list[ResourceTrackingResult], iterations: int
) -> dict[str, Any]:
    """Compute duration and memory stats for a benchmark run."""
    durations = [r.duration for r in results]
    memory_peaks = [r.peak_memory_rss_mb for r in results]
    mean_d = sum(durations) / len(durations)
    return {
        "iterations": iterations,
        "duration_stats": {
            "min": min(durations),
            "max": max(durations),
            "mean": mean_d,
            "std_dev": (sum((d - mean_d) ** 2 for d in durations) / len(durations))
            ** 0.5,
        },
        "memory_stats": {
            "min_peak": min(memory_peaks),
            "max_peak": max(memory_peaks),
            "mean_peak": sum(memory_peaks) / len(memory_peaks),
        },
    }


def benchmark_resource_usage(
    func: Callable, iterations: int = 10, *args, **kwargs
) -> dict[str, Any]:
    """Benchmark resource usage of a function over multiple iterations."""
    tracker = ResourceTracker(sample_interval=0.05)
    results = []
    for i in range(iterations):
        label = f"{func.__name__}_iteration_{i + 1}"
        tracker.start_tracking(label)
        try:
            func(*args, **kwargs)
        except Exception as e:
            logger.error("Benchmark iteration %s failed: %s", i + 1, e)
        results.append(tracker.stop_tracking(label))
    report = create_resource_report(results)
    if results:
        report["benchmark_metrics"] = _benchmark_metrics(results, iterations)
    return report
