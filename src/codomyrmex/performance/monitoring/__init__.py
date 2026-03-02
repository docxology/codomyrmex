"""
Monitoring subpackage for Codomyrmex performance module.

Provides performance monitoring and resource tracking capabilities including
execution time tracking, memory profiling, CPU usage monitoring, and
comprehensive system resource reporting.
"""

from .resource_tracker import (
    ResourceSnapshot,
    ResourceTracker,
    ResourceTrackingResult,
    benchmark_resource_usage,
    create_resource_report,
    track_memory_usage,
)

# Import performance_monitor with fallback if psutil is not available
try:
    from .performance_monitor import (
        PerformanceMetrics,
        PerformanceMonitor,
        SystemMetrics,
        SystemMonitor,
        get_system_metrics,
        monitor_performance,
        performance_context,
        profile_memory_usage,
        track_resource_usage,
    )

    PERFORMANCE_MONITOR_AVAILABLE = True
except ImportError:
    PerformanceMonitor = None
    PERFORMANCE_MONITOR_AVAILABLE = False

    def monitor_performance(*args, **kwargs):
        """No-op decorator if dependencies missing."""
        def decorator(func):
            """decorator ."""
            return func
        return decorator

    class performance_context:
        """No-op context manager if dependencies missing."""
        def __init__(self, *args, **kwargs): return None  # No-op stub
        def __enter__(self): return self
        def __exit__(self, *args): return None  # No-op stub

    def get_system_metrics(*args, **kwargs):
        return {}

__all__ = [
    "ResourceSnapshot",
    "ResourceTracker",
    "ResourceTrackingResult",
    "benchmark_resource_usage",
    "create_resource_report",
    "track_memory_usage",
    "PerformanceMonitor",
    "PerformanceMetrics",
    "SystemMetrics",
    "SystemMonitor",
    "monitor_performance",
    "performance_context",
    "get_system_metrics",
    "profile_memory_usage",
    "track_resource_usage",
    "PERFORMANCE_MONITOR_AVAILABLE",
]
