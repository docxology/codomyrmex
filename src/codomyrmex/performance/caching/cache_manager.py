import functools
import hashlib
import json
import pickle
import tempfile
import time
from pathlib import Path
from typing import Any
from collections.abc import Callable

from codomyrmex.logging_monitoring.logger_config import get_logger

"""Caching utilities for Codomyrmex modules.

This module provides caching capabilities to improve performance
by storing expensive computation results and avoiding redundant work.
"""

logger = get_logger(__name__)

class CacheManager:
    """
    A cache manager that provides persistent caching for expensive operations.

    This class supports both in-memory and disk-based caching with
    configurable expiration times and cache size limits.
    """

    def __init__(
        self,
        cache_dir: str | Path | None = None,
        max_memory_items: int = 1000,
        default_ttl: int = 3600,
    ):  # 1 hour default TTL
        """
        Initialize the cache manager.

        Args:
            cache_dir: Directory for persistent cache files. If None, uses temp directory.
            max_memory_items: Maximum number of items to keep in memory cache.
            default_ttl: Default time-to-live for cache entries in seconds.
        """
        self.cache_dir = (
            Path(cache_dir)
            if cache_dir
            else Path(tempfile.gettempdir()) / "codomyrmex_cache"
        )
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.max_memory_items = max_memory_items
        self.default_ttl = default_ttl

        # In-memory cache: {key: (value, timestamp)}
        self._memory_cache: dict[str, tuple] = {}

        # Access tracking for LRU eviction
        self._access_times: dict[str, float] = {}

    def _generate_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Generate a cache key from function name and arguments."""
        # Create a deterministic string representation of the arguments
        key_data = {
            "func_name": func_name,
            "args": args,
            "kwargs": sorted(kwargs.items()) if kwargs else {},
        }

        # Create a hash of the key data
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()

    def _is_expired(self, timestamp: float, ttl: int) -> bool:
        """Check if a cache entry has expired."""
        return time.time() - timestamp > ttl

    def _evict_oldest(self):
        """Evict the oldest item from the memory cache."""
        if not self._access_times:
            return

        # Find the item with the oldest access time
        oldest_key = min(self._access_times.keys(), key=lambda k: self._access_times[k])

        # Remove from both caches
        self._memory_cache.pop(oldest_key, None)
        self._access_times.pop(oldest_key, None)

    def get(self, key: str) -> Any | None:
        """Get a value from the cache."""
        # Check memory cache first
        if key in self._memory_cache:
            cached_item = self._memory_cache[key]

            # Handle both old format (value, timestamp) and new format (value, timestamp, ttl)
            if len(cached_item) == 3:
                value, timestamp, ttl = cached_item
            else:
                value, timestamp = cached_item
                ttl = self.default_ttl

            if not self._is_expired(timestamp, ttl):
                # Update access time for LRU
                self._access_times[key] = time.time()
                return value
            else:
                # Remove expired entry
                self._memory_cache.pop(key, None)
                self._access_times.pop(key, None)

        # Check disk cache
        cache_file = self.cache_dir / f"{key}.pkl"
        if cache_file.exists():
            try:
                with open(cache_file, "rb") as f:
                    cached_data = pickle.load(f)

                # Handle both old format (value, timestamp) and new format (value, timestamp, ttl)
                if len(cached_data) == 3:
                    value, timestamp, ttl = cached_data
                else:
                    value, timestamp = cached_data
                    ttl = self.default_ttl

                if not self._is_expired(timestamp, ttl):
                    # Load into memory cache
                    self._memory_cache[key] = (value, timestamp, ttl)
                    self._access_times[key] = time.time()
                    return value
                else:
                    # Remove expired file
                    cache_file.unlink(missing_ok=True)
            except (pickle.PickleError, EOFError, OSError):
                # Remove corrupted cache file
                cache_file.unlink(missing_ok=True)

        return None

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set a value in the cache."""
        ttl = ttl or self.default_ttl
        timestamp = time.time()

        # Store in memory cache (value, timestamp, ttl)
        self._memory_cache[key] = (value, timestamp, ttl)
        self._access_times[key] = time.time()

        # Evict if we exceed the memory limit
        while len(self._memory_cache) > self.max_memory_items:
            self._evict_oldest()

        # Store in disk cache
        cache_file = self.cache_dir / f"{key}.pkl"
        try:
            with open(cache_file, "wb") as f:
                pickle.dump((value, timestamp, ttl), f)
        except (OSError, pickle.PickleError):
            # If we can't write to disk, that's okay - we still have it in memory
            pass

    def clear(self) -> None:
        """Clear all caches."""
        self._memory_cache.clear()
        self._access_times.clear()

        # Clear disk cache
        for cache_file in self.cache_dir.glob("*.pkl"):
            cache_file.unlink(missing_ok=True)

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return {
            "memory_items": len(self._memory_cache),
            "max_memory_items": self.max_memory_items,
            "cache_dir": str(self.cache_dir),
            "disk_files": len(list(self.cache_dir.glob("*.pkl"))),
        }


# Global cache manager instance
_cache_manager = CacheManager()


def cached_function(
    ttl: int | None = None,
    cache_key_prefix: str | None = None,
    cache_manager: CacheManager | None = None,
) -> Callable:
    """
    Decorator for caching function results.

    Args:
        ttl: Time-to-live for cache entries in seconds. If None, uses default.
        cache_key_prefix: Prefix for cache keys. If None, uses function name.
        cache_manager: Cache manager to use. If None, uses global instance.

    Returns:
        Decorated function with caching enabled

    Example:
        >>> @cached_function(ttl=3600)  # Cache for 1 hour
        ... def expensive_computation(data):
        ...     # Some expensive operation
        ...     return result
    """

    def decorator(func: Callable) -> Callable:
        """Decorator.

            Args:        func: Parameter for the operation.

            Returns:        The result of the operation.
            """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """Wrapper.

                Returns:        The result of the operation.
                """
            # Generate cache key
            prefix = cache_key_prefix or func.__name__
            key = _cache_manager._generate_key(prefix, args, kwargs)

            # Try to get from cache
            cached_result = _cache_manager.get(key)
            if cached_result is not None:
                return cached_result

            # Compute result
            result = func(*args, **kwargs)

            # Store in cache
            _cache_manager.set(key, result, ttl)

            return result

        # Add cache management methods to the wrapper
        wrapper.cache_clear = lambda: _cache_manager.clear()
        wrapper.cache_stats = lambda: _cache_manager.get_stats()

        return wrapper

    return decorator


def clear_cache() -> None:
    """Clear the global cache."""
    _cache_manager.clear()


def get_cache_stats() -> dict[str, Any]:
    """Get statistics for the global cache."""
    return _cache_manager.get_stats()
