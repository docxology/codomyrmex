"""Zero-mock unit tests for cache/backends/file_based.py.

Tests FileBasedCache with real temp files (tmp_path fixture).
Covers: init, get/set/delete/clear/exists, TTL expiry,
stats tracking, persistence across instances, and edge cases.

No mocks, stubs, or monkeypatching used.
"""

from __future__ import annotations

import json
import time

import pytest

from codomyrmex.cache.backends.file_based import FileBasedCache
from codomyrmex.cache.stats import CacheStats

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def cache(tmp_path):
    """Return a FileBasedCache backed by an isolated temp directory."""
    return FileBasedCache(cache_dir=tmp_path / "cache")


# ===========================================================================
# Initialization
# ===========================================================================


@pytest.mark.unit
class TestFileBasedCacheInit:
    """Tests for FileBasedCache.__init__."""

    def test_cache_dir_created_on_init(self, tmp_path):
        cache_dir = tmp_path / "my_cache"
        assert not cache_dir.exists()
        FileBasedCache(cache_dir=cache_dir)
        assert cache_dir.exists()

    def test_default_cache_dir_is_in_tmp(self):
        cache = FileBasedCache()
        import tempfile

        assert str(tempfile.gettempdir()) in str(cache.cache_dir)

    def test_custom_cache_dir_stored(self, tmp_path):
        cache_dir = tmp_path / "custom"
        cache = FileBasedCache(cache_dir=cache_dir)
        assert cache.cache_dir == cache_dir

    def test_default_ttl_stored(self, tmp_path):
        cache = FileBasedCache(cache_dir=tmp_path / "c", default_ttl=300)
        assert cache.default_ttl == 300

    def test_default_ttl_is_none_when_unset(self, tmp_path):
        cache = FileBasedCache(cache_dir=tmp_path / "c")
        assert cache.default_ttl is None

    def test_nested_cache_dir_created(self, tmp_path):
        deep = tmp_path / "a" / "b" / "c"
        FileBasedCache(cache_dir=deep)
        assert deep.exists()


# ===========================================================================
# get / set
# ===========================================================================


@pytest.mark.unit
class TestFileBasedCacheGetSet:
    """Tests for get() and set() on FileBasedCache."""

    def test_set_returns_true(self, cache):
        result = cache.set("k", "v")
        assert result is True

    def test_get_after_set_returns_value(self, cache):
        cache.set("key", "value")
        assert cache.get("key") == "value"

    def test_get_missing_key_returns_none(self, cache):
        assert cache.get("nonexistent") is None

    def test_set_and_get_integer(self, cache):
        cache.set("num", 42)
        assert cache.get("num") == 42

    def test_set_and_get_float(self, cache):
        cache.set("pi", 3.14159)
        assert cache.get("pi") == pytest.approx(3.14159)

    def test_set_and_get_list(self, cache):
        cache.set("lst", [1, 2, 3])
        assert cache.get("lst") == [1, 2, 3]

    def test_set_and_get_dict(self, cache):
        payload = {"name": "Alice", "age": 30}
        cache.set("user", payload)
        assert cache.get("user") == payload

    def test_set_and_get_nested_structure(self, cache):
        nested = {"outer": {"inner": [1, 2, {"deep": True}]}}
        cache.set("nested", nested)
        assert cache.get("nested") == nested

    def test_overwrite_existing_key(self, cache):
        cache.set("key", "first")
        cache.set("key", "second")
        assert cache.get("key") == "second"

    def test_cache_files_created_on_set(self, tmp_path):
        cache = FileBasedCache(cache_dir=tmp_path / "c")
        cache.set("mykey", "myval")
        cache_files = list((tmp_path / "c").glob("*.cache"))
        meta_files = list((tmp_path / "c").glob("*.meta"))
        assert len(cache_files) == 1
        assert len(meta_files) == 1

    def test_meta_file_contains_timestamp(self, tmp_path):
        cache = FileBasedCache(cache_dir=tmp_path / "c")
        before = time.time()
        cache.set("k", "v")
        meta_files = list((tmp_path / "c").glob("*.meta"))
        meta = json.loads(meta_files[0].read_text())
        assert meta["timestamp"] >= before

    def test_meta_file_ttl_none_when_unset(self, tmp_path):
        cache = FileBasedCache(cache_dir=tmp_path / "c")
        cache.set("k", "v")
        meta_files = list((tmp_path / "c").glob("*.meta"))
        meta = json.loads(meta_files[0].read_text())
        assert meta["ttl"] is None

    def test_meta_file_ttl_stored_when_set(self, tmp_path):
        cache = FileBasedCache(cache_dir=tmp_path / "c")
        cache.set("k", "v", ttl=120)
        meta_files = list((tmp_path / "c").glob("*.meta"))
        meta = json.loads(meta_files[0].read_text())
        assert meta["ttl"] == 120


