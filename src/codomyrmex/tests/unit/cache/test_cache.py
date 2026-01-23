"""Unit tests for the Codomyrmex cache module.

Comprehensive tests for InMemoryCache, FileBasedCache, NamespacedCache,
CacheStats, CacheManager, TTLManager, TTL handling, eviction, and cache operations.
"""

import time
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from codomyrmex.cache.backends.in_memory import InMemoryCache
from codomyrmex.cache.stats import CacheStats


class TestCacheModuleImport:
    """Tests for cache module import."""

    def test_cache_module_import(self):
        """Test that cache module can be imported."""
        from codomyrmex import cache
        assert cache is not None

    def test_cache_module_exports(self):
        """Test cache module exports key components."""
        from codomyrmex import cache
        assert hasattr(cache, "Cache")
        assert hasattr(cache, "CacheManager")
        assert hasattr(cache, "CacheStats")
        assert hasattr(cache, "NamespacedCache")
        assert hasattr(cache, "TTLManager")
        assert hasattr(cache, "get_cache")


class TestCacheStats:
    """Tests for CacheStats class."""

    def test_cache_stats_initial(self):
        """Test initial cache stats."""
        stats = CacheStats(max_size=100)

        assert stats.size == 0
        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.max_size == 100

    def test_cache_stats_defaults(self):
        """Test CacheStats default values."""
        stats = CacheStats()

        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.total_requests == 0
        assert stats.size == 0
        assert stats.max_size == 0

    def test_cache_stats_initialization(self):
        """Test CacheStats with initial values."""
        stats = CacheStats(hits=10, misses=5, total_requests=15, size=100, max_size=1000)

        assert stats.hits == 10
        assert stats.misses == 5
        assert stats.total_requests == 15
        assert stats.size == 100
        assert stats.max_size == 1000

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

    def test_hit_rate_zero_requests(self):
        """Test hit rate with zero requests."""
        stats = CacheStats()

        assert stats.hit_rate == 0.0

    def test_hit_rate_calculation(self):
        """Test hit rate calculation."""
        stats = CacheStats(hits=75, misses=25, total_requests=100)

        assert stats.hit_rate == 0.75

    def test_miss_rate_zero_requests(self):
        """Test miss rate with zero requests."""
        stats = CacheStats()

        assert stats.miss_rate == 0.0

    def test_miss_rate_calculation(self):
        """Test miss rate calculation."""
        stats = CacheStats(hits=60, misses=40, total_requests=100)

        assert stats.miss_rate == 0.40

    def test_usage_percent_zero_max(self):
        """Test usage percent with zero max size."""
        stats = CacheStats(size=50, max_size=0)

        assert stats.usage_percent == 0.0

    def test_usage_percent_calculation(self):
        """Test usage percent calculation."""
        stats = CacheStats(size=50, max_size=100)

        assert stats.usage_percent == 50.0


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

    def test_set_overwrite(self):
        """Test overwriting an existing key."""
        cache = InMemoryCache()
        cache.set("key", "value1")
        cache.set("key", "value2")

        assert cache.get("key") == "value2"

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

    def test_cache_complex_nested(self):
        """Test caching complex nested structures."""
        cache = InMemoryCache()

        complex_value = {
            "list": [1, 2, 3],
            "nested": {"a": {"b": "c"}},
            "tuple": (1, 2),
        }
        cache.set("complex", complex_value)

        result = cache.get("complex")
        assert result == complex_value


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

    def test_ttl_not_expired(self):
        """Test value not expired within TTL."""
        cache = InMemoryCache()
        cache.set("key", "value", ttl=10)

        time.sleep(0.1)
        assert cache.get("key") == "value"


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

    def test_eviction_removes_oldest(self):
        """Test that eviction removes the oldest entry."""
        cache = InMemoryCache(max_size=3)

        cache.set("key1", "value1")
        time.sleep(0.01)
        cache.set("key2", "value2")
        time.sleep(0.01)
        cache.set("key3", "value3")
        time.sleep(0.01)
        cache.set("key4", "value4")  # Should evict key1

        assert cache.get("key1") is None  # Evicted
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
        assert cache.get("key4") == "value4"

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


