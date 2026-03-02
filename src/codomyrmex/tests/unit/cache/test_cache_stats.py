"""
Unit tests for cache.stats — Zero-Mock compliant.

Covers: CacheStats (hit_rate/miss_rate/usage_percent/eviction_rate,
record_hit/miss/write/eviction/delete, hit_rate_window, hottest_keys,
reset, snapshot, to_dict, text).
"""

import pytest

from codomyrmex.cache.stats import CacheStats

# ── Properties ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestCacheStatsProperties:
    def test_hit_rate_zero_requests(self):
        s = CacheStats()
        assert s.hit_rate == 0.0

    def test_hit_rate_all_hits(self):
        s = CacheStats()
        s.record_hit()
        s.record_hit()
        assert s.hit_rate == 1.0

    def test_hit_rate_half(self):
        s = CacheStats()
        s.record_hit()
        s.record_miss()
        assert s.hit_rate == pytest.approx(0.5)

    def test_miss_rate_zero_requests(self):
        s = CacheStats()
        assert s.miss_rate == 0.0

    def test_miss_rate_all_misses(self):
        s = CacheStats()
        s.record_miss()
        s.record_miss()
        assert s.miss_rate == 1.0

    def test_usage_percent_zero_max_size(self):
        s = CacheStats(max_size=0)
        assert s.usage_percent == 0.0

    def test_usage_percent_half_full(self):
        s = CacheStats(size=5, max_size=10)
        assert s.usage_percent == pytest.approx(50.0)

    def test_eviction_rate_zero_writes(self):
        s = CacheStats()
        assert s.eviction_rate == 0.0

    def test_eviction_rate_some(self):
        s = CacheStats()
        s.record_write()
        s.record_write()
        s.record_eviction()
        assert s.eviction_rate == pytest.approx(0.5)


# ── Recording ─────────────────────────────────────────────────────────


@pytest.mark.unit
class TestCacheStatsRecording:
    def test_record_hit_increments_hits(self):
        s = CacheStats()
        s.record_hit()
        assert s.hits == 1

    def test_record_hit_increments_total(self):
        s = CacheStats()
        s.record_hit()
        assert s.total_requests == 1

    def test_record_hit_tracks_key(self):
        s = CacheStats()
        s.record_hit("mykey")
        assert s._key_hits["mykey"] == 1

    def test_record_hit_no_key_no_tracking(self):
        s = CacheStats()
        s.record_hit()  # no key
        assert len(s._key_hits) == 0

    def test_record_hit_key_accumulates(self):
        s = CacheStats()
        s.record_hit("k")
        s.record_hit("k")
        assert s._key_hits["k"] == 2

    def test_record_miss_increments_misses(self):
        s = CacheStats()
        s.record_miss()
        assert s.misses == 1

    def test_record_miss_increments_total(self):
        s = CacheStats()
        s.record_miss()
        assert s.total_requests == 1

    def test_record_write_increments_writes(self):
        s = CacheStats()
        s.record_write()
        assert s.writes == 1

    def test_record_eviction_increments_evictions(self):
        s = CacheStats()
        s.record_eviction()
        assert s.evictions == 1

    def test_record_delete_increments_deletes(self):
        s = CacheStats()
        s.record_delete()
        assert s.deletes == 1


# ── Time-Windowed Hit Rate ────────────────────────────────────────────


@pytest.mark.unit
class TestCacheStatsWindowedHitRate:
    def test_empty_timestamps_returns_zero(self):
        s = CacheStats()
        assert s.hit_rate_window(60.0) == 0.0

    def test_recent_hits_only(self):
        s = CacheStats()
        s.record_hit()
        s.record_hit()
        assert s.hit_rate_window(60.0) == 1.0

    def test_recent_misses_only(self):
        s = CacheStats()
        s.record_miss()
        s.record_miss()
        assert s.hit_rate_window(60.0) == 0.0

    def test_mixed_recent_half_hit_rate(self):
        s = CacheStats()
        s.record_hit()
        s.record_miss()
        assert s.hit_rate_window(60.0) == pytest.approx(0.5)


# ── Hottest Keys ──────────────────────────────────────────────────────


@pytest.mark.unit
class TestCacheStatsHottestKeys:
    def test_empty_returns_empty(self):
        s = CacheStats()
        assert s.hottest_keys() == []

    def test_returns_sorted_by_frequency(self):
        s = CacheStats()
        s.record_hit("low")
        s.record_hit("high")
        s.record_hit("high")
        s.record_hit("high")
        top = s.hottest_keys(1)
        assert top[0][0] == "high"
        assert top[0][1] == 3

    def test_respects_n_limit(self):
        s = CacheStats()
        for i in range(5):
            s.record_hit(f"key{i}")
        top = s.hottest_keys(n=3)
        assert len(top) == 3


# ── Reset / Snapshot ─────────────────────────────────────────────────


@pytest.mark.unit
class TestCacheStatsReset:
    def test_reset_clears_counters(self):
        s = CacheStats()
        s.record_hit()
        s.record_miss()
        s.record_write()
        s.reset()
        assert s.hits == 0
        assert s.misses == 0
        assert s.total_requests == 0
        assert s.writes == 0

    def test_reset_clears_timestamps(self):
        s = CacheStats()
        s.record_hit()
        s.reset()
        assert s._timestamps == []

    def test_reset_clears_key_hits(self):
        s = CacheStats()
        s.record_hit("k")
        s.reset()
        assert len(s._key_hits) == 0


@pytest.mark.unit
class TestCacheStatsSnapshot:
    def test_snapshot_is_independent_copy(self):
        s = CacheStats()
        s.record_hit()
        snap = s.snapshot()
        s.record_miss()
        # snapshot should not reflect the new miss
        assert snap.misses == 0
        assert snap.hits == 1

    def test_snapshot_preserves_values(self):
        s = CacheStats(max_size=100)
        s.record_hit()
        s.record_miss()
        snap = s.snapshot()
        assert snap.hits == 1
        assert snap.misses == 1
        assert snap.total_requests == 2
        assert snap.max_size == 100


# ── to_dict / text ────────────────────────────────────────────────────


@pytest.mark.unit
class TestCacheStatsOutput:
    def test_to_dict_has_required_keys(self):
        s = CacheStats()
        d = s.to_dict()
        for key in ("hits", "misses", "total_requests", "hit_rate",
                    "size", "max_size", "usage_percent", "evictions",
                    "writes", "deletes"):
            assert key in d

    def test_to_dict_values(self):
        s = CacheStats(size=5, max_size=10)
        s.record_hit()
        s.record_miss()
        d = s.to_dict()
        assert d["hits"] == 1
        assert d["misses"] == 1
        assert d["total_requests"] == 2
        assert d["hit_rate"] == 0.5

    def test_text_contains_hit_rate(self):
        s = CacheStats()
        s.record_hit()
        s.record_miss()
        t = s.text()
        assert "50.0%" in t

    def test_text_contains_entry_count(self):
        s = CacheStats(size=3, max_size=10)
        t = s.text()
        assert "3/10" in t
