"""Identity Module — Identity Provider & Authentication Orchestration.

Provides a configurable identity system supporting:
- Multiple authentication providers (password, token, bio-cognitive)
- Session management with expiry and token refresh
- Authentication event auditing
- Integration with the persona/bio-cognitive subsystems
"""

from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
import secrets
import time
from dataclasses import dataclass, field
from typing import Any

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


@dataclass
class AuthToken:
    """An authentication token with expiry."""

    token: str
    user_id: str
    issued_at: float
    expires_at: float
    scopes: list[str] = field(default_factory=list)

    @property
    def is_expired(self) -> bool:
        """Execute Is Expired operations natively."""
        return time.time() > self.expires_at

    @property
    def remaining_seconds(self) -> float:
        """Execute Remaining Seconds operations natively."""
        return max(0.0, self.expires_at - time.time())


@dataclass
class AuthEvent:
    """An authentication event for audit logging."""

    user_id: str
    event_type: str  # "login", "logout", "failed", "token_refresh"
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


class AuthProvider(ABC):
    """Pluggable authentication backend."""

    @abstractmethod
    def authenticate(self, credentials: dict[str, Any]) -> bool:
        """Return True if credentials are valid."""
        raise NotImplementedError


class PasswordProvider(AuthProvider):
    """Password-based authentication using salted SHA-256 hashing."""

    def __init__(self) -> None:
        """Execute   Init   operations natively."""
        self._users: dict[str, tuple[str, str]] = {}  # user_id -> (salt, hash)

    def register(self, user_id: str, password: str) -> None:
        """Register a user with a password."""
        salt = secrets.token_hex(16)
        pw_hash = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
        self._users[user_id] = (salt, pw_hash)

    def authenticate(self, credentials: dict[str, Any]) -> bool:
        """Execute Authenticate operations natively."""
        user_id = credentials.get("user_id", "")
        password = credentials.get("password", "")
        if user_id not in self._users:
            return False
        salt, expected_hash = self._users[user_id]
        actual_hash = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
        return secrets.compare_digest(actual_hash, expected_hash)


class TokenProvider(AuthProvider):
    """API-key / bearer token authentication."""

    def __init__(self) -> None:
        """Execute   Init   operations natively."""
        self._valid_tokens: set[str] = set()

    def create_token(self) -> str:
        """Issue a new API token."""
        token = secrets.token_urlsafe(32)
        self._valid_tokens.add(token)
        return token

    def revoke_token(self, token: str) -> bool:
        """Revoke an existing token."""
        if token in self._valid_tokens:
            self._valid_tokens.discard(token)
            return True
        return False

    def authenticate(self, credentials: dict[str, Any]) -> bool:
        """Execute Authenticate operations natively."""
        return credentials.get("token", "") in self._valid_tokens


class Identity:
    """Identity orchestrator with session management and audit logging.

    Supports pluggable auth providers, session tokens with TTL,
    scope-based access, and event auditing.

    Example::

        ident = Identity()
        pw = PasswordProvider()
        pw.register("alice", "s3cret")
        ident.register_provider("password", pw)

        token = ident.login("alice", {"user_id": "alice", "password": "s3cret"}, provider="password")
        assert token is not None
        assert ident.validate_token(token.token)
        ident.logout(token.token)
    """

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        session_ttl: float = 3600.0,
    ) -> None:
        """Execute   Init   operations natively."""
        self.config = config or {}
        self.session_ttl = session_ttl
        self._providers: dict[str, AuthProvider] = {}
        self._sessions: dict[str, AuthToken] = {}  # token_str -> AuthToken
        self._events: list[AuthEvent] = []
        logger.info("Identity system initialized (ttl=%.0fs)", session_ttl)

    # ── Provider registration ───────────────────────────────────────

    def register_provider(self, name: str, provider: AuthProvider) -> None:
        """Register an authentication provider."""
        self._providers[name] = provider
        logger.info("Registered auth provider: %s", name)

    # ── Login / Logout ──────────────────────────────────────────────

    def login(
        self,
        user_id: str,
        credentials: dict[str, Any],
        provider: str = "password",
        scopes: list[str] | None = None,
    ) -> AuthToken | None:
        """Authenticate and issue a session token.

        Returns:
            AuthToken if authentication succeeds, None otherwise.
        """
        prov = self._providers.get(provider)
        if prov is None:
            self._audit(user_id, "failed", {"reason": f"unknown provider: {provider}"})
            return None

        if not prov.authenticate(credentials):
            self._audit(user_id, "failed", {"provider": provider})
            return None

        now = time.time()
        token = AuthToken(
            token=secrets.token_urlsafe(32),
            user_id=user_id,
            issued_at=now,
            expires_at=now + self.session_ttl,
            scopes=scopes or [],
        )
        self._sessions[token.token] = token
        self._audit(user_id, "login", {"provider": provider})
        return token

    def logout(self, token_str: str) -> bool:
        """Invalidate a session token."""
        session = self._sessions.pop(token_str, None)
        if session:
            self._audit(session.user_id, "logout")
            return True
        return False

    # ── Token validation ────────────────────────────────────────────

    def validate_token(self, token_str: str) -> bool:
        """Check if a token is valid and not expired."""
        session = self._sessions.get(token_str)
        if session is None:
            return False
        if session.is_expired:
            del self._sessions[token_str]
            self._audit(session.user_id, "expired")
            return False
        return True

    def get_session(self, token_str: str) -> AuthToken | None:
        """Retrieve session info for a valid token."""
        if self.validate_token(token_str):
            return self._sessions.get(token_str)
        return None

    def refresh_token(self, token_str: str) -> AuthToken | None:
        """Extend a valid session by issuing a new token."""
        old = self._sessions.pop(token_str, None)
        if old is None or old.is_expired:
            return None
        now = time.time()
        new_token = AuthToken(
            token=secrets.token_urlsafe(32),
            user_id=old.user_id,
            issued_at=now,
            expires_at=now + self.session_ttl,
            scopes=old.scopes,
        )
        self._sessions[new_token.token] = new_token
        self._audit(old.user_id, "token_refresh")
        return new_token

    # ── Audit ───────────────────────────────────────────────────────

    def _audit(self, user_id: str, event_type: str, metadata: dict[str, Any] | None = None) -> None:
        """Execute  Audit operations natively."""
        event = AuthEvent(user_id=user_id, event_type=event_type, metadata=metadata or {})
        self._events.append(event)
        logger.info("Auth event: %s for %s", event_type, user_id)

    @property
    def audit_log(self) -> list[AuthEvent]:
        """Execute Audit Log operations natively."""
        return list(self._events)

    @property
    def active_session_count(self) -> int:
        """Execute Active Session Count operations natively."""
        return sum(1 for s in self._sessions.values() if not s.is_expired)


def create_identity(config: dict[str, Any] | None = None) -> Identity:
    """Create a new Identity instance."""
    return Identity(config)
