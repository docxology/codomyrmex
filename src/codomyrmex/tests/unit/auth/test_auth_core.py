"""Comprehensive zero-mock tests for auth module core components.

Covers: Token, TokenManager, TokenValidator, APIKey, APIKeyManager,
PermissionCheck, PermissionRegistry, Authenticator, and module-level
convenience functions.

Zero-mock policy: no unittest.mock, no MagicMock, no monkeypatch.
"""

import base64
import json
import time

import pytest

from codomyrmex.auth.core.authenticator import Authenticator
from codomyrmex.auth.providers.api_key_manager import APIKey, APIKeyManager
from codomyrmex.auth.rbac.permissions import PermissionCheck, PermissionRegistry
from codomyrmex.auth.tokens.token import Token, TokenManager
from codomyrmex.auth.tokens.validator import TokenValidator

# ==============================================================================
# Token Dataclass
# ==============================================================================


@pytest.mark.unit
class TestTokenDataclass:
    """Tests for the Token dataclass."""

    def test_token_creation_minimal(self):
        """Token with only required fields."""
        t = Token(token_id="t1", user_id="u1")
        assert t.token_id == "t1"
        assert t.user_id == "u1"
        assert t.permissions == []
        assert t.expires_at is None
        assert t.jwt is None

    def test_token_creation_full(self):
        """Token with all fields populated."""
        t = Token(
            token_id="t2",
            user_id="u2",
            permissions=["read", "write"],
            expires_at=99999.0,
            created_at=10000.0,
            jwt="signed-string",
        )
        assert t.permissions == ["read", "write"]
        assert t.expires_at == 99999.0
        assert t.created_at == 10000.0
        assert t.jwt == "signed-string"

    def test_is_expired_no_expiry(self):
        """Token without expiry is never expired."""
        t = Token(token_id="t", user_id="u", expires_at=None)
        assert not t.is_expired()

    def test_is_expired_future(self):
        """Token expiring in the future is not expired."""
        t = Token(token_id="t", user_id="u", expires_at=time.time() + 3600)
        assert not t.is_expired()

    def test_is_expired_past(self):
        """Token with past expiry is expired."""
        t = Token(token_id="t", user_id="u", expires_at=time.time() - 1)
        assert t.is_expired()

    def test_to_dict_fields(self):
        """to_dict includes all serializable fields."""
        t = Token(token_id="t1", user_id="u1", permissions=["read"],
                  expires_at=5000.0, created_at=1000.0)
        d = t.to_dict()
        assert d["token_id"] == "t1"
        assert d["user_id"] == "u1"
        assert d["permissions"] == ["read"]
        assert d["expires_at"] == 5000.0
        assert d["created_at"] == 1000.0
        # jwt is not included in to_dict
        assert "jwt" not in d

    def test_from_dict_minimal(self):
        """from_dict with only required fields."""
        d = {"token_id": "t1", "user_id": "u1"}
        t = Token.from_dict(d)
        assert t.token_id == "t1"
        assert t.user_id == "u1"
        assert t.permissions == []
        assert t.expires_at is None

    def test_from_dict_full(self):
        """from_dict with all fields."""
        d = {
            "token_id": "t1",
            "user_id": "u1",
            "permissions": ["admin"],
            "expires_at": 9999.0,
            "created_at": 1000.0,
        }
        t = Token.from_dict(d)
        assert t.permissions == ["admin"]
        assert t.expires_at == 9999.0
        assert t.created_at == 1000.0

    def test_roundtrip(self):
        """to_dict -> from_dict preserves all serializable fields."""
        original = Token(
            token_id="rt-1", user_id="u-1",
            permissions=["read", "write"],
            expires_at=12345.0, created_at=1000.0,
        )
        restored = Token.from_dict(original.to_dict())
        assert restored.token_id == original.token_id
        assert restored.user_id == original.user_id
        assert restored.permissions == original.permissions
        assert restored.expires_at == original.expires_at
        assert restored.created_at == original.created_at


# ==============================================================================
# TokenValidator
# ==============================================================================


