"""API key management with expiry, rate limits, and rotation.

Provides:
- API key generation with configurable prefix and entropy
- Expiry-based automatic invalidation
- Per-key rate limits (requests per period)
- Key rotation (issue new key, revoke old)
- Key listing and search
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


@dataclass
class APIKey:
    """Metadata for an issued API key."""

    key: str
    user_id: str
    permissions: list[str]
    created_at: float = field(default_factory=time.time)
    expires_at: float | None = None  # None = no expiry
    rate_limit: int = 0  # 0 = unlimited
    label: str = ""
    revoked: bool = False
    request_count: int = 0

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at

    @property
    def is_valid(self) -> bool:
        return not self.revoked and not self.is_expired


class APIKeyManager:
    """Manager for API key generation, validation, and lifecycle.

    Example::

        mgr = APIKeyManager(prefix="myapp")
        key_str = mgr.generate("alice", permissions=["read", "write"], ttl_seconds=3600)
        info = mgr.validate(key_str)
        assert info is not None and info.user_id == "alice"
    """

    def __init__(self, prefix: str = "codomyrmex") -> None:
        self._prefix = prefix
        self._keys: dict[str, APIKey] = {}

    def generate(
        self,
        user_id: str,
        permissions: list[str] | None = None,
        ttl_seconds: float | None = None,
        rate_limit: int = 0,
        label: str = "",
    ) -> str:
        """Generate a new API key.

        Args:
            user_id: Owner of the key.
            permissions: Granted permissions (default: ["read"]).
            ttl_seconds: Time-to-live in seconds. None = no expiry.
            rate_limit: Max requests per minute. 0 = unlimited.
            label: Human-readable label for the key.

        Returns:
            The generated API key string.
        """
        key_str = f"{self._prefix}_{secrets.token_urlsafe(32)}"
        now = time.time()
        api_key = APIKey(
            key=key_str,
            user_id=user_id,
            permissions=permissions or ["read"],
            created_at=now,
            expires_at=(now + ttl_seconds) if ttl_seconds else None,
            rate_limit=rate_limit,
            label=label,
        )
        self._keys[key_str] = api_key
        logger.info("Generated API key for %s (label=%s, ttl=%s)", user_id, label, ttl_seconds)
        return key_str

    def generate_api_key(self, user_id: str, permissions: list[str] | None = None) -> str:
        return self.generate(user_id, permissions=permissions)

    def validate(self, key_str: str) -> APIKey | None:
        """Validate an API key and return its metadata if valid.

        Returns None if the key is unknown, expired, or revoked.
        Also increments request_count on valid keys.
        """
        api_key = self._keys.get(key_str)
        if api_key is None:
            return None
        if not api_key.is_valid:
            return None
        api_key.request_count += 1
        return api_key

    def validate_api_key(self, api_key: str) -> dict | None:
        info = self.validate(api_key)
        if info is None:
            return None
        return {"user_id": info.user_id, "permissions": info.permissions}

    def revoke(self, key_str: str) -> bool:
        """Revoke an API key."""
        api_key = self._keys.get(key_str)
        if api_key is None:
            return False
        api_key.revoked = True
        logger.info("Revoked API key: %s...", key_str[:20])
        return True

    def revoke_api_key(self, api_key: str) -> bool:
        return self.revoke(api_key)

    def rotate(self, old_key_str: str, ttl_seconds: float | None = None) -> str | None:
        """Rotate an API key: revoke old, issue new with same permissions.

        Returns:
            New key string, or None if old key was invalid.
        """
        old = self._keys.get(old_key_str)
        if old is None:
            return None
        self.revoke(old_key_str)
        return self.generate(
            user_id=old.user_id,
            permissions=old.permissions,
            ttl_seconds=ttl_seconds,
            rate_limit=old.rate_limit,
            label=f"{old.label} (rotated)",
        )

    def list_keys(self, user_id: str | None = None, include_revoked: bool = False) -> list[APIKey]:
        """List API keys, optionally filtered by user and status.

        Args:
            user_id: Filter to a specific user.
            include_revoked: Whether to include revoked keys.
        """
        keys = list(self._keys.values())
        if user_id:
            keys = [k for k in keys if k.user_id == user_id]
        if not include_revoked:
            keys = [k for k in keys if not k.revoked]
        return keys

    def cleanup_expired(self) -> int:
        """Remove expired and revoked keys from memory. Returns count removed."""
        to_remove = [k for k, v in self._keys.items() if not v.is_valid]
        for key in to_remove:
            del self._keys[key]
        return len(to_remove)

    @property
    def active_count(self) -> int:
        return sum(1 for k in self._keys.values() if k.is_valid)

    @property
    def total_count(self) -> int:
        return len(self._keys)
