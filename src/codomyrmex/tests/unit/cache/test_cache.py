"""Unit tests for cache module."""

import pytest
from codomyrmex.cache.backends.in_memory import InMemoryCache
from codomyrmex.cache.stats import CacheStats

def test_cache_stats_property():
    """Test the standardized .stats property."""
    cache = InMemoryCache(max_size=100)
    
    # Verify initial stats via standardized property
    stats = cache.stats
    assert isinstance(stats, CacheStats)
    assert stats.size == 0
    assert stats.hits == 0
    assert stats.misses == 0
    
    # Perform some operations
    cache.set("key1", "value1")
    cache.get("key1")
    cache.get("missing")
    
    # Verify updated stats
    updated_stats = cache.stats
    assert updated_stats.size == 1
    assert updated_stats.hits == 1
    assert updated_stats.misses == 1

def test_cache_basic_ops():
    """Test basic cache operations."""
    cache = InMemoryCache()
    cache.set("a", 1)
    assert cache.get("a") == 1
    assert cache.exists("a") is True
    cache.delete("a")
    assert cache.exists("a") is False
    assert cache.get("a") is None
