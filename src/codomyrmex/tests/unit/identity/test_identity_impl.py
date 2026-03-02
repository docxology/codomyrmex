"""Tests for identity module auth system -- zero-mock policy enforced.

Covers AuthToken, AuthEvent, PasswordProvider, TokenProvider, Identity
orchestrator, session management, audit logging, and create_identity factory.
No mocks, stubs, or monkeypatch.
"""

import time

import pytest

from codomyrmex.identity.identity import (
    AuthEvent,
    AuthProvider,
    AuthToken,
    Identity,
    PasswordProvider,
    TokenProvider,
    create_identity,
)


@pytest.mark.unit
class TestAuthToken:
    """Tests for the AuthToken dataclass."""

    def test_not_expired_for_future_expiry(self):
        """AuthToken.is_expired returns False for future expiry."""
        token = AuthToken(
            token="abc123",
            user_id="user1",
            issued_at=time.time(),
            expires_at=time.time() + 3600,
        )
        assert token.is_expired is False

    def test_expired_for_past_expiry(self):
        """AuthToken.is_expired returns True for past expiry."""
        token = AuthToken(
            token="abc123",
            user_id="user1",
            issued_at=time.time() - 7200,
            expires_at=time.time() - 3600,
        )
        assert token.is_expired is True

    def test_remaining_seconds_positive(self):
        """AuthToken.remaining_seconds returns positive for valid token."""
        token = AuthToken(
            token="abc123",
            user_id="user1",
            issued_at=time.time(),
            expires_at=time.time() + 3600,
        )
        assert token.remaining_seconds > 0

    def test_remaining_seconds_zero_for_expired(self):
        """AuthToken.remaining_seconds returns 0.0 for expired token."""
        token = AuthToken(
            token="abc123",
            user_id="user1",
            issued_at=time.time() - 7200,
            expires_at=time.time() - 3600,
        )
        assert token.remaining_seconds == 0.0

    def test_default_scopes_empty(self):
        """AuthToken scopes default to empty list."""
        token = AuthToken(
            token="t", user_id="u", issued_at=0.0, expires_at=0.0,
        )
        assert token.scopes == []

    def test_custom_scopes(self):
        """AuthToken accepts custom scopes."""
        token = AuthToken(
            token="t", user_id="u",
            issued_at=0.0, expires_at=0.0,
            scopes=["read", "write"],
        )
        assert "read" in token.scopes
        assert "write" in token.scopes


@pytest.mark.unit
class TestAuthEvent:
    """Tests for the AuthEvent dataclass."""

    def test_creation_with_required_fields(self):
        """AuthEvent can be created with required fields."""
        event = AuthEvent(user_id="alice", event_type="login")
        assert event.user_id == "alice"
        assert event.event_type == "login"
        assert event.timestamp > 0

    def test_default_metadata_empty(self):
        """AuthEvent metadata defaults to empty dict."""
        event = AuthEvent(user_id="bob", event_type="logout")
        assert event.metadata == {}

    def test_custom_metadata(self):
        """AuthEvent accepts custom metadata."""
        event = AuthEvent(
            user_id="charlie",
            event_type="failed",
            metadata={"reason": "bad password"},
        )
        assert event.metadata["reason"] == "bad password"


@pytest.mark.unit
class TestAuthProviderABC:
    """Tests for AuthProvider abstract base class."""

    def test_is_abstract(self):
        """AuthProvider is abstract and cannot be instantiated."""
        import abc
        assert issubclass(AuthProvider, abc.ABC)

    def test_has_authenticate_method(self):
        """AuthProvider declares authenticate as abstract."""
        assert hasattr(AuthProvider, "authenticate")


@pytest.mark.unit
class TestPasswordProvider:
    """Tests for the PasswordProvider class."""

    def test_register_and_authenticate(self):
        """PasswordProvider authenticates registered users."""
        prov = PasswordProvider()
        prov.register("alice", "s3cret")
        assert prov.authenticate({"user_id": "alice", "password": "s3cret"}) is True

    def test_wrong_password(self):
        """PasswordProvider rejects wrong password."""
        prov = PasswordProvider()
        prov.register("bob", "correct")
        assert prov.authenticate({"user_id": "bob", "password": "wrong"}) is False

    def test_unknown_user(self):
        """PasswordProvider rejects unknown user."""
        prov = PasswordProvider()
        assert prov.authenticate({"user_id": "nobody", "password": "x"}) is False

    def test_empty_credentials(self):
        """PasswordProvider handles empty credentials dict."""
        prov = PasswordProvider()
        assert prov.authenticate({}) is False

    def test_register_overwrites_previous(self):
        """PasswordProvider.register overwrites existing password."""
        prov = PasswordProvider()
        prov.register("alice", "old_pass")
        prov.register("alice", "new_pass")
        assert prov.authenticate({"user_id": "alice", "password": "new_pass"}) is True
        assert prov.authenticate({"user_id": "alice", "password": "old_pass"}) is False

    def test_multiple_users(self):
        """PasswordProvider authenticates multiple users independently."""
        prov = PasswordProvider()
        prov.register("alice", "pass_a")
        prov.register("bob", "pass_b")
        assert prov.authenticate({"user_id": "alice", "password": "pass_a"}) is True
        assert prov.authenticate({"user_id": "bob", "password": "pass_b"}) is True
        assert prov.authenticate({"user_id": "alice", "password": "pass_b"}) is False


