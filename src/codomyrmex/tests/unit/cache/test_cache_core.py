"""Zero-mock tests for cache module core components.

Covers:
- CacheStats: all recording methods, properties, snapshot, reset, to_dict, text
- InMemoryCache: set/get/delete/clear/exists, TTL expiry, eviction, delete_pattern
- CacheManager: summary, clear_all, has_cache, backend selection edge cases
- TTLManager: register, start, stop, cleanup lifecycle
- MCP tools: cache_get, cache_set, cache_delete, cache_stats

Zero-Mock Policy: no unittest.mock, MagicMock, monkeypatch, or pytest-mock.
All tests use real in-memory data only.
"""

from __future__ import annotations

import time

import pytest

# ===========================================================================
# CacheStats
# ===========================================================================


@pytest.mark.unit
class TestCacheStatsRecording:
    """CacheStats recording methods and computed properties."""

    def _fresh(self, max_size: int = 100):
        from codomyrmex.cache.stats import CacheStats

        return CacheStats(max_size=max_size)

    def test_initial_state_is_zero(self):
        stats = self._fresh()
        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.total_requests == 0
        assert stats.size == 0
        assert stats.evictions == 0
        assert stats.writes == 0
        assert stats.deletes == 0

    def test_hit_rate_zero_on_empty(self):
        stats = self._fresh()
        assert stats.hit_rate == 0.0

    def test_miss_rate_zero_on_empty(self):
        stats = self._fresh()
        assert stats.miss_rate == 0.0

    def test_record_hit_increments_counters(self):
        stats = self._fresh()
        stats.record_hit("k1")
        assert stats.hits == 1
        assert stats.total_requests == 1
        assert stats.misses == 0

    def test_record_miss_increments_counters(self):
        stats = self._fresh()
        stats.record_miss("k1")
        assert stats.misses == 1
        assert stats.total_requests == 1
        assert stats.hits == 0

    def test_hit_rate_after_hits_and_misses(self):
        stats = self._fresh()
        stats.record_hit("k")
        stats.record_hit("k")
        stats.record_miss("k")
        assert stats.hit_rate == pytest.approx(2 / 3, rel=1e-6)

    def test_miss_rate_after_mixed(self):
        stats = self._fresh()
        stats.record_hit("k")
        stats.record_miss("k")
        assert stats.miss_rate == pytest.approx(0.5, rel=1e-6)

    def test_record_write_increments_writes(self):
        stats = self._fresh()
        stats.record_write()
        stats.record_write()
        assert stats.writes == 2

    def test_record_eviction_increments_evictions(self):
        stats = self._fresh()
        stats.record_eviction()
        assert stats.evictions == 1

    def test_eviction_rate_with_no_writes(self):
        stats = self._fresh()
        stats.record_eviction()
        assert stats.eviction_rate == 0.0  # writes == 0 → 0.0

    def test_eviction_rate_with_writes(self):
        stats = self._fresh()
        stats.record_write()
        stats.record_write()
        stats.record_eviction()
        assert stats.eviction_rate == pytest.approx(0.5, rel=1e-6)

    def test_record_delete_increments_deletes(self):
        stats = self._fresh()
        stats.record_delete()
        assert stats.deletes == 1

    def test_usage_percent_zero_max_size(self):
        from codomyrmex.cache.stats import CacheStats

        stats = CacheStats(max_size=0)
        assert stats.usage_percent == 0.0

    def test_usage_percent_half_full(self):
        stats = self._fresh(max_size=100)
        stats.size = 50
        assert stats.usage_percent == pytest.approx(50.0, rel=1e-6)

    def test_hottest_keys_empty(self):
        stats = self._fresh()
        assert stats.hottest_keys(5) == []

    def test_hottest_keys_tracks_key_hits(self):
        stats = self._fresh()
        stats.record_hit("a")
        stats.record_hit("a")
        stats.record_hit("b")
        top = stats.hottest_keys(5)
        keys = [k for k, _ in top]
        assert keys[0] == "a"
        assert "b" in keys

    def test_hottest_keys_respects_n(self):
        stats = self._fresh()
        for i in range(10):
            for _ in range(i + 1):
                stats.record_hit(f"key{i}")
        top = stats.hottest_keys(3)
        assert len(top) == 3

    def test_hit_rate_window_returns_zero_on_no_records(self):
        stats = self._fresh()
        assert stats.hit_rate_window(60.0) == 0.0

    def test_hit_rate_window_counts_recent_hits(self):
        stats = self._fresh()
        stats.record_hit("k")
        stats.record_hit("k")
        stats.record_miss("k")
        rate = stats.hit_rate_window(60.0)
        assert rate == pytest.approx(2 / 3, rel=1e-6)

    def test_reset_clears_all_counters(self):
        stats = self._fresh()
        stats.record_hit("k")
        stats.record_miss("k")
        stats.record_write()
        stats.size = 5
        stats.reset()
        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.total_requests == 0
        assert stats.size == 0
        assert stats.writes == 0

    def test_snapshot_is_independent_copy(self):
        stats = self._fresh()
        stats.record_hit("k")
        snap = stats.snapshot()
        stats.record_miss("k")
        assert snap.hits == 1
        assert snap.misses == 0  # snapshot not affected by later changes
        assert stats.misses == 1

    def test_to_dict_has_required_keys(self):
        stats = self._fresh()
        stats.record_hit("k")
        d = stats.to_dict()
        for key in (
            "hits",
            "misses",
            "total_requests",
            "hit_rate",
            "size",
            "max_size",
            "usage_percent",
            "evictions",
            "writes",
            "deletes",
        ):
            assert key in d

    def test_to_dict_values_match_state(self):
        stats = self._fresh(max_size=200)
        stats.record_hit("k")
        stats.record_miss("k")
        d = stats.to_dict()
        assert d["hits"] == 1
        assert d["misses"] == 1
        assert d["total_requests"] == 2
        assert d["max_size"] == 200

    def test_text_returns_string(self):
        stats = self._fresh()
        t = stats.text()
        assert isinstance(t, str)
        assert "Cache" in t


