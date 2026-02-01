"""
Cache Invalidation Module

Cache invalidation strategies and policies.
"""

__version__ = "0.1.0"

import threading
import time
import hashlib
from typing import Optional, List, Dict, Any, Set, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from abc import ABC, abstractmethod


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
    ttl_seconds: Optional[float] = None
    tags: Set[str] = field(default_factory=set)
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
    def select_for_eviction(self, entries: Dict[str, CacheEntry]) -> Optional[str]:
        """Select an entry for eviction."""
        pass


class TTLPolicy(InvalidationPolicy):
    """Time-to-live based invalidation."""
    
    def __init__(self, default_ttl: float = 300.0):
        self.default_ttl = default_ttl
    
    def should_evict(self, entry: CacheEntry) -> bool:
        return entry.is_expired
    
    def select_for_eviction(self, entries: Dict[str, CacheEntry]) -> Optional[str]:
        for key, entry in entries.items():
            if entry.is_expired:
                return key
        return None


class LRUPolicy(InvalidationPolicy):
    """Least recently used invalidation."""
    
    def should_evict(self, entry: CacheEntry) -> bool:
        return False  # LRU doesn't auto-evict
    
    def select_for_eviction(self, entries: Dict[str, CacheEntry]) -> Optional[str]:
        if not entries:
            return None
        oldest = min(entries.items(), key=lambda x: x[1].last_accessed)
        return oldest[0]


class LFUPolicy(InvalidationPolicy):
    """Least frequently used invalidation."""
    
    def should_evict(self, entry: CacheEntry) -> bool:
        return False
    
    def select_for_eviction(self, entries: Dict[str, CacheEntry]) -> Optional[str]:
        if not entries:
            return None
        least_used = min(entries.items(), key=lambda x: x[1].access_count)
        return least_used[0]


class FIFOPolicy(InvalidationPolicy):
    """First in, first out invalidation."""
    
    def should_evict(self, entry: CacheEntry) -> bool:
        return False
    
    def select_for_eviction(self, entries: Dict[str, CacheEntry]) -> Optional[str]:
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
        policy: Optional[InvalidationPolicy] = None,
        max_size: int = 1000,
    ):
        self.policy = policy or TTLPolicy()
        self.max_size = max_size
        self._entries: Dict[str, CacheEntry] = {}
        self._tags: Dict[str, Set[str]] = {}  # tag -> keys
        self._versions: Dict[str, int] = {}  # namespace -> version
        self._lock = threading.Lock()
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[float] = None,
        tags: Optional[Set[str]] = None,
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
    
    def get(self, key: str) -> Optional[Any]:
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
    
    def stats(self) -> Dict[str, Any]:
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
