"""Comprehensive unit tests for APIKeyManager and APIKey.

Covers:
- APIKey dataclass: construction, is_expired, is_valid properties
- APIKeyManager: generate, validate, revoke, rotate, list_keys,
  cleanup_expired, active_count, total_count
- Wrapper methods: generate_api_key, validate_api_key, revoke_api_key
- Edge cases: custom prefix, TTL expiry, rate-limit tracking, label propagation
"""

from __future__ import annotations

import time

import pytest

from codomyrmex.auth.providers.api_key_manager import APIKey, APIKeyManager


# ==============================================================================
# APIKey Dataclass Tests
# ==============================================================================


@pytest.mark.unit
class TestAPIKey:
    """Tests for the APIKey dataclass and its properties."""

    def test_apikey_construction_defaults(self):
        """APIKey constructed with only required fields has sane defaults."""
        key = APIKey(key="k1", user_id="alice", permissions=["read"])
        assert key.key == "k1"
        assert key.user_id == "alice"
        assert key.permissions == ["read"]
        assert key.expires_at is None
        assert key.rate_limit == 0
        assert key.label == ""
        assert key.revoked is False
        assert key.request_count == 0
        assert isinstance(key.created_at, float)

    def test_apikey_is_expired_false_when_no_expiry(self):
        """A key with no expires_at is never expired."""
        key = APIKey(key="k", user_id="u", permissions=[])
        assert key.is_expired is False

    def test_apikey_is_expired_false_when_future(self):
        """A key with a future expires_at is not expired."""
        key = APIKey(key="k", user_id="u", permissions=[], expires_at=time.time() + 3600)
        assert key.is_expired is False

    def test_apikey_is_expired_true_when_past(self):
        """A key with a past expires_at is expired."""
        key = APIKey(key="k", user_id="u", permissions=[], expires_at=time.time() - 1)
        assert key.is_expired is True

    def test_apikey_is_valid_when_not_revoked_and_not_expired(self):
        """is_valid is True for a fresh, non-expired key."""
        key = APIKey(key="k", user_id="u", permissions=[])
        assert key.is_valid is True

    def test_apikey_is_valid_false_when_revoked(self):
        """is_valid is False for a revoked key."""
        key = APIKey(key="k", user_id="u", permissions=[], revoked=True)
        assert key.is_valid is False

    def test_apikey_is_valid_false_when_expired(self):
        """is_valid is False for an expired key."""
        key = APIKey(key="k", user_id="u", permissions=[], expires_at=time.time() - 1)
        assert key.is_valid is False

    def test_apikey_is_valid_false_when_revoked_and_expired(self):
        """is_valid is False when both revoked and expired."""
        key = APIKey(
            key="k", user_id="u", permissions=[],
            expires_at=time.time() - 1, revoked=True,
        )
        assert key.is_valid is False


# ==============================================================================
# APIKeyManager Core Tests
# ==============================================================================


@pytest.mark.unit
class TestAPIKeyManagerGenerate:
    """Tests for key generation via the generate() method."""

    def test_generate_returns_string_with_prefix(self):
        """Generated key starts with the configured prefix."""
        mgr = APIKeyManager(prefix="test")
        key = mgr.generate("alice")
        assert key.startswith("test_")

    def test_generate_default_prefix(self):
        """Default prefix is 'codomyrmex'."""
        mgr = APIKeyManager()
        key = mgr.generate("alice")
        assert key.startswith("codomyrmex_")

    def test_generate_default_permissions(self):
        """Omitting permissions yields ['read']."""
        mgr = APIKeyManager()
        key_str = mgr.generate("alice")
        info = mgr.validate(key_str)
        assert info is not None
        assert info.permissions == ["read"]

    def test_generate_custom_permissions(self):
        """Explicit permissions are stored."""
        mgr = APIKeyManager()
        key_str = mgr.generate("alice", permissions=["write", "admin"])
        info = mgr.validate(key_str)
        assert info is not None
        assert info.permissions == ["write", "admin"]

    def test_generate_with_ttl(self):
        """Key generated with ttl_seconds has a future expires_at."""
        mgr = APIKeyManager()
        key_str = mgr.generate("alice", ttl_seconds=3600)
        info = mgr.validate(key_str)
        assert info is not None
        assert info.expires_at is not None
        assert info.expires_at > time.time()

    def test_generate_without_ttl_has_no_expiry(self):
        """Key generated without ttl_seconds has expires_at=None."""
        mgr = APIKeyManager()
        key_str = mgr.generate("alice")
        info = mgr.validate(key_str)
        assert info is not None
        assert info.expires_at is None

    def test_generate_with_rate_limit(self):
        """rate_limit is stored on the key."""
        mgr = APIKeyManager()
        key_str = mgr.generate("alice", rate_limit=100)
        info = mgr.validate(key_str)
        assert info is not None
        assert info.rate_limit == 100

    def test_generate_with_label(self):
        """label is stored on the key."""
        mgr = APIKeyManager()
        key_str = mgr.generate("alice", label="production-key")
        info = mgr.validate(key_str)
        assert info is not None
        assert info.label == "production-key"

    def test_generate_unique_keys(self):
        """Multiple generate() calls produce unique key strings."""
        mgr = APIKeyManager()
        keys = {mgr.generate("alice") for _ in range(20)}
        assert len(keys) == 20


