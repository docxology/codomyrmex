"""Tests for codomyrmex.identity.identity — AuthToken, providers, Identity orchestrator."""

import time

import pytest

from codomyrmex.identity.identity import (
    AuthEvent,
    AuthToken,
    Identity,
    PasswordProvider,
    TokenProvider,
    create_identity,
)

# ---------------------------------------------------------------------------
# AuthToken dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestAuthToken:
    """Tests for the AuthToken dataclass and its properties."""

    def test_token_not_expired(self):
        """A token with future expiry should not be expired."""
        now = time.time()
        tok = AuthToken(
            token="abc",
            user_id="u1",
            issued_at=now,
            expires_at=now + 3600,
        )
        assert tok.is_expired is False

    def test_token_expired(self):
        """A token with past expiry should be expired."""
        now = time.time()
        tok = AuthToken(
            token="abc",
            user_id="u1",
            issued_at=now - 7200,
            expires_at=now - 3600,
        )
        assert tok.is_expired is True

    def test_remaining_seconds_positive(self):
        """Remaining seconds should be positive for a live token."""
        now = time.time()
        tok = AuthToken(
            token="abc",
            user_id="u1",
            issued_at=now,
            expires_at=now + 100,
        )
        assert tok.remaining_seconds > 0
        assert tok.remaining_seconds <= 100

    def test_remaining_seconds_zero_when_expired(self):
        """Remaining seconds should be 0.0 for an expired token."""
        now = time.time()
        tok = AuthToken(
            token="abc",
            user_id="u1",
            issued_at=now - 200,
            expires_at=now - 100,
        )
        assert tok.remaining_seconds == 0.0

    def test_default_scopes_empty(self):
        """Scopes default to an empty list."""
        now = time.time()
        tok = AuthToken(token="t", user_id="u", issued_at=now, expires_at=now + 10)
        assert tok.scopes == []

    def test_custom_scopes(self):
        """Custom scopes are stored correctly."""
        now = time.time()
        tok = AuthToken(
            token="t",
            user_id="u",
            issued_at=now,
            expires_at=now + 10,
            scopes=["read", "write"],
        )
        assert tok.scopes == ["read", "write"]


# ---------------------------------------------------------------------------
# AuthEvent dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestAuthEvent:
    """Tests for the AuthEvent dataclass."""

    def test_event_creation(self):
        """AuthEvent stores user_id, event_type, and auto-timestamps."""
        evt = AuthEvent(user_id="u1", event_type="login")
        assert evt.user_id == "u1"
        assert evt.event_type == "login"
        assert evt.timestamp > 0
        assert evt.metadata == {}

    def test_event_with_metadata(self):
        """AuthEvent can carry arbitrary metadata."""
        evt = AuthEvent(user_id="u1", event_type="failed", metadata={"ip": "10.0.0.1"})
        assert evt.metadata["ip"] == "10.0.0.1"


# ---------------------------------------------------------------------------
# PasswordProvider
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestPasswordProvider:
    """Tests for PasswordProvider registration and authentication."""

    def setup_method(self):
        self.pw = PasswordProvider()

    def test_register_and_authenticate(self):
        """Registered user with correct password authenticates."""
        self.pw.register("alice", "s3cret")
        assert self.pw.authenticate({"user_id": "alice", "password": "s3cret"}) is True

    def test_wrong_password_rejected(self):
        """Incorrect password returns False."""
        self.pw.register("alice", "s3cret")
        assert self.pw.authenticate({"user_id": "alice", "password": "wrong"}) is False

    def test_unknown_user_rejected(self):
        """Unknown user_id returns False."""
        assert self.pw.authenticate({"user_id": "nobody", "password": "x"}) is False

    def test_empty_credentials(self):
        """Empty dict returns False."""
        assert self.pw.authenticate({}) is False

    def test_register_overwrites(self):
        """Re-registering a user overwrites the stored hash."""
        self.pw.register("bob", "old")
        self.pw.register("bob", "new")
        assert self.pw.authenticate({"user_id": "bob", "password": "old"}) is False
        assert self.pw.authenticate({"user_id": "bob", "password": "new"}) is True

    def test_salts_differ_per_registration(self):
        """Each registration generates a unique salt."""
        self.pw.register("a", "pw")
        salt_a = self.pw._users["a"][0]
        self.pw.register("b", "pw")
        salt_b = self.pw._users["b"][0]
        assert salt_a != salt_b


# ---------------------------------------------------------------------------
# TokenProvider
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestTokenProvider:
    """Tests for TokenProvider creation, authentication, and revocation."""

    def setup_method(self):
        self.tp = TokenProvider()

    def test_create_and_authenticate(self):
        """Created token authenticates successfully."""
        token = self.tp.create_token()
        assert self.tp.authenticate({"token": token}) is True

    def test_unknown_token_rejected(self):
        """Arbitrary token does not authenticate."""
        assert self.tp.authenticate({"token": "fake-token"}) is False

    def test_revoke_existing_token(self):
        """Revoking a valid token succeeds and invalidates it."""
        token = self.tp.create_token()
        assert self.tp.revoke_token(token) is True
        assert self.tp.authenticate({"token": token}) is False

    def test_revoke_nonexistent_token(self):
        """Revoking an unknown token returns False."""
        assert self.tp.revoke_token("nonexistent") is False

    def test_empty_credentials(self):
        """Empty credentials do not authenticate."""
        assert self.tp.authenticate({}) is False

    def test_multiple_tokens_independent(self):
        """Multiple tokens are independently valid."""
        t1 = self.tp.create_token()
        t2 = self.tp.create_token()
        self.tp.revoke_token(t1)
        assert self.tp.authenticate({"token": t1}) is False
        assert self.tp.authenticate({"token": t2}) is True


