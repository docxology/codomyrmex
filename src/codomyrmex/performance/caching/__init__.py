"""
Caching subpackage for Codomyrmex performance module.

Provides caching capabilities to improve performance by storing expensive
computation results and avoiding redundant work. Supports both in-memory
and disk-based caching with configurable expiration and size limits.
"""

from .cache_manager import (
    CacheManager,
    cached_function,
    clear_cache,
    get_cache_stats,
)

__all__ = [
    "CacheManager",
    "cached_function",
    "clear_cache",
    "get_cache_stats",
]
