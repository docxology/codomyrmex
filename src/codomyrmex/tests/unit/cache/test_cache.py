"""Unit tests for the Codomyrmex cache module.

Tests for InMemoryCache, CacheStats, TTL handling, and cache operations.
"""

import time
import pytest

from codomyrmex.cache.backends.in_memory import InMemoryCache
from codomyrmex.cache.stats import CacheStats


class TestCacheStats:
    """Tests for CacheStats class."""

    def test_cache_stats_initial(self):
        """Test initial cache stats."""
        stats = CacheStats(max_size=100)

        assert stats.size == 0
        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.max_size == 100

    def test_cache_stats_property(self):
        """Test the standardized .stats property."""
        cache = InMemoryCache(max_size=100)

        stats = cache.stats
        assert isinstance(stats, CacheStats)
        assert stats.size == 0
        assert stats.hits == 0
        assert stats.misses == 0

        # Perform operations
        cache.set("key1", "value1")
        cache.get("key1")
        cache.get("missing")

        updated_stats = cache.stats
        assert updated_stats.size == 1
        assert updated_stats.hits == 1
        assert updated_stats.misses == 1

    def test_cache_stats_total_requests(self):
        """Test total requests tracking."""
        cache = InMemoryCache()

        cache.get("a")
        cache.get("b")
        cache.get("c")

        assert cache.stats.total_requests == 3


class TestInMemoryCacheBasics:
    """Tests for basic InMemoryCache operations."""

    def test_create_cache(self):
        """Test creating a cache instance."""
        cache = InMemoryCache()

        assert cache is not None
        assert cache.max_size == 1000  # Default

    def test_create_cache_custom_size(self):
        """Test creating a cache with custom max size."""
        cache = InMemoryCache(max_size=50)

        assert cache.max_size == 50

    def test_set_and_get(self):
        """Test basic set and get operations."""
        cache = InMemoryCache()

        cache.set("key", "value")
        result = cache.get("key")

        assert result == "value"

    def test_get_missing_key(self):
        """Test getting a missing key returns None."""
        cache = InMemoryCache()

        result = cache.get("nonexistent")

        assert result is None

    def test_exists(self):
        """Test exists method."""
        cache = InMemoryCache()

        cache.set("key", "value")

        assert cache.exists("key") is True
        assert cache.exists("missing") is False

    def test_delete(self):
        """Test delete method."""
        cache = InMemoryCache()

        cache.set("key", "value")
        result = cache.delete("key")

        assert result is True
        assert cache.exists("key") is False

    def test_delete_missing_key(self):
        """Test deleting a missing key returns False."""
        cache = InMemoryCache()

        result = cache.delete("nonexistent")

        assert result is False

    def test_clear(self):
        """Test clearing the cache."""
        cache = InMemoryCache()

        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)

        result = cache.clear()

        assert result is True
        assert cache.stats.size == 0


class TestInMemoryCacheTypes:
    """Tests for caching different types."""

    def test_cache_string(self):
        """Test caching strings."""
        cache = InMemoryCache()

        cache.set("key", "string value")

        assert cache.get("key") == "string value"

    def test_cache_integer(self):
        """Test caching integers."""
        cache = InMemoryCache()

        cache.set("key", 42)

        assert cache.get("key") == 42

    def test_cache_float(self):
        """Test caching floats."""
        cache = InMemoryCache()

        cache.set("key", 3.14)

        assert cache.get("key") == 3.14

    def test_cache_list(self):
        """Test caching lists."""
        cache = InMemoryCache()

        cache.set("key", [1, 2, 3])

        assert cache.get("key") == [1, 2, 3]

    def test_cache_dict(self):
        """Test caching dictionaries."""
        cache = InMemoryCache()

        cache.set("key", {"a": 1, "b": 2})

        assert cache.get("key") == {"a": 1, "b": 2}

    def test_cache_none(self):
        """Test caching None value."""
        cache = InMemoryCache()

        cache.set("key", None)

        # get returns None for both missing and None values
        # but exists should return True
        assert cache.exists("key") is True


