"""Namespaced cache wrapper."""

from typing import Any

from .cache import Cache
from .stats import CacheStats


class NamespacedCache(Cache):
    """Wraps a cache with a namespace prefix."""

    def __init__(self, cache: Cache, namespace: str):
        self.cache = cache
        self.namespace = namespace

    def _full_key(self, key: str) -> str:
        return f"{self.namespace}:{key}"

    def get(self, key: str) -> Any | None:
        """Return the requested value."""
        return self.cache.get(self._full_key(key))

    def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """Set the value."""
        return self.cache.set(self._full_key(key), value, ttl)

    def delete(self, key: str) -> bool:
        """Delete the specified resource."""
        return self.cache.delete(self._full_key(key))

    def clear(self) -> bool:
        """clear ."""
        return self.cache.delete_pattern(f"{self.namespace}:*") > 0

    def exists(self, key: str) -> bool:
        """exists ."""
        return self.cache.exists(self._full_key(key))

    @property
    def stats(self) -> CacheStats:
        """stats ."""
        return self.cache.stats


    def delete_pattern(self, pattern: str) -> int:
        return self.cache.delete_pattern(f"{self.namespace}:{pattern}")