# ===========================================================================
# InMemoryCache
# ===========================================================================


@pytest.mark.unit
class TestInMemoryCacheCore:
    """InMemoryCache: set/get/delete/clear/exists, TTL, eviction, patterns."""

    def _cache(self, max_size: int = 100, default_ttl=None):
        from codomyrmex.cache.backends.in_memory import InMemoryCache

        return InMemoryCache(max_size=max_size, default_ttl=default_ttl)

    def test_set_returns_true(self):
        c = self._cache()
        assert c.set("k", "v") is True

    def test_get_returns_stored_value(self):
        c = self._cache()
        c.set("key", 42)
        assert c.get("key") == 42

    def test_get_missing_returns_none(self):
        c = self._cache()
        assert c.get("nonexistent") is None

    def test_delete_existing_returns_true(self):
        c = self._cache()
        c.set("k", "v")
        assert c.delete("k") is True

    def test_delete_missing_returns_false(self):
        c = self._cache()
        assert c.delete("no_such_key") is False

    def test_delete_removes_value(self):
        c = self._cache()
        c.set("k", "v")
        c.delete("k")
        assert c.get("k") is None

    def test_clear_returns_true(self):
        c = self._cache()
        c.set("a", 1)
        c.set("b", 2)
        assert c.clear() is True

    def test_clear_removes_all_entries(self):
        c = self._cache()
        c.set("a", 1)
        c.set("b", 2)
        c.clear()
        assert c.get("a") is None
        assert c.get("b") is None

    def test_exists_true_for_stored_key(self):
        c = self._cache()
        c.set("x", "y")
        assert c.exists("x") is True

    def test_exists_false_for_missing_key(self):
        c = self._cache()
        assert c.exists("missing") is False

    def test_ttl_expiry(self):
        c = self._cache()
        c.set("temp", "value", ttl=1)
        assert c.get("temp") == "value"
        time.sleep(1.1)
        assert c.get("temp") is None

    def test_exists_false_after_ttl_expiry(self):
        c = self._cache()
        c.set("expiring", "val", ttl=1)
        time.sleep(1.1)
        assert c.exists("expiring") is False

    def test_eviction_at_max_size(self):
        c = self._cache(max_size=3)
        c.set("a", 1)
        c.set("b", 2)
        c.set("c", 3)
        # Adding 4th should evict oldest
        c.set("d", 4)
        # Total size stays at 3
        assert c.stats.size == 3

    def test_overwrite_does_not_increase_size(self):
        c = self._cache(max_size=5)
        c.set("k", "v1")
        c.set("k", "v2")
        assert c.stats.size == 1

    def test_stats_hits_and_misses(self):
        c = self._cache()
        c.set("k", "v")
        c.get("k")  # hit
        c.get("nope")  # miss
        assert c.stats.hits == 1
        assert c.stats.misses == 1

    def test_delete_pattern_removes_matching_keys(self):
        c = self._cache()
        c.set("user:1", "a")
        c.set("user:2", "b")
        c.set("session:1", "c")
        removed = c.delete_pattern("user:*")
        assert removed == 2
        assert c.get("user:1") is None
        assert c.get("session:1") == "c"

    def test_delete_pattern_no_match_returns_zero(self):
        c = self._cache()
        c.set("k", "v")
        assert c.delete_pattern("xyz:*") == 0

    def test_store_complex_values(self):
        c = self._cache()
        val = {"nested": [1, 2, {"deep": True}]}
        c.set("complex", val)
        assert c.get("complex") == val

    def test_default_ttl_applied_when_no_explicit_ttl(self):
        c = self._cache(default_ttl=1)
        c.set("k", "v")  # uses default_ttl=1
        time.sleep(1.1)
        assert c.get("k") is None


