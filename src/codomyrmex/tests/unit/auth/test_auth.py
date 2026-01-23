"""Comprehensive tests for the auth module.

Tests cover:
- Token creation, validation, and lifecycle
- API key generation and validation
- Permission registry and RBAC
- Authenticator integration
- Token validator and signatures
"""

import time
import pytest

from codomyrmex import auth
from codomyrmex.auth.token import Token, TokenManager
from codomyrmex.auth.api_key_manager import APIKeyManager
from codomyrmex.auth.permissions import PermissionRegistry
from codomyrmex.auth.authenticator import Authenticator, AuthenticationError
from codomyrmex.auth.validator import TokenValidator


# ==============================================================================
# Module Import Tests
# ==============================================================================

class TestAuthModuleImport:
    """Test auth module import and structure."""

    def test_auth_module_import(self):
        """Verify that the auth module can be imported successfully."""
        assert auth is not None
        assert hasattr(auth, "__path__")

    def test_auth_module_structure(self):
        """Verify basic structure of auth module."""
        assert hasattr(auth, "__file__")


# ==============================================================================
# Token Tests
# ==============================================================================

class TestToken:
    """Tests for Token dataclass."""

    def test_token_creation(self):
        """Test basic token creation."""
        token = Token(
            token_id="test-123",
            user_id="user-456",
            permissions=["read", "write"]
        )
        assert token.token_id == "test-123"
        assert token.user_id == "user-456"
        assert token.permissions == ["read", "write"]
        assert token.expires_at is None
        assert token.created_at is not None

    def test_token_not_expired_when_no_expiration(self):
        """Test token without expiration is never expired."""
        token = Token(token_id="test", user_id="user")
        assert not token.is_expired()

    def test_token_not_expired_when_future_expiration(self):
        """Test token with future expiration is not expired."""
        token = Token(
            token_id="test",
            user_id="user",
            expires_at=time.time() + 3600
        )
        assert not token.is_expired()

    def test_token_expired_when_past_expiration(self):
        """Test token with past expiration is expired."""
        token = Token(
            token_id="test",
            user_id="user",
            expires_at=time.time() - 1
        )
        assert token.is_expired()

    def test_token_to_dict(self):
        """Test token serialization to dictionary."""
        token = Token(
            token_id="test-123",
            user_id="user-456",
            permissions=["read"],
            expires_at=1000.0,
            created_at=500.0
        )
        data = token.to_dict()
        assert data["token_id"] == "test-123"
        assert data["user_id"] == "user-456"
        assert data["permissions"] == ["read"]
        assert data["expires_at"] == 1000.0
        assert data["created_at"] == 500.0

    def test_token_from_dict(self):
        """Test token deserialization from dictionary."""
        data = {
            "token_id": "test-123",
            "user_id": "user-456",
            "permissions": ["write"],
            "expires_at": 2000.0,
            "created_at": 1000.0
        }
        token = Token.from_dict(data)
        assert token.token_id == "test-123"
        assert token.user_id == "user-456"
        assert token.permissions == ["write"]
        assert token.expires_at == 2000.0
        assert token.created_at == 1000.0

    def test_token_from_dict_with_defaults(self):
        """Test token deserialization with missing optional fields."""
        data = {
            "token_id": "test-123",
            "user_id": "user-456"
        }
        token = Token.from_dict(data)
        assert token.token_id == "test-123"
        assert token.permissions == []
        assert token.expires_at is None


# ==============================================================================
# TokenManager Tests
# ==============================================================================

