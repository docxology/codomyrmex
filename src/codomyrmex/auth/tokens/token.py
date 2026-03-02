"""Token management for authentication.

This module provides token functionality including:
- Token data class
- Token generation and verification
- Token revocation and refreshing
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field

from codomyrmex.logging_monitoring.core.logger_config import get_logger

from .validator import TokenValidator

logger = get_logger(__name__)


@dataclass
class Token:
    """Authentication token."""

    token_id: str
    user_id: str
    permissions: list[str] = field(default_factory=list)
    expires_at: float | None = None
    created_at: float = field(default_factory=time.time)
    jwt: str | None = None  # Signed representation

    def is_expired(self) -> bool:
        """Check if token is expired."""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at

    def to_dict(self) -> dict:
        """Convert token to dictionary."""
        return {
            "token_id": self.token_id,
            "user_id": self.user_id,
            "permissions": self.permissions,
            "expires_at": self.expires_at,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Token:
        """Create token from dictionary."""
        return cls(
            token_id=data["token_id"],
            user_id=data["user_id"],
            permissions=data.get("permissions", []),
            expires_at=data.get("expires_at"),
            created_at=data.get("created_at", time.time()),
        )


class TokenManager:
    """Manager for token operations."""

    def __init__(self, secret: str | None = None):
        """Initialize token manager.

        Args:
            secret: Secret key for token signing
        """
        self.secret = secret or "default_secret_change_in_production"
        self.validator = TokenValidator(self.secret)
        self._tokens: dict[str, Token] = {}
        self._revoked_tokens: set[str] = set()

    def create_token(self, user_id: str, permissions: list[str] | None = None, ttl: int = 3600) -> Token:
        """Create a new authentication token.

        Args:
            user_id: User identifier
            permissions: List of permissions
            ttl: Time-to-live in seconds. 0 = no expiry.

        Returns:
            Token object
        """
        token_id = str(uuid.uuid4())
        expires_at = time.time() + ttl if ttl > 0 else None

        token = Token(
            token_id=token_id,
            user_id=user_id,
            permissions=permissions or [],
            expires_at=expires_at,
        )

        # Create signed JWT-like string
        token.jwt = self.validator.sign_token_data(token.to_dict())

        self._tokens[token_id] = token
        return token

    def validate_token(self, token: Token | str) -> bool:
        """Validate a token object or signed string.

        Args:
            token: Token object or signed token string

        Returns:
            True if token is valid
        """
        if isinstance(token, str):
            # Validate signed string
            data = self.validator.validate_signed_token(token)
            if not data:
                return False
            token_id = data.get("token_id")
            if not token_id:
                return False
        else:
            token_id = token.token_id
            if token.is_expired():
                return False

        if token_id in self._revoked_tokens:
            return False

        if token_id not in self._tokens:
            # We don't have it in memory, but if it was signed correctly
            # and not expired, in a stateless system it might be valid.
            # However, this implementation tracks tokens.
            return False

        return True

    def revoke_token(self, token: Token | str) -> bool:
        """Revoke a token.

        Args:
            token: Token object or token ID or signed string

        Returns:
            True if revocation successful
        """
        token_id = None
        if isinstance(token, str):
            # Try as signed string first
            data = self.validator.validate_signed_token(token)
            if data:
                token_id = data.get("token_id")
            else:
                # Fallback: assume it's just a token_id
                token_id = token
        else:
            token_id = token.token_id

        if not token_id:
            return False

        self._revoked_tokens.add(token_id)
        self._tokens.pop(token_id, None)
        return True

    def refresh_token(self, token: Token, ttl: int = 3600) -> Token | None:
        """Refresh an expired or soon-to-expire token.

        Args:
            token: Current token
            ttl: New time-to-live in seconds

        Returns:
            New token if refresh successful, None otherwise
        """
        if not self.validate_token(token):
            return None

        # Create new token with same permissions
        new_token = self.create_token(token.user_id, token.permissions, ttl)
        # Revoke old token
        self.revoke_token(token)
        return new_token
