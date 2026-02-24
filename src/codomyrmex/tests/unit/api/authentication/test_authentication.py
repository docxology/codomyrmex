"""Comprehensive tests for the codomyrmex.api.authentication module."""

import base64
import time
from datetime import datetime, timedelta

import pytest

from codomyrmex.api.authentication import (
    APIKeyAuthenticator,
    AuthCredentials,
    AuthResult,
    AuthType,
    BasicAuthenticator,
    BearerTokenAuthenticator,
    HMACAuthenticator,
    create_authenticator,
)


class TestAuthType:
    """Verify AuthType enum members and values."""

    def test_api_key_member(self):
        """Test functionality: api key member."""
        assert AuthType.API_KEY.value == "api_key"

    def test_bearer_token_member(self):
        """Test functionality: bearer token member."""
        assert AuthType.BEARER_TOKEN.value == "bearer_token"

    def test_basic_auth_member(self):
        """Test functionality: basic auth member."""
        assert AuthType.BASIC_AUTH.value == "basic_auth"

    def test_oauth2_member(self):
        """Test functionality: oauth2 member."""
        assert AuthType.OAUTH2.value == "oauth2"

    def test_hmac_member(self):
        """Test functionality: hmac member."""
        assert AuthType.HMAC.value == "hmac"

    def test_jwt_member(self):
        """Test functionality: jwt member."""
        assert AuthType.JWT.value == "jwt"

    def test_member_count(self):
        """Test functionality: member count."""
        assert len(AuthType) == 6


class TestAuthCredentials:
    """Verify AuthCredentials dataclass field access and defaults."""

    def test_field_access(self):
        """Test functionality: field access."""
        creds = AuthCredentials(
            auth_type=AuthType.API_KEY,
            identifier="user-123",
            secret="s3cret",
        )
        assert creds.auth_type == AuthType.API_KEY
        assert creds.identifier == "user-123"
        assert creds.secret == "s3cret"
        assert creds.metadata == {}

    def test_metadata_default_is_empty_dict(self):
        """Test functionality: metadata default is empty dict."""
        creds = AuthCredentials(AuthType.BASIC_AUTH, "u", "p")
        assert creds.metadata == {}

    def test_metadata_custom(self):
        """Test functionality: metadata custom."""
        creds = AuthCredentials(AuthType.HMAC, "c", "s", metadata={"env": "prod"})
        assert creds.metadata["env"] == "prod"


class TestAuthResult:
    """Verify AuthResult defaults and to_dict serialization."""

    def test_defaults(self):
        """Test functionality: defaults."""
        result = AuthResult(authenticated=False)
        assert result.authenticated is False
        assert result.identity is None
        assert result.roles == []
        assert result.scopes == []
        assert result.expires_at is None
        assert result.error is None
        assert result.metadata == {}

    def test_to_dict_unauthenticated(self):
        """Test functionality: to dict unauthenticated."""
        result = AuthResult(authenticated=False, error="denied")
        d = result.to_dict()
        assert d["authenticated"] is False
        assert d["error"] == "denied"
        assert d["expires_at"] is None

    def test_to_dict_authenticated_with_expiry(self):
        """Test functionality: to dict authenticated with expiry."""
        exp = datetime(2030, 1, 1, 0, 0, 0)
        result = AuthResult(
            authenticated=True,
            identity="alice",
            roles=["admin"],
            scopes=["read", "write"],
            expires_at=exp,
        )
        d = result.to_dict()
        assert d["authenticated"] is True
        assert d["identity"] == "alice"
        assert d["roles"] == ["admin"]
        assert d["scopes"] == ["read", "write"]
        assert d["expires_at"] == exp.isoformat()


