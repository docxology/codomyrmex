"""Tests for codomyrmex.cache.cache_manager — CacheManager orchestration.

Covers:
- CacheManager lifecycle (create, get, remove, clear, summary)
- Backend selection (in_memory, file_based, unknown, redis fallback)
- InMemoryCache operations (get, set, delete, clear, exists, TTL, eviction, stats, patterns)
- FileBasedCache operations (get, set, delete, clear, exists, TTL, stats)
- TTLManager periodic cleanup registration
"""

import time

import pytest


@pytest.mark.unit
class TestCacheManagerLifecycle:
    """CacheManager creation, listing, removal, and summary."""

    def test_default_construction(self):
        from codomyrmex.cache.cache_manager import CacheManager

        mgr = CacheManager()
        assert mgr.cache_count == 0
        assert mgr.default_backend == "in_memory"

    def test_custom_defaults(self):
        from codomyrmex.cache.cache_manager import CacheManager

        mgr = CacheManager(default_backend="file_based", default_ttl=120)
        assert mgr.default_backend == "file_based"
        assert mgr._default_ttl == 120

    def test_get_cache_creates_instance(self):
        from codomyrmex.cache.cache_manager import CacheManager

        mgr = CacheManager()
        cache = mgr.get_cache("test")
        assert cache is not None
        assert mgr.cache_count == 1

    def test_get_cache_returns_same_instance(self):
        from codomyrmex.cache.cache_manager import CacheManager

        mgr = CacheManager()
        c1 = mgr.get_cache("alpha")
        c2 = mgr.get_cache("alpha")
        assert c1 is c2
        assert mgr.cache_count == 1

    def test_get_cache_different_names(self):
        from codomyrmex.cache.cache_manager import CacheManager

        mgr = CacheManager()
        mgr.get_cache("one")
        mgr.get_cache("two")
        assert mgr.cache_count == 2

    def test_has_cache_true(self):
        from codomyrmex.cache.cache_manager import CacheManager

        mgr = CacheManager()
        mgr.get_cache("present")
        assert mgr.has_cache("present") is True

    def test_has_cache_false(self):
        from codomyrmex.cache.cache_manager import CacheManager

        mgr = CacheManager()
        assert mgr.has_cache("absent") is False

    def test_remove_cache(self):
        from codomyrmex.cache.cache_manager import CacheManager

        mgr = CacheManager()
        mgr.get_cache("removable")
        assert mgr.remove_cache("removable") is True
        assert mgr.cache_count == 0
        assert mgr.has_cache("removable") is False

    def test_remove_nonexistent_cache(self):
        from codomyrmex.cache.cache_manager import CacheManager

        mgr = CacheManager()
        assert mgr.remove_cache("ghost") is False

    def test_list_caches(self):
        from codomyrmex.cache.cache_manager import CacheManager

        mgr = CacheManager()
        mgr.get_cache("first")
        mgr.get_cache("second")
        listing = mgr.list_caches()
        assert len(listing) == 2
        keys = [entry["key"] for entry in listing]
        assert "first:in_memory" in keys
        assert "second:in_memory" in keys
        for entry in listing:
            assert "backend" in entry
            assert "created_at" in entry
            assert entry["created_at"] > 0

    def test_clear_all(self):
        from codomyrmex.cache.cache_manager import CacheManager

        mgr = CacheManager()
        c1 = mgr.get_cache("a")
        c2 = mgr.get_cache("b")
        c1.set("k1", "v1")
        c2.set("k2", "v2")
        cleared = mgr.clear_all()
        assert cleared == 2
        assert c1.get("k1") is None
        assert c2.get("k2") is None

    def test_summary(self):
        from codomyrmex.cache.cache_manager import CacheManager

        mgr = CacheManager(default_ttl=300)
        mgr.get_cache("s1")
        mgr.get_cache("s2", backend="file_based")
        s = mgr.summary()
        assert s["total_caches"] == 2
        assert "in_memory" in s["backends_used"]
        assert "file_based" in s["backends_used"]
        assert s["default_ttl"] == 300


