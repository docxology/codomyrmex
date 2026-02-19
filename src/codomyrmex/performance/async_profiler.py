# DEPRECATED(v0.2.0): Shim module. Import from codomyrmex.performance.profiling.async_profiler instead. Will be removed in v0.3.0.
"""
Backward-compatibility shim.

This module has been moved to codomyrmex.performance.profiling.async_profiler.
All imports are re-exported here for backward compatibility.
"""

from codomyrmex.performance.profiling.async_profiler import (  # noqa: F401
    AsyncProfiler,
)