class TestAPIKeyAuthenticator:
    """Verify API key registration, authentication, revocation, and generation."""

    def setup_method(self):
        self.auth = APIKeyAuthenticator()
        self.valid_key = "sk_test_abc123"
        self.auth.register_key(self.valid_key, identity="svc-billing", scopes=["read"])

    def test_authenticate_success_via_header(self):
        """Test functionality: authenticate success via header."""
        request = {"headers": {"X-API-Key": self.valid_key}}
        result = self.auth.authenticate(request)
        assert result.authenticated is True
        assert result.identity == "svc-billing"
        assert "read" in result.scopes

    def test_authenticate_success_via_query_param(self):
        """Test functionality: authenticate success via query param."""
        auth = APIKeyAuthenticator(query_param="api_key")
        auth.register_key("qk_1", identity="web")
        request = {"headers": {}, "query": {"api_key": "qk_1"}}
        result = auth.authenticate(request)
        assert result.authenticated is True
        assert result.identity == "web"

    def test_authenticate_missing_key(self):
        """Test functionality: authenticate missing key."""
        result = self.auth.authenticate({"headers": {}})
        assert result.authenticated is False
        assert result.error == "API key not provided"

    def test_authenticate_invalid_key(self):
        """Test functionality: authenticate invalid key."""
        request = {"headers": {"X-API-Key": "bad-key"}}
        result = self.auth.authenticate(request)
        assert result.authenticated is False
        assert result.error == "Invalid API key"

    def test_authenticate_expired_key(self):
        """Test functionality: authenticate expired key."""
        expired = datetime.now() - timedelta(hours=1)
        self.auth.register_key("exp_key", identity="old", expires_at=expired)
        request = {"headers": {"X-API-Key": "exp_key"}}
        result = self.auth.authenticate(request)
        assert result.authenticated is False
        assert result.error == "API key expired"

    def test_revoke_key(self):
        """Test functionality: revoke key."""
        self.auth.revoke_key(self.valid_key)
        request = {"headers": {"X-API-Key": self.valid_key}}
        result = self.auth.authenticate(request)
        assert result.authenticated is False

    def test_revoke_nonexistent_key_does_not_raise(self):
        """Test functionality: revoke nonexistent key does not raise."""
        self.auth.revoke_key("nonexistent")  # should not raise

    def test_generate_key_default_prefix(self):
        """Test functionality: generate key default prefix."""
        key = APIKeyAuthenticator.generate_key()
        assert key.startswith("sk_")
        assert len(key) > 10

    def test_generate_key_custom_prefix(self):
        """Test functionality: generate key custom prefix."""
        key = APIKeyAuthenticator.generate_key(prefix="pk")
        assert key.startswith("pk_")


class TestBearerTokenAuthenticator:
    """Verify bearer token creation, authentication, expiry, and custom validators."""

    def setup_method(self):
        self.auth = BearerTokenAuthenticator()

    def test_create_token_and_authenticate(self):
        """Test functionality: create token and authenticate."""
        token = self.auth.create_token("alice", scopes=["read"])
        request = {"headers": {"Authorization": f"Bearer {token}"}}
        result = self.auth.authenticate(request)
        assert result.authenticated is True
        assert result.identity == "alice"
        assert "read" in result.scopes

    def test_authenticate_missing_bearer_prefix(self):
        """Test functionality: authenticate missing bearer prefix."""
        request = {"headers": {"Authorization": "Token abc"}}
        result = self.auth.authenticate(request)
        assert result.authenticated is False
        assert result.error == "Bearer token not provided"

    def test_authenticate_missing_authorization_header(self):
        """Test functionality: authenticate missing authorization header."""
        result = self.auth.authenticate({"headers": {}})
        assert result.authenticated is False

    def test_authenticate_invalid_token(self):
        """Test functionality: authenticate invalid token."""
        request = {"headers": {"Authorization": "Bearer invalid_tok"}}
        result = self.auth.authenticate(request)
        assert result.authenticated is False
        assert result.error == "Invalid token"

    def test_authenticate_expired_token(self):
        """Test functionality: authenticate expired token."""
        token = self.auth.create_token("bob", ttl_seconds=0)
        # Allow token to expire
        time.sleep(0.05)
        request = {"headers": {"Authorization": f"Bearer {token}"}}
        result = self.auth.authenticate(request)
        assert result.authenticated is False
        assert result.error == "Token expired"

    def test_custom_validator_takes_precedence(self):
        """Test functionality: custom validator takes precedence."""
        def my_validator(tok):
            if tok == "magic":
                return {"identity": "wizard", "scopes": ["all"]}
            return None

        auth = BearerTokenAuthenticator(validator=my_validator)
        request = {"headers": {"Authorization": "Bearer magic"}}
        result = auth.authenticate(request)
        assert result.authenticated is True
        assert result.identity == "wizard"

    def test_custom_validator_returns_none_falls_through(self):
        """Test functionality: custom validator returns none falls through."""
        auth = BearerTokenAuthenticator(validator=lambda t: None)
        request = {"headers": {"Authorization": "Bearer unknown"}}
        result = auth.authenticate(request)
        assert result.authenticated is False
        assert result.error == "Invalid token"


