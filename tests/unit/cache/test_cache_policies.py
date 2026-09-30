"""
Unit tests for cache.policies — Zero-Mock compliant.

Covers: CacheEntry (is_expired/touch), EvictionPolicy.contains,
LRUPolicy (get/put/remove/clear/size/eviction/expiry),
LFUPolicy (get/put/remove/clear/size/eviction/frequency-update),
TTLPolicy (get/put/remove/clear/size/cleanup_expired),
FIFOPolicy (get/put/remove/clear/size/eviction),
create_policy factory.
"""

import time
from datetime import timedelta

import pytest

from codomyrmex.cache.policies import (
    CacheEntry,
    FIFOPolicy,
    LFUPolicy,
    LRUPolicy,
    TTLPolicy,
    create_policy,
)

# ── CacheEntry ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestCacheEntry:
    def test_not_expired_without_ttl(self):
        e = CacheEntry(value="v")
        assert e.is_expired() is False

    def test_not_expired_within_ttl(self):
        e = CacheEntry(value="v", ttl=timedelta(hours=1))
        assert e.is_expired() is False

    def test_expired_with_past_ttl(self):
        e = CacheEntry(value="v", ttl=timedelta(seconds=-1))
        assert e.is_expired() is True

    def test_touch_increments_access_count(self):
        e = CacheEntry(value="v")
        e.touch()
        assert e.access_count == 1

    def test_touch_updates_accessed_at(self):
        e = CacheEntry(value="v")
        before = e.accessed_at
        time.sleep(0.005)
        e.touch()
        assert e.accessed_at > before

    def test_touch_multiple_times(self):
        e = CacheEntry(value="v")
        e.touch()
        e.touch()
        e.touch()
        assert e.access_count == 3


# ── LRUPolicy ─────────────────────────────────────────────────────────


@pytest.mark.unit
class TestLRUPolicy:
    def test_get_miss_returns_none(self):
        lru = LRUPolicy(max_size=5)
        assert lru.get("missing") is None

    def test_put_and_get(self):
        lru = LRUPolicy(max_size=5)
        lru.put("k", "v")
        assert lru.get("k") == "v"

    def test_size_after_put(self):
        lru = LRUPolicy(max_size=5)
        lru.put("a", 1)
        lru.put("b", 2)
        assert lru.size() == 2

    def test_put_update_existing(self):
        lru = LRUPolicy(max_size=5)
        lru.put("k", "original")
        lru.put("k", "updated")
        assert lru.get("k") == "updated"
        assert lru.size() == 1

    def test_lru_eviction_on_capacity(self):
        lru = LRUPolicy(max_size=3)
        lru.put("a", 1)
        lru.put("b", 2)
        lru.put("c", 3)
        # Access "a" to make it recently used
        lru.get("a")
        # "b" is now the LRU
        lru.put("d", 4)  # triggers eviction of "b"
        assert lru.get("b") is None
        assert lru.get("a") == 1
        assert lru.get("c") == 3

    def test_remove_existing_returns_value(self):
        lru = LRUPolicy(max_size=5)
        lru.put("k", "v")
        result = lru.remove("k")
        assert result == "v"

    def test_remove_missing_returns_none(self):
        lru = LRUPolicy(max_size=5)
        assert lru.remove("nonexistent") is None

    def test_remove_decrements_size(self):
        lru = LRUPolicy(max_size=5)
        lru.put("k", "v")
        lru.remove("k")
        assert lru.size() == 0

    def test_clear(self):
        lru = LRUPolicy(max_size=5)
        lru.put("a", 1)
        lru.put("b", 2)
        lru.clear()
        assert lru.size() == 0

    def test_get_expired_entry_returns_none(self):
        lru = LRUPolicy(max_size=5)
        lru.put("k", "v", ttl=timedelta(seconds=-1))
        assert lru.get("k") is None

    def test_get_expired_removes_entry(self):
        lru = LRUPolicy(max_size=5)
        lru.put("k", "v", ttl=timedelta(seconds=-1))
        lru.get("k")  # triggers removal
        assert lru.size() == 0

    def test_contains_true(self):
        lru = LRUPolicy(max_size=5)
        lru.put("x", "val")
        assert lru.contains("x") is True

    def test_contains_false(self):
        lru = LRUPolicy(max_size=5)
        assert lru.contains("x") is False


# ── LFUPolicy ─────────────────────────────────────────────────────────


