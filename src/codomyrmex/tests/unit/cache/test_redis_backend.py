"""Zero-mock unit tests for RedisCache backend.

Tests RedisCache with real Redis if available, otherwise skips.
Zero-Mock Policy: no unittest.mock, MagicMock, monkeypatch, or pytest-mock.
"""

from __future__ import annotations

import os

import pytest

from codomyrmex.cache.backends.redis_backend import REDIS_AVAILABLE, RedisCache


def is_redis_running():
    if not REDIS_AVAILABLE:
        return False
    try:
        import redis

        host = os.getenv("REDIS_HOST", "localhost")
        port = int(os.getenv("REDIS_PORT", "6379"))
        client = redis.Redis(host=host, port=port, socket_connect_timeout=1)
        return client.ping()
    except Exception:
        return False


skip_if_no_redis = pytest.mark.skipif(
    not is_redis_running(), reason="Redis server not running or redis package missing"
)


@pytest.fixture
def redis_cache():
    cache = RedisCache()
    cache.clear()
    yield cache
    cache.clear()


@pytest.mark.unit
@skip_if_no_redis
class TestRedisCache:
    """Zero-mock tests for RedisCache."""

    def test_set_and_get(self, redis_cache):
        assert redis_cache.set("k1", "v1") is True
        assert redis_cache.get("k1") == "v1"

    def test_get_missing(self, redis_cache):
        assert redis_cache.get("missing") is None

    def test_delete(self, redis_cache):
        redis_cache.set("k2", "v2")
        assert redis_cache.delete("k2") is True
        assert redis_cache.get("k2") is None

    def test_exists(self, redis_cache):
        redis_cache.set("k3", "v3")
        assert redis_cache.exists("k3") is True
        assert redis_cache.exists("missing") is False

    def test_clear(self, redis_cache):
        redis_cache.set("a", 1)
        redis_cache.set("b", 2)
        assert redis_cache.clear() is True
        assert redis_cache.exists("a") is False
        assert redis_cache.exists("b") is False

    def test_stats(self, redis_cache):
        redis_cache.set("s1", "v1")
        redis_cache.get("s1")
        stats = redis_cache.stats
        assert stats.total_requests >= 1
        # Redis internal stats might not be 100% predictable in tests depending on shared environment
        # but size should be.
        assert redis_cache.stats.size >= 1

    def test_ttl(self, redis_cache):
        import time

        redis_cache.set("temp", "val", ttl=1)
        assert redis_cache.get("temp") == "val"
        time.sleep(1.1)
        assert redis_cache.get("temp") is None
