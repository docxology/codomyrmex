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
    from .performance_monitor import PerformanceMonitor

    PERFORMANCE_MONITOR_AVAILABLE = True
except ImportError:
    PerformanceMonitor = None
    PERFORMANCE_MONITOR_AVAILABLE = False

__all__ = [
    "LazyLoader",
    "lazy_import",
    "CacheManager",
    "cached_function",
]

if PERFORMANCE_MONITOR_AVAILABLE:
    __all__.append("PerformanceMonitor")

__version__ = "0.1.0"
