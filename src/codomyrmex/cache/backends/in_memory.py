"""
In-memory cache backend.
"""

import time
from typing import Any, Optional

from codomyrmex.logging_monitoring.logger_config import get_logger

from ..cache import Cache
from ..stats import CacheStats

logger = get_logger(__name__)


class InMemoryCache(Cache):
    """In-memory cache implementation."""

    def __init__(self, max_size: int = 1000, default_ttl: Optional[int] = None):
        """Initialize in-memory cache.

        Args:
            max_size: Maximum number of items
            default_ttl: Default time-to-live in seconds
        """
        self._cache: dict[str, tuple[Any, float, Optional[int]]] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._stats = CacheStats(max_size=max_size)

    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache."""
        self._stats.total_requests += 1

        if key not in self._cache:
            self._stats.misses += 1
            return None

        value, timestamp, ttl = self._cache[key]

        # Check expiration
        if ttl is not None:
            if time.time() - timestamp > ttl:
                del self._cache[key]
                self._stats.misses += 1
                return None

        self._stats.hits += 1
        return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in the cache."""
        # Evict if at max size
        if len(self._cache) >= self.max_size and key not in self._cache:
            # Remove oldest entry
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][1])
            del self._cache[oldest_key]
            self._stats.size -= 1

        ttl = ttl or self.default_ttl
        self._cache[key] = (value, time.time(), ttl)
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
        if ttl is not None:
            if time.time() - timestamp > ttl:
                del self._cache[key]
                return False

        return True

    @property
    def stats(self) -> CacheStats:
        """Get cache statistics."""
        self._stats.size = len(self._cache)
        return self._stats

    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern."""
        import fnmatch
        keys_to_delete = [k for k in self._cache.keys() if fnmatch.fnmatch(k, pattern)]
        for key in keys_to_delete:
            self.delete(key)
        return len(keys_to_delete)