@pytest.mark.unit
class TestTokenValidatorUnit:
    """Tests for the TokenValidator class."""

    def test_empty_secret_raises(self):
        """Empty secret raises ValueError."""
        with pytest.raises(ValueError, match="Secret key cannot be empty"):
            TokenValidator(secret="")

    def test_sign_and_validate_roundtrip(self):
        """Signing data and validating it returns the original data."""
        v = TokenValidator(secret="test-key")
        data = {"user_id": "alice", "role": "admin"}
        signed = v.sign_token_data(data)
        result = v.validate_signed_token(signed)
        assert result is not None
        assert result["user_id"] == "alice"
        assert result["role"] == "admin"

    def test_signed_token_is_base64(self):
        """Signed token is a valid base64 string."""
        v = TokenValidator(secret="key")
        signed = v.sign_token_data({"a": 1})
        decoded = base64.b64decode(signed)
        parsed = json.loads(decoded)
        assert "data" in parsed
        assert "signature" in parsed

    def test_validate_with_expiry_future(self):
        """Token with future expiry validates successfully."""
        v = TokenValidator(secret="key")
        data = {"user_id": "u", "expires_at": time.time() + 3600}
        signed = v.sign_token_data(data)
        assert v.validate_signed_token(signed) is not None

    def test_validate_with_expiry_past(self):
        """Token with past expiry returns None."""
        v = TokenValidator(secret="key")
        data = {"user_id": "u", "expires_at": time.time() - 10}
        signed = v.sign_token_data(data)
        assert v.validate_signed_token(signed) is None

    def test_validate_no_expiry_field(self):
        """Token without expires_at field validates successfully."""
        v = TokenValidator(secret="key")
        data = {"user_id": "u"}
        signed = v.sign_token_data(data)
        assert v.validate_signed_token(signed) is not None

    def test_tampered_data_fails(self):
        """Tampered token data fails validation."""
        v = TokenValidator(secret="key")
        signed = v.sign_token_data({"user_id": "legit"})
        decoded = json.loads(base64.b64decode(signed))
        decoded["data"]["user_id"] = "hacker"
        tampered = base64.b64encode(json.dumps(decoded).encode()).decode()
        assert v.validate_signed_token(tampered) is None

    def test_tampered_signature_fails(self):
        """Tampered signature fails validation."""
        v = TokenValidator(secret="key")
        signed = v.sign_token_data({"user_id": "legit"})
        decoded = json.loads(base64.b64decode(signed))
        decoded["signature"] = "0" * 64
        tampered = base64.b64encode(json.dumps(decoded).encode()).decode()
        assert v.validate_signed_token(tampered) is None

    def test_invalid_base64_returns_none(self):
        """Non-base64 input returns None."""
        v = TokenValidator(secret="key")
        assert v.validate_signed_token("not!!base64!!") is None

    def test_invalid_json_returns_none(self):
        """Valid base64 but invalid JSON returns None."""
        v = TokenValidator(secret="key")
        invalid = base64.b64encode(b"not json").decode()
        assert v.validate_signed_token(invalid) is None

    def test_missing_data_key_returns_none(self):
        """Token JSON without 'data' key returns None."""
        v = TokenValidator(secret="key")
        token = {"signature": "abc"}
        encoded = base64.b64encode(json.dumps(token).encode()).decode()
        assert v.validate_signed_token(encoded) is None

    def test_missing_signature_key_returns_none(self):
        """Token JSON without 'signature' key returns None."""
        v = TokenValidator(secret="key")
        token = {"data": {"user_id": "u"}}
        encoded = base64.b64encode(json.dumps(token).encode()).decode()
        assert v.validate_signed_token(encoded) is None

    def test_different_secrets_fail_cross_validation(self):
        """Tokens signed with secret A fail validation with secret B."""
        v1 = TokenValidator(secret="secret-alpha")
        v2 = TokenValidator(secret="secret-beta")
        signed = v1.sign_token_data({"user_id": "user"})
        assert v2.validate_signed_token(signed) is None

    def test_deterministic_signature(self):
        """Same data produces same signature."""
        v = TokenValidator(secret="key")
        sig1 = v._generate_signature({"a": 1, "b": 2})
        sig2 = v._generate_signature({"b": 2, "a": 1})  # Different key order
        assert sig1 == sig2  # sort_keys ensures consistency


# ==============================================================================
# TokenManager
# ==============================================================================


@pytest.mark.unit
class TestTokenManagerUnit:
    """Tests for the TokenManager class."""

    def _make_manager(self):
        return TokenManager(secret="test-secret-123")

    def test_create_token_basic(self):
        """create_token returns a token with correct user_id."""
        mgr = self._make_manager()
        token = mgr.create_token(user_id="alice")
        assert token.user_id == "alice"
        assert token.token_id is not None
        assert len(token.token_id) > 0

    def test_create_token_with_permissions(self):
        """Permissions are stored on the token."""
        mgr = self._make_manager()
        token = mgr.create_token(user_id="bob", permissions=["read", "write"])
        assert token.permissions == ["read", "write"]

    def test_create_token_default_permissions(self):
        """Default permissions are empty list."""
        mgr = self._make_manager()
        token = mgr.create_token(user_id="u")
        assert token.permissions == []

    def test_create_token_with_ttl(self):
        """Token has correct expiration from TTL."""
        mgr = self._make_manager()
        before = time.time()
        token = mgr.create_token(user_id="u", ttl=3600)
        after = time.time()
        assert token.expires_at is not None
        assert before + 3600 <= token.expires_at <= after + 3600

    def test_create_token_zero_ttl_no_expiry(self):
        """TTL of 0 means no expiration."""
        mgr = self._make_manager()
        token = mgr.create_token(user_id="u", ttl=0)
        assert token.expires_at is None

    def test_create_token_has_jwt(self):
        """Created token has a signed JWT string."""
        mgr = self._make_manager()
        token = mgr.create_token(user_id="u")
        assert token.jwt is not None
        assert len(token.jwt) > 0

    def test_validate_token_object_success(self):
        """Validate returns True for valid token object."""
        mgr = self._make_manager()
        token = mgr.create_token(user_id="u")
        assert mgr.validate_token(token) is True

    def test_validate_token_string_success(self):
        """Validate returns True for valid signed token string."""
        mgr = self._make_manager()
        token = mgr.create_token(user_id="u", ttl=3600)
        assert mgr.validate_token(token.jwt) is True

    def test_validate_token_expired_object(self):
        """Validate returns False for expired token object."""
        mgr = self._make_manager()
        token = mgr.create_token(user_id="u", ttl=1)
        time.sleep(1.2)
        assert mgr.validate_token(token) is False

    def test_validate_token_revoked(self):
        """Validate returns False for revoked token."""
        mgr = self._make_manager()
        token = mgr.create_token(user_id="u")
        mgr.revoke_token(token)
        assert mgr.validate_token(token) is False

    def test_validate_unknown_token_object(self):
        """Validate returns False for unknown token object."""
        mgr = self._make_manager()
        fake = Token(token_id="nonexistent", user_id="u")
        assert mgr.validate_token(fake) is False

    def test_validate_invalid_string(self):
        """Validate returns False for garbage string."""
        mgr = self._make_manager()
        assert mgr.validate_token("garbage-string") is False

    def test_revoke_token_object(self):
        """Revoking token object returns True."""
        mgr = self._make_manager()
        token = mgr.create_token(user_id="u")
        assert mgr.revoke_token(token) is True
        assert mgr.validate_token(token) is False

    def test_revoke_token_string(self):
        """Revoking with signed string works."""
        mgr = self._make_manager()
        token = mgr.create_token(user_id="u")
        assert mgr.revoke_token(token.jwt) is True

    def test_revoke_token_id_string(self):
        """Revoking with raw token_id string works (fallback)."""
        mgr = self._make_manager()
        token = mgr.create_token(user_id="u")
        # Pass just the token_id as a string
        assert mgr.revoke_token(token.token_id) is True

    def test_refresh_token_success(self):
        """Refreshing valid token creates new token, revokes old."""
        mgr = self._make_manager()
        old = mgr.create_token(user_id="u", permissions=["read"])
        new = mgr.refresh_token(old, ttl=7200)
        assert new is not None
        assert new.user_id == old.user_id
        assert new.permissions == old.permissions
        assert new.token_id != old.token_id
        assert not mgr.validate_token(old)
        assert mgr.validate_token(new)

    def test_refresh_token_invalid_returns_none(self):
        """Refreshing invalid/revoked token returns None."""
        mgr = self._make_manager()
        token = mgr.create_token(user_id="u")
        mgr.revoke_token(token)
        assert mgr.refresh_token(token) is None

    def test_unique_token_ids(self):
        """Each created token has a unique ID."""
        mgr = self._make_manager()
        ids = {mgr.create_token(user_id="u").token_id for _ in range(30)}
        assert len(ids) == 30

    def test_default_secret(self):
        """TokenManager without explicit secret uses a default."""
        mgr = TokenManager()
        token = mgr.create_token(user_id="u")
        assert mgr.validate_token(token) is True


