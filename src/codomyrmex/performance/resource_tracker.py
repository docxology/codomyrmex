from typing import Dict, List, Any, Optional, Callable
import logging
import time

from contextlib import contextmanager
from dataclasses import dataclass, field
import psutil
import threading

from codomyrmex.logging_monitoring.logger_config import get_logger







Resource Tracker for Codomyrmex Performance Monitoring

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
    psutil = None
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
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
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
            "context": self.context
        }

@dataclass
class ResourceTrackingResult:
    """Result of resource tracking for an operation."""

    operation: str
    start_time: float
    end_time: float
    duration: float
    snapshots: List[ResourceSnapshot]
    peak_memory_rss_mb: float
    peak_memory_vms_mb: float
    average_cpu_percent: float
    total_cpu_time: float
    memory_delta_mb: float
    summary: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
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
            "summary": self.summary
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
        self._snapshots: List[ResourceSnapshot] = []
        self._lock = threading.Lock()

        if not HAS_PSUTIL:
            logger.warning("psutil not available, resource tracking will be limited")

    def start_tracking(self, operation: str, context: Optional[Dict[str, Any]] = None) -> None:
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

        logger.info(f"Started resource tracking for operation: {operation}")

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
            logger.warning(f"Operation name mismatch: expected {self._operation}, got {operation}")

        self._tracking = False
        end_time = time.time()

        # Take final snapshot
        self._take_snapshot("end")

        # Calculate results
        result = self._calculate_results(operation, end_time)

        logger.info(f"Stopped resource tracking for operation: {operation}")
        logger.info(f"Tracking summary: {result.duration:.3f}s, "
                   f"peak memory: {result.peak_memory_rss_mb:.1f}MB, "
                   f"avg CPU: {result.average_cpu_percent:.1f}%")

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
                context={"phase": phase, **self._context}
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
            logger.error(f"Error taking resource snapshot: {e}")

    def _calculate_results(self, operation: str, end_time: float) -> ResourceTrackingResult:
        """Calculate tracking results from snapshots."""
        if not self._snapshots:
            return self._create_empty_result(operation)

        start_snapshot = self._snapshots[0]
        end_snapshot = self._snapshots[-1]

        # Calculate peaks and averages
        memory_rss_values = [s.memory_rss_mb for s in self._snapshots]
        memory_vms_values = [s.memory_vms_mb for s in self._snapshots]
        cpu_values = [s.cpu_percent for s in self._snapshots]

        peak_memory_rss = max(memory_rss_values) if memory_rss_values else 0.0
        peak_memory_vms = max(memory_vms_values) if memory_vms_values else 0.0
        average_cpu = sum(cpu_values) / len(cpu_values) if cpu_values else 0.0

        # Calculate CPU time (approximate)
        if len(self._snapshots) > 1:
            time_span = self._snapshots[-1].timestamp - self._snapshots[0].timestamp
            total_cpu_time = average_cpu * time_span / 100.0  # Convert percent to fraction
        else:
            total_cpu_time = 0.0

        memory_delta = end_snapshot.memory_rss_mb - start_snapshot.memory_rss_mb

        # Create summary
        summary = {
            "total_snapshots": len(self._snapshots),
            "sample_interval": self.sample_interval,
            "memory_trend": "increasing" if memory_delta > 1.0 else "stable" if abs(memory_delta) < 1.0 else "decreasing",
            "cpu_intensity": "high" if average_cpu > 50 else "medium" if average_cpu > 20 else "low",
            "thread_count": end_snapshot.num_threads,
            "tracking_quality": "good" if len(self._snapshots) > 10 else "limited"
        }

        return ResourceTrackingResult(
            operation=operation,
            start_time=start_snapshot.timestamp,
            end_time=end_time,
            duration=end_time - start_snapshot.timestamp,
            snapshots=self._snapshots.copy(),
            peak_memory_rss_mb=peak_memory_rss,
            peak_memory_vms_mb=peak_memory_vms,
            average_cpu_percent=average_cpu,
            total_cpu_time=total_cpu_time,
            memory_delta_mb=memory_delta,
            summary=summary
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
            summary={"error": "No tracking data available"}
        )

    def get_current_snapshot(self) -> Optional[ResourceSnapshot]:
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
        """Brief description of wrapper.
        
        Args:
        
            Returns: Description of return value
        """
