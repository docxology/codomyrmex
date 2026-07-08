"""
Unit tests for cache.exceptions — Zero-Mock compliant.

Covers: CacheError (base), CacheExpiredError, CacheFullError,
CacheConnectionError, CacheKeyError, CacheSerializationError,
CacheInvalidationError — context field storage, inheritance, raise/catch.
"""

import pytest

from codomyrmex.cache.exceptions import (
    CacheConnectionError,
    CacheError,
    CacheExpiredError,
    CacheFullError,
    CacheInvalidationError,
    CacheKeyError,
    CacheSerializationError,
)
from codomyrmex.exceptions import CodomyrmexError

# ── CacheError ─────────────────────────────────────────────────────────


@pytest.mark.unit
class TestCacheError:
    def test_is_codomyrmex_error(self):
        e = CacheError("base error")
        assert isinstance(e, CodomyrmexError)

    def test_message_stored(self):
        e = CacheError("something failed")
        assert "something failed" in str(e)

    def test_cache_name_stored_in_context(self):
        e = CacheError("err", cache_name="my_cache")
        assert e.context["cache_name"] == "my_cache"

    def test_backend_stored_in_context(self):
        e = CacheError("err", backend="redis")
        assert e.context["backend"] == "redis"

    def test_cache_name_none_not_in_context(self):
        e = CacheError("err")
        assert "cache_name" not in e.context

    def test_backend_none_not_in_context(self):
        e = CacheError("err")
        assert "backend" not in e.context

    def test_both_fields_stored(self):
        e = CacheError("err", cache_name="c", backend="memory")
        assert e.context["cache_name"] == "c"
        assert e.context["backend"] == "memory"

    def test_raise_and_catch(self):
        with pytest.raises(CacheError, match="test"):
            raise CacheError("test")

    def test_catch_as_base_error(self):
        with pytest.raises(CodomyrmexError):
            raise CacheError("test")


# ── CacheExpiredError ──────────────────────────────────────────────────


@pytest.mark.unit
class TestCacheExpiredError:
    def test_is_cache_error(self):
        e = CacheExpiredError("expired")
        assert isinstance(e, CacheError)

    def test_key_stored_when_provided(self):
        e = CacheExpiredError("expired", key="user:1")
        assert e.context["key"] == "user:1"

    def test_key_not_stored_when_none(self):
        e = CacheExpiredError("expired")
        assert "key" not in e.context

    def test_expired_at_stored_when_provided(self):
        e = CacheExpiredError("expired", expired_at=1234567890.5)
        assert e.context["expired_at"] == pytest.approx(1234567890.5)

    def test_expired_at_zero_stored(self):
        e = CacheExpiredError("expired", expired_at=0.0)
        assert "expired_at" in e.context
        assert e.context["expired_at"] == pytest.approx(0.0)

    def test_ttl_stored_when_provided(self):
        e = CacheExpiredError("expired", ttl=300.0)
        assert e.context["ttl"] == pytest.approx(300.0)

    def test_ttl_zero_stored(self):
        e = CacheExpiredError("expired", ttl=0.0)
        assert "ttl" in e.context

    def test_all_fields_stored(self):
        e = CacheExpiredError("expired", key="k", expired_at=100.0, ttl=60.0)
        assert e.context["key"] == "k"
        assert e.context["expired_at"] == pytest.approx(100.0)
        assert e.context["ttl"] == pytest.approx(60.0)

    def test_raise_and_catch(self):
        with pytest.raises(CacheExpiredError):
            raise CacheExpiredError("entry expired", key="session:abc")


# ── CacheFullError ─────────────────────────────────────────────────────


@pytest.mark.unit
class TestCacheFullError:
    def test_is_cache_error(self):
        e = CacheFullError("cache full")
        assert isinstance(e, CacheError)

    def test_max_size_stored(self):
        e = CacheFullError("full", max_size=1000)
        assert e.context["max_size"] == 1000

    def test_max_size_zero_stored(self):
        e = CacheFullError("full", max_size=0)
        assert "max_size" in e.context
        assert e.context["max_size"] == 0

    def test_current_size_stored(self):
        e = CacheFullError("full", current_size=999)
        assert e.context["current_size"] == 999

    def test_required_space_stored(self):
        e = CacheFullError("full", required_space=5)
        assert e.context["required_space"] == 5

    def test_none_fields_not_in_context(self):
        e = CacheFullError("full")
        assert "max_size" not in e.context
        assert "current_size" not in e.context
        assert "required_space" not in e.context

    def test_all_fields_stored(self):
        e = CacheFullError("full", max_size=100, current_size=100, required_space=1)
        assert e.context["max_size"] == 100
        assert e.context["current_size"] == 100
        assert e.context["required_space"] == 1