class TestBasicAuthenticator:
    """Verify basic auth user registration and credential validation."""

    def setup_method(self):
        self.auth = BasicAuthenticator()
        self.auth.register_user("admin", "hunter2", roles=["admin", "user"])

    def _make_request(self, username, password):
        encoded = base64.b64encode(f"{username}:{password}".encode()).decode()
        return {"headers": {"Authorization": f"Basic {encoded}"}}

    def test_authenticate_success(self):
        """Test functionality: authenticate success."""
        request = self._make_request("admin", "hunter2")
        result = self.auth.authenticate(request)
        assert result.authenticated is True
        assert result.identity == "admin"
        assert "admin" in result.roles

    def test_authenticate_wrong_password(self):
        """Test functionality: authenticate wrong password."""
        request = self._make_request("admin", "wrong")
        result = self.auth.authenticate(request)
        assert result.authenticated is False
        assert result.error == "Invalid password"

    def test_authenticate_unknown_user(self):
        """Test functionality: authenticate unknown user."""
        request = self._make_request("nobody", "pass")
        result = self.auth.authenticate(request)
        assert result.authenticated is False
        assert result.error == "User not found"

    def test_authenticate_missing_header(self):
        """Test functionality: authenticate missing header."""
        result = self.auth.authenticate({"headers": {}})
        assert result.authenticated is False
        assert result.error == "Basic auth not provided"

    def test_authenticate_malformed_base64(self):
        """Test functionality: authenticate malformed base64."""
        request = {"headers": {"Authorization": "Basic %%%invalid%%"}}
        result = self.auth.authenticate(request)
        assert result.authenticated is False
        assert result.error == "Invalid Basic auth format"


class TestHMACAuthenticator:
    """Verify HMAC client registration, signing, and signature validation."""

    def setup_method(self):
        self.auth = HMACAuthenticator(max_age_seconds=60)
        self.client_id = "client-a"
        self.secret = "super-secret-key"
        self.auth.register_client(self.client_id, self.secret, scopes=["webhook"])

    def _signed_request(self, body="payload", ts=None):
        ts = ts or int(time.time())
        sig = self.auth.sign_request(self.client_id, body, timestamp=ts)
        return {
            "headers": {
                "X-Signature": sig,
                "X-Timestamp": str(ts),
                "X-Client-ID": self.client_id,
            },
            "body": body,
        }

    def test_authenticate_success(self):
        """Test functionality: authenticate success."""
        request = self._signed_request()
        result = self.auth.authenticate(request)
        assert result.authenticated is True
        assert result.identity == self.client_id
        assert "webhook" in result.scopes

    def test_authenticate_missing_headers(self):
        """Test functionality: authenticate missing headers."""
        result = self.auth.authenticate({"headers": {}})
        assert result.authenticated is False
        assert result.error == "Missing authentication headers"

    def test_authenticate_old_timestamp(self):
        """Test functionality: authenticate old timestamp."""
        old_ts = int(time.time()) - 600
        request = self._signed_request(ts=old_ts)
        result = self.auth.authenticate(request)
        assert result.authenticated is False
        assert result.error == "Request too old"

    def test_authenticate_invalid_signature(self):
        """Test functionality: authenticate invalid signature."""
        request = self._signed_request()
        request["headers"]["X-Signature"] = "tampered"
        result = self.auth.authenticate(request)
        assert result.authenticated is False
        assert result.error == "Invalid signature"

    def test_authenticate_unknown_client(self):
        """Test functionality: authenticate unknown client."""
        ts = int(time.time())
        request = {
            "headers": {
                "X-Signature": "abc",
                "X-Timestamp": str(ts),
                "X-Client-ID": "unknown",
            },
            "body": "",
        }
        result = self.auth.authenticate(request)
        assert result.authenticated is False
        assert result.error == "Unknown client"

    def test_sign_request_unknown_client_raises(self):
        """Test functionality: sign request unknown client raises."""
        with pytest.raises(ValueError, match="Unknown client"):
            self.auth.sign_request("ghost", "body")


class TestCreateAuthenticator:
    """Verify the factory function returns correct authenticator types."""

    def test_creates_api_key_authenticator(self):
        """Test functionality: creates api key authenticator."""
        auth = create_authenticator(AuthType.API_KEY)
        assert isinstance(auth, APIKeyAuthenticator)

    def test_creates_bearer_token_authenticator(self):
        """Test functionality: creates bearer token authenticator."""
        auth = create_authenticator(AuthType.BEARER_TOKEN)
        assert isinstance(auth, BearerTokenAuthenticator)

    def test_creates_basic_authenticator(self):
        """Test functionality: creates basic authenticator."""
        auth = create_authenticator(AuthType.BASIC_AUTH)
        assert isinstance(auth, BasicAuthenticator)

    def test_creates_hmac_authenticator(self):
        """Test functionality: creates hmac authenticator."""
        auth = create_authenticator(AuthType.HMAC)
        assert isinstance(auth, HMACAuthenticator)

    def test_unsupported_type_raises(self):
        """Test functionality: unsupported type raises."""
        with pytest.raises(ValueError, match="Unsupported auth type"):
            create_authenticator(AuthType.OAUTH2)

    def test_passes_kwargs_to_constructor(self):
        """Test functionality: passes kwargs to constructor."""
        auth = create_authenticator(AuthType.API_KEY, header_name="X-Custom")
        assert auth.header_name == "X-Custom"
