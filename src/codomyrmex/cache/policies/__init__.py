"""
Cache eviction policies.

Provides different strategies for cache eviction when capacity is reached.
"""

import heapq
import threading
from abc import ABC, abstractmethod
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, Generic, List, Optional, TypeVar

K = TypeVar('K')
V = TypeVar('V')


@dataclass
class CacheEntry(Generic[V]):
    """A single cache entry with metadata."""
    value: V
    created_at: datetime = field(default_factory=datetime.now)
    accessed_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    ttl: timedelta | None = None
    size: int = 1

    def is_expired(self) -> bool:
        """Check if the entry has expired."""
        if self.ttl is None:
            return False
        return datetime.now() > self.created_at + self.ttl

    def touch(self) -> None:
        """Update access metadata."""
        self.accessed_at = datetime.now()
        self.access_count += 1


class EvictionPolicy(ABC, Generic[K, V]):
    """Abstract base class for eviction policies."""

    def __init__(self, max_size: int):
        """Execute   Init   operations natively."""
        self.max_size = max_size
        self._lock = threading.RLock()

    @abstractmethod
    def get(self, key: K) -> V | None:
        """Get a value from the cache."""
        pass

    @abstractmethod
    def put(self, key: K, value: V, ttl: timedelta | None = None) -> None:
        """Put a value in the cache."""
        pass

    @abstractmethod
    def remove(self, key: K) -> V | None:
        """Remove a value from the cache."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear the cache."""
        pass

    @abstractmethod
    def size(self) -> int:
        """Get current cache size."""
        pass

    def contains(self, key: K) -> bool:
        """Check if key exists in cache."""
        return self.get(key) is not None


class LRUPolicy(EvictionPolicy[K, V]):
    """Least Recently Used eviction policy."""

    def __init__(self, max_size: int):
        """Execute   Init   operations natively."""
        super().__init__(max_size)
        self._cache: OrderedDict[K, CacheEntry[V]] = OrderedDict()

    def get(self, key: K) -> V | None:
        """Execute Get operations natively."""
        with self._lock:
            if key not in self._cache:
                return None

            entry = self._cache[key]
            if entry.is_expired():
                del self._cache[key]
                return None

            # Move to end (most recently used)
            self._cache.move_to_end(key)
            entry.touch()
            return entry.value

    def put(self, key: K, value: V, ttl: timedelta | None = None) -> None:
        """Execute Put operations natively."""
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
                self._cache[key] = CacheEntry(value=value, ttl=ttl)
            else:
                if len(self._cache) >= self.max_size:
                    # Remove least recently used (first item)
                    self._cache.popitem(last=False)
                self._cache[key] = CacheEntry(value=value, ttl=ttl)

    def remove(self, key: K) -> V | None:
        """Execute Remove operations natively."""
        with self._lock:
            if key in self._cache:
                entry = self._cache.pop(key)
                return entry.value
            return None

    def clear(self) -> None:
        """Execute Clear operations natively."""
        with self._lock:
            self._cache.clear()

    def size(self) -> int:
        """Execute Size operations natively."""
        return len(self._cache)


class LFUPolicy(EvictionPolicy[K, V]):
    """Least Frequently Used eviction policy."""

    def __init__(self, max_size: int):
        """Execute   Init   operations natively."""
        super().__init__(max_size)
        self._cache: dict[K, CacheEntry[V]] = {}
        self._freq_map: dict[int, OrderedDict[K, None]] = {}
        self._min_freq: int = 0

    def _update_frequency(self, key: K) -> None:
        """Update the frequency of a key."""
        entry = self._cache[key]
        old_freq = entry.access_count
        entry.touch()
        new_freq = entry.access_count

        # Remove from old frequency list
        if old_freq in self._freq_map:
            del self._freq_map[old_freq][key]
            if not self._freq_map[old_freq]:
                del self._freq_map[old_freq]
                if self._min_freq == old_freq:
                    self._min_freq = new_freq

        # Add to new frequency list
        if new_freq not in self._freq_map:
            self._freq_map[new_freq] = OrderedDict()
        self._freq_map[new_freq][key] = None

    def get(self, key: K) -> V | None:
        """Execute Get operations natively."""
        with self._lock:
            if key not in self._cache:
                return None

            entry = self._cache[key]
            if entry.is_expired():
                self.remove(key)
                return None

            self._update_frequency(key)
            return entry.value

    def put(self, key: K, value: V, ttl: timedelta | None = None) -> None:
        """Execute Put operations natively."""
        with self._lock:
            if self.max_size <= 0:
                return

            if key in self._cache:
                self._cache[key].value = value
                self._cache[key].ttl = ttl
                self._update_frequency(key)
            else:
                if len(self._cache) >= self.max_size:
                    # Evict least frequently used
                    if self._min_freq in self._freq_map:
                        evict_key = next(iter(self._freq_map[self._min_freq]))
                        self.remove(evict_key)

                self._cache[key] = CacheEntry(value=value, ttl=ttl)
                self._min_freq = 1

                if 1 not in self._freq_map:
                    self._freq_map[1] = OrderedDict()
                self._freq_map[1][key] = None

    def remove(self, key: K) -> V | None:
        """Execute Remove operations natively."""
        with self._lock:
            if key not in self._cache:
                return None

            entry = self._cache.pop(key)
            freq = entry.access_count or 1

            if freq in self._freq_map and key in self._freq_map[freq]:
                del self._freq_map[freq][key]
                if not self._freq_map[freq]:
                    del self._freq_map[freq]

            return entry.value

    def clear(self) -> None:
        """Execute Clear operations natively."""
        with self._lock:
            self._cache.clear()
            self._freq_map.clear()
            self._min_freq = 0

    def size(self) -> int:
        """Execute Size operations natively."""
        return len(self._cache)