# ── CacheConnectionError ───────────────────────────────────────────────


@pytest.mark.unit
class TestCacheConnectionError:
    def test_is_cache_error(self):
        e = CacheConnectionError("conn failed")
        assert isinstance(e, CacheError)

    def test_host_stored(self):
        e = CacheConnectionError("fail", host="redis.example.com")
        assert e.context["host"] == "redis.example.com"

    def test_host_not_stored_when_none(self):
        e = CacheConnectionError("fail")
        assert "host" not in e.context

    def test_port_stored(self):
        e = CacheConnectionError("fail", port=6379)
        assert e.context["port"] == 6379

    def test_port_zero_stored(self):
        e = CacheConnectionError("fail", port=0)
        assert "port" in e.context
        assert e.context["port"] == 0

    def test_connection_timeout_stored(self):
        e = CacheConnectionError("fail", connection_timeout=5.0)
        assert e.context["connection_timeout"] == pytest.approx(5.0)

    def test_all_fields_stored(self):
        e = CacheConnectionError("fail", host="h", port=6379, connection_timeout=2.5)
        assert e.context["host"] == "h"
        assert e.context["port"] == 6379
        assert e.context["connection_timeout"] == pytest.approx(2.5)


# ── CacheKeyError ──────────────────────────────────────────────────────


@pytest.mark.unit
class TestCacheKeyError:
    def test_is_cache_error(self):
        e = CacheKeyError("bad key")
        assert isinstance(e, CacheError)

    def test_key_stored(self):
        e = CacheKeyError("bad key", key="invalid::key")
        assert e.context["key"] == "invalid::key"

    def test_key_not_stored_when_none(self):
        e = CacheKeyError("bad key")
        assert "key" not in e.context

    def test_reason_stored(self):
        e = CacheKeyError("bad key", reason="contains illegal chars")
        assert e.context["reason"] == "contains illegal chars"

    def test_reason_not_stored_when_none(self):
        e = CacheKeyError("bad key")
        assert "reason" not in e.context

    def test_both_fields(self):
        e = CacheKeyError("bad key", key="k", reason="too long")
        assert e.context["key"] == "k"
        assert e.context["reason"] == "too long"

    def test_raise_and_catch(self):
        with pytest.raises(CacheKeyError):
            raise CacheKeyError("no such key", key="missing:123")


# ── CacheSerializationError ────────────────────────────────────────────


@pytest.mark.unit
class TestCacheSerializationError:
    def test_is_cache_error(self):
        e = CacheSerializationError("ser failed")
        assert isinstance(e, CacheError)

    def test_key_stored(self):
        e = CacheSerializationError("fail", key="obj:42")
        assert e.context["key"] == "obj:42"

    def test_value_type_stored(self):
        e = CacheSerializationError("fail", value_type="MyClass")
        assert e.context["value_type"] == "MyClass"

    def test_neither_field_when_none(self):
        e = CacheSerializationError("fail")
        assert "key" not in e.context
        assert "value_type" not in e.context

    def test_both_fields(self):
        e = CacheSerializationError("fail", key="k", value_type="set")
        assert e.context["key"] == "k"
        assert e.context["value_type"] == "set"


# ── CacheInvalidationError ────────────────────────────────────────────


@pytest.mark.unit
class TestCacheInvalidationError:
    def test_is_cache_error(self):
        e = CacheInvalidationError("inv failed")
        assert isinstance(e, CacheError)

    def test_pattern_stored(self):
        e = CacheInvalidationError("fail", pattern="user:*")
        assert e.context["pattern"] == "user:*"

    def test_pattern_not_stored_when_none(self):
        e = CacheInvalidationError("fail")
        assert "pattern" not in e.context

    def test_keys_affected_stored(self):
        e = CacheInvalidationError("fail", keys_affected=50)
        assert e.context["keys_affected"] == 50

    def test_keys_affected_zero_stored(self):
        e = CacheInvalidationError("fail", keys_affected=0)
        assert "keys_affected" in e.context
        assert e.context["keys_affected"] == 0

    def test_keys_affected_not_stored_when_none(self):
        e = CacheInvalidationError("fail")
        assert "keys_affected" not in e.context

    def test_both_fields(self):
        e = CacheInvalidationError("fail", pattern="*", keys_affected=100)
        assert e.context["pattern"] == "*"
        assert e.context["keys_affected"] == 100

    def test_raise_and_catch(self):
        with pytest.raises(CacheInvalidationError):
            raise CacheInvalidationError("failed to invalidate", pattern="session:*")