class TestFileBasedCache:
    """Tests for FileBasedCache backend."""

    def test_create_cache(self, tmp_path):
        """Test creating a file-based cache."""
        from codomyrmex.cache.backends.file_based import FileBasedCache

        cache = FileBasedCache(cache_dir=tmp_path / "cache")

        assert cache is not None
        assert cache.cache_dir.exists()

    def test_set_and_get(self, tmp_path):
        """Test basic set and get operations."""
        from codomyrmex.cache.backends.file_based import FileBasedCache

        cache = FileBasedCache(cache_dir=tmp_path / "cache")
        cache.set("key1", "value1")

        assert cache.get("key1") == "value1"

    def test_get_missing_key(self, tmp_path):
        """Test getting a missing key returns None."""
        from codomyrmex.cache.backends.file_based import FileBasedCache

        cache = FileBasedCache(cache_dir=tmp_path / "cache")

        assert cache.get("missing") is None

    def test_delete_existing_key(self, tmp_path):
        """Test deleting an existing key."""
        from codomyrmex.cache.backends.file_based import FileBasedCache

        cache = FileBasedCache(cache_dir=tmp_path / "cache")
        cache.set("key", "value")

        result = cache.delete("key")

        assert result is True
        assert cache.get("key") is None

    def test_clear(self, tmp_path):
        """Test clearing the cache."""
        from codomyrmex.cache.backends.file_based import FileBasedCache

        cache = FileBasedCache(cache_dir=tmp_path / "cache")
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        result = cache.clear()

        assert result is True
        assert cache.get("key1") is None

    def test_exists(self, tmp_path):
        """Test exists for file-based cache."""
        from codomyrmex.cache.backends.file_based import FileBasedCache

        cache = FileBasedCache(cache_dir=tmp_path / "cache")
        cache.set("key", "value")

        assert cache.exists("key") is True
        assert cache.exists("missing") is False

    def test_ttl_expiration(self, tmp_path):
        """Test TTL expiration for file-based cache."""
        from codomyrmex.cache.backends.file_based import FileBasedCache

        cache = FileBasedCache(cache_dir=tmp_path / "cache")
        cache.set("key", "value", ttl=1)

        assert cache.get("key") == "value"
        time.sleep(1.1)
        assert cache.get("key") is None

    def test_persistence(self, tmp_path):
        """Test cache persistence across instances."""
        from codomyrmex.cache.backends.file_based import FileBasedCache

        cache_dir = tmp_path / "cache"

        # First instance
        cache1 = FileBasedCache(cache_dir=cache_dir)
        cache1.set("persistent", "value")

        # Second instance
        cache2 = FileBasedCache(cache_dir=cache_dir)
        assert cache2.get("persistent") == "value"

    def test_complex_values(self, tmp_path):
        """Test caching complex values."""
        from codomyrmex.cache.backends.file_based import FileBasedCache

        cache = FileBasedCache(cache_dir=tmp_path / "cache")
        complex_value = {"list": [1, 2, 3], "nested": {"a": 1}}
        cache.set("complex", complex_value)

        result = cache.get("complex")

        assert result == complex_value


class TestNamespacedCache:
    """Tests for NamespacedCache."""

    def test_namespaced_cache_create(self):
        """Test creating a namespaced cache."""
        from codomyrmex.cache.namespaced import NamespacedCache

        base_cache = InMemoryCache()
        ns_cache = NamespacedCache(base_cache, "myapp")

        assert ns_cache is not None
        assert ns_cache.namespace == "myapp"

    def test_namespaced_set_and_get(self):
        """Test set and get with namespace prefix."""
        from codomyrmex.cache.namespaced import NamespacedCache

        base_cache = InMemoryCache()
        ns_cache = NamespacedCache(base_cache, "myapp")

        ns_cache.set("key", "value")

        assert ns_cache.get("key") == "value"
        # Verify it's stored with prefix
        assert base_cache.get("myapp:key") == "value"

    def test_namespaced_isolation(self):
        """Test namespace isolation."""
        from codomyrmex.cache.namespaced import NamespacedCache

        base_cache = InMemoryCache()
        ns1 = NamespacedCache(base_cache, "app1")
        ns2 = NamespacedCache(base_cache, "app2")

        ns1.set("key", "value1")
        ns2.set("key", "value2")

        assert ns1.get("key") == "value1"
        assert ns2.get("key") == "value2"

    def test_namespaced_delete(self):
        """Test delete with namespace."""
        from codomyrmex.cache.namespaced import NamespacedCache

        base_cache = InMemoryCache()
        ns_cache = NamespacedCache(base_cache, "myapp")

        ns_cache.set("key", "value")
        result = ns_cache.delete("key")

        assert result is True
        assert ns_cache.get("key") is None

    def test_namespaced_exists(self):
        """Test exists with namespace."""
        from codomyrmex.cache.namespaced import NamespacedCache

        base_cache = InMemoryCache()
        ns_cache = NamespacedCache(base_cache, "myapp")

        ns_cache.set("key", "value")

        assert ns_cache.exists("key") is True
        assert ns_cache.exists("missing") is False

    def test_namespaced_delete_pattern(self):
        """Test delete_pattern with namespace."""
        from codomyrmex.cache.namespaced import NamespacedCache

        base_cache = InMemoryCache()
        ns_cache = NamespacedCache(base_cache, "myapp")

        ns_cache.set("user:1", "alice")
        ns_cache.set("user:2", "bob")
        ns_cache.set("config", "value")

        deleted = ns_cache.delete_pattern("user:*")

        assert deleted == 2
        assert ns_cache.get("user:1") is None
        assert ns_cache.get("config") == "value"