@pytest.mark.unit
class TestCacheManagerBackendSelection:
    """Backend creation and fallback logic."""

    def test_in_memory_backend(self):
        from codomyrmex.cache.cache_manager import CacheManager
        from codomyrmex.cache.backends.in_memory import InMemoryCache

        mgr = CacheManager()
        cache = mgr.get_cache("mem", backend="in_memory")
        assert isinstance(cache, InMemoryCache)

    def test_file_based_backend(self):
        from codomyrmex.cache.cache_manager import CacheManager
        from codomyrmex.cache.backends.file_based import FileBasedCache

        mgr = CacheManager()
        cache = mgr.get_cache("fb", backend="file_based")
        assert isinstance(cache, FileBasedCache)

    def test_unknown_backend_falls_back(self):
        from codomyrmex.cache.cache_manager import CacheManager
        from codomyrmex.cache.backends.in_memory import InMemoryCache

        mgr = CacheManager()
        cache = mgr.get_cache("unk", backend="memcached_nonexistent")
        assert isinstance(cache, InMemoryCache)

    def test_redis_backend_returns_valid_cache(self):
        """Redis backend returns a valid Cache instance (RedisCache or fallback)."""
        from codomyrmex.cache.cache_manager import CacheManager
        from codomyrmex.cache.cache import Cache

        mgr = CacheManager()
        cache = mgr.get_cache("red", backend="redis")
        # If redis package is installed, we get a RedisCache;
        # otherwise CacheManager falls back to InMemoryCache.
        # Either way it must be a valid Cache.
        assert isinstance(cache, Cache)

    def test_same_name_different_backend_creates_two(self):
        from codomyrmex.cache.cache_manager import CacheManager

        mgr = CacheManager()
        mgr.get_cache("shared", backend="in_memory")
        mgr.get_cache("shared", backend="file_based")
        assert mgr.cache_count == 2

    def test_default_backend_used_when_none(self):
        from codomyrmex.cache.cache_manager import CacheManager
        from codomyrmex.cache.backends.file_based import FileBasedCache

        mgr = CacheManager(default_backend="file_based")
        cache = mgr.get_cache("auto")
        assert isinstance(cache, FileBasedCache)


@pytest.mark.unit
class TestInMemoryCacheOperations:
    """InMemoryCache get/set/delete/clear/exists/stats."""

    def _make_cache(self, **kwargs):
        from codomyrmex.cache.backends.in_memory import InMemoryCache
        return InMemoryCache(**kwargs)

    def test_set_and_get(self):
        cache = self._make_cache()
        assert cache.set("key", "value") is True
        assert cache.get("key") == "value"

    def test_get_missing_key(self):
        cache = self._make_cache()
        assert cache.get("nope") is None

    def test_overwrite_key(self):
        cache = self._make_cache()
        cache.set("k", "old")
        cache.set("k", "new")
        assert cache.get("k") == "new"

    def test_delete_existing(self):
        cache = self._make_cache()
        cache.set("k", 1)
        assert cache.delete("k") is True
        assert cache.get("k") is None

    def test_delete_missing(self):
        cache = self._make_cache()
        assert cache.delete("nope") is False

    def test_exists(self):
        cache = self._make_cache()
        cache.set("there", 42)
        assert cache.exists("there") is True
        assert cache.exists("nowhere") is False

    def test_clear(self):
        cache = self._make_cache()
        cache.set("a", 1)
        cache.set("b", 2)
        assert cache.clear() is True
        assert cache.get("a") is None
        assert cache.get("b") is None

    def test_stats_hits_and_misses(self):
        cache = self._make_cache()
        cache.set("x", 10)
        cache.get("x")  # hit
        cache.get("y")  # miss
        s = cache.stats
        assert s.hits == 1
        assert s.misses == 1
        assert s.total_requests == 2

    def test_ttl_expiration(self):
        cache = self._make_cache()
        cache.set("temp", "data", ttl=1)
        assert cache.get("temp") == "data"
        time.sleep(1.1)
        assert cache.get("temp") is None

    def test_ttl_exists_expiration(self):
        cache = self._make_cache()
        cache.set("tmp", "val", ttl=1)
        assert cache.exists("tmp") is True
        time.sleep(1.1)
        assert cache.exists("tmp") is False

    def test_default_ttl(self):
        cache = self._make_cache(default_ttl=1)
        cache.set("auto_ttl", "data")
        assert cache.get("auto_ttl") == "data"
        time.sleep(1.1)
        assert cache.get("auto_ttl") is None

    def test_eviction_at_max_size(self):
        cache = self._make_cache(max_size=2)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)  # should evict oldest
        assert cache.stats.size == 2
        # 'c' and one of the earlier keys should be present
        assert cache.get("c") == 3

    def test_delete_pattern(self):
        cache = self._make_cache()
        cache.set("user:1", "alice")
        cache.set("user:2", "bob")
        cache.set("session:1", "abc")
        deleted = cache.delete_pattern("user:*")
        assert deleted == 2
        assert cache.get("user:1") is None
        assert cache.get("session:1") == "abc"

    def test_complex_values(self):
        cache = self._make_cache()
        cache.set("dict", {"nested": [1, 2, 3]})
        assert cache.get("dict") == {"nested": [1, 2, 3]}


