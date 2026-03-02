"""
Unit tests for cache.warmers — Zero-Mock compliant.

Covers: WarmingStrategy (enum), WarmingConfig (dataclass), WarmingStats
(success_rate), StaticKeyProvider, CallableKeyProvider, CallableValueLoader,
BatchValueLoader, CacheWarmer (warm/warm_key/is_warming/stats),
AccessTracker (record_access/get_access_count/get_hot_keys/get_recent_keys/clear),
AdaptiveKeyProvider.
"""

import pytest

from codomyrmex.cache.warmers import (
    AccessTracker,
    AdaptiveKeyProvider,
    BatchValueLoader,
    CacheWarmer,
    CallableKeyProvider,
    CallableValueLoader,
    StaticKeyProvider,
    WarmingConfig,
    WarmingStats,
    WarmingStrategy,
)

# ── WarmingStrategy ───────────────────────────────────────────────────


@pytest.mark.unit
class TestWarmingStrategy:
    def test_eager_value(self):
        assert WarmingStrategy.EAGER.value == "eager"

    def test_lazy_value(self):
        assert WarmingStrategy.LAZY.value == "lazy"

    def test_scheduled_value(self):
        assert WarmingStrategy.SCHEDULED.value == "scheduled"

    def test_adaptive_value(self):
        assert WarmingStrategy.ADAPTIVE.value == "adaptive"


# ── WarmingConfig ─────────────────────────────────────────────────────


@pytest.mark.unit
class TestWarmingConfig:
    def test_defaults(self):
        c = WarmingConfig()
        assert c.strategy == WarmingStrategy.LAZY
        assert c.batch_size == 100
        assert c.max_workers == 4
        assert c.max_retries == 3

    def test_custom_values(self):
        c = WarmingConfig(strategy=WarmingStrategy.EAGER, batch_size=50, max_workers=2)
        assert c.strategy == WarmingStrategy.EAGER
        assert c.batch_size == 50
        assert c.max_workers == 2


# ── WarmingStats ──────────────────────────────────────────────────────


@pytest.mark.unit
class TestWarmingStats:
    def test_success_rate_all_warmed(self):
        s = WarmingStats(keys_warmed=10, keys_failed=0)
        assert s.success_rate == 1.0

    def test_success_rate_all_failed(self):
        s = WarmingStats(keys_warmed=0, keys_failed=5)
        assert s.success_rate == 0.0

    def test_success_rate_mixed(self):
        s = WarmingStats(keys_warmed=3, keys_failed=1)
        assert s.success_rate == pytest.approx(0.75)

    def test_success_rate_zero_total(self):
        s = WarmingStats()
        # Both 0 → default to 1.0 (no failures = success)
        assert s.success_rate == 1.0


# ── StaticKeyProvider ─────────────────────────────────────────────────


@pytest.mark.unit
class TestStaticKeyProvider:
    def test_returns_all_keys(self):
        prov = StaticKeyProvider(["a", "b", "c"])
        assert prov.get_keys() == ["a", "b", "c"]

    def test_returns_copy(self):
        keys = ["x", "y"]
        prov = StaticKeyProvider(keys)
        returned = prov.get_keys()
        returned.append("z")
        # Provider's internal list should not change
        assert prov.get_keys() == ["x", "y"]

    def test_empty_keys(self):
        prov = StaticKeyProvider([])
        assert prov.get_keys() == []


# ── CallableKeyProvider ───────────────────────────────────────────────


@pytest.mark.unit
class TestCallableKeyProvider:
    def test_calls_function_for_keys(self):
        prov = CallableKeyProvider(lambda: ["key1", "key2"])
        assert prov.get_keys() == ["key1", "key2"]

    def test_calls_function_each_time(self):
        call_count = [0]

        def counter():
            call_count[0] += 1
            return [f"key{call_count[0]}"]

        prov = CallableKeyProvider(counter)
        prov.get_keys()
        prov.get_keys()
        assert call_count[0] == 2


# ── CallableValueLoader ───────────────────────────────────────────────


@pytest.mark.unit
class TestCallableValueLoader:
    def test_loads_value_via_callable(self):
        loader = CallableValueLoader(lambda k: k.upper())
        assert loader.load("hello") == "HELLO"

    def test_loads_different_keys(self):
        loader = CallableValueLoader(lambda k: k * 2)
        assert loader.load(3) == 6
        assert loader.load(5) == 10


# ── BatchValueLoader ──────────────────────────────────────────────────


@pytest.mark.unit
class TestBatchValueLoader:
    def test_load_batch_returns_results(self):
        def batch_fn(keys):
            return {k: k.upper() for k in keys}

        loader = BatchValueLoader(batch_fn)
        result = loader.load_batch(["a", "b", "c"])
        assert result == {"a": "A", "b": "B", "c": "C"}

    def test_load_batch_updates_cache(self):
        loader = BatchValueLoader(lambda ks: {k: k * 10 for k in ks})
        loader.load_batch([1, 2])
        assert loader.load(1) == 10  # from cache

    def test_load_single_via_batch_fn(self):
        loader = BatchValueLoader(lambda ks: {k: k + 100 for k in ks})
        result = loader.load(5)  # not in cache → calls batch_fn([5])
        assert result == 105


# ── CacheWarmer ───────────────────────────────────────────────────────


