"""
In-memory cache backend.
"""

import collections
import time
from typing import Any

from codomyrmex.cache.cache import Cache
from codomyrmex.cache.stats import CacheStats
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class InMemoryCache(Cache):
    """In-memory cache implementation."""

    def __init__(self, max_size: int = 1000, default_ttl: int | None = None):
        """Initialize in-memory cache.

        Args:
            max_size: Maximum number of items
            default_ttl: Default time-to-live in seconds
        """
        # Optimized dictionary eviction using OrderedDict for O(1) removals.
        self._cache: collections.OrderedDict[str, tuple[Any, float, int | None]] = (
            collections.OrderedDict()
        )
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._stats = CacheStats(max_size=max_size)

    def get(self, key: str) -> Any | None:
        """Get a value from the cache."""
        self._stats.total_requests += 1

        if key not in self._cache:
            self._stats.misses += 1
            return None

        value, timestamp, ttl = self._cache[key]

        # Check expiration
        if ttl is not None and time.time() - timestamp > ttl:
            del self._cache[key]
            self._stats.misses += 1
            return None

        # Move accessed item to the end (most recently used) to maintain O(1) LRU eviction
        self._cache.move_to_end(key)
        self._stats.hits += 1
        return value

    def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """set a value in the cache."""
        # Evict if at max size using O(1) popitem(last=False)
        if len(self._cache) >= self.max_size and key not in self._cache:
            # Remove oldest entry (first item)
            self._cache.popitem(last=False)
            self._stats.size -= 1

        ttl = ttl or self.default_ttl
        self._cache[key] = (value, time.time(), ttl)
        self._cache.move_to_end(key)
        self._stats.size = len(self._cache)
        return True

    def delete(self, key: str) -> bool:
        """Delete a key from the cache."""
        if key in self._cache:
            del self._cache[key]
            self._stats.size = len(self._cache)
            return True
        return False

    def clear(self) -> bool:
        """Clear all entries from the cache."""
        self._cache.clear()
        self._stats.size = 0
        return True

    def exists(self, key: str) -> bool:
        """Check if a key exists in the cache."""
        if key not in self._cache:
            return False

        # Check expiration
        _, timestamp, ttl = self._cache[key]
        if ttl is not None and time.time() - timestamp > ttl:
            del self._cache[key]
            return False

        # Move accessed item to the end (most recently used) to maintain O(1) LRU eviction
        self._cache.move_to_end(key)

        return True

    @property
    def stats(self) -> CacheStats:
        """Get cache statistics."""
        self._stats.size = len(self._cache)
        return self._stats

    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern."""
        import fnmatch

        keys_to_delete = [k for k in self._cache if fnmatch.fnmatch(k, pattern)]
        for key in keys_to_delete:
            self.delete(key)
        return len(keys_to_delete)
