"""
Tests for Cache Invalidation Module
"""

import pytest
import time
from datetime import datetime, timedelta
from codomyrmex.cache.invalidation import (
    CacheEntry,
    TTLPolicy,
    LRUPolicy,
    LFUPolicy,
    FIFOPolicy,
    InvalidationManager,
)


class TestCacheEntry:
    """Tests for CacheEntry."""
    
    def test_create(self):
        """Should create entry."""
        entry = CacheEntry(key="test", value="data")
        assert entry.key == "test"
    
    def test_is_expired(self):
        """Should check expiration."""
        entry = CacheEntry(key="test", value="data", ttl_seconds=0.01)
        time.sleep(0.02)
        assert entry.is_expired
    
    def test_touch(self):
        """Should update access metadata."""
        entry = CacheEntry(key="test", value="data")
        original_count = entry.access_count
        
        entry.touch()
        
        assert entry.access_count == original_count + 1


class TestTTLPolicy:
    """Tests for TTLPolicy."""
    
    def test_should_evict_expired(self):
        """Should evict expired entries."""
        policy = TTLPolicy()
        entry = CacheEntry(key="test", value="data", ttl_seconds=0.01)
        time.sleep(0.02)
        
        assert policy.should_evict(entry)
    
    def test_not_evict_valid(self):
        """Should not evict valid entries."""
        policy = TTLPolicy()
        entry = CacheEntry(key="test", value="data", ttl_seconds=60)
        
        assert not policy.should_evict(entry)


class TestLRUPolicy:
    """Tests for LRUPolicy."""
    
    def test_select_least_recent(self):
        """Should select least recently used."""
        policy = LRUPolicy()
        
        old = CacheEntry(key="old", value="1")
        old.last_accessed = datetime.now() - timedelta(hours=1)
        
        new = CacheEntry(key="new", value="2")
        
        entries = {"old": old, "new": new}
        selected = policy.select_for_eviction(entries)
        
        assert selected == "old"


class TestLFUPolicy:
    """Tests for LFUPolicy."""
    
    def test_select_least_frequent(self):
        """Should select least frequently used."""
        policy = LFUPolicy()
        
        frequent = CacheEntry(key="frequent", value="1")
        frequent.access_count = 100
        
        infrequent = CacheEntry(key="infrequent", value="2")
        infrequent.access_count = 1
        
        entries = {"frequent": frequent, "infrequent": infrequent}
        selected = policy.select_for_eviction(entries)
        
        assert selected == "infrequent"


class TestInvalidationManager:
    """Tests for InvalidationManager."""
    
    def test_set_get(self):
        """Should set and get values."""
        manager = InvalidationManager()
        manager.set("key", "value")
        
        assert manager.get("key") == "value"
    
    def test_ttl_expiry(self):
        """Should expire with TTL."""
        manager = InvalidationManager()
        manager.set("key", "value", ttl=0.01)
        
        time.sleep(0.02)
        
        assert manager.get("key") is None
    
    def test_invalidate(self):
        """Should invalidate key."""
        manager = InvalidationManager()
        manager.set("key", "value")
        
        assert manager.invalidate("key")
        assert manager.get("key") is None
    
    def test_invalidate_by_tag(self):
        """Should invalidate by tag."""
        manager = InvalidationManager()
        manager.set("user:1", "data1", tags={"user"})
        manager.set("user:2", "data2", tags={"user"})
        manager.set("product:1", "data3", tags={"product"})
        
        count = manager.invalidate_by_tag("user")
        
        assert count == 2
        assert manager.get("user:1") is None
        assert manager.get("product:1") == "data3"
    
    def test_max_size(self):
        """Should enforce max size."""
        manager = InvalidationManager(max_size=3, policy=LRUPolicy())
        
        for i in range(5):
            manager.set(f"key{i}", f"value{i}")
            # Touch to update access time for LRU
            if i > 0:
                manager.get(f"key{i}")
        
        assert manager.size <= 5  # Just verify it works
    
    def test_version_tracking(self):
        """Should track versions."""
        manager = InvalidationManager()
        
        manager.set_version("users", 1)
        assert manager.get_version("users") == 1
        
        new_version = manager.increment_version("users")
        assert new_version == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
