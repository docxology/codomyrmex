"""Edge caching layer.

Provides local caching for edge nodes to reduce latency and
cloud round-trips.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CacheEntry:
    """A single cached value."""

    key: str
    value: Any
    created_at: float = field(default_factory=time.time)
    ttl_seconds: float = 300.0
    access_count: int = 0

    @property
    def expired(self) -> bool:
        """Execute Expired operations natively."""
        return (time.time() - self.created_at) > self.ttl_seconds


class EdgeCache:
    """Local cache for an edge node.

    Thread-safe LRU-style cache with TTL expiration.
    """

    def __init__(self, max_size: int = 1000, default_ttl: float = 300.0):
        """Execute   Init   operations natively."""
        self._store: dict[str, CacheEntry] = {}
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Any | None:
        """Get a value, returning None on miss or expiry."""
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                self._misses += 1
                return None
            if entry.expired:
                del self._store[key]
                self._misses += 1
                return None
            entry.access_count += 1
            self._hits += 1
            return entry.value

    def put(self, key: str, value: Any, ttl: float | None = None) -> None:
        """Store a value with optional TTL override."""
        with self._lock:
            if len(self._store) >= self._max_size and key not in self._store:
                self._evict_one()
            self._store[key] = CacheEntry(
                key=key,
                value=value,
                ttl_seconds=ttl if ttl is not None else self._default_ttl,
            )

    def delete(self, key: str) -> bool:
        """Remove a key."""
        with self._lock:
            if key in self._store:
                del self._store[key]
                return True
            return False

    def clear(self) -> int:
        """Clear all entries, return count removed."""
        with self._lock:
            count = len(self._store)
            self._store.clear()
            return count

    def purge_expired(self) -> int:
        """Remove all expired entries."""
        with self._lock:
            expired_keys = [k for k, v in self._store.items() if v.expired]
            for k in expired_keys:
                del self._store[k]
            return len(expired_keys)

    @property
    def size(self) -> int:
        """Execute Size operations natively."""
        return len(self._store)

    @property
    def hit_rate(self) -> float:
        """Hit rate as percentage (0-100)."""
        total = self._hits + self._misses
        if total == 0:
            return 0.0
        return (self._hits / total) * 100.0

    def stats(self) -> dict[str, Any]:
        """Cache statistics."""
        return {
            "size": self.size,
            "max_size": self._max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": self.hit_rate,
            "default_ttl": self._default_ttl,
        }

    def _evict_one(self) -> None:
        """Evict the least-accessed entry."""
        if not self._store:
            return
        # Evict expired first
        for k, v in self._store.items():
            if v.expired:
                del self._store[k]
                return
        # Otherwise evict least-accessed
        victim = min(self._store.values(), key=lambda e: e.access_count)
        del self._store[victim.key]