class TestCacheManager:
    """Tests for CacheManager class."""

    def test_cache_manager_create(self):
        """Test creating a cache manager."""
        from codomyrmex.cache.cache_manager import CacheManager

        manager = CacheManager()

        assert manager is not None

    def test_get_default_cache(self):
        """Test getting default cache."""
        from codomyrmex.cache.cache_manager import CacheManager

        manager = CacheManager()
        cache = manager.get_cache()

        assert cache is not None

    def test_get_named_cache(self):
        """Test getting named cache."""
        from codomyrmex.cache.cache_manager import CacheManager

        manager = CacheManager()
        cache1 = manager.get_cache("cache1")
        cache2 = manager.get_cache("cache2")

        assert cache1 is not None
        assert cache2 is not None

    def test_same_name_returns_same_cache(self):
        """Test same name returns same cache instance."""
        from codomyrmex.cache.cache_manager import CacheManager

        manager = CacheManager()
        cache1 = manager.get_cache("mycache")
        cache2 = manager.get_cache("mycache")

        assert cache1 is cache2

    def test_get_in_memory_backend(self):
        """Test getting in-memory backend."""
        from codomyrmex.cache.cache_manager import CacheManager

        manager = CacheManager()
        cache = manager.get_cache(backend="in_memory")

        assert isinstance(cache, InMemoryCache)

    def test_get_file_based_backend(self):
        """Test getting file-based backend."""
        from codomyrmex.cache.cache_manager import CacheManager
        from codomyrmex.cache.backends.file_based import FileBasedCache

        manager = CacheManager()
        cache = manager.get_cache(backend="file_based")

        assert isinstance(cache, FileBasedCache)

    def test_unknown_backend_fallback(self):
        """Test unknown backend falls back to in-memory."""
        from codomyrmex.cache.cache_manager import CacheManager

        manager = CacheManager()
        cache = manager.get_cache(backend="unknown_backend")

        assert isinstance(cache, InMemoryCache)


class TestTTLManager:
    """Tests for TTLManager class."""

    def test_ttl_manager_create(self):
        """Test creating a TTL manager."""
        from codomyrmex.cache.ttl_manager import TTLManager

        manager = TTLManager(cleanup_interval=60)

        assert manager is not None
        assert manager.cleanup_interval == 60

    def test_register_cache(self):
        """Test registering a cache."""
        from codomyrmex.cache.ttl_manager import TTLManager

        manager = TTLManager(cleanup_interval=60)
        cache = InMemoryCache()

        manager.register_cache(cache)

        assert cache in manager._cache_registry

    def test_start_and_stop(self):
        """Test starting and stopping the cleanup thread."""
        from codomyrmex.cache.ttl_manager import TTLManager

        manager = TTLManager(cleanup_interval=1)
        manager.start()

        assert manager._thread is not None
        assert manager._thread.is_alive()

        manager.stop()

        # Thread should be stopped
        time.sleep(0.1)

    def test_cleanup_called(self):
        """Test cleanup is called on registered caches."""
        from codomyrmex.cache.ttl_manager import TTLManager

        manager = TTLManager(cleanup_interval=60)

        # Create mock cache with cleanup_expired method
        mock_cache = MagicMock()
        mock_cache.cleanup_expired = MagicMock()

        manager.register_cache(mock_cache)
        manager.cleanup()

        mock_cache.cleanup_expired.assert_called_once()