@pytest.mark.unit
class TestCacheWarmer:
    def _make_warmer(self, keys, loader_fn=None):
        cache = {}
        key_prov = StaticKeyProvider(keys)
        val_loader = CallableValueLoader(loader_fn or (lambda k: k.upper()))
        return CacheWarmer(cache=cache, key_provider=key_prov, value_loader=val_loader), cache

    def test_warm_populates_cache(self):
        warmer, cache = self._make_warmer(["a", "b", "c"])
        warmer.warm()
        assert cache == {"a": "A", "b": "B", "c": "C"}

    def test_warm_returns_stats(self):
        warmer, _ = self._make_warmer(["x", "y"])
        stats = warmer.warm()
        assert isinstance(stats, WarmingStats)
        assert stats.keys_warmed == 2
        assert stats.keys_failed == 0

    def test_warm_with_explicit_keys(self):
        warmer, cache = self._make_warmer(["a", "b", "c"])
        warmer.warm(keys=["a"])
        assert "a" in cache
        assert "b" not in cache

    def test_warm_with_failing_loader(self):
        def bad_loader(k):
            raise ValueError("load failed")

        cache = {}
        warmer = CacheWarmer(
            cache=cache,
            key_provider=StaticKeyProvider(["k1"]),
            value_loader=CallableValueLoader(bad_loader),
            config=WarmingConfig(max_retries=0, retry_on_failure=False),
        )
        stats = warmer.warm()
        assert stats.keys_failed == 1
        assert len(stats.errors) == 1

    def test_stats_updated_after_warm(self):
        warmer, _ = self._make_warmer(["a"])
        warmer.warm()
        assert warmer.stats.keys_warmed == 1

    def test_is_warming_false_initially(self):
        warmer, _ = self._make_warmer([])
        assert warmer.is_warming is False

    def test_warm_key_success(self):
        cache = {}
        warmer = CacheWarmer(
            cache=cache,
            key_provider=StaticKeyProvider([]),
            value_loader=CallableValueLoader(lambda k: k * 2),
        )
        result = warmer.warm_key("z")
        assert result is True
        assert cache["z"] == "zz"

    def test_warm_key_failure_returns_false(self):
        warmer = CacheWarmer(
            cache={},
            key_provider=StaticKeyProvider([]),
            value_loader=CallableValueLoader(lambda k: (_ for _ in ()).throw(RuntimeError("fail"))),
        )
        result = warmer.warm_key("x")
        assert result is False

    def test_warm_with_batch_loader(self):
        cache = {}
        batch_loader = BatchValueLoader(lambda ks: {k: k + "_val" for k in ks})
        warmer = CacheWarmer(
            cache=cache,
            key_provider=StaticKeyProvider(["a", "b"]),
            value_loader=batch_loader,
        )
        stats = warmer.warm()
        assert stats.keys_warmed == 2
        assert cache["a"] == "a_val"


# ── AccessTracker ─────────────────────────────────────────────────────


@pytest.mark.unit
class TestAccessTracker:
    def test_initial_count_zero(self):
        tracker = AccessTracker()
        assert tracker.get_access_count("missing") == 0

    def test_record_access_increments_count(self):
        tracker = AccessTracker()
        tracker.record_access("key1")
        assert tracker.get_access_count("key1") == 1

    def test_multiple_accesses(self):
        tracker = AccessTracker()
        tracker.record_access("k")
        tracker.record_access("k")
        tracker.record_access("k")
        assert tracker.get_access_count("k") == 3

    def test_get_hot_keys_threshold(self):
        tracker = AccessTracker()
        for _ in range(5):
            tracker.record_access("popular")
        for _ in range(2):
            tracker.record_access("less_popular")
        hot = tracker.get_hot_keys(threshold=3)
        assert "popular" in hot
        assert "less_popular" not in hot

    def test_get_hot_keys_empty(self):
        tracker = AccessTracker()
        assert tracker.get_hot_keys() == []

    def test_get_recent_keys(self):
        tracker = AccessTracker()
        tracker.record_access("recent_key")
        recent = tracker.get_recent_keys(seconds=60.0)
        assert "recent_key" in recent

    def test_get_recent_keys_limit(self):
        tracker = AccessTracker()
        for i in range(10):
            tracker.record_access(f"key{i}")
        recent = tracker.get_recent_keys(seconds=60.0, limit=5)
        assert len(recent) <= 5

    def test_clear_resets_counts(self):
        tracker = AccessTracker()
        tracker.record_access("x")
        tracker.clear()
        assert tracker.get_access_count("x") == 0

    def test_clear_removes_recency_data(self):
        tracker = AccessTracker()
        tracker.record_access("x")
        tracker.clear()
        assert tracker.get_recent_keys(seconds=60.0) == []


# ── AdaptiveKeyProvider ───────────────────────────────────────────────


@pytest.mark.unit
class TestAdaptiveKeyProvider:
    def test_returns_hot_keys(self):
        tracker = AccessTracker()
        for _ in range(10):
            tracker.record_access("hot_key")
        prov = AdaptiveKeyProvider(tracker, threshold=5)
        assert "hot_key" in prov.get_keys()

    def test_excludes_cold_keys(self):
        tracker = AccessTracker()
        tracker.record_access("cold_key")  # only 1 access
        prov = AdaptiveKeyProvider(tracker, threshold=5)
        assert "cold_key" not in prov.get_keys()

    def test_respects_limit(self):
        tracker = AccessTracker()
        for i in range(20):
            for _ in range(10):
                tracker.record_access(f"key{i}")
        prov = AdaptiveKeyProvider(tracker, threshold=5, limit=3)
        assert len(prov.get_keys()) <= 3