# ===========================================================================
# TTL expiry
# ===========================================================================


@pytest.mark.unit
class TestFileBasedCacheTTL:
    """Tests for TTL expiry behaviour."""

    def test_value_accessible_before_expiry(self, cache):
        cache.set("k", "v", ttl=10)
        assert cache.get("k") == "v"

    def test_value_gone_after_expiry(self, cache):
        cache.set("k", "v", ttl=1)
        time.sleep(1.1)
        assert cache.get("k") is None

    def test_exists_false_after_expiry(self, cache):
        cache.set("k", "v", ttl=1)
        time.sleep(1.1)
        assert cache.exists("k") is False

    def test_expiry_removes_files(self, tmp_path):
        cache = FileBasedCache(cache_dir=tmp_path / "c")
        cache.set("k", "v", ttl=1)
        time.sleep(1.1)
        cache.get("k")  # triggers cleanup
        assert len(list((tmp_path / "c").glob("*.cache"))) == 0

    def test_default_ttl_applied(self, tmp_path):
        cache = FileBasedCache(cache_dir=tmp_path / "c", default_ttl=1)
        cache.set("k", "v")
        time.sleep(1.1)
        assert cache.get("k") is None

    def test_per_set_ttl_overrides_default(self, tmp_path):
        cache = FileBasedCache(cache_dir=tmp_path / "c", default_ttl=100)
        cache.set("k", "v", ttl=1)
        time.sleep(1.1)
        assert cache.get("k") is None

    def test_no_ttl_persists_indefinitely(self, cache):
        cache.set("k", "v")
        time.sleep(0.1)
        assert cache.get("k") == "v"


# ===========================================================================
# exists
# ===========================================================================


@pytest.mark.unit
class TestFileBasedCacheExists:
    """Tests for exists()."""

    def test_exists_true_for_set_key(self, cache):
        cache.set("k", "v")
        assert cache.exists("k") is True

    def test_exists_false_for_missing_key(self, cache):
        assert cache.exists("missing") is False

    def test_exists_false_after_delete(self, cache):
        cache.set("k", "v")
        cache.delete("k")
        assert cache.exists("k") is False

    def test_exists_false_after_clear(self, cache):
        cache.set("k", "v")
        cache.clear()
        assert cache.exists("k") is False


# ===========================================================================
# delete
# ===========================================================================


@pytest.mark.unit
class TestFileBasedCacheDelete:
    """Tests for delete()."""

    def test_delete_returns_true_for_existing_key(self, cache):
        cache.set("k", "v")
        assert cache.delete("k") is True

    def test_delete_returns_false_for_missing_key(self, cache):
        assert cache.delete("nonexistent") is False

    def test_deleted_key_not_gettable(self, cache):
        cache.set("k", "v")
        cache.delete("k")
        assert cache.get("k") is None

    def test_delete_removes_both_cache_and_meta_files(self, tmp_path):
        cache = FileBasedCache(cache_dir=tmp_path / "c")
        cache.set("k", "v")
        cache.delete("k")
        assert len(list((tmp_path / "c").glob("*.cache"))) == 0
        assert len(list((tmp_path / "c").glob("*.meta"))) == 0

    def test_delete_does_not_affect_other_keys(self, cache):
        cache.set("a", 1)
        cache.set("b", 2)
        cache.delete("a")
        assert cache.get("b") == 2


# ===========================================================================
# clear
# ===========================================================================


@pytest.mark.unit
class TestFileBasedCacheClear:
    """Tests for clear()."""

    def test_clear_returns_true(self, cache):
        cache.set("k", "v")
        assert cache.clear() is True

    def test_clear_removes_all_entries(self, tmp_path):
        cache = FileBasedCache(cache_dir=tmp_path / "c")
        for i in range(5):
            cache.set(f"key{i}", f"val{i}")
        cache.clear()
        assert len(list((tmp_path / "c").glob("*.cache"))) == 0
        assert len(list((tmp_path / "c").glob("*.meta"))) == 0

    def test_clear_on_empty_cache_returns_true(self, cache):
        assert cache.clear() is True

    def test_get_returns_none_after_clear(self, cache):
        cache.set("k", "v")
        cache.clear()
        assert cache.get("k") is None

    def test_cache_usable_after_clear(self, cache):
        cache.set("a", 1)
        cache.clear()
        cache.set("b", 2)
        assert cache.get("b") == 2