# ===========================================================================
# CacheManager (additive, not duplicating test_cache_manager.py)
# ===========================================================================


@pytest.mark.unit
class TestCacheManagerCore:
    """CacheManager summary, clear_all, has_cache, unsupported backend."""

    def _mgr(self):
        from codomyrmex.cache.cache_manager import CacheManager

        return CacheManager()

    def test_summary_empty(self):
        mgr = self._mgr()
        s = mgr.summary()
        assert s["total_caches"] == 0
        assert s["backends_used"] == []

    def test_summary_after_cache_creation(self):
        mgr = self._mgr()
        mgr.get_cache("alpha", backend="in_memory")
        s = mgr.summary()
        assert s["total_caches"] == 1
        assert "in_memory" in s["backends_used"]

    def test_summary_default_backend_present(self):
        mgr = self._mgr()
        s = mgr.summary()
        assert s["default_backend"] == "in_memory"

    def test_summary_default_ttl_present(self):
        from codomyrmex.cache.cache_manager import CacheManager

        mgr = CacheManager(default_ttl=999)
        s = mgr.summary()
        assert s["default_ttl"] == 999

    def test_has_cache_false_before_create(self):
        mgr = self._mgr()
        assert mgr.has_cache("sessions") is False

    def test_has_cache_true_after_create(self):
        mgr = self._mgr()
        mgr.get_cache("sessions")
        assert mgr.has_cache("sessions") is True

    def test_clear_all_returns_count(self):
        mgr = self._mgr()
        mgr.get_cache("c1")
        mgr.get_cache("c2")
        count = mgr.clear_all()
        assert count == 2

    def test_clear_all_empties_caches(self):
        mgr = self._mgr()
        c = mgr.get_cache("test")
        c.set("key", "val")
        mgr.clear_all()
        assert c.get("key") is None

    def test_unknown_backend_falls_back_to_in_memory(self):
        mgr = self._mgr()
        # Should not raise — falls back to InMemoryCache
        cache = mgr.get_cache("x", backend="nonexistent_backend")
        assert cache is not None
        cache.set("hello", "world")
        assert cache.get("hello") == "world"

    def test_list_caches_is_sorted(self):
        mgr = self._mgr()
        mgr.get_cache("z_cache")
        mgr.get_cache("a_cache")
        entries = mgr.list_caches()
        keys = [e["key"] for e in entries]
        assert keys == sorted(keys)

    def test_list_caches_contains_backend_info(self):
        mgr = self._mgr()
        mgr.get_cache("myc", backend="in_memory")
        entries = mgr.list_caches()
        assert any(e["backend"] == "in_memory" for e in entries)

    def test_remove_cache_returns_true_when_exists(self):
        mgr = self._mgr()
        mgr.get_cache("rc")
        assert mgr.remove_cache("rc") is True

    def test_remove_cache_returns_false_when_missing(self):
        mgr = self._mgr()
        assert mgr.remove_cache("never_existed") is False

    def test_remove_cache_decrements_count(self):
        mgr = self._mgr()
        mgr.get_cache("del_me")
        before = mgr.cache_count
        mgr.remove_cache("del_me")
        assert mgr.cache_count == before - 1


# ===========================================================================
# MCP Tools
# ===========================================================================