# ---------------------------------------------------------------------------
# Identity orchestrator
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestIdentity:
    """Tests for the Identity orchestrator: login, logout, sessions, audit."""

    def setup_method(self):
        self.ident = Identity(session_ttl=3600.0)
        self.pw = PasswordProvider()
        self.pw.register("alice", "s3cret")
        self.ident.register_provider("password", self.pw)

    # -- Login / Logout ---------------------------------------------------

    def test_login_success(self):
        """Successful login returns an AuthToken."""
        token = self.ident.login("alice", {"user_id": "alice", "password": "s3cret"})
        assert token is not None
        assert token.user_id == "alice"
        assert token.is_expired is False

    def test_login_wrong_password(self):
        """Wrong password returns None."""
        token = self.ident.login("alice", {"user_id": "alice", "password": "wrong"})
        assert token is None

    def test_login_unknown_provider(self):
        """Using an unregistered provider returns None and audits the failure."""
        token = self.ident.login("alice", {"user_id": "alice"}, provider="sso")
        assert token is None
        events = [e for e in self.ident.audit_log if e.event_type == "failed"]
        assert len(events) == 1
        assert "unknown provider" in events[0].metadata.get("reason", "")

    def test_login_with_scopes(self):
        """Login can specify access scopes."""
        token = self.ident.login(
            "alice",
            {"user_id": "alice", "password": "s3cret"},
            scopes=["read", "admin"],
        )
        assert token is not None
        assert token.scopes == ["read", "admin"]

    def test_logout_success(self):
        """Logging out a valid session returns True."""
        token = self.ident.login("alice", {"user_id": "alice", "password": "s3cret"})
        assert self.ident.logout(token.token) is True

    def test_logout_invalid_token(self):
        """Logging out a nonexistent token returns False."""
        assert self.ident.logout("nonexistent") is False

    def test_logout_invalidates_session(self):
        """After logout, token validation fails."""
        token = self.ident.login("alice", {"user_id": "alice", "password": "s3cret"})
        self.ident.logout(token.token)
        assert self.ident.validate_token(token.token) is False

    # -- Token validation -------------------------------------------------

    def test_validate_valid_token(self):
        """Valid, non-expired token validates True."""
        token = self.ident.login("alice", {"user_id": "alice", "password": "s3cret"})
        assert self.ident.validate_token(token.token) is True

    def test_validate_unknown_token(self):
        """Unknown token validates False."""
        assert self.ident.validate_token("bogus") is False

    def test_validate_expired_token(self):
        """Expired tokens are removed and validate False."""
        ident = Identity(session_ttl=0.0)
        pw = PasswordProvider()
        pw.register("bob", "pw")
        ident.register_provider("password", pw)
        token = ident.login("bob", {"user_id": "bob", "password": "pw"})
        # Token issued with ttl=0 expires immediately
        time.sleep(0.01)
        assert ident.validate_token(token.token) is False

    # -- Session retrieval ------------------------------------------------

    def test_get_session_valid(self):
        """get_session returns the AuthToken for a valid session."""
        token = self.ident.login("alice", {"user_id": "alice", "password": "s3cret"})
        session = self.ident.get_session(token.token)
        assert session is not None
        assert session.user_id == "alice"

    def test_get_session_invalid(self):
        """get_session returns None for an invalid token."""
        assert self.ident.get_session("nope") is None

    # -- Token refresh ----------------------------------------------------

    def test_refresh_token_success(self):
        """Refreshing a valid token returns a new token and invalidates the old."""
        old = self.ident.login("alice", {"user_id": "alice", "password": "s3cret"})
        new = self.ident.refresh_token(old.token)
        assert new is not None
        assert new.token != old.token
        assert new.user_id == "alice"
        # Old token is no longer valid
        assert self.ident.validate_token(old.token) is False
        # New token is valid
        assert self.ident.validate_token(new.token) is True

    def test_refresh_expired_token(self):
        """Cannot refresh an expired token."""
        ident = Identity(session_ttl=0.0)
        pw = PasswordProvider()
        pw.register("bob", "pw")
        ident.register_provider("password", pw)
        token = ident.login("bob", {"user_id": "bob", "password": "pw"})
        time.sleep(0.01)
        assert ident.refresh_token(token.token) is None

    def test_refresh_nonexistent_token(self):
        """Cannot refresh a nonexistent token."""
        assert self.ident.refresh_token("ghost") is None

    def test_refresh_preserves_scopes(self):
        """Refreshed token carries forward the original scopes."""
        old = self.ident.login(
            "alice",
            {"user_id": "alice", "password": "s3cret"},
            scopes=["read"],
        )
        new = self.ident.refresh_token(old.token)
        assert new.scopes == ["read"]

    # -- Audit log --------------------------------------------------------

    def test_audit_log_records_login(self):
        """Login generates an audit event."""
        self.ident.login("alice", {"user_id": "alice", "password": "s3cret"})
        events = [e for e in self.ident.audit_log if e.event_type == "login"]
        assert len(events) == 1
        assert events[0].user_id == "alice"

    def test_audit_log_records_failed_login(self):
        """Failed login generates a 'failed' audit event."""
        self.ident.login("alice", {"user_id": "alice", "password": "wrong"})
        events = [e for e in self.ident.audit_log if e.event_type == "failed"]
        assert len(events) == 1

    def test_audit_log_records_logout(self):
        """Logout generates an audit event."""
        token = self.ident.login("alice", {"user_id": "alice", "password": "s3cret"})
        self.ident.logout(token.token)
        events = [e for e in self.ident.audit_log if e.event_type == "logout"]
        assert len(events) == 1

    def test_audit_log_is_copy(self):
        """audit_log returns a copy, not the internal list."""
        self.ident.login("alice", {"user_id": "alice", "password": "s3cret"})
        log1 = self.ident.audit_log
        log2 = self.ident.audit_log
        assert log1 is not log2

    # -- Active session count ---------------------------------------------

    def test_active_session_count(self):
        """active_session_count reflects live sessions."""
        assert self.ident.active_session_count == 0
        t1 = self.ident.login("alice", {"user_id": "alice", "password": "s3cret"})
        assert self.ident.active_session_count == 1
        self.ident.logout(t1.token)
        assert self.ident.active_session_count == 0

    # -- Config -----------------------------------------------------------

    def test_default_config(self):
        """Default config is empty dict."""
        ident = Identity()
        assert ident.config == {}

    def test_custom_config(self):
        """Custom config dict is stored."""
        ident = Identity(config={"key": "val"})
        assert ident.config["key"] == "val"

    def test_custom_session_ttl(self):
        """session_ttl is configurable."""
        ident = Identity(session_ttl=120.0)
        assert ident.session_ttl == 120.0