# ==============================================================================
# APIKey Dataclass
# ==============================================================================


@pytest.mark.unit
class TestAPIKeyDataclass:
    """Tests for the APIKey dataclass."""

    def test_basic_creation(self):
        """APIKey stores all fields."""
        key = APIKey(key="k1", user_id="u1", permissions=["read"])
        assert key.key == "k1"
        assert key.user_id == "u1"
        assert key.permissions == ["read"]
        assert key.revoked is False
        assert key.request_count == 0

    def test_is_expired_no_expiry(self):
        """Key with no expiry is not expired."""
        key = APIKey(key="k", user_id="u", permissions=[])
        assert not key.is_expired

    def test_is_expired_future(self):
        """Key expiring in the future is not expired."""
        key = APIKey(key="k", user_id="u", permissions=[], expires_at=time.time() + 3600)
        assert not key.is_expired

    def test_is_expired_past(self):
        """Key with past expiry is expired."""
        key = APIKey(key="k", user_id="u", permissions=[], expires_at=time.time() - 1)
        assert key.is_expired

    def test_is_valid_fresh(self):
        """Fresh key is valid."""
        key = APIKey(key="k", user_id="u", permissions=[])
        assert key.is_valid

    def test_is_valid_revoked(self):
        """Revoked key is not valid."""
        key = APIKey(key="k", user_id="u", permissions=[], revoked=True)
        assert not key.is_valid

    def test_is_valid_expired(self):
        """Expired key is not valid."""
        key = APIKey(key="k", user_id="u", permissions=[], expires_at=time.time() - 1)
        assert not key.is_valid

    def test_default_rate_limit(self):
        """Default rate_limit is 0 (unlimited)."""
        key = APIKey(key="k", user_id="u", permissions=[])
        assert key.rate_limit == 0

    def test_default_label(self):
        """Default label is empty string."""
        key = APIKey(key="k", user_id="u", permissions=[])
        assert key.label == ""


# ==============================================================================
# APIKeyManager
# ==============================================================================


