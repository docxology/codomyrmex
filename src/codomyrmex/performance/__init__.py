"""
Performance optimization utilities for Codomyrmex.

This module provides lazy loading, caching, and other performance optimizations
to improve startup time and runtime performance.
"""

from codomyrmex.exceptions import CodomyrmexError

from .cache_manager import CacheManager, cached_function
from .lazy_loader import LazyLoader, lazy_import

# Import PerformanceMonitor with fallback if psutil is not available
try:
    from .performance_monitor import PerformanceMonitor, monitor_performance, performance_context

    PERFORMANCE_MONITOR_AVAILABLE = True
except ImportError:
    PerformanceMonitor = None
    PERFORMANCE_MONITOR_AVAILABLE = False
    
    def monitor_performance(*args, **kwargs):
        """No-op decorator if dependencies missing."""
        def decorator(func):

            return func
        return decorator

    class performance_context:
        """No-op context manager if dependencies missing."""
        def __init__(self, *args, **kwargs): pass

        def __enter__(self): return self

        def __exit__(self, *args): pass

__all__ = [
    "LazyLoader",
    "lazy_import",
    "CacheManager",
    "cached_function",
]

if PERFORMANCE_MONITOR_AVAILABLE:
    __all__.append("PerformanceMonitor")
    __all__.append("monitor_performance")
    __all__.append("performance_context")
else:
    __all__.append("monitor_performance") # Export the no-op version
    __all__.append("performance_context") # Export the no-op version

__version__ = "0.1.0"
