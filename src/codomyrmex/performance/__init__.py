"""
Performance optimization utilities for Codomyrmex.

This module provides lazy loading, caching, and other performance optimizations
to improve startup time and runtime performance.
"""

from .lazy_loader import LazyLoader, lazy_import
from .cache_manager import CacheManager, cached_function
from .performance_monitor import PerformanceMonitor

__all__ = [
    'LazyLoader',
    'lazy_import', 
    'CacheManager',
    'cached_function',
    'PerformanceMonitor'
]

__version__ = "0.1.0"