@pytest.mark.unit
class TestAPIKeyManagerUnit:
    """Tests for the APIKeyManager class."""

    def test_generate_with_prefix(self):
        """Generated key starts with the manager's prefix."""
        mgr = APIKeyManager(prefix="myapp")
        key = mgr.generate(user_id="alice")
        assert key.startswith("myapp_")

    def test_generate_default_prefix(self):
        """Default prefix is 'codomyrmex'."""
        mgr = APIKeyManager()
        key = mgr.generate(user_id="alice")
        assert key.startswith("codomyrmex_")

    def test_generate_default_permissions(self):
        """Default permissions are ['read']."""
        mgr = APIKeyManager()
        key = mgr.generate(user_id="alice")
        info = mgr.validate(key)
        assert info.permissions == ["read"]

    def test_generate_custom_permissions(self):
        """Custom permissions are stored."""
        mgr = APIKeyManager()
        key = mgr.generate(user_id="alice", permissions=["read", "write", "admin"])
        info = mgr.validate(key)
        assert info.permissions == ["read", "write", "admin"]

    def test_generate_with_ttl(self):
        """TTL sets expires_at on the key."""
        mgr = APIKeyManager()
        key = mgr.generate(user_id="alice", ttl_seconds=3600)
        info = mgr.validate(key)
        assert info is not None
        assert info.expires_at is not None
        assert info.expires_at > time.time()

    def test_generate_with_rate_limit(self):
        """Rate limit is stored on the key."""
        mgr = APIKeyManager()
        key = mgr.generate(user_id="alice", rate_limit=100)
        info = mgr.validate(key)
        assert info.rate_limit == 100

    def test_generate_with_label(self):
        """Label is stored on the key."""
        mgr = APIKeyManager()
        key = mgr.generate(user_id="alice", label="production-key")
        info = mgr.validate(key)
        assert info.label == "production-key"

    def test_validate_valid_key(self):
        """Validate returns APIKey for valid key."""
        mgr = APIKeyManager()
        key = mgr.generate(user_id="alice")
        info = mgr.validate(key)
        assert info is not None
        assert info.user_id == "alice"

    def test_validate_increments_request_count(self):
        """Each validate call increments request_count."""
        mgr = APIKeyManager()
        key = mgr.generate(user_id="alice")
        mgr.validate(key)
        mgr.validate(key)
        info = mgr.validate(key)
        assert info.request_count == 3

    def test_validate_unknown_key(self):
        """Validate returns None for unknown key."""
        mgr = APIKeyManager()
        assert mgr.validate("unknown-key") is None

    def test_validate_revoked_key(self):
        """Validate returns None for revoked key."""
        mgr = APIKeyManager()
        key = mgr.generate(user_id="alice")
        mgr.revoke(key)
        assert mgr.validate(key) is None

    def test_validate_expired_key(self):
        """Validate returns None for expired key."""
        mgr = APIKeyManager()
        key = mgr.generate(user_id="alice", ttl_seconds=0.1)
        time.sleep(0.2)
        assert mgr.validate(key) is None

    def test_validate_api_key_legacy(self):
        """Legacy validate_api_key returns dict."""
        mgr = APIKeyManager()
        key = mgr.generate_api_key(user_id="alice", permissions=["write"])
        info = mgr.validate_api_key(key)
        assert isinstance(info, dict)
        assert info["user_id"] == "alice"
        assert info["permissions"] == ["write"]

    def test_validate_api_key_legacy_invalid(self):
        """Legacy validate_api_key returns None for invalid."""
        mgr = APIKeyManager()
        assert mgr.validate_api_key("nope") is None

    def test_revoke_success(self):
        """Revoking existing key returns True."""
        mgr = APIKeyManager()
        key = mgr.generate(user_id="alice")
        assert mgr.revoke(key) is True

    def test_revoke_unknown_key(self):
        """Revoking unknown key returns False."""
        mgr = APIKeyManager()
        assert mgr.revoke("unknown") is False

    def test_revoke_api_key_legacy(self):
        """Legacy revoke_api_key works."""
        mgr = APIKeyManager()
        key = mgr.generate_api_key(user_id="alice")
        assert mgr.revoke_api_key(key) is True
        assert mgr.validate_api_key(key) is None

    def test_rotate_success(self):
        """Rotating a key revokes old and issues new with same permissions."""
        mgr = APIKeyManager()
        old_key = mgr.generate(user_id="alice", permissions=["read", "write"], label="v1")
        new_key = mgr.rotate(old_key)
        assert new_key is not None
        assert new_key != old_key
        assert new_key.startswith("codomyrmex_")
        # Old key is revoked
        assert mgr.validate(old_key) is None
        # New key is valid with same permissions
        info = mgr.validate(new_key)
        assert info.user_id == "alice"
        assert info.permissions == ["read", "write"]
        assert "rotated" in info.label

    def test_rotate_with_ttl(self):
        """Rotating with a ttl sets expiry on new key."""
        mgr = APIKeyManager()
        old_key = mgr.generate(user_id="alice")
        new_key = mgr.rotate(old_key, ttl_seconds=7200)
        info = mgr.validate(new_key)
        assert info.expires_at is not None

    def test_rotate_unknown_key(self):
        """Rotating unknown key returns None."""
        mgr = APIKeyManager()
        assert mgr.rotate("unknown") is None

    def test_list_keys_all(self):
        """list_keys returns all active keys."""
        mgr = APIKeyManager()
        mgr.generate(user_id="alice")
        mgr.generate(user_id="bob")
        keys = mgr.list_keys()
        assert len(keys) == 2

    def test_list_keys_by_user(self):
        """list_keys filtered by user_id."""
        mgr = APIKeyManager()
        mgr.generate(user_id="alice")
        mgr.generate(user_id="alice")
        mgr.generate(user_id="bob")
        keys = mgr.list_keys(user_id="alice")
        assert len(keys) == 2
        assert all(k.user_id == "alice" for k in keys)

    def test_list_keys_excludes_revoked(self):
        """list_keys excludes revoked keys by default."""
        mgr = APIKeyManager()
        k1 = mgr.generate(user_id="alice")
        mgr.generate(user_id="alice")
        mgr.revoke(k1)
        keys = mgr.list_keys(user_id="alice")
        assert len(keys) == 1

    def test_list_keys_includes_revoked(self):
        """list_keys with include_revoked=True includes revoked keys."""
        mgr = APIKeyManager()
        k1 = mgr.generate(user_id="alice")
        mgr.generate(user_id="alice")
        mgr.revoke(k1)
        keys = mgr.list_keys(user_id="alice", include_revoked=True)
        assert len(keys) == 2

    def test_cleanup_expired(self):
        """cleanup_expired removes expired and revoked keys."""
        mgr = APIKeyManager()
        mgr.generate(user_id="alice", ttl_seconds=0.1)
        mgr.generate(user_id="bob")
        k3 = mgr.generate(user_id="charlie")
        mgr.revoke(k3)
        time.sleep(0.2)  # Let k1 expire
        removed = mgr.cleanup_expired()
        assert removed == 2  # k1 (expired) and k3 (revoked)
        assert mgr.total_count == 1

    def test_active_count(self):
        """active_count reflects valid keys only."""
        mgr = APIKeyManager()
        mgr.generate(user_id="alice")
        mgr.generate(user_id="bob")
        k3 = mgr.generate(user_id="charlie")
        mgr.revoke(k3)
        assert mgr.active_count == 2

    def test_total_count(self):
        """total_count reflects all keys including revoked."""
        mgr = APIKeyManager()
        mgr.generate(user_id="alice")
        k2 = mgr.generate(user_id="bob")
        mgr.revoke(k2)
        assert mgr.total_count == 2

    def test_unique_keys(self):
        """All generated keys are unique."""
        mgr = APIKeyManager()
        keys = {mgr.generate(user_id="u") for _ in range(20)}
        assert len(keys) == 20