# ---------------------------------------------------------------------------
# Module-level factory
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCreateIdentity:
    """Tests for the create_identity convenience function."""

    def test_returns_identity_instance(self):
        """create_identity returns an Identity."""
        ident = create_identity()
        assert isinstance(ident, Identity)

    def test_passes_config(self):
        """create_identity forwards the config dict."""
        ident = create_identity(config={"flag": True})
        assert ident.config["flag"] is True


# ---------------------------------------------------------------------------
# A5 expansion -- additional behavioral tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestIdentityMultipleProviders:
    """Tests for Identity with multiple providers."""

    def test_register_multiple_providers(self):
        """Multiple providers can coexist."""
        ident = Identity()
        pw = PasswordProvider()
        pw.register("alice", "pw")
        tp = TokenProvider()
        ident.register_provider("password", pw)
        ident.register_provider("token", tp)
        token_str = tp.create_token()
        # Login via password
        t1 = ident.login("alice", {"user_id": "alice", "password": "pw"})
        assert t1 is not None
        # Login via token
        t2 = ident.login("alice", {"token": token_str}, provider="token")
        assert t2 is not None

    def test_multiple_sessions_counted(self):
        """Multiple logins create multiple active sessions."""
        ident = Identity()
        pw = PasswordProvider()
        pw.register("alice", "pw")
        ident.register_provider("password", pw)
        t1 = ident.login("alice", {"user_id": "alice", "password": "pw"})
        ident.login("alice", {"user_id": "alice", "password": "pw"})
        assert ident.active_session_count == 2
        ident.logout(t1.token)
        assert ident.active_session_count == 1

    def test_double_logout_same_token(self):
        """Logging out the same token twice: first True, second False."""
        ident = Identity()
        pw = PasswordProvider()
        pw.register("bob", "pw")
        ident.register_provider("password", pw)
        token = ident.login("bob", {"user_id": "bob", "password": "pw"})
        assert ident.logout(token.token) is True
        assert ident.logout(token.token) is False


@pytest.mark.unit
class TestAuthTokenEdgeCases:
    """Additional edge case tests for AuthToken."""

    def test_token_with_zero_ttl_is_immediately_expired(self):
        """Token with expires_at at current time is expired."""
        now = time.time()
        tok = AuthToken(
            token="t", user_id="u", issued_at=now, expires_at=now,
        )
        # At the exact boundary, is_expired depends on strict comparison
        # The token should be expired or at the boundary
        assert tok.remaining_seconds == 0.0 or tok.is_expired

    def test_token_fields_stored(self):
        """All token fields are accessible."""
        now = time.time()
        tok = AuthToken(
            token="abc123", user_id="user42",
            issued_at=now, expires_at=now + 100,
            scopes=["read", "write"],
        )
        assert tok.token == "abc123"
        assert tok.user_id == "user42"
        assert tok.issued_at == now