@pytest.mark.unit
class TestTokenProvider:
    """Tests for the TokenProvider class."""

    def test_create_and_authenticate(self):
        """TokenProvider authenticates with issued token."""
        prov = TokenProvider()
        token = prov.create_token()
        assert prov.authenticate({"token": token}) is True

    def test_invalid_token(self):
        """TokenProvider rejects invalid token."""
        prov = TokenProvider()
        assert prov.authenticate({"token": "invalid_token_xyz"}) is False

    def test_revoke_token(self):
        """TokenProvider rejects revoked token."""
        prov = TokenProvider()
        token = prov.create_token()
        assert prov.revoke_token(token) is True
        assert prov.authenticate({"token": token}) is False

    def test_revoke_nonexistent(self):
        """TokenProvider.revoke_token returns False for unknown token."""
        prov = TokenProvider()
        assert prov.revoke_token("nonexistent_token") is False

    def test_tokens_are_unique(self):
        """TokenProvider generates unique tokens."""
        prov = TokenProvider()
        tokens = [prov.create_token() for _ in range(50)]
        assert len(set(tokens)) == 50

    def test_empty_credentials(self):
        """TokenProvider handles empty credentials dict."""
        prov = TokenProvider()
        assert prov.authenticate({}) is False


@pytest.mark.unit
class TestIdentityLogin:
    """Tests for Identity.login."""

    def setup_method(self):
        self.ident = Identity()
        self.prov = PasswordProvider()
        self.prov.register("alice", "s3cret")
        self.ident.register_provider("password", self.prov)

    def test_login_valid_credentials(self):
        """Identity.login returns AuthToken for valid credentials."""
        token = self.ident.login("alice", {"user_id": "alice", "password": "s3cret"})
        assert token is not None
        assert token.user_id == "alice"
        assert not token.is_expired

    def test_login_wrong_password(self):
        """Identity.login returns None for wrong password."""
        token = self.ident.login("alice", {"user_id": "alice", "password": "wrong"})
        assert token is None

    def test_login_unknown_provider(self):
        """Identity.login returns None for unknown provider."""
        token = self.ident.login("alice", {}, provider="nonexistent")
        assert token is None

    def test_login_with_scopes(self):
        """Identity.login accepts scopes and stores them."""
        token = self.ident.login(
            "alice",
            {"user_id": "alice", "password": "s3cret"},
            scopes=["read", "write"],
        )
        assert token is not None
        assert "read" in token.scopes
        assert "write" in token.scopes

    def test_login_without_scopes(self):
        """Identity.login defaults to empty scopes."""
        token = self.ident.login("alice", {"user_id": "alice", "password": "s3cret"})
        assert token is not None
        assert token.scopes == []


@pytest.mark.unit
class TestIdentitySession:
    """Tests for Identity session management."""

    def setup_method(self):
        self.ident = Identity()
        self.prov = PasswordProvider()
        self.prov.register("u", "p")
        self.ident.register_provider("password", self.prov)

    def test_validate_token_valid(self):
        """Identity.validate_token returns True for valid session."""
        token = self.ident.login("u", {"user_id": "u", "password": "p"})
        assert self.ident.validate_token(token.token) is True

    def test_validate_invalid_token(self):
        """Identity.validate_token returns False for unknown token."""
        assert self.ident.validate_token("not_a_real_token") is False

    def test_get_session(self):
        """Identity.get_session returns AuthToken for valid session."""
        token = self.ident.login("u", {"user_id": "u", "password": "p"})
        session = self.ident.get_session(token.token)
        assert session is not None
        assert session.user_id == "u"

    def test_get_session_invalid(self):
        """Identity.get_session returns None for invalid token."""
        assert self.ident.get_session("invalid") is None

    def test_logout(self):
        """Identity.logout invalidates session."""
        token = self.ident.login("u", {"user_id": "u", "password": "p"})
        assert self.ident.logout(token.token) is True
        assert self.ident.validate_token(token.token) is False

    def test_logout_invalid_token(self):
        """Identity.logout returns False for unknown token."""
        assert self.ident.logout("invalid") is False

    def test_refresh_token(self):
        """Identity.refresh_token returns new token."""
        old_token = self.ident.login("u", {"user_id": "u", "password": "p"})
        new_token = self.ident.refresh_token(old_token.token)

        assert new_token is not None
        assert new_token.token != old_token.token
        assert new_token.user_id == "u"
        assert self.ident.validate_token(new_token.token) is True

    def test_refresh_invalidates_old_token(self):
        """Identity.refresh_token invalidates the old session."""
        old_token = self.ident.login("u", {"user_id": "u", "password": "p"})
        self.ident.refresh_token(old_token.token)
        assert self.ident.validate_token(old_token.token) is False

    def test_refresh_invalid_token(self):
        """Identity.refresh_token returns None for unknown token."""
        assert self.ident.refresh_token("invalid") is None

    def test_active_session_count(self):
        """Identity.active_session_count reflects active sessions."""
        assert self.ident.active_session_count == 0

        t1 = self.ident.login("u", {"user_id": "u", "password": "p"})
        assert self.ident.active_session_count == 1

        self.prov.register("u2", "p2")
        t2 = self.ident.login("u2", {"user_id": "u2", "password": "p2"})
        assert self.ident.active_session_count == 2

        self.ident.logout(t1.token)
        assert self.ident.active_session_count == 1


