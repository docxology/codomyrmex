"""
Inference Cache

LRU cache for inference results.
"""

import threading
from typing import Any


class InferenceCache:
    """
    Cache for inference results.

    Usage:
        cache = InferenceCache(max_size=1000)

        cache.put("key1", result1)
        result = cache.get("key1")
    """

    def __init__(self, max_size: int = 1000):
        """Initialize this instance."""
        self.max_size = max_size
        self._cache: dict[str, Any] = {}
        self._access_order: list[str] = []
        self._lock = threading.Lock()

    def get(self, key: str) -> Any | None:
        """Get cached result."""
        with self._lock:
            if key in self._cache:
                # Move to end (most recently used)
                self._access_order.remove(key)
                self._access_order.append(key)
                return self._cache[key]
        return None

    def put(self, key: str, value: Any) -> None:
        """Cache a result."""
        with self._lock:
            if key in self._cache:
                self._access_order.remove(key)
            elif len(self._cache) >= self.max_size:
                # Evict LRU
                lru_key = self._access_order.pop(0)
                del self._cache[lru_key]

            self._cache[key] = value
            self._access_order.append(key)

    def contains(self, key: str) -> bool:
        """Check if key is cached."""
        return key in self._cache

    def clear(self) -> None:
        """Clear the cache."""
        with self._lock:
            self._cache.clear()
            self._access_order.clear()

    @property
    def size(self) -> int:
        """Get current cache size."""
        return len(self._cache)
