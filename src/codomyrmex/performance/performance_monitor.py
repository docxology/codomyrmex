"""
Backward-compatibility shim.

This module has been moved to codomyrmex.performance.monitoring.performance_monitor.
All imports are re-exported here for backward compatibility.
"""

from codomyrmex.performance.monitoring.performance_monitor import (  # noqa: F401
    PerformanceMetrics,
    SystemMetrics,
    SystemMonitor,
    PerformanceMonitor,
    monitor_performance,
    profile_function,
    profile_memory_usage,
    get_system_metrics,
    track_resource_usage,
    _performance_monitor,
    HAS_PSUTIL,
)