@pytest.mark.unit
class TestIdentityAuditLog:
    """Tests for Identity audit logging."""

    def setup_method(self):
        self.ident = Identity()
        self.prov = PasswordProvider()
        self.prov.register("u", "p")
        self.ident.register_provider("password", self.prov)

    def test_audit_log_records_login_and_logout(self):
        """Identity.audit_log records auth events."""
        token = self.ident.login("u", {"user_id": "u", "password": "p"})
        self.ident.logout(token.token)

        log = self.ident.audit_log
        assert len(log) >= 2
        event_types = [e.event_type for e in log]
        assert "login" in event_types
        assert "logout" in event_types

    def test_audit_log_records_failed_login(self):
        """Identity.audit_log records failed login attempts."""
        self.ident.login("u", {"user_id": "u", "password": "wrong"})
        log = self.ident.audit_log
        event_types = [e.event_type for e in log]
        assert "failed" in event_types

    def test_audit_log_is_copy(self):
        """audit_log returns a copy, not the internal list."""
        log = self.ident.audit_log
        log.append("bad data")
        assert len(self.ident.audit_log) == 0

    def test_audit_log_records_token_refresh(self):
        """audit_log records token_refresh events."""
        token = self.ident.login("u", {"user_id": "u", "password": "p"})
        self.ident.refresh_token(token.token)
        log = self.ident.audit_log
        event_types = [e.event_type for e in log]
        assert "token_refresh" in event_types


@pytest.mark.unit
class TestIdentityMultipleProviders:
    """Tests for Identity with multiple providers."""

    def test_register_and_use_token_provider(self):
        """Identity works with TokenProvider."""
        ident = Identity()
        tok_prov = TokenProvider()
        api_key = tok_prov.create_token()
        ident.register_provider("token", tok_prov)

        token = ident.login("api_user", {"token": api_key}, provider="token")
        assert token is not None
        assert token.user_id == "api_user"

    def test_multiple_provider_types(self):
        """Identity supports both password and token providers simultaneously."""
        ident = Identity()

        pw_prov = PasswordProvider()
        pw_prov.register("alice", "pass")
        ident.register_provider("password", pw_prov)

        tok_prov = TokenProvider()
        api_key = tok_prov.create_token()
        ident.register_provider("token", tok_prov)

        pw_token = ident.login("alice", {"user_id": "alice", "password": "pass"}, provider="password")
        api_token = ident.login("bot", {"token": api_key}, provider="token")

        assert pw_token is not None
        assert api_token is not None
        assert ident.active_session_count == 2


@pytest.mark.unit
class TestCreateIdentityFactory:
    """Tests for the create_identity factory function."""

    def test_returns_identity_instance(self):
        """create_identity() returns Identity instance."""
        ident = create_identity()
        assert isinstance(ident, Identity)

    def test_accepts_config(self):
        """create_identity accepts config dict."""
        ident = create_identity(config={"session_ttl": 7200})
        assert isinstance(ident, Identity)
        assert ident.config == {"session_ttl": 7200}

    def test_default_config_is_empty(self):
        """create_identity with no args has empty config."""
        ident = create_identity()
        assert ident.config == {}


@pytest.mark.unit
class TestIdentityCustomTTL:
    """Tests for Identity with custom session TTL."""

    def test_custom_session_ttl(self):
        """Identity uses custom session_ttl for token expiry."""
        ident = Identity(session_ttl=10.0)
        prov = PasswordProvider()
        prov.register("u", "p")
        ident.register_provider("password", prov)

        token = ident.login("u", {"user_id": "u", "password": "p"})
        assert token is not None
        # Token should expire within 10 seconds, so remaining should be <= 10
        assert token.remaining_seconds <= 10.0
        assert token.remaining_seconds > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