class TestGetCacheFunction:
    """Tests for get_cache convenience function."""

    def test_get_cache_default(self):
        """Test get_cache with default parameters."""
        from codomyrmex.cache import get_cache

        cache = get_cache()

        assert cache is not None

    def test_get_cache_named(self):
        """Test get_cache with name."""
        from codomyrmex.cache import get_cache

        cache = get_cache("mycache")

        assert cache is not None

    def test_get_cache_with_backend(self):
        """Test get_cache with specific backend."""
        from codomyrmex.cache import get_cache
        from codomyrmex.cache.backends.file_based import FileBasedCache

        cache = get_cache(backend="file_based")

        assert isinstance(cache, FileBasedCache)


class TestCacheError:
    """Tests for CacheError exception."""

    def test_cache_error_creation(self):
        """Test CacheError can be created."""
        from codomyrmex.cache import CacheError

        error = CacheError("Test error")

        assert str(error) == "Test error"
        assert isinstance(error, Exception)


class TestCacheIntegration:
    """Integration tests for cache module."""

    def test_full_workflow(self):
        """Test full cache workflow."""
        from codomyrmex.cache import get_cache

        cache = get_cache("workflow_test")

        # Set values
        cache.set("key1", "value1")
        cache.set("key2", {"nested": "data"})

        # Get values
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == {"nested": "data"}

        # Check existence
        assert cache.exists("key1") is True
        assert cache.exists("missing") is False

        # Delete
        cache.delete("key1")
        assert cache.get("key1") is None

        # Clear
        cache.clear()
        assert cache.get("key2") is None

    def test_ttl_workflow(self):
        """Test TTL workflow."""
        from codomyrmex.cache import get_cache

        cache = get_cache("ttl_test")

        cache.set("short_lived", "value", ttl=1)
        cache.set("long_lived", "value", ttl=100)

        assert cache.get("short_lived") == "value"
        assert cache.get("long_lived") == "value"

        time.sleep(1.1)

        assert cache.get("short_lived") is None
        assert cache.get("long_lived") == "value"

    def test_stats_workflow(self):
        """Test stats tracking workflow."""
        cache = InMemoryCache(max_size=100)

        # Generate some activity
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.get("key1")  # Hit
        cache.get("key2")  # Hit
        cache.get("missing1")  # Miss
        cache.get("missing2")  # Miss
        cache.get("missing3")  # Miss

        stats = cache.stats

        assert stats.hits == 2
        assert stats.misses == 3
        assert stats.total_requests == 5
        assert stats.hit_rate == 0.4
        assert stats.miss_rate == 0.6
        assert stats.size == 2

    def test_namespace_workflow(self):
        """Test namespaced cache workflow."""
        from codomyrmex.cache.namespaced import NamespacedCache

        base = InMemoryCache()
        users_cache = NamespacedCache(base, "users")
        products_cache = NamespacedCache(base, "products")

        users_cache.set("1", {"name": "Alice"})
        products_cache.set("1", {"name": "Widget"})

        assert users_cache.get("1") == {"name": "Alice"}
        assert products_cache.get("1") == {"name": "Widget"}


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

    def test_cache_set_returns_true(self):
        """Test cache set returns True on success."""
        cache = InMemoryCache()
        result = cache.set("key", "value")
        assert result is True

    def test_cache_clear_returns_true(self):
        """Test cache clear returns True on success."""
        cache = InMemoryCache()
        cache.set("key", "value")
        result = cache.clear()
        assert result is True

    def test_multiple_operations(self):
        """Test multiple cache operations in sequence."""
        cache = InMemoryCache()

        # Set multiple values
        for i in range(10):
            cache.set(f"key{i}", f"value{i}")

        # Verify all values
        for i in range(10):
            assert cache.get(f"key{i}") == f"value{i}"

        # Delete half
        for i in range(5):
            cache.delete(f"key{i}")

        # Verify deletion
        for i in range(5):
            assert cache.exists(f"key{i}") is False
        for i in range(5, 10):
            assert cache.exists(f"key{i}") is True
