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
        # ⚡ Bolt: Use OrderedDict to allow O(1) eviction of the oldest element.
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
        # ⚡ Bolt: time.monotonic() is generally faster than time.time() for duration tracking.
        if ttl is not None and time.monotonic() - timestamp > ttl:
            del self._cache[key]
            self._stats.misses += 1
            return None

        self._stats.hits += 1
        return value

    def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """set a value in the cache."""

        # ⚡ Bolt: Replace O(n) eviction min() lookup with O(1) popitem(last=False).
        # Expected performance impact: Reduces eviction time from O(n) to O(1).
        if key in self._cache:
            # Need to remove first to re-insert at end for order consistency
            del self._cache[key]
            self._stats.size -= 1

        elif len(self._cache) >= self.max_size:
            # Remove oldest entry
            self._cache.popitem(last=False)
            self._stats.size -= 1

        ttl = ttl or self.default_ttl
        self._cache[key] = (value, time.monotonic(), ttl)
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
        if ttl is not None and time.monotonic() - timestamp > ttl:
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

        keys_to_delete = [k for k in self._cache if fnmatch.fnmatch(k, pattern)]
        for key in keys_to_delete:
            self.delete(key)
        return len(keys_to_delete)