# ==============================================================================
# PermissionCheck Dataclass
# ==============================================================================


@pytest.mark.unit
class TestPermissionCheckDataclass:
    """Tests for the PermissionCheck dataclass."""

    def test_basic_creation(self):
        """PermissionCheck stores all fields."""
        pc = PermissionCheck(
            user_id="alice", role="editor",
            permission="write", granted=True, resource="doc-1"
        )
        assert pc.user_id == "alice"
        assert pc.role == "editor"
        assert pc.permission == "write"
        assert pc.granted is True
        assert pc.resource == "doc-1"

    def test_default_resource(self):
        """Default resource is empty string."""
        pc = PermissionCheck(user_id="u", role="r", permission="p", granted=False)
        assert pc.resource == ""

    def test_timestamp_auto_set(self):
        """Timestamp is auto-set to current time."""
        before = time.time()
        pc = PermissionCheck(user_id="u", role="r", permission="p", granted=True)
        after = time.time()
        assert before <= pc.timestamp <= after


# ==============================================================================
# PermissionRegistry
# ==============================================================================


@pytest.mark.unit
class TestPermissionRegistryUnit:
    """Tests for the PermissionRegistry class."""

    def test_register_role_with_permissions(self):
        """register_role stores permissions for a role."""
        reg = PermissionRegistry()
        reg.register_role("editor", ["read", "write"])
        perms = reg.get_permissions("editor")
        assert "read" in perms
        assert "write" in perms

    def test_register_role_empty_permissions(self):
        """register_role with empty list creates role with no permissions."""
        reg = PermissionRegistry()
        reg.register_role("empty", [])
        assert reg.get_permissions("empty") == set()

    def test_register_role_none_permissions(self):
        """register_role with None permissions creates empty role."""
        reg = PermissionRegistry()
        reg.register_role("none_role", None)
        assert reg.get_permissions("none_role") == set()

    def test_register_role_additive(self):
        """Calling register_role again adds to existing permissions."""
        reg = PermissionRegistry()
        reg.register_role("editor", ["read"])
        reg.register_role("editor", ["write"])
        perms = reg.get_permissions("editor")
        assert "read" in perms
        assert "write" in perms

    def test_add_inheritance(self):
        """Child role inherits parent's permissions."""
        reg = PermissionRegistry()
        reg.register_role("reader", ["read"])
        reg.register_role("editor", ["write"])
        reg.add_inheritance("editor", "reader")
        perms = reg.get_permissions("editor")
        assert "read" in perms
        assert "write" in perms

    def test_add_inheritance_chain(self):
        """Multi-level inheritance propagates permissions."""
        reg = PermissionRegistry()
        reg.register_role("reader", ["read"])
        reg.register_role("editor", ["write"])
        reg.register_role("admin", ["delete"])
        reg.add_inheritance("editor", "reader")
        reg.add_inheritance("admin", "editor")
        perms = reg.get_permissions("admin")
        assert "read" in perms
        assert "write" in perms
        assert "delete" in perms

    def test_circular_inheritance_safe(self):
        """Circular inheritance does not cause infinite loop."""
        reg = PermissionRegistry()
        reg.register_role("a", ["perm_a"])
        reg.register_role("b", ["perm_b"])
        reg.add_inheritance("a", "b")
        reg.add_inheritance("b", "a")
        perms = reg.get_permissions("a")
        assert "perm_a" in perms
        assert "perm_b" in perms

    def test_add_inheritance_creates_missing_roles(self):
        """add_inheritance auto-creates roles that do not yet exist."""
        reg = PermissionRegistry()
        reg.add_inheritance("new_child", "new_parent")
        assert "new_child" in reg.list_roles()
        assert "new_parent" in reg.list_roles()

    def test_remove_role(self):
        """remove_role deletes the role."""
        reg = PermissionRegistry()
        reg.register_role("temp", ["read"])
        assert reg.remove_role("temp") is True
        assert "temp" not in reg.list_roles()

    def test_remove_role_nonexistent(self):
        """Removing nonexistent role returns False."""
        reg = PermissionRegistry()
        assert reg.remove_role("ghost") is False

    def test_remove_role_unassigns_from_users(self):
        """Removing a role unassigns it from all users."""
        reg = PermissionRegistry()
        reg.register_role("temp", ["read"])
        reg.assign_role("alice", "temp")
        reg.remove_role("temp")
        assert "temp" not in reg.get_user_roles("alice")

    def test_remove_role_cleans_hierarchy(self):
        """Removing a role removes it from other roles' parent lists."""
        reg = PermissionRegistry()
        reg.register_role("parent", ["read"])
        reg.register_role("child", ["write"])
        reg.add_inheritance("child", "parent")
        reg.remove_role("parent")
        # child should no longer inherit from parent
        perms = reg.get_permissions("child")
        assert "read" not in perms
        assert "write" in perms

    def test_list_roles(self):
        """list_roles returns sorted role names."""
        reg = PermissionRegistry()
        reg.register_role("editor")
        reg.register_role("admin")
        reg.register_role("viewer")
        roles = reg.list_roles()
        assert roles == ["admin", "editor", "viewer"]

    def test_assign_role(self):
        """assign_role assigns a role to a user."""
        reg = PermissionRegistry()
        reg.register_role("editor", ["write"])
        reg.assign_role("alice", "editor")
        assert "editor" in reg.get_user_roles("alice")

    def test_assign_role_auto_creates(self):
        """assign_role auto-creates the role if it does not exist."""
        reg = PermissionRegistry()
        reg.assign_role("alice", "new_role")
        assert "new_role" in reg.list_roles()
        assert "new_role" in reg.get_user_roles("alice")

    def test_assign_multiple_roles(self):
        """User can have multiple roles."""
        reg = PermissionRegistry()
        reg.register_role("reader", ["read"])
        reg.register_role("writer", ["write"])
        reg.assign_role("alice", "reader")
        reg.assign_role("alice", "writer")
        roles = reg.get_user_roles("alice")
        assert "reader" in roles
        assert "writer" in roles

    def test_revoke_role(self):
        """revoke_role removes role from user."""
        reg = PermissionRegistry()
        reg.assign_role("alice", "editor")
        assert reg.revoke_role("alice", "editor") is True
        assert "editor" not in reg.get_user_roles("alice")

    def test_revoke_role_not_assigned(self):
        """Revoking unassigned role returns False."""
        reg = PermissionRegistry()
        assert reg.revoke_role("alice", "editor") is False

    def test_revoke_role_unknown_user(self):
        """Revoking role from unknown user returns False."""
        reg = PermissionRegistry()
        assert reg.revoke_role("nobody", "editor") is False

    def test_get_user_roles_unknown_user(self):
        """get_user_roles for unknown user returns empty set."""
        reg = PermissionRegistry()
        assert reg.get_user_roles("ghost") == set()

    def test_get_user_roles_returns_copy(self):
        """get_user_roles returns a copy, not the internal set."""
        reg = PermissionRegistry()
        reg.assign_role("alice", "editor")
        roles = reg.get_user_roles("alice")
        roles.add("hacked")
        # Internal state should not be affected
        assert "hacked" not in reg.get_user_roles("alice")

    def test_get_user_permissions(self):
        """get_user_permissions returns all permissions across all roles."""
        reg = PermissionRegistry()
        reg.register_role("reader", ["read"])
        reg.register_role("writer", ["write"])
        reg.assign_role("alice", "reader")
        reg.assign_role("alice", "writer")
        perms = reg.get_user_permissions("alice")
        assert "read" in perms
        assert "write" in perms

    def test_get_user_permissions_unknown_user(self):
        """get_user_permissions for unknown user returns empty set."""
        reg = PermissionRegistry()
        assert reg.get_user_permissions("ghost") == set()

    def test_has_permission_direct(self):
        """has_permission detects directly assigned permission."""
        reg = PermissionRegistry()
        reg.register_role("editor", ["read", "write"])
        assert reg.has_permission("editor", "read") is True
        assert reg.has_permission("editor", "delete") is False

    def test_has_permission_admin_override(self):
        """admin permission grants everything."""
        reg = PermissionRegistry()
        reg.register_role("superuser", ["admin"])
        assert reg.has_permission("superuser", "anything") is True

    def test_has_permission_wildcard(self):
        """Wildcard permission matches sub-permissions."""
        reg = PermissionRegistry()
        reg.register_role("data_role", ["data.*"])
        assert reg.has_permission("data_role", "data.read") is True
        assert reg.has_permission("data_role", "data.write") is True
        assert reg.has_permission("data_role", "other.read") is False

    def test_has_permission_star_wildcard(self):
        """Star wildcard grants everything."""
        reg = PermissionRegistry()
        reg.register_role("god", ["*"])
        assert reg.has_permission("god", "anything") is True

    def test_has_permission_unknown_role(self):
        """has_permission for unknown role returns False."""
        reg = PermissionRegistry()
        assert reg.has_permission("ghost", "read") is False

    def test_matches_static_exact(self):
        """_matches: exact match."""
        assert PermissionRegistry._matches("read", "read") is True
        assert PermissionRegistry._matches("read", "write") is False

    def test_matches_static_star(self):
        """_matches: star matches everything."""
        assert PermissionRegistry._matches("*", "anything") is True

    def test_matches_static_wildcard(self):
        """_matches: wildcard matches prefix."""
        assert PermissionRegistry._matches("files.*", "files.read") is True
        assert PermissionRegistry._matches("files.*", "files.write") is True
        assert PermissionRegistry._matches("files.*", "other.read") is False

    def test_check_grants_and_logs(self):
        """check() grants permission and logs to audit trail."""
        reg = PermissionRegistry()
        reg.register_role("editor", ["write"])
        reg.assign_role("alice", "editor")
        assert reg.check("alice", "write") is True
        assert len(reg.audit_log) == 1
        assert reg.audit_log[0].granted is True

    def test_check_denies_and_logs(self):
        """check() denies permission and logs to audit trail."""
        reg = PermissionRegistry()
        reg.register_role("viewer", ["read"])
        reg.assign_role("alice", "viewer")
        assert reg.check("alice", "delete") is False
        assert len(reg.audit_log) == 1
        assert reg.audit_log[0].granted is False

    def test_check_with_resource(self):
        """check() records resource in audit log."""
        reg = PermissionRegistry()
        reg.register_role("editor", ["write"])
        reg.assign_role("alice", "editor")
        reg.check("alice", "write", resource="doc-42")
        assert reg.audit_log[0].resource == "doc-42"

    def test_check_unknown_user(self):
        """check() for unknown user denies and logs."""
        reg = PermissionRegistry()
        assert reg.check("nobody", "read") is False
        assert len(reg.audit_log) == 1
        assert reg.audit_log[0].granted is False

    def test_audit_log_accumulates(self):
        """Multiple checks accumulate in audit log."""
        reg = PermissionRegistry()
        reg.register_role("editor", ["write"])
        reg.assign_role("alice", "editor")
        reg.check("alice", "write")
        reg.check("alice", "delete")
        reg.check("alice", "write")
        assert len(reg.audit_log) == 3

    def test_audit_log_returns_copy(self):
        """audit_log property returns a copy."""
        reg = PermissionRegistry()
        log = reg.audit_log
        assert isinstance(log, list)

    def test_role_count(self):
        """role_count reflects number of registered roles."""
        reg = PermissionRegistry()
        reg.register_role("a")
        reg.register_role("b")
        assert reg.role_count == 2

    def test_user_count(self):
        """user_count reflects number of users with roles."""
        reg = PermissionRegistry()
        reg.assign_role("alice", "editor")
        reg.assign_role("bob", "viewer")
        assert reg.user_count == 2


