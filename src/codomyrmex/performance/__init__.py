"""
Performance optimization utilities for Codomyrmex.

This module provides lazy loading, caching, and other performance optimizations
to improve startup time and runtime performance.

Subpackages:
    profiling    - Benchmarking and async function profiling
    caching      - In-memory and disk-based caching
    optimization - Lazy loading utilities
    monitoring   - Performance monitoring and resource tracking
"""

from codomyrmex.exceptions import CodomyrmexError

from . import analysis, benchmarking  # noqa: F401
from .caching.cache_manager import CacheManager, cached_function
from .optimization.lazy_loader import LazyLoader, lazy_import

# Import benchmark utilities
from .profiling.benchmark import (
    PerformanceProfiler,
    profile_function,
    run_benchmark,
)

# Import PerformanceMonitor — requires psutil. If unavailable, callers must guard
# with `if PERFORMANCE_MONITOR_AVAILABLE:` before using monitor_performance.
try:
    from .monitoring.performance_monitor import (
        PerformanceMonitor,
        get_system_metrics,
        monitor_performance,
        performance_context,
    )

    PERFORMANCE_MONITOR_AVAILABLE = True
except ImportError:
    import logging as _logging
    _logging.getLogger("codomyrmex.performance").warning(
        "psutil is not installed; performance monitoring is disabled. "
        "Enable it with: uv sync --extra performance"
    )
    PerformanceMonitor = None
    PERFORMANCE_MONITOR_AVAILABLE = False

    # Provide no-op fallbacks
    def monitor_performance(*args, **kwargs):
        def decorator(func):
            return func
        if len(args) == 1 and callable(args[0]):
            return args[0]
        return decorator

    class _NoOpContext:
        def __enter__(self): return self
        def __exit__(self, exc_type, exc_val, exc_tb): pass

    def performance_context(*args, **kwargs):
        return _NoOpContext()

    def get_system_metrics(*args, **kwargs):
        return {}


__version__ = "0.1.0"


def cli_commands():
    """Return CLI commands for the performance module."""

    def _run_profiler():
        """Run the performance profiler."""
        print(f"Performance module v{__version__}")
        print("Profiler: PerformanceProfiler")
        print("  Use profile_function() to profile individual functions")
        print("  Use run_benchmark() for benchmark suites")
        if PERFORMANCE_MONITOR_AVAILABLE:
            print("  PerformanceMonitor: available (psutil detected)")
        else:
            print("  PerformanceMonitor: unavailable (psutil not installed)")

    def _performance_report():
        """Show performance report."""
        print(f"Performance module v{__version__}")
        print("Components:")
        print("  LazyLoader: available")
        print("  CacheManager: available")
        print("  PerformanceProfiler: available")
        print(
            f"  PerformanceMonitor: {'available' if PERFORMANCE_MONITOR_AVAILABLE else 'unavailable'}"
        )

    return {
        "profile": _run_profiler,
        "report": _performance_report,
    }


__all__ = [
    "LazyLoader",
    "lazy_import",
    "CacheManager",
    "cached_function",
    "PerformanceProfiler",
    "profile_function",
    "run_benchmark",
    "cli_commands",
]

if PERFORMANCE_MONITOR_AVAILABLE:
    __all__.append("PerformanceMonitor")

__all__.extend([
    "monitor_performance",
    "performance_context",
    "get_system_metrics"
])