@pytest.mark.unit
class TestAPIKeyManagerValidate:
    """Tests for key validation."""

    def test_validate_returns_apikey_for_valid_key(self):
        """validate() returns an APIKey object for a valid key."""
        mgr = APIKeyManager()
        key_str = mgr.generate("alice")
        result = mgr.validate(key_str)
        assert isinstance(result, APIKey)
        assert result.user_id == "alice"

    def test_validate_returns_none_for_unknown_key(self):
        """validate() returns None for an unregistered key string."""
        mgr = APIKeyManager()
        assert mgr.validate("unknown_key_abc") is None

    def test_validate_increments_request_count(self):
        """Each successful validate() call increments request_count."""
        mgr = APIKeyManager()
        key_str = mgr.generate("alice")
        mgr.validate(key_str)
        mgr.validate(key_str)
        info = mgr.validate(key_str)
        assert info is not None
        assert info.request_count == 3

    def test_validate_returns_none_for_revoked_key(self):
        """validate() returns None after the key is revoked."""
        mgr = APIKeyManager()
        key_str = mgr.generate("alice")
        mgr.revoke(key_str)
        assert mgr.validate(key_str) is None

    def test_validate_returns_none_for_expired_key(self):
        """validate() returns None for a key whose TTL has elapsed."""
        mgr = APIKeyManager()
        key_str = mgr.generate("alice", ttl_seconds=0.1)
        time.sleep(0.2)
        assert mgr.validate(key_str) is None


@pytest.mark.unit
class TestAPIKeyManagerRevoke:
    """Tests for key revocation."""

    def test_revoke_existing_key_returns_true(self):
        """revoke() returns True for a known key."""
        mgr = APIKeyManager()
        key_str = mgr.generate("alice")
        assert mgr.revoke(key_str) is True

    def test_revoke_unknown_key_returns_false(self):
        """revoke() returns False for an unknown key."""
        mgr = APIKeyManager()
        assert mgr.revoke("nonexistent_key") is False

    def test_revoke_makes_key_invalid(self):
        """After revoke(), the key's is_valid is False."""
        mgr = APIKeyManager()
        key_str = mgr.generate("alice")
        mgr.revoke(key_str)
        assert mgr.validate(key_str) is None


@pytest.mark.unit
class TestAPIKeyManagerRotate:
    """Tests for key rotation."""

    def test_rotate_returns_new_key_string(self):
        """rotate() returns a new key string different from the old one."""
        mgr = APIKeyManager()
        old_key = mgr.generate("alice", permissions=["read", "write"], rate_limit=50)
        new_key = mgr.rotate(old_key)
        assert new_key is not None
        assert new_key != old_key

    def test_rotate_revokes_old_key(self):
        """After rotate(), the old key is revoked."""
        mgr = APIKeyManager()
        old_key = mgr.generate("alice")
        mgr.rotate(old_key)
        assert mgr.validate(old_key) is None

    def test_rotate_preserves_user_and_permissions(self):
        """The new rotated key retains user_id and permissions."""
        mgr = APIKeyManager()
        old_key = mgr.generate("alice", permissions=["write", "admin"])
        new_key = mgr.rotate(old_key)
        assert new_key is not None
        info = mgr.validate(new_key)
        assert info is not None
        assert info.user_id == "alice"
        assert info.permissions == ["write", "admin"]

    def test_rotate_preserves_rate_limit(self):
        """The new rotated key retains the original rate_limit."""
        mgr = APIKeyManager()
        old_key = mgr.generate("alice", rate_limit=200)
        new_key = mgr.rotate(old_key)
        assert new_key is not None
        info = mgr.validate(new_key)
        assert info is not None
        assert info.rate_limit == 200

    def test_rotate_appends_rotated_label(self):
        """The rotated key's label indicates it was rotated."""
        mgr = APIKeyManager()
        old_key = mgr.generate("alice", label="prod")
        new_key = mgr.rotate(old_key)
        assert new_key is not None
        info = mgr.validate(new_key)
        assert info is not None
        assert "rotated" in info.label

    def test_rotate_unknown_key_returns_none(self):
        """rotate() returns None for an unknown key."""
        mgr = APIKeyManager()
        assert mgr.rotate("nonexistent") is None

    def test_rotate_with_ttl(self):
        """rotate() can apply a new TTL to the rotated key."""
        mgr = APIKeyManager()
        old_key = mgr.generate("alice")
        new_key = mgr.rotate(old_key, ttl_seconds=7200)
        assert new_key is not None
        info = mgr.validate(new_key)
        assert info is not None
        assert info.expires_at is not None
        assert info.expires_at > time.time()