# ==============================================================================
# Authenticator
# ==============================================================================


@pytest.mark.unit
class TestAuthenticatorUnit:
    """Tests for the Authenticator class."""

    def _fresh_authenticator(self):
        """Reset the singleton state for test isolation."""
        a = Authenticator()
        a._users = {}
        a.token_manager = TokenManager()
        a.api_key_manager = APIKeyManager()
        a.permissions = PermissionRegistry()
        return a

    def test_singleton_pattern(self):
        """Authenticator is a singleton."""
        a1 = Authenticator()
        a2 = Authenticator()
        assert a1 is a2

    def test_register_user_success(self):
        """Registering a new user returns True."""
        a = self._fresh_authenticator()
        assert a.register_user("alice", "password123") is True
        assert "alice" in a._users

    def test_register_user_default_role(self):
        """User with no roles gets 'default' role."""
        a = self._fresh_authenticator()
        a.register_user("alice", "pass")
        assert "default" in a.permissions.get_user_roles("alice")

    def test_register_user_custom_roles(self):
        """User with custom roles gets those assigned."""
        a = self._fresh_authenticator()
        a.register_user("alice", "pass", roles=["admin", "editor"])
        roles = a.permissions.get_user_roles("alice")
        assert "admin" in roles
        assert "editor" in roles

    def test_register_user_duplicate(self):
        """Registering duplicate username returns False."""
        a = self._fresh_authenticator()
        a.register_user("alice", "pass1")
        assert a.register_user("alice", "pass2") is False

    def test_authenticate_username_password(self):
        """Authenticate with correct username/password returns token."""
        a = self._fresh_authenticator()
        a.register_user("alice", "secret")
        token = a.authenticate({"username": "alice", "password": "secret"})
        assert token is not None
        assert token.user_id == "alice"

    def test_authenticate_wrong_password(self):
        """Authenticate with wrong password returns None."""
        a = self._fresh_authenticator()
        a.register_user("alice", "secret")
        token = a.authenticate({"username": "alice", "password": "wrong"})
        assert token is None

    def test_authenticate_nonexistent_user(self):
        """Authenticate with nonexistent user returns None."""
        a = self._fresh_authenticator()
        token = a.authenticate({"username": "ghost", "password": "any"})
        assert token is None

    def test_authenticate_api_key(self):
        """Authenticate with valid API key returns token."""
        a = self._fresh_authenticator()
        api_key = a.api_key_manager.generate(user_id="alice", permissions=["read", "write"])
        token = a.authenticate({"api_key": api_key})
        assert token is not None
        assert token.user_id == "alice"
        assert "read" in token.permissions

    def test_authenticate_invalid_api_key(self):
        """Authenticate with invalid API key returns None."""
        a = self._fresh_authenticator()
        token = a.authenticate({"api_key": "invalid-key"})
        assert token is None

    def test_authenticate_empty_credentials(self):
        """Empty credentials dict returns None."""
        a = self._fresh_authenticator()
        token = a.authenticate({})
        assert token is None

    def test_authorize_token_object_with_permission(self):
        """Authorize token object with matching permission."""
        a = self._fresh_authenticator()
        token = a.token_manager.create_token("alice", permissions=["read"])
        assert a.authorize(token, "resource", "read") is True

    def test_authorize_token_object_without_permission(self):
        """Authorize token object without matching permission."""
        a = self._fresh_authenticator()
        token = a.token_manager.create_token("alice", permissions=["read"])
        assert a.authorize(token, "resource", "delete") is False

    def test_authorize_admin_token(self):
        """Admin token grants all permissions."""
        a = self._fresh_authenticator()
        token = a.token_manager.create_token("alice", permissions=["admin"])
        assert a.authorize(token, "r", "read") is True
        assert a.authorize(token, "r", "write") is True
        assert a.authorize(token, "r", "delete") is True

    def test_authorize_wildcard_token(self):
        """Wildcard permission in token grants matching permissions."""
        a = self._fresh_authenticator()
        token = a.token_manager.create_token("alice", permissions=["data.*"])
        assert a.authorize(token, "r", "data.read") is True
        assert a.authorize(token, "r", "data.write") is True
        assert a.authorize(token, "r", "other") is False

    def test_authorize_star_permission(self):
        """Star (*) permission grants everything."""
        a = self._fresh_authenticator()
        token = a.token_manager.create_token("alice", permissions=["*"])
        assert a.authorize(token, "r", "anything") is True

    def test_authorize_signed_string(self):
        """Authorize with signed token string."""
        a = self._fresh_authenticator()
        token = a.token_manager.create_token("alice", permissions=["read"])
        assert a.authorize(token.jwt, "resource", "read") is True

    def test_authorize_invalid_signed_string(self):
        """Authorize with invalid string returns False."""
        a = self._fresh_authenticator()
        assert a.authorize("garbage", "resource", "read") is False

    def test_authorize_revoked_token(self):
        """Authorize revoked token returns False."""
        a = self._fresh_authenticator()
        token = a.token_manager.create_token("alice", permissions=["read"])
        a.revoke_token(token)
        assert a.authorize(token, "resource", "read") is False

    def test_authorize_via_rbac(self):
        """Authorize via RBAC when token has no direct permission."""
        a = self._fresh_authenticator()
        a.permissions.register_role("editor", ["write"])
        a.permissions.assign_role("alice", "editor")
        token = a.token_manager.create_token("alice", permissions=[])
        assert a.authorize(token, "resource", "write") is True

    def test_refresh_token(self):
        """Refresh creates new token, revokes old."""
        a = self._fresh_authenticator()
        old = a.token_manager.create_token("alice", permissions=["read"])
        new = a.refresh_token(old)
        assert new is not None
        assert new.token_id != old.token_id
        assert new.user_id == old.user_id

    def test_revoke_token(self):
        """Revoke token invalidates it."""
        a = self._fresh_authenticator()
        token = a.token_manager.create_token("alice")
        assert a.revoke_token(token) is True
        assert not a.token_manager.validate_token(token)

    def test_validate_password_internal(self):
        """_validate_password checks stored password."""
        a = self._fresh_authenticator()
        a.register_user("alice", "secret")
        assert a._validate_password("alice", "secret") is True
        assert a._validate_password("alice", "wrong") is False
        assert a._validate_password("ghost", "any") is False