@pytest.mark.unit
class TestCacheMcpTools:
    """MCP tools: cache_get, cache_set, cache_delete, cache_stats via real singleton."""

    def setup_method(self):
        # Reset singleton so each test class method starts fresh
        import codomyrmex.cache.mcp_tools as mt

        mt._manager = None

    def test_cache_set_returns_true(self):
        from codomyrmex.cache.mcp_tools import cache_set

        assert cache_set("key1", "val1") is True

    def test_cache_get_returns_stored_value(self):
        from codomyrmex.cache.mcp_tools import cache_get, cache_set

        cache_set("msg_key", "hello")
        assert cache_get("msg_key") == "hello"

    def test_cache_get_missing_returns_none(self):
        from codomyrmex.cache.mcp_tools import cache_get

        assert cache_get("no_such_key_xyz") is None

    def test_cache_delete_returns_true_when_exists(self):
        from codomyrmex.cache.mcp_tools import cache_delete, cache_set

        cache_set("del_key", "v")
        assert cache_delete("del_key") is True

    def test_cache_delete_returns_false_when_missing(self):
        from codomyrmex.cache.mcp_tools import cache_delete

        assert cache_delete("nonexistent_key_abc") is False

    def test_cache_stats_returns_dict(self):
        from codomyrmex.cache.mcp_tools import cache_stats

        stats = cache_stats()
        assert isinstance(stats, dict)

    def test_cache_stats_has_hits_key(self):
        from codomyrmex.cache.mcp_tools import cache_get, cache_set, cache_stats

        cache_set("sk", "sv")
        cache_get("sk")
        stats = cache_stats()
        assert "hits" in stats

    def test_cache_set_with_named_cache(self):
        from codomyrmex.cache.mcp_tools import cache_get, cache_set

        cache_set("k", "v", cache_name="namespace1")
        # Different namespace — should not see it
        assert cache_get("k", cache_name="namespace2") is None
        assert cache_get("k", cache_name="namespace1") == "v"

    def test_cache_stats_hit_rate_after_hit(self):
        import codomyrmex.cache.mcp_tools as mt
        from codomyrmex.cache.mcp_tools import cache_get, cache_set, cache_stats

        mt._manager = None
        cache_set("hr_key", "hr_val")
        cache_get("hr_key")  # 1 hit
        cache_get("missing")  # 1 miss
        stats = cache_stats()
        assert stats["hit_rate"] >= 0.0


# ===========================================================================
# TTLManager
# ===========================================================================


@pytest.mark.unit
class TestTtlManagerCore:
    """TTLManager: register, start, stop, cleanup."""

    def _mgr(self, interval: int = 3600):
        from codomyrmex.cache.ttl_manager import TTLManager

        return TTLManager(cleanup_interval=interval)

    def test_construction(self):
        mgr = self._mgr(60)
        assert mgr.cleanup_interval == 60

    def test_register_cache_starts_thread(self):
        from codomyrmex.cache.backends.in_memory import InMemoryCache

        mgr = self._mgr(3600)
        cache = InMemoryCache()
        mgr.register_cache(cache)
        try:
            assert mgr._thread is not None
            assert mgr._thread.is_alive()
        finally:
            mgr.stop()

    def test_stop_sets_stop_event(self):
        from codomyrmex.cache.backends.in_memory import InMemoryCache

        mgr = self._mgr(3600)
        cache = InMemoryCache()
        mgr.register_cache(cache)
        try:
            assert not mgr._stop_event.is_set()
        finally:
            mgr.stop()
        # After stop(), the stop event must be set regardless of thread sleep state
        assert mgr._stop_event.is_set()

    def test_cleanup_does_not_raise_on_empty_registry(self):
        mgr = self._mgr()
        # Calling cleanup with nothing registered should not raise
        mgr.cleanup()

    def test_cleanup_calls_cleanup_expired_if_available(self):
        """Register a cache with cleanup_expired and verify it gets called."""

        class TrackingCache:
            def __init__(self):
                self.cleaned = False

            def cleanup_expired(self):
                self.cleaned = True

        mgr = self._mgr(3600)
        tracker = TrackingCache()
        mgr._cache_registry.add(tracker)
        mgr.cleanup()
        assert tracker.cleaned is True

    def test_double_start_does_not_create_second_thread(self):
        from codomyrmex.cache.backends.in_memory import InMemoryCache

        mgr = self._mgr(3600)
        c = InMemoryCache()
        mgr.register_cache(c)
        first_thread = mgr._thread
        mgr.start()  # Should be a no-op since thread is already alive
        try:
            assert mgr._thread is first_thread
        finally:
            mgr.stop()