@pytest.mark.unit
class TestLFUPolicy:
    def test_get_miss_returns_none(self):
        lfu = LFUPolicy(max_size=5)
        assert lfu.get("missing") is None

    def test_put_and_get(self):
        lfu = LFUPolicy(max_size=5)
        lfu.put("k", "v")
        assert lfu.get("k") == "v"

    def test_size_after_put(self):
        lfu = LFUPolicy(max_size=5)
        lfu.put("a", 1)
        lfu.put("b", 2)
        assert lfu.size() == 2

    def test_put_update_existing(self):
        lfu = LFUPolicy(max_size=5)
        lfu.put("k", "original")
        lfu.put("k", "updated")
        assert lfu.get("k") == "updated"
        assert lfu.size() == 1

    def test_lfu_eviction_preserves_most_frequent(self):
        lfu = LFUPolicy(max_size=3)
        lfu.put("a", 1)
        lfu.put("b", 2)
        lfu.put("c", 3)
        # Access "a" twice — it moves to a higher frequency bucket
        lfu.get("a")
        lfu.get("a")
        # Adding "d" should evict one of b/c (less frequent than a)
        lfu.put("d", 4)
        # "a" must be preserved (it has higher frequency)
        assert lfu.get("a") == 1
        # Total size should be max_size=3
        assert lfu.size() == 3

    def test_max_size_zero_no_storage(self):
        lfu = LFUPolicy(max_size=0)
        lfu.put("k", "v")
        assert lfu.get("k") is None

    def test_remove_existing_returns_value(self):
        lfu = LFUPolicy(max_size=5)
        lfu.put("k", "v")
        result = lfu.remove("k")
        assert result == "v"

    def test_remove_missing_returns_none(self):
        lfu = LFUPolicy(max_size=5)
        assert lfu.remove("nonexistent") is None

    def test_clear(self):
        lfu = LFUPolicy(max_size=5)
        lfu.put("a", 1)
        lfu.put("b", 2)
        lfu.clear()
        assert lfu.size() == 0

    def test_get_expired_entry_returns_none(self):
        lfu = LFUPolicy(max_size=5)
        lfu.put("k", "v", ttl=timedelta(seconds=-1))
        assert lfu.get("k") is None

    def test_frequency_increases_on_access(self):
        lfu = LFUPolicy(max_size=5)
        lfu.put("k", "v")
        lfu.get("k")
        lfu.get("k")
        lfu.get("k")
        # Still retrievable after 3 accesses
        assert lfu.get("k") == "v"


# ── TTLPolicy ─────────────────────────────────────────────────────────


@pytest.mark.unit
class TestTTLPolicy:
    def test_get_miss_returns_none(self):
        ttl_pol = TTLPolicy(max_size=5)
        assert ttl_pol.get("missing") is None

    def test_put_and_get(self):
        ttl_pol = TTLPolicy(max_size=5, default_ttl=timedelta(hours=1))
        ttl_pol.put("k", "v")
        assert ttl_pol.get("k") == "v"

    def test_size_after_put(self):
        ttl_pol = TTLPolicy(max_size=5, default_ttl=timedelta(hours=1))
        ttl_pol.put("a", 1)
        ttl_pol.put("b", 2)
        assert ttl_pol.size() == 2

    def test_custom_ttl_used(self):
        ttl_pol = TTLPolicy(max_size=5, default_ttl=timedelta(hours=1))
        ttl_pol.put("k", "v", ttl=timedelta(seconds=-1))
        assert ttl_pol.get("k") is None

    def test_default_ttl_applied_when_no_ttl(self):
        ttl_pol = TTLPolicy(max_size=5, default_ttl=timedelta(hours=1))
        ttl_pol.put("k", "v")
        assert ttl_pol.get("k") == "v"

    def test_eviction_when_capacity_reached(self):
        ttl_pol = TTLPolicy(max_size=2, default_ttl=timedelta(hours=1))
        ttl_pol.put("a", 1)
        ttl_pol.put("b", 2)
        ttl_pol.put("c", 3)  # should evict oldest
        assert ttl_pol.size() == 2

    def test_remove_existing_returns_value(self):
        ttl_pol = TTLPolicy(max_size=5, default_ttl=timedelta(hours=1))
        ttl_pol.put("k", "v")
        result = ttl_pol.remove("k")
        assert result == "v"

    def test_remove_missing_returns_none(self):
        ttl_pol = TTLPolicy(max_size=5)
        assert ttl_pol.remove("nonexistent") is None

    def test_clear(self):
        ttl_pol = TTLPolicy(max_size=5, default_ttl=timedelta(hours=1))
        ttl_pol.put("a", 1)
        ttl_pol.put("b", 2)
        ttl_pol.clear()
        assert ttl_pol.size() == 0

    def test_cleanup_expired_entries_on_get(self):
        ttl_pol = TTLPolicy(max_size=10, default_ttl=timedelta(hours=1))
        # Put entry with past expiry
        ttl_pol.put("expire_me", "v", ttl=timedelta(seconds=-1))
        ttl_pol.put("keep_me", "v2", ttl=timedelta(hours=1))
        # Get triggers cleanup
        assert ttl_pol.get("expire_me") is None
        assert ttl_pol.get("keep_me") == "v2"

    def test_size_excludes_expired(self):
        ttl_pol = TTLPolicy(max_size=10, default_ttl=timedelta(hours=1))
        ttl_pol.put("expired", "v", ttl=timedelta(seconds=-1))
        ttl_pol.put("live", "v2", ttl=timedelta(hours=1))
        # size() calls _cleanup_expired first
        assert ttl_pol.size() == 1