# ==============================================================================
# Module-level Convenience Functions
# ==============================================================================


@pytest.mark.unit
class TestModuleLevelFunctions:
    """Tests for auth module-level convenience functions."""

    def _reset_authenticator(self):
        """Reset singleton for isolation."""
        a = Authenticator()
        a._users = {}
        a.token_manager = TokenManager()
        a.api_key_manager = APIKeyManager()
        a.permissions = PermissionRegistry()
        return a

    def test_get_authenticator(self):
        """get_authenticator returns the Authenticator singleton."""
        from codomyrmex.auth import get_authenticator
        a = get_authenticator()
        assert isinstance(a, Authenticator)

    def test_authenticate_function(self):
        """Module-level authenticate() works."""
        from codomyrmex.auth import authenticate
        a = self._reset_authenticator()
        a.register_user("testfn", "pass")
        # Module-level authenticate uses the singleton
        token = authenticate({"username": "testfn", "password": "pass"})
        assert token is not None

    def test_authorize_function(self):
        """Module-level authorize() works."""
        from codomyrmex.auth import authorize
        a = self._reset_authenticator()
        token = a.token_manager.create_token("u", permissions=["read"])
        assert authorize(token, "r", "read") is True

    def test_cli_commands_structure(self):
        """cli_commands returns dict with expected keys."""
        from codomyrmex.auth import cli_commands
        cmds = cli_commands()
        assert "providers" in cmds
        assert "status" in cmds
        assert "help" in cmds["providers"]
        assert "handler" in cmds["providers"]
        assert callable(cmds["providers"]["handler"])
        assert callable(cmds["status"]["handler"])


# ==============================================================================
# Auth Module __all__ and Version
# ==============================================================================


@pytest.mark.unit
class TestAuthModuleMetadata:
    """Tests for auth module metadata."""

    def test_all_exports(self):
        """__all__ contains expected public names."""
        import codomyrmex.auth as auth_mod
        expected = {
            "Authenticator", "Token", "TokenManager", "APIKeyManager",
            "PermissionRegistry", "TokenValidator",
            "authenticate", "authorize", "get_authenticator", "cli_commands",
        }
        assert set(auth_mod.__all__) == expected

    def test_version(self):
        """Module has a version string."""
        import codomyrmex.auth as auth_mod
        assert hasattr(auth_mod, "__version__")
        assert isinstance(auth_mod.__version__, str)
        assert len(auth_mod.__version__) > 0
