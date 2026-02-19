# DEPRECATED(v0.2.0): Shim module. Import from codomyrmex.performance.monitoring.resource_tracker instead. Will be removed in v0.3.0.
"""
Backward-compatibility shim.

This module has been moved to codomyrmex.performance.monitoring.resource_tracker.
All imports are re-exported here for backward compatibility.
"""

from codomyrmex.performance.monitoring.resource_tracker import (  # noqa: F401
    ResourceSnapshot,
    ResourceTrackingResult,
    ResourceTracker,
    track_memory_usage,
    create_resource_report,
    benchmark_resource_usage,
)
