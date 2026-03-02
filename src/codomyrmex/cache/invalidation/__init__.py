"""
Cache Invalidation Module

Cache invalidation strategies and policies.
"""

__version__ = "0.1.0"

import hashlib
import threading
import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional


class InvalidationStrategy(Enum):
    """Cache invalidation strategies."""
    TTL = "ttl"
    LRU = "lru"
    LFU = "lfu"
    FIFO = "fifo"
    TAG_BASED = "tag_based"
    VERSION_BASED = "version_based"

@dataclass
class CacheEntry:
    """A cache entry with metadata."""
    key: str
    value: Any
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    ttl_seconds: float | None = None
    tags: set[str] = field(default_factory=set)
    version: int = 1

    @property
    def is_expired(self) -> bool:
        """Check if entry is expired."""
        if self.ttl_seconds is None:
            return False
        age = (datetime.now() - self.created_at).total_seconds()
        return age > self.ttl_seconds

    def touch(self) -> None:
        """Update access time and count."""
        self.last_accessed = datetime.now()
        self.access_count += 1

class InvalidationPolicy(ABC):
    """Base class for invalidation policies."""

    @abstractmethod
    def should_evict(self, entry: CacheEntry) -> bool:
        """Check if entry should be evicted."""
        pass

    @abstractmethod
    def select_for_eviction(self, entries: dict[str, CacheEntry]) -> str | None:
        """Select an entry for eviction."""
        pass

class TTLPolicy(InvalidationPolicy):
    """Time-to-live based invalidation."""

    def __init__(self, default_ttl: float = 300.0):
        """Initialize TTL policy with a default time-to-live in seconds."""
        self.default_ttl = default_ttl

    def should_evict(self, entry: CacheEntry) -> bool:
        """Return True if the entry has exceeded its TTL and should be evicted."""
        return entry.is_expired

    def select_for_eviction(self, entries: dict[str, CacheEntry]) -> str | None:
        """Return the key of the first expired entry, or None if all are fresh."""
        for key, entry in entries.items():
            if entry.is_expired:
                return key
        return None

class LRUPolicy(InvalidationPolicy):
    """Least recently used invalidation."""

    def should_evict(self, entry: CacheEntry) -> bool:
        """Return False; LRU eviction is triggered by capacity, not per-entry expiry."""
        return False  # LRU doesn't auto-evict

    def select_for_eviction(self, entries: dict[str, CacheEntry]) -> str | None:
        """Return the key of the least recently accessed entry."""
        if not entries:
            return None
        oldest = min(entries.items(), key=lambda x: x[1].last_accessed)
        return oldest[0]

class LFUPolicy(InvalidationPolicy):
    """Least frequently used invalidation."""

    def should_evict(self, entry: CacheEntry) -> bool:
        """Return False; LFU eviction is triggered by capacity, not per-entry expiry."""
        return False

    def select_for_eviction(self, entries: dict[str, CacheEntry]) -> str | None:
        """Return the key of the entry with the lowest access count."""
        if not entries:
            return None
        least_used = min(entries.items(), key=lambda x: x[1].access_count)
        return least_used[0]

class FIFOPolicy(InvalidationPolicy):
    """First in, first out invalidation."""

    def should_evict(self, entry: CacheEntry) -> bool:
        """Return False; FIFO eviction is triggered by capacity, not per-entry expiry."""
        return False

    def select_for_eviction(self, entries: dict[str, CacheEntry]) -> str | None:
        """Return the key of the oldest entry by creation time."""
        if not entries:
            return None
        oldest = min(entries.items(), key=lambda x: x[1].created_at)
        return oldest[0]

class InvalidationManager:
    """
    Manages cache invalidation.

    Usage:
        manager = InvalidationManager(policy=LRUPolicy())

        # Store entries
        manager.set("key1", "value1", tags={"user", "data"})
        manager.set("key2", "value2", ttl=60)

        # Access
        value = manager.get("key1")

        # Invalidate
        manager.invalidate_by_tag("user")
    """

    def __init__(
        self,
        policy: InvalidationPolicy | None = None,
        max_size: int = 1000,
    ):
        """Initialize the manager with an invalidation policy and maximum cache size."""
        self.policy = policy or TTLPolicy()
        self.max_size = max_size
        self._entries: dict[str, CacheEntry] = {}
        self._tags: dict[str, set[str]] = {}  # tag -> keys
        self._versions: dict[str, int] = {}  # namespace -> version
        self._lock = threading.Lock()

    def set(
        self,
        key: str,
        value: Any,
        ttl: float | None = None,
        tags: set[str] | None = None,
    ) -> None:
        """Set a cache entry."""
        with self._lock:
            # Evict if at capacity
            while len(self._entries) >= self.max_size:
                to_evict = self.policy.select_for_eviction(self._entries)
                if to_evict:
                    self._remove_entry(to_evict)
                else:
                    break

            entry = CacheEntry(
                key=key,
                value=value,
                ttl_seconds=ttl,
                tags=tags or set(),
            )

            self._entries[key] = entry

            # Update tag index
            for tag in entry.tags:
                if tag not in self._tags:
                    self._tags[tag] = set()
                self._tags[tag].add(key)

    def get(self, key: str) -> Any | None:
        """Get a cache entry."""
        entry = self._entries.get(key)

        if entry is None:
            return None

        if self.policy.should_evict(entry):
            self._remove_entry(key)
            return None

        entry.touch()
        return entry.value

    def _remove_entry(self, key: str) -> None:
        """Remove an entry."""
        entry = self._entries.pop(key, None)
        if entry:
            for tag in entry.tags:
                if tag in self._tags:
                    self._tags[tag].discard(key)

    def invalidate(self, key: str) -> bool:
        """Invalidate a specific key."""
        with self._lock:
            if key in self._entries:
                self._remove_entry(key)
                return True
        return False

    def invalidate_by_tag(self, tag: str) -> int:
        """Invalidate all entries with a tag."""
        with self._lock:
            keys = self._tags.get(tag, set()).copy()
            for key in keys:
                self._remove_entry(key)
            return len(keys)

    def invalidate_all(self) -> int:
        """Invalidate all entries."""
        with self._lock:
            count = len(self._entries)
            self._entries.clear()
            self._tags.clear()
            return count

    def set_version(self, namespace: str, version: int) -> None:
        """Set namespace version for version-based invalidation."""
        self._versions[namespace] = version

    def get_version(self, namespace: str) -> int:
        """Get namespace version."""
        return self._versions.get(namespace, 1)

    def increment_version(self, namespace: str) -> int:
        """Increment namespace version (invalidates cached data)."""
        current = self._versions.get(namespace, 1)
        self._versions[namespace] = current + 1
        return self._versions[namespace]

    @property
    def size(self) -> int:
        """Get current cache size."""
        return len(self._entries)

    def stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return {
            "size": self.size,
            "max_size": self.max_size,
            "tags": len(self._tags),
            "namespaces": len(self._versions),
        }

__all__ = [
    # Enums
    "InvalidationStrategy",
    # Data classes
    "CacheEntry",
    # Policies
    "InvalidationPolicy",
    "TTLPolicy",
    "LRUPolicy",
    "LFUPolicy",
    "FIFOPolicy",
    # Core
    "InvalidationManager",
]