# ===========================================================================
# stats
# ===========================================================================


@pytest.mark.unit
class TestFileBasedCacheStats:
    """Tests for the stats property."""

    def test_stats_returns_cache_stats_instance(self, cache):
        assert isinstance(cache.stats, CacheStats)

    def test_initial_hits_zero(self, cache):
        assert cache.stats.hits == 0

    def test_initial_misses_zero(self, cache):
        assert cache.stats.misses == 0

    def test_hit_increments_hits(self, cache):
        cache.set("k", "v")
        cache.get("k")
        assert cache.stats.hits == 1

    def test_miss_increments_misses(self, cache):
        cache.get("missing")
        assert cache.stats.misses == 1

    def test_total_requests_tracked(self, cache):
        cache.set("k", "v")
        cache.get("k")  # hit
        cache.get("none")  # miss
        assert cache.stats.total_requests == 2

    def test_stats_size_reflects_set_entries(self, tmp_path):
        cache = FileBasedCache(cache_dir=tmp_path / "c")
        cache.set("a", 1)
        cache.set("b", 2)
        assert cache.stats.size == 2

    def test_stats_size_decrements_after_delete(self, cache):
        cache.set("a", 1)
        cache.set("b", 2)
        cache.delete("a")
        assert cache.stats.size == 1

    def test_stats_size_zero_after_clear(self, cache):
        cache.set("a", 1)
        cache.set("b", 2)
        cache.clear()
        assert cache.stats.size == 0


# ===========================================================================
# Persistence across instances
# ===========================================================================


@pytest.mark.unit
class TestFileBasedCachePersistence:
    """Tests that data survives across separate FileBasedCache instances."""

    def test_value_readable_from_new_instance(self, tmp_path):
        cache_dir = tmp_path / "shared"
        c1 = FileBasedCache(cache_dir=cache_dir)
        c1.set("persistent", {"data": 123})
        c2 = FileBasedCache(cache_dir=cache_dir)
        assert c2.get("persistent") == {"data": 123}

    def test_multiple_keys_survive_new_instance(self, tmp_path):
        cache_dir = tmp_path / "shared"
        c1 = FileBasedCache(cache_dir=cache_dir)
        c1.set("x", 10)
        c1.set("y", 20)
        c2 = FileBasedCache(cache_dir=cache_dir)
        assert c2.get("x") == 10
        assert c2.get("y") == 20

    def test_ttl_survives_new_instance(self, tmp_path):
        cache_dir = tmp_path / "shared"
        c1 = FileBasedCache(cache_dir=cache_dir)
        c1.set("expiring", "v", ttl=1)
        time.sleep(1.1)
        c2 = FileBasedCache(cache_dir=cache_dir)
        assert c2.get("expiring") is None


# ===========================================================================
# Edge cases
# ===========================================================================


@pytest.mark.unit
class TestFileBasedCacheEdgeCases:
    """Edge case and boundary tests."""

    def test_empty_string_key(self, cache):
        cache.set("", "empty key")
        assert cache.get("") == "empty key"

    def test_key_with_special_characters(self, cache):
        key = "user:profile/settings?v=1&lang=en"
        cache.set(key, "special")
        assert cache.get(key) == "special"

    def test_large_value(self, cache):
        big = {"data": "x" * 100_000}
        cache.set("large", big)
        result = cache.get("large")
        assert result == big

    def test_boolean_value_true(self, cache):
        cache.set("flag", True)
        assert cache.get("flag") is True

    def test_boolean_value_false(self, cache):
        cache.set("flag", False)
        # key must exist even though value is falsy
        assert cache.exists("flag") is True

    def test_zero_integer_value(self, cache):
        cache.set("zero", 0)
        assert cache.get("zero") == 0
        assert cache.exists("zero") is True

    def test_different_keys_produce_different_files(self, tmp_path):
        cache = FileBasedCache(cache_dir=tmp_path / "c")
        cache.set("key_alpha", 1)
        cache.set("key_beta", 2)
        files = list((tmp_path / "c").glob("*.cache"))
        assert len(files) == 2