class TTLPolicy(EvictionPolicy[K, V]):
    """TTL-based eviction policy with lazy expiration."""

    def __init__(self, max_size: int, default_ttl: timedelta = timedelta(hours=1)):
        """Execute   Init   operations natively."""
        super().__init__(max_size)
        self._cache: dict[K, CacheEntry[V]] = {}
        self._default_ttl = default_ttl
        self._expiry_heap: list[tuple[datetime, K]] = []

    def _cleanup_expired(self) -> None:
        """Remove expired entries."""
        now = datetime.now()
        while self._expiry_heap and self._expiry_heap[0][0] <= now:
            _, key = heapq.heappop(self._expiry_heap)
            if key in self._cache and self._cache[key].is_expired():
                del self._cache[key]

    def get(self, key: K) -> V | None:
        """Execute Get operations natively."""
        with self._lock:
            self._cleanup_expired()

            if key not in self._cache:
                return None

            entry = self._cache[key]
            if entry.is_expired():
                del self._cache[key]
                return None

            entry.touch()
            return entry.value

    def put(self, key: K, value: V, ttl: timedelta | None = None) -> None:
        """Execute Put operations natively."""
        with self._lock:
            self._cleanup_expired()

            actual_ttl = ttl or self._default_ttl
            entry = CacheEntry(value=value, ttl=actual_ttl)

            if len(self._cache) >= self.max_size and key not in self._cache:
                # Evict oldest entry
                if self._cache:
                    oldest_key = min(self._cache.keys(),
                                    key=lambda k: self._cache[k].created_at)
                    del self._cache[oldest_key]

            self._cache[key] = entry
            expiry_time = entry.created_at + actual_ttl
            heapq.heappush(self._expiry_heap, (expiry_time, key))

    def remove(self, key: K) -> V | None:
        """Execute Remove operations natively."""
        with self._lock:
            if key in self._cache:
                entry = self._cache.pop(key)
                return entry.value
            return None

    def clear(self) -> None:
        """Execute Clear operations natively."""
        with self._lock:
            self._cache.clear()
            self._expiry_heap.clear()

    def size(self) -> int:
        """Execute Size operations natively."""
        self._cleanup_expired()
        return len(self._cache)


class FIFOPolicy(EvictionPolicy[K, V]):
    """First In First Out eviction policy."""

    def __init__(self, max_size: int):
        """Execute   Init   operations natively."""
        super().__init__(max_size)
        self._cache: OrderedDict[K, CacheEntry[V]] = OrderedDict()

    def get(self, key: K) -> V | None:
        """Execute Get operations natively."""
        with self._lock:
            if key not in self._cache:
                return None

            entry = self._cache[key]
            if entry.is_expired():
                del self._cache[key]
                return None

            entry.touch()
            return entry.value

    def put(self, key: K, value: V, ttl: timedelta | None = None) -> None:
        """Execute Put operations natively."""
        with self._lock:
            if key in self._cache:
                self._cache[key] = CacheEntry(value=value, ttl=ttl)
            else:
                if len(self._cache) >= self.max_size:
                    self._cache.popitem(last=False)
                self._cache[key] = CacheEntry(value=value, ttl=ttl)

    def remove(self, key: K) -> V | None:
        """Execute Remove operations natively."""
        with self._lock:
            if key in self._cache:
                entry = self._cache.pop(key)
                return entry.value
            return None

    def clear(self) -> None:
        """Execute Clear operations natively."""
        with self._lock:
            self._cache.clear()

    def size(self) -> int:
        """Execute Size operations natively."""
        return len(self._cache)


def create_policy(policy_name: str, max_size: int, **kwargs) -> EvictionPolicy:
    """Factory function to create eviction policies."""
    policies = {
        "lru": LRUPolicy,
        "lfu": LFUPolicy,
        "ttl": TTLPolicy,
        "fifo": FIFOPolicy,
    }

    policy_class = policies.get(policy_name.lower())
    if not policy_class:
        raise ValueError(f"Unknown policy: {policy_name}")

    return policy_class(max_size, **kwargs)


__all__ = [
    "CacheEntry",
    "EvictionPolicy",
    "LRUPolicy",
    "LFUPolicy",
    "TTLPolicy",
    "FIFOPolicy",
    "create_policy",
]