class TestInMemoryCacheTTL:
    """Tests for TTL (time-to-live) functionality."""

    def test_set_with_ttl(self):
        """Test setting value with TTL."""
        cache = InMemoryCache()

        cache.set("key", "value", ttl=10)

        assert cache.get("key") == "value"

    def test_ttl_expiration(self):
        """Test TTL expiration."""
        cache = InMemoryCache()

        cache.set("key", "value", ttl=1)

        # Value should exist immediately
        assert cache.get("key") == "value"

        # Wait for TTL to expire
        time.sleep(1.1)

        # Value should be gone
        assert cache.get("key") is None

    def test_default_ttl(self):
        """Test default TTL on cache creation."""
        cache = InMemoryCache(default_ttl=1)

        cache.set("key", "value")

        assert cache.get("key") == "value"

        time.sleep(1.1)

        assert cache.get("key") is None

    def test_ttl_overrides_default(self):
        """Test specific TTL overrides default."""
        cache = InMemoryCache(default_ttl=10)

        cache.set("key", "value", ttl=1)

        time.sleep(1.1)

        assert cache.get("key") is None

    def test_exists_respects_ttl(self):
        """Test exists method respects TTL."""
        cache = InMemoryCache()

        cache.set("key", "value", ttl=1)

        assert cache.exists("key") is True

        time.sleep(1.1)

        assert cache.exists("key") is False


class TestInMemoryCacheEviction:
    """Tests for cache eviction."""

    def test_eviction_at_max_size(self):
        """Test eviction when cache reaches max size."""
        cache = InMemoryCache(max_size=3)

        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)

        # Cache is at max, adding new item should evict oldest
        cache.set("d", 4)

        assert cache.stats.size == 3
        assert cache.exists("d") is True

    def test_update_existing_no_eviction(self):
        """Test updating existing key doesn't trigger eviction."""
        cache = InMemoryCache(max_size=2)

        cache.set("a", 1)
        cache.set("b", 2)

        # Update existing key
        cache.set("a", 10)

        assert cache.stats.size == 2
        assert cache.get("a") == 10
        assert cache.get("b") == 2


class TestInMemoryCachePatterns:
    """Tests for pattern-based operations."""

    def test_delete_pattern(self):
        """Test deleting by pattern."""
        cache = InMemoryCache()

        cache.set("user:1", "data1")
        cache.set("user:2", "data2")
        cache.set("session:1", "session_data")

        deleted = cache.delete_pattern("user:*")

        assert deleted == 2
        assert cache.exists("user:1") is False
        assert cache.exists("user:2") is False
        assert cache.exists("session:1") is True

    def test_delete_pattern_no_match(self):
        """Test delete pattern with no matches."""
        cache = InMemoryCache()

        cache.set("key1", "value1")

        deleted = cache.delete_pattern("nonexistent:*")

        assert deleted == 0


class TestCacheHitMissTracking:
    """Tests for hit/miss tracking."""

    def test_hit_tracking(self):
        """Test cache hit tracking."""
        cache = InMemoryCache()

        cache.set("key", "value")
        cache.get("key")
        cache.get("key")
        cache.get("key")

        assert cache.stats.hits == 3

    def test_miss_tracking(self):
        """Test cache miss tracking."""
        cache = InMemoryCache()

        cache.get("missing1")
        cache.get("missing2")

        assert cache.stats.misses == 2

    def test_mixed_hit_miss(self):
        """Test mixed hits and misses."""
        cache = InMemoryCache()

        cache.set("key", "value")

        cache.get("key")  # hit
        cache.get("missing")  # miss
        cache.get("key")  # hit
        cache.get("another_missing")  # miss

        assert cache.stats.hits == 2
        assert cache.stats.misses == 2
        assert cache.stats.total_requests == 4


class TestCacheBasicOps:
    """Legacy test for basic operations."""

    def test_cache_basic_ops(self):
        """Test basic cache operations."""
        cache = InMemoryCache()
        cache.set("a", 1)
        assert cache.get("a") == 1
        assert cache.exists("a") is True
        cache.delete("a")
        assert cache.exists("a") is False
        assert cache.get("a") is None