class TestTokenManager:
    """Tests for TokenManager."""

    @pytest.fixture
    def manager(self):
        """Create a fresh TokenManager for each test."""
        return TokenManager(secret="test-secret")

    def test_create_token(self, manager):
        """Test basic token creation."""
        token = manager.create_token(user_id="user-123")
        assert token.user_id == "user-123"
        assert token.token_id is not None
        assert len(token.token_id) > 0

    def test_create_token_with_permissions(self, manager):
        """Test token creation with permissions."""
        token = manager.create_token(
            user_id="user-123",
            permissions=["read", "write", "admin"]
        )
        assert token.permissions == ["read", "write", "admin"]

    def test_create_token_with_ttl(self, manager):
        """Test token creation with custom TTL."""
        token = manager.create_token(user_id="user-123", ttl=7200)
        assert token.expires_at is not None
        assert token.expires_at > time.time()
        assert token.expires_at < time.time() + 7201

    def test_create_token_with_no_expiration(self, manager):
        """Test token creation without expiration."""
        token = manager.create_token(user_id="user-123", ttl=0)
        assert token.expires_at is None

    def test_validate_token_success(self, manager):
        """Test successful token validation."""
        token = manager.create_token(user_id="user-123")
        assert manager.validate_token(token)

    def test_validate_token_revoked(self, manager):
        """Test validation fails for revoked token."""
        token = manager.create_token(user_id="user-123")
        manager.revoke_token(token)
        assert not manager.validate_token(token)

    def test_validate_token_expired(self, manager):
        """Test validation fails for expired token."""
        token = manager.create_token(user_id="user-123", ttl=1)
        time.sleep(1.1)  # Wait for expiration
        assert not manager.validate_token(token)

    def test_validate_unknown_token(self, manager):
        """Test validation fails for unknown token."""
        unknown_token = Token(token_id="unknown", user_id="user")
        assert not manager.validate_token(unknown_token)

    def test_revoke_token(self, manager):
        """Test token revocation."""
        token = manager.create_token(user_id="user-123")
        assert manager.revoke_token(token)
        assert not manager.validate_token(token)

    def test_refresh_token_success(self, manager):
        """Test successful token refresh."""
        original_token = manager.create_token(user_id="user-123", permissions=["read"])
        new_token = manager.refresh_token(original_token, ttl=3600)

        assert new_token is not None
        assert new_token.user_id == original_token.user_id
        assert new_token.permissions == original_token.permissions
        assert new_token.token_id != original_token.token_id
        # Original token should be revoked
        assert not manager.validate_token(original_token)

    def test_refresh_token_invalid(self, manager):
        """Test refresh fails for invalid token."""
        token = manager.create_token(user_id="user-123")
        manager.revoke_token(token)
        new_token = manager.refresh_token(token)
        assert new_token is None


# ==============================================================================
# APIKeyManager Tests
# ==============================================================================

class TestAPIKeyManager:
    """Tests for APIKeyManager."""

    @pytest.fixture
    def manager(self):
        """Create a fresh APIKeyManager for each test."""
        return APIKeyManager()

    def test_generate_api_key(self, manager):
        """Test API key generation."""
        api_key = manager.generate_api_key(user_id="user-123")
        assert api_key.startswith("codomyrmex_")
        assert len(api_key) > 20

    def test_generate_api_key_with_permissions(self, manager):
        """Test API key generation with custom permissions."""
        api_key = manager.generate_api_key(
            user_id="user-123",
            permissions=["read", "write"]
        )
        info = manager.validate_api_key(api_key)
        assert info["permissions"] == ["read", "write"]

    def test_generate_api_key_default_permissions(self, manager):
        """Test API key has default read permission."""
        api_key = manager.generate_api_key(user_id="user-123")
        info = manager.validate_api_key(api_key)
        assert info["permissions"] == ["read"]

    def test_validate_api_key_success(self, manager):
        """Test successful API key validation."""
        api_key = manager.generate_api_key(user_id="user-123")
        info = manager.validate_api_key(api_key)
        assert info is not None
        assert info["user_id"] == "user-123"

    def test_validate_api_key_invalid(self, manager):
        """Test validation fails for invalid API key."""
        info = manager.validate_api_key("invalid-key")
        assert info is None

    def test_revoke_api_key_success(self, manager):
        """Test successful API key revocation."""
        api_key = manager.generate_api_key(user_id="user-123")
        assert manager.revoke_api_key(api_key)
        assert manager.validate_api_key(api_key) is None

    def test_revoke_api_key_nonexistent(self, manager):
        """Test revoking nonexistent API key returns False."""
        assert not manager.revoke_api_key("nonexistent-key")

    def test_multiple_api_keys_per_user(self, manager):
        """Test user can have multiple API keys."""
        key1 = manager.generate_api_key(user_id="user-123")
        key2 = manager.generate_api_key(user_id="user-123")
        assert key1 != key2
        assert manager.validate_api_key(key1)["user_id"] == "user-123"
        assert manager.validate_api_key(key2)["user_id"] == "user-123"


# ==============================================================================
# PermissionRegistry Tests
# ==============================================================================

