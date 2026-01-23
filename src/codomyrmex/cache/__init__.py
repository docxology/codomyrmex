"""
Cache module for Codomyrmex.

This module provides unified caching strategies for code analysis results,
LLM responses, build artifacts, and other frequently accessed data.
"""

from typing import Any, Optional

from .cache import Cache
from .cache_manager import CacheManager
from .stats import CacheStats
from .namespaced import NamespacedCache
from .ttl_manager import TTLManager
from .exceptions import (
    CacheError,
    CacheExpiredError,
    CacheFullError,
    CacheConnectionError,
    CacheKeyError,
    CacheSerializationError,
    CacheInvalidationError,
)

# New submodule exports
from . import policies
from . import invalidation
from . import distributed
from . import serializers

__all__ = [
    # Core classes
    "Cache",
    "CacheManager",
    "CacheStats",
    "NamespacedCache",
    "TTLManager",
    # Functions
    "get_cache",
    # Exceptions
    "CacheError",
    "CacheExpiredError",
    "CacheFullError",
    "CacheConnectionError",
    "CacheKeyError",
    "CacheSerializationError",
    "CacheInvalidationError",
    # Submodules
    "policies",
    "invalidation",
    "distributed",
    "serializers",
]

__version__ = "0.1.0"


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
