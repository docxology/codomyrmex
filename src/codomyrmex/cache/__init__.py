"""
Cache module for Codomyrmex.

This module provides unified caching strategies for code analysis results,
LLM responses, build artifacts, and other frequently accessed data.
"""

from typing import Any, Optional

from codomyrmex.exceptions import CodomyrmexError

from .cache import Cache
from .cache_manager import CacheManager
from .stats import CacheStats

__all__ = [
    "Cache",
    "CacheManager",
    "CacheStats",
    "get_cache",
]

__version__ = "0.1.0"


class CacheError(CodomyrmexError):
    """Raised when cache operations fail."""

    pass


def get_cache(name: str = "default", backend: str = "in_memory") -> Cache:
    """Get a cache instance by name.

    Args:
        name: Cache name
        backend: Cache backend (in_memory, file_based, redis)

    Returns:
        Cache instance
    """
    manager = CacheManager()
    return manager.get_cache(name, backend)

