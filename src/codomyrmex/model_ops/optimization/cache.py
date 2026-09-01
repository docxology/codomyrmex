"""
Inference Cache

LRU cache for inference results.
"""

import threading
from collections import OrderedDict
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
        self.max_size = max_size
        # ⚡ Bolt: Optimized LRU cache using OrderedDict for O(1) get/put operations.
        # Previously used a list for access order which caused O(N) removals.
        self._cache: OrderedDict[str, Any] = OrderedDict()
        self._lock = threading.Lock()

    def get(self, key: str) -> Any | None:
        """Get cached result."""
        with self._lock:
            if key in self._cache:
                # Move to end (most recently used)
                self._cache.move_to_end(key)
                return self._cache[key]
        return None

    def put(self, key: str, value: Any) -> None:
        """Cache a result."""
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
            elif len(self._cache) >= self.max_size:
                # Evict LRU
                self._cache.popitem(last=False)

            self._cache[key] = value

    def contains(self, key: str) -> bool:
        """Check if key is cached."""
        return key in self._cache

    def clear(self) -> None:
        """Clear the cache."""
        with self._lock:
            self._cache.clear()

    @property
    def size(self) -> int:
        """Get current cache size."""
        return len(self._cache)