# ── FIFOPolicy ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestFIFOPolicy:
    def test_get_miss_returns_none(self):
        fifo = FIFOPolicy(max_size=5)
        assert fifo.get("missing") is None

    def test_put_and_get(self):
        fifo = FIFOPolicy(max_size=5)
        fifo.put("k", "v")
        assert fifo.get("k") == "v"

    def test_size_after_put(self):
        fifo = FIFOPolicy(max_size=5)
        fifo.put("a", 1)
        fifo.put("b", 2)
        assert fifo.size() == 2

    def test_put_update_existing(self):
        fifo = FIFOPolicy(max_size=5)
        fifo.put("k", "original")
        fifo.put("k", "updated")
        assert fifo.get("k") == "updated"
        assert fifo.size() == 1

    def test_fifo_eviction_removes_oldest(self):
        fifo = FIFOPolicy(max_size=3)
        fifo.put("first", 1)
        fifo.put("second", 2)
        fifo.put("third", 3)
        # "first" should be evicted
        fifo.put("fourth", 4)
        assert fifo.get("first") is None
        assert fifo.get("fourth") == 4

    def test_get_expired_entry_returns_none(self):
        fifo = FIFOPolicy(max_size=5)
        fifo.put("k", "v", ttl=timedelta(seconds=-1))
        assert fifo.get("k") is None

    def test_get_expired_removes_entry(self):
        fifo = FIFOPolicy(max_size=5)
        fifo.put("k", "v", ttl=timedelta(seconds=-1))
        fifo.get("k")
        assert fifo.size() == 0

    def test_remove_existing_returns_value(self):
        fifo = FIFOPolicy(max_size=5)
        fifo.put("k", "v")
        result = fifo.remove("k")
        assert result == "v"

    def test_remove_missing_returns_none(self):
        fifo = FIFOPolicy(max_size=5)
        assert fifo.remove("nonexistent") is None

    def test_clear(self):
        fifo = FIFOPolicy(max_size=5)
        fifo.put("a", 1)
        fifo.put("b", 2)
        fifo.clear()
        assert fifo.size() == 0

    def test_contains_true(self):
        fifo = FIFOPolicy(max_size=5)
        fifo.put("x", "val")
        assert fifo.contains("x") is True

    def test_contains_false(self):
        fifo = FIFOPolicy(max_size=5)
        assert fifo.contains("x") is False


# ── create_policy ─────────────────────────────────────────────────────


@pytest.mark.unit
class TestCreatePolicy:
    def test_create_lru(self):
        p = create_policy("lru", max_size=10)
        assert isinstance(p, LRUPolicy)

    def test_create_lfu(self):
        p = create_policy("lfu", max_size=10)
        assert isinstance(p, LFUPolicy)

    def test_create_ttl(self):
        p = create_policy("ttl", max_size=10)
        assert isinstance(p, TTLPolicy)

    def test_create_fifo(self):
        p = create_policy("fifo", max_size=10)
        assert isinstance(p, FIFOPolicy)

    def test_unknown_policy_raises(self):
        with pytest.raises(ValueError, match="Unknown policy"):
            create_policy("mru", max_size=10)

    def test_case_insensitive(self):
        p = create_policy("LRU", max_size=5)
        assert isinstance(p, LRUPolicy)

    def test_kwargs_passed_to_ttl(self):
        p = create_policy("ttl", max_size=5, default_ttl=timedelta(minutes=30))
        assert isinstance(p, TTLPolicy)