"""
        tracker.start_tracking(func.__name__, {"args_count": len(args), "kwargs_count": len(kwargs)})

        try:
            result = func(*args, **kwargs)
            return result
        finally:
            tracking_result = tracker.stop_tracking(func.__name__)

            logger.info(
                f"Memory tracking for {func.__name__}: "
                f"duration={tracking_result.duration:.3f}s, "
                f"peak_memory={tracking_result.peak_memory_rss_mb:.1f}MB, "
                f"memory_delta={tracking_result.memory_delta_mb:+.1f}MB"
            )

    yield wrapper

def create_resource_report(results: List[ResourceTrackingResult]) -> Dict[str, Any]:
    """
    Create a comprehensive resource usage report from multiple tracking results.

    Args:
        results: List of resource tracking results

    Returns:
        Comprehensive report dictionary
    """
    if not results:
        return {"status": "no_data", "message": "No resource tracking results provided"}

    # Aggregate statistics
    total_operations = len(results)
    total_duration = sum(r.duration for r in results)
    avg_duration = total_duration / total_operations if total_operations > 0 else 0

    peak_memories = [r.peak_memory_rss_mb for r in results]
    max_peak_memory = max(peak_memories) if peak_memories else 0
    avg_peak_memory = sum(peak_memories) / len(peak_memories) if peak_memories else 0

    cpu_usages = [r.average_cpu_percent for r in results]
    max_cpu_usage = max(cpu_usages) if cpu_usages else 0
    avg_cpu_usage = sum(cpu_usages) / len(cpu_usages) if cpu_usages else 0

    # Identify resource-intensive operations
    memory_hogs = sorted(results, key=lambda r: r.peak_memory_rss_mb, reverse=True)[:5]
    cpu_hogs = sorted(results, key=lambda r: r.average_cpu_percent, reverse=True)[:5]
    slow_operations = sorted(results, key=lambda r: r.duration, reverse=True)[:5]

    return {
        "summary": {
            "total_operations": total_operations,
            "total_duration_seconds": total_duration,
            "average_duration_seconds": avg_duration,
            "max_peak_memory_mb": max_peak_memory,
            "average_peak_memory_mb": avg_peak_memory,
            "max_cpu_usage_percent": max_cpu_usage,
            "average_cpu_usage_percent": avg_cpu_usage
        },
        "top_consumers": {
            "memory_hogs": [{"operation": r.operation, "peak_memory_mb": r.peak_memory_rss_mb} for r in memory_hogs],
            "cpu_hogs": [{"operation": r.operation, "avg_cpu_percent": r.average_cpu_percent} for r in cpu_hogs],
            "slow_operations": [{"operation": r.operation, "duration_seconds": r.duration} for r in slow_operations]
        },
        "detailed_results": [r.to_dict() for r in results],
        "generated_at": time.time()
    }

def benchmark_resource_usage(func: Callable, iterations: int = 10, *args, **kwargs) -> Dict[str, Any]:
    """
    Benchmark resource usage of a function over multiple iterations.

    Args:
        func: Function to benchmark
        iterations: Number of iterations to run
        *args, **kwargs: Arguments to pass to the function

    Returns:
        Benchmark results dictionary
    """
    tracker = ResourceTracker(sample_interval=0.05)  # More frequent sampling for benchmarks

    results = []

    for i in range(iterations):
        tracker.start_tracking(f"{func.__name__}_iteration_{i+1}")

        try:
            result = func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Benchmark iteration {i+1} failed: {e}")
            result = None

        tracking_result = tracker.stop_tracking(f"{func.__name__}_iteration_{i+1}")
        results.append(tracking_result)

    # Create benchmark report
    report = create_resource_report(results)

    # Add benchmark-specific metrics
    if results:
        durations = [r.duration for r in results]
        memory_peaks = [r.peak_memory_rss_mb for r in results]

        report["benchmark_metrics"] = {
            "iterations": iterations,
            "duration_stats": {
                "min": min(durations),
                "max": max(durations),
                "mean": sum(durations) / len(durations),
                "std_dev": (sum((d - sum(durations)/len(durations))**2 for d in durations) / len(durations))**0.5
            },
            "memory_stats": {
                "min_peak": min(memory_peaks),
                "max_peak": max(memory_peaks),
                "mean_peak": sum(memory_peaks) / len(memory_peaks)
            }
        }

    return report
