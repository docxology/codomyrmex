"""Zero-mock unit tests for NamespacedCache.

Zero-Mock Policy: no unittest.mock, MagicMock, monkeypatch, or pytest-mock.
"""

from __future__ import annotations

import pytest

from codomyrmex.cache.backends.in_memory import InMemoryCache
from codomyrmex.cache.namespaced import NamespacedCache


@pytest.fixture
def base_cache():
    return InMemoryCache()


@pytest.fixture
def ns_cache(base_cache):
    return NamespacedCache(base_cache, "ns")


@pytest.mark.unit
class TestNamespacedCacheExtended:
    """Zero-mock tests for NamespacedCache."""

    def test_set_prefixes_key(self, base_cache, ns_cache):
        ns_cache.set("k", "v")
        assert base_cache.get("ns:k") == "v"
        assert ns_cache.get("k") == "v"

    def test_delete_prefixes_key(self, base_cache, ns_cache):
        base_cache.set("ns:k", "v")
        assert ns_cache.delete("k") is True
        assert base_cache.exists("ns:k") is False

    def test_exists_prefixes_key(self, base_cache, ns_cache):
        base_cache.set("ns:k", "v")
        assert ns_cache.exists("k") is True
        assert ns_cache.exists("other") is False

    def test_delete_pattern_prefixes_pattern(self, base_cache, ns_cache):
        ns_cache.set("user:1", "a")
        ns_cache.set("user:2", "b")
        ns_cache.set("other", "c")

        count = ns_cache.delete_pattern("user:*")
        assert count == 2
        assert ns_cache.get("user:1") is None
        assert ns_cache.get("other") == "c"

    def test_clear_removes_only_namespace(self, base_cache, ns_cache):
        ns_cache.set("k1", "v1")
        base_cache.set("other:k2", "v2")

        ns_cache.clear()
        assert ns_cache.get("k1") is None
        assert base_cache.get("other:k2") == "v2"

    def test_nested_namespaces(self, base_cache):
        ns1 = NamespacedCache(base_cache, "outer")
        ns2 = NamespacedCache(ns1, "inner")

        ns2.set("k", "v")
        assert base_cache.get("outer:inner:k") == "v"
        assert ns2.get("k") == "v"
        assert ns1.get("inner:k") == "v"

    def test_namespaced_file_based_cache(self, tmp_path):
        from codomyrmex.cache.backends.file_based import FileBasedCache

        fb_cache = FileBasedCache(cache_dir=tmp_path / "fb")
        ns_fb = NamespacedCache(fb_cache, "app")

        ns_fb.set("config", {"theme": "dark"})
        assert ns_fb.get("config") == {"theme": "dark"}
        assert fb_cache.exists("app:config") is True

        ns_fb.delete_pattern("*")
        assert ns_fb.get("config") is None
