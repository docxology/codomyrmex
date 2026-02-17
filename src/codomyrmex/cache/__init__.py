"""
Cache module for Codomyrmex.

This module provides unified caching strategies for code analysis results,
LLM responses, build artifacts, and other frequently accessed data.
"""

from typing import Any, Optional

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None

# New submodule exports
from . import (
    async_ops,
    distributed,
    invalidation,
    policies,
    replication,
    serializers,
    warmers,
)
from .cache import Cache
from .cache_manager import CacheManager
from .exceptions import (
    CacheConnectionError,
    CacheError,
    CacheExpiredError,
    CacheFullError,
    CacheInvalidationError,
    CacheKeyError,
    CacheSerializationError,
)
from .namespaced import NamespacedCache
from .stats import CacheStats
from .ttl_manager import TTLManager

def cli_commands():
    """Return CLI commands for the cache module."""
    return {
        "backends": {
            "help": "List available cache backends",
            "handler": lambda **kwargs: print(
                "Cache Backends:\n"
                "  - in_memory   (default, dictionary-based)\n"
                "  - file_based  (disk-persistent cache)\n"
                "  - redis       (distributed cache)"
            ),
        },
        "stats": {
            "help": "Show cache statistics",
            "handler": lambda **kwargs: print(
                "Cache Statistics:\n"
                "  Active caches : 0\n"
                "  Total hits    : 0\n"
                "  Total misses  : 0\n"
                "  Hit ratio     : N/A"
            ),
        },
    }


__all__ = [
    # CLI integration
    "cli_commands",
    'replication',
    'async_ops',
    'warmers',
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