@pytest.mark.unit
class TestFileBasedCacheOperations:
    """FileBasedCache get/set/delete/clear/exists/stats using tmp_path."""

    def _make_cache(self, tmp_path, **kwargs):
        from codomyrmex.cache.backends.file_based import FileBasedCache
        return FileBasedCache(cache_dir=tmp_path / "test_cache", **kwargs)

    def test_set_and_get(self, tmp_path):
        cache = self._make_cache(tmp_path)
        assert cache.set("k", "v") is True
        assert cache.get("k") == "v"

    def test_get_missing(self, tmp_path):
        cache = self._make_cache(tmp_path)
        assert cache.get("none") is None

    def test_overwrite(self, tmp_path):
        cache = self._make_cache(tmp_path)
        cache.set("k", "old")
        cache.set("k", "new")
        assert cache.get("k") == "new"

    def test_delete_existing(self, tmp_path):
        cache = self._make_cache(tmp_path)
        cache.set("k", 100)
        assert cache.delete("k") is True
        assert cache.get("k") is None

    def test_delete_missing(self, tmp_path):
        cache = self._make_cache(tmp_path)
        assert cache.delete("ghost") is False

    def test_exists(self, tmp_path):
        cache = self._make_cache(tmp_path)
        cache.set("here", "yes")
        assert cache.exists("here") is True
        assert cache.exists("not_here") is False

    def test_clear(self, tmp_path):
        cache = self._make_cache(tmp_path)
        cache.set("a", 1)
        cache.set("b", 2)
        assert cache.clear() is True
        assert cache.get("a") is None
        assert cache.get("b") is None

    def test_stats(self, tmp_path):
        cache = self._make_cache(tmp_path)
        cache.set("x", 10)
        cache.get("x")  # hit
        cache.get("y")  # miss
        s = cache.stats
        assert s.hits == 1
        assert s.misses == 1

    def test_ttl_expiration(self, tmp_path):
        cache = self._make_cache(tmp_path)
        cache.set("temp", "data", ttl=1)
        assert cache.get("temp") == "data"
        time.sleep(1.1)
        assert cache.get("temp") is None

    def test_ttl_exists_expiration(self, tmp_path):
        cache = self._make_cache(tmp_path)
        cache.set("tmp", "val", ttl=1)
        assert cache.exists("tmp") is True
        time.sleep(1.1)
        assert cache.exists("tmp") is False

    def test_default_ttl(self, tmp_path):
        cache = self._make_cache(tmp_path, default_ttl=1)
        cache.set("auto", "val")
        assert cache.get("auto") == "val"
        time.sleep(1.1)
        assert cache.get("auto") is None

    def test_json_serializable_values(self, tmp_path):
        cache = self._make_cache(tmp_path)
        cache.set("dict", {"nested": [1, 2, 3]})
        assert cache.get("dict") == {"nested": [1, 2, 3]}

    def test_cache_dir_created(self, tmp_path):
        cache = self._make_cache(tmp_path)
        assert cache.cache_dir.exists()


@pytest.mark.unit
class TestTTLManager:
    """TTLManager registration and cleanup."""

    def test_register_cache(self):
        from codomyrmex.cache.ttl_manager import TTLManager

        mgr = TTLManager(cleanup_interval=3600)
        # Use a real InMemoryCache as the registrant
        from codomyrmex.cache.backends.in_memory import InMemoryCache
        cache = InMemoryCache()
        mgr.register_cache(cache)
        assert cache in mgr._cache_registry
        mgr.stop()

    def test_cleanup_calls_cleanup_expired(self):
        from codomyrmex.cache.ttl_manager import TTLManager

        mgr = TTLManager(cleanup_interval=3600)

        class FakeExpirer:
            cleaned = False
            def cleanup_expired(self):
                self.cleaned = True

        obj = FakeExpirer()
        mgr._cache_registry.add(obj)
        mgr.cleanup()
        assert obj.cleaned is True

    def test_cleanup_handles_missing_method(self):
        from codomyrmex.cache.ttl_manager import TTLManager

        mgr = TTLManager(cleanup_interval=3600)

        class Bare:
            pass

        mgr._cache_registry.add(Bare())
        # Should not raise
        mgr.cleanup()

    def test_stop_idempotent(self):
        from codomyrmex.cache.ttl_manager import TTLManager

        mgr = TTLManager(cleanup_interval=3600)
        mgr.stop()  # No thread started, should not raise
        mgr.stop()


# ── helpers ──────────────────────────────────────────────────────────


def _redis_available() -> bool:
    """Check if redis package is importable."""
    import importlib.util
    return importlib.util.find_spec("redis") is not None