@pytest.mark.unit
class TestAPIKeyManagerListKeys:
    """Tests for list_keys()."""

    def test_list_keys_returns_all_active(self):
        """list_keys() returns all non-revoked keys by default."""
        mgr = APIKeyManager()
        mgr.generate("alice")
        mgr.generate("bob")
        keys = mgr.list_keys()
        assert len(keys) == 2

    def test_list_keys_filters_by_user_id(self):
        """list_keys(user_id=...) returns only that user's keys."""
        mgr = APIKeyManager()
        mgr.generate("alice")
        mgr.generate("bob")
        mgr.generate("alice")
        keys = mgr.list_keys(user_id="alice")
        assert len(keys) == 2
        assert all(k.user_id == "alice" for k in keys)

    def test_list_keys_excludes_revoked_by_default(self):
        """Revoked keys are excluded when include_revoked=False."""
        mgr = APIKeyManager()
        k1 = mgr.generate("alice")
        mgr.generate("alice")
        mgr.revoke(k1)
        keys = mgr.list_keys(user_id="alice")
        assert len(keys) == 1

    def test_list_keys_includes_revoked_when_requested(self):
        """Revoked keys are included when include_revoked=True."""
        mgr = APIKeyManager()
        k1 = mgr.generate("alice")
        mgr.generate("alice")
        mgr.revoke(k1)
        keys = mgr.list_keys(user_id="alice", include_revoked=True)
        assert len(keys) == 2

    def test_list_keys_empty_manager(self):
        """list_keys() returns empty list for fresh manager."""
        mgr = APIKeyManager()
        assert mgr.list_keys() == []


@pytest.mark.unit
class TestAPIKeyManagerCleanup:
    """Tests for cleanup_expired() and count properties."""

    def test_cleanup_removes_revoked_keys(self):
        """cleanup_expired() removes revoked keys and returns the count."""
        mgr = APIKeyManager()
        k1 = mgr.generate("alice")
        mgr.generate("bob")
        mgr.revoke(k1)
        removed = mgr.cleanup_expired()
        assert removed == 1
        assert mgr.total_count == 1

    def test_cleanup_removes_expired_keys(self):
        """cleanup_expired() removes expired keys."""
        mgr = APIKeyManager()
        mgr.generate("alice", ttl_seconds=0.05)
        mgr.generate("bob")
        time.sleep(0.1)
        removed = mgr.cleanup_expired()
        assert removed == 1
        assert mgr.total_count == 1

    def test_cleanup_returns_zero_when_all_valid(self):
        """cleanup_expired() returns 0 when all keys are valid."""
        mgr = APIKeyManager()
        mgr.generate("alice")
        mgr.generate("bob")
        assert mgr.cleanup_expired() == 0

    def test_active_count_reflects_valid_keys(self):
        """active_count excludes revoked and expired keys."""
        mgr = APIKeyManager()
        mgr.generate("alice")
        k2 = mgr.generate("bob")
        mgr.generate("carol", ttl_seconds=0.05)
        mgr.revoke(k2)
        time.sleep(0.1)
        assert mgr.active_count == 1

    def test_total_count_includes_all_keys(self):
        """total_count includes revoked and expired keys."""
        mgr = APIKeyManager()
        mgr.generate("alice")
        k2 = mgr.generate("bob")
        mgr.revoke(k2)
        assert mgr.total_count == 2


# ==============================================================================
# Wrapper Method Tests
# ==============================================================================


@pytest.mark.unit
class TestAPIKeyManagerWrappers:
    """Tests for the convenience wrapper methods."""

    def test_generate_api_key_delegates_to_generate(self):
        """generate_api_key() produces a valid key via generate()."""
        mgr = APIKeyManager()
        key_str = mgr.generate_api_key("alice")
        assert key_str.startswith("codomyrmex_")
        assert mgr.validate(key_str) is not None

    def test_validate_api_key_returns_dict(self):
        """validate_api_key() returns a dict with user_id and permissions."""
        mgr = APIKeyManager()
        key_str = mgr.generate_api_key("alice", permissions=["write"])
        result = mgr.validate_api_key(key_str)
        assert isinstance(result, dict)
        assert result["user_id"] == "alice"
        assert result["permissions"] == ["write"]

    def test_validate_api_key_returns_none_for_invalid(self):
        """validate_api_key() returns None for an unknown key."""
        mgr = APIKeyManager()
        assert mgr.validate_api_key("bogus") is None

    def test_revoke_api_key_delegates_to_revoke(self):
        """revoke_api_key() revokes the key."""
        mgr = APIKeyManager()
        key_str = mgr.generate_api_key("alice")
        assert mgr.revoke_api_key(key_str) is True
        assert mgr.validate_api_key(key_str) is None
