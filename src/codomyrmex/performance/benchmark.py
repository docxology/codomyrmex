"""
Backward-compatibility shim.

This module has been moved to codomyrmex.performance.profiling.benchmark.
All imports are re-exported here for backward compatibility.
"""

from codomyrmex.performance.profiling.benchmark import (  # noqa: F401
    PerformanceProfiler,
    profile_function,
    run_benchmark,
)