class TestPermissionRegistry:
    """Tests for PermissionRegistry."""

    @pytest.fixture
    def registry(self):
        """Create a fresh PermissionRegistry for each test."""
        return PermissionRegistry()

    def test_register_role(self, registry):
        """Test role registration."""
        registry.register_role("editor", ["read", "write"])
        perms = registry.get_permissions("editor")
        assert "read" in perms
        assert "write" in perms

    def test_register_role_multiple_times(self, registry):
        """Test adding permissions to existing role."""
        registry.register_role("editor", ["read"])
        registry.register_role("editor", ["write"])
        perms = registry.get_permissions("editor")
        assert "read" in perms
        assert "write" in perms

    def test_has_permission_direct(self, registry):
        """Test direct permission check."""
        registry.register_role("editor", ["read", "write"])
        assert registry.has_permission("editor", "read")
        assert registry.has_permission("editor", "write")
        assert not registry.has_permission("editor", "delete")

    def test_has_permission_admin_override(self, registry):
        """Test admin permission grants all access."""
        registry.register_role("superuser", ["admin"])
        assert registry.has_permission("superuser", "read")
        assert registry.has_permission("superuser", "write")
        assert registry.has_permission("superuser", "delete")
        assert registry.has_permission("superuser", "anything")

    def test_role_inheritance(self, registry):
        """Test role inheritance."""
        registry.register_role("reader", ["read"])
        registry.register_role("editor", ["write"])
        registry.add_inheritance("editor", "reader")

        perms = registry.get_permissions("editor")
        assert "read" in perms
        assert "write" in perms

    def test_role_inheritance_chain(self, registry):
        """Test multi-level role inheritance."""
        registry.register_role("reader", ["read"])
        registry.register_role("editor", ["write"])
        registry.register_role("admin", ["delete"])

        registry.add_inheritance("editor", "reader")
        registry.add_inheritance("admin", "editor")

        perms = registry.get_permissions("admin")
        assert "read" in perms
        assert "write" in perms
        assert "delete" in perms

    def test_get_permissions_unknown_role(self, registry):
        """Test getting permissions for unknown role returns empty set."""
        perms = registry.get_permissions("unknown")
        assert perms == set()


# ==============================================================================
# TokenValidator Tests
# ==============================================================================

@pytest.mark.security
class TestTokenValidator:
    """Tests for TokenValidator."""

    @pytest.fixture
    def validator(self):
        """Create a fresh TokenValidator for each test."""
        return TokenValidator(secret="test-secret-key")

    def test_sign_and_validate_token(self, validator):
        """Test token signing and validation roundtrip."""
        token_data = {
            "user_id": "user-123",
            "permissions": ["read"],
            "expires_at": time.time() + 3600
        }
        signed = validator.sign_token_data(token_data)
        validated = validator.validate_signed_token(signed)

        assert validated is not None
        assert validated["user_id"] == "user-123"
        assert validated["permissions"] == ["read"]

    def test_validate_expired_token(self, validator):
        """Test validation fails for expired token."""
        token_data = {
            "user_id": "user-123",
            "expires_at": time.time() - 1  # Expired
        }
        signed = validator.sign_token_data(token_data)
        validated = validator.validate_signed_token(signed)
        assert validated is None

    def test_validate_tampered_token(self, validator):
        """Test validation fails for tampered token."""
        token_data = {"user_id": "user-123"}
        signed = validator.sign_token_data(token_data)

        # Tamper with the token
        import base64
        import json
        decoded = json.loads(base64.b64decode(signed))
        decoded["data"]["user_id"] = "hacker"
        tampered = base64.b64encode(json.dumps(decoded).encode()).decode()

        validated = validator.validate_signed_token(tampered)
        assert validated is None

    def test_validate_invalid_base64(self, validator):
        """Test validation handles invalid base64."""
        validated = validator.validate_signed_token("not-valid-base64!!!")
        assert validated is None

    def test_validate_invalid_json(self, validator):
        """Test validation handles invalid JSON."""
        import base64
        invalid = base64.b64encode(b"not json").decode()
        validated = validator.validate_signed_token(invalid)
        assert validated is None

    def test_validate_missing_signature(self, validator):
        """Test validation fails when signature is missing."""
        import base64
        import json
        token = {"data": {"user_id": "user-123"}}  # No signature
        encoded = base64.b64encode(json.dumps(token).encode()).decode()
        validated = validator.validate_signed_token(encoded)
        assert validated is None

    def test_different_secrets_fail_validation(self):
        """Test tokens signed with different secret fail validation."""
        validator1 = TokenValidator(secret="secret-1")
        validator2 = TokenValidator(secret="secret-2")

        token_data = {"user_id": "user-123"}
        signed = validator1.sign_token_data(token_data)

        # Should fail with different secret
        validated = validator2.validate_signed_token(signed)
        assert validated is None


