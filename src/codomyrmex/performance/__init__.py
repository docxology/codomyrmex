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

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None

from .caching.cache_manager import CacheManager, cached_function
from .optimization.lazy_loader import LazyLoader, lazy_import

# Import benchmark utilities
from .profiling.benchmark import (
    PerformanceProfiler,
    profile_function,
    run_benchmark,
)

# Import PerformanceMonitor with fallback if psutil is not available
try:
    from .monitoring.performance_monitor import (
        PerformanceMonitor,
        get_system_metrics,
        monitor_performance,
        performance_context,
    )

    PERFORMANCE_MONITOR_AVAILABLE = True
except ImportError:
    PerformanceMonitor = None
    PERFORMANCE_MONITOR_AVAILABLE = False

    def monitor_performance(*args, **kwargs):
        raise ImportError(
            "psutil is required for performance monitoring. "
            "Install with: uv sync --extra performance"
        )

    class performance_context:
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "psutil is required for performance monitoring. "
                "Install with: uv sync --extra performance"
            )
        def __enter__(self): raise ImportError("psutil required for performance monitoring")
        def __exit__(self, *args): return None  # No-op: psutil not available

    def get_system_metrics(*args, **kwargs):
        raise ImportError(
            "psutil is required for performance monitoring. "
            "Install with: uv sync --extra performance"
        )

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
        print(f"  PerformanceMonitor: {'available' if PERFORMANCE_MONITOR_AVAILABLE else 'unavailable'}")

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
    __all__.append("monitor_performance")
    __all__.append("performance_context")
    __all__.append("get_system_metrics")
else:
    __all__.append("monitor_performance") # Export the no-op version
    __all__.append("performance_context") # Export the no-op version
    __all__.append("get_system_metrics")

__version__ = "0.1.0"

from . import analysis, benchmarking  # noqa: E402, F401