# ==============================================================================
# Authenticator Integration Tests
# ==============================================================================

@pytest.mark.security
class TestAuthenticator:
    """Integration tests for Authenticator."""

    @pytest.fixture
    def authenticator(self):
        """Create a fresh Authenticator for each test."""
        return Authenticator()

    def test_authenticate_with_api_key(self, authenticator):
        """Test authentication with API key."""
        # Generate an API key
        api_key = authenticator.api_key_manager.generate_api_key(
            user_id="user-123",
            permissions=["read", "write"]
        )

        # Authenticate
        token = authenticator.authenticate({"api_key": api_key})
        assert token is not None
        assert token.user_id == "user-123"
        assert "read" in token.permissions
        assert "write" in token.permissions

    def test_authenticate_with_invalid_api_key(self, authenticator):
        """Test authentication fails with invalid API key."""
        token = authenticator.authenticate({"api_key": "invalid-key"})
        assert token is None

    def test_authenticate_with_username_password(self, authenticator):
        """Test authentication with username/password."""
        # Add a user
        authenticator._users["testuser"] = {"password": "testpass"}

        token = authenticator.authenticate({
            "username": "testuser",
            "password": "testpass"
        })
        assert token is not None
        assert token.user_id == "testuser"

    def test_authenticate_with_wrong_password(self, authenticator):
        """Test authentication fails with wrong password."""
        authenticator._users["testuser"] = {"password": "testpass"}

        token = authenticator.authenticate({
            "username": "testuser",
            "password": "wrongpass"
        })
        assert token is None

    def test_authenticate_with_nonexistent_user(self, authenticator):
        """Test authentication fails with nonexistent user."""
        token = authenticator.authenticate({
            "username": "nonexistent",
            "password": "anypass"
        })
        assert token is None

    def test_authorize_with_valid_permission(self, authenticator):
        """Test authorization with valid permission."""
        api_key = authenticator.api_key_manager.generate_api_key(
            user_id="user-123",
            permissions=["read"]
        )
        token = authenticator.authenticate({"api_key": api_key})

        assert authenticator.authorize(token, "resource", "read")

    def test_authorize_with_invalid_permission(self, authenticator):
        """Test authorization fails with invalid permission."""
        api_key = authenticator.api_key_manager.generate_api_key(
            user_id="user-123",
            permissions=["read"]
        )
        token = authenticator.authenticate({"api_key": api_key})

        assert not authenticator.authorize(token, "resource", "write")

    def test_authorize_with_admin_permission(self, authenticator):
        """Test admin permission grants all access."""
        api_key = authenticator.api_key_manager.generate_api_key(
            user_id="admin-user",
            permissions=["admin"]
        )
        token = authenticator.authenticate({"api_key": api_key})

        assert authenticator.authorize(token, "resource", "read")
        assert authenticator.authorize(token, "resource", "write")
        assert authenticator.authorize(token, "resource", "delete")

    def test_authorize_with_revoked_token(self, authenticator):
        """Test authorization fails with revoked token."""
        api_key = authenticator.api_key_manager.generate_api_key(
            user_id="user-123",
            permissions=["read"]
        )
        token = authenticator.authenticate({"api_key": api_key})
        authenticator.revoke_token(token)

        assert not authenticator.authorize(token, "resource", "read")

    def test_refresh_token(self, authenticator):
        """Test token refresh."""
        api_key = authenticator.api_key_manager.generate_api_key(
            user_id="user-123",
            permissions=["read"]
        )
        original_token = authenticator.authenticate({"api_key": api_key})
        new_token = authenticator.refresh_token(original_token)

        assert new_token is not None
        assert new_token.user_id == original_token.user_id
        assert new_token.token_id != original_token.token_id

    def test_revoke_token(self, authenticator):
        """Test token revocation."""
        api_key = authenticator.api_key_manager.generate_api_key(
            user_id="user-123",
            permissions=["read"]
        )
        token = authenticator.authenticate({"api_key": api_key})

        assert authenticator.revoke_token(token)
        assert not authenticator.token_manager.validate_token(token)

    def test_authorize_with_role_based_permissions(self, authenticator):
        """Test role-based authorization."""
        # Register role with permissions
        authenticator.permissions.register_role("editor", ["read", "write"])

        # Create token for user with role name as user_id
        token = authenticator.token_manager.create_token(
            user_id="editor",
            permissions=[]
        )

        assert authenticator.authorize(token, "resource", "read")
        assert authenticator.authorize(token, "resource", "write")
