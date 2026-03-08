"""Credential rotation with TTL-aware caching and audit logging.

Provides automated credential lifecycle management for cloud providers
with configurable rotation policies, expiry tracking, and a pluggable
backend via the :class:`CredentialStore` protocol.

Example::

    rotator = CredentialRotator()
    rotator.register_provider("openai", lambda: os.environ["OPENAI_API_KEY"])

    # Get credential — rotates automatically when TTL expires
    cred = rotator.get_credential("openai")
    print(cred.value)

    # View rotation history
    for event in rotator.audit_log:
        print(event)
"""

from __future__ import annotations

import logging
import threading
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

logger = logging.getLogger(__name__)


@dataclass
class CredentialEntry:
    """A cached credential with lifecycle metadata.

    Attributes:
        key: Unique identifier for this credential.
        value: The credential secret value.
        provider: Provider name this credential belongs to.
        created_at: Unix timestamp when the credential was fetched.
        expires_at: Unix timestamp when the credential expires.
        rotation_id: Unique ID for this rotation cycle.
    """

    key: str
    value: str
    provider: str
    created_at: float = field(default_factory=time.time)
    expires_at: float = 0.0
    rotation_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])

    @property
    def is_expired(self) -> bool:
        """Check whether this credential has passed its expiry time."""
        if self.expires_at <= 0:
            return False
        return time.time() >= self.expires_at

    @property
    def remaining_seconds(self) -> float:
        """Seconds remaining before expiry (0 if already expired)."""
        if self.expires_at <= 0:
            return float("inf")
        return max(0.0, self.expires_at - time.time())


@dataclass(frozen=True)
class RotationPolicy:
    """Policy controlling when credentials should be rotated.

    Attributes:
        ttl_seconds: Time-to-live for cached credentials.
        max_age_seconds: Hard maximum age regardless of TTL.
        rotate_before_expiry_seconds: Pre-emptive rotation buffer.
    """

    ttl_seconds: float = 3600.0
    max_age_seconds: float = 86400.0
    rotate_before_expiry_seconds: float = 300.0


@dataclass
class AuditEvent:
    """Record of a credential lifecycle event.

    Attributes:
        provider: Provider name.
        event_type: One of ``"fetch"``, ``"rotate"``, ``"expire"``, ``"error"``.
        rotation_id: Rotation cycle ID.
        timestamp: Unix timestamp.
        details: Optional extra context.
    """

    provider: str
    event_type: str
    rotation_id: str
    timestamp: float = field(default_factory=time.time)
    details: str = ""


@runtime_checkable
class CredentialStore(Protocol):
    """Protocol for pluggable credential backends."""

    def save(self, entry: CredentialEntry) -> None:
        """Persist a credential entry."""
        ...

    def load(self, provider: str) -> CredentialEntry | None:
        """Load the current credential for *provider*."""
        ...

    def delete(self, provider: str) -> bool:
        """Delete stored credential for *provider*."""
        ...


class InMemoryCredentialStore:
    """In-memory credential store (default backend).

    Suitable for single-process use and testing.
    """

    def __init__(self) -> None:
        self._store: dict[str, CredentialEntry] = {}

    def save(self, entry: CredentialEntry) -> None:
        """Persist a credential entry in memory."""
        self._store[entry.provider] = entry

    def load(self, provider: str) -> CredentialEntry | None:
        """Load credential for *provider*."""
        return self._store.get(provider)

    def delete(self, provider: str) -> bool:
        """Delete credential for *provider*."""
        if provider in self._store:
            del self._store[provider]
            return True
        return False


CredentialFetcher = Callable[[], str]


class CredentialRotator:
    """Manages credential rotation with TTL caching and audit trail.

    Args:
        policy: Default rotation policy.
        store: Pluggable credential backend.

    Example::

        rotator = CredentialRotator(
            policy=RotationPolicy(ttl_seconds=1800)
        )
        rotator.register_provider("aws", fetch_aws_key)
        cred = rotator.get_credential("aws")
    """

    def __init__(
        self,
        policy: RotationPolicy | None = None,
        store: CredentialStore | None = None,
    ) -> None:
        self._policy = policy or RotationPolicy()
        self._store: CredentialStore = store or InMemoryCredentialStore()
        self._fetchers: dict[str, CredentialFetcher] = {}
        self._policies: dict[str, RotationPolicy] = {}
        self._audit: list[AuditEvent] = []
        self._lock = threading.Lock()

    @property
    def audit_log(self) -> list[AuditEvent]:
        """Return the full audit trail."""
        return list(self._audit)

    @property
    def registered_providers(self) -> list[str]:
        """List all registered provider names."""
        return list(self._fetchers.keys())

    def register_provider(
        self,
        provider: str,
        fetcher: CredentialFetcher,
        policy: RotationPolicy | None = None,
    ) -> None:
        """Register a credential fetcher for *provider*.

        Args:
            provider: Unique provider name.
            fetcher: Callable that returns the credential value.
            policy: Optional per-provider rotation policy.
        """
        with self._lock:
            self._fetchers[provider] = fetcher
            if policy:
                self._policies[provider] = policy
            logger.info("Registered credential provider: %s", provider)

    def get_credential(self, provider: str) -> CredentialEntry:
        """Get a valid credential, rotating if necessary.

        Args:
            provider: Provider name.

        Returns:
            A :class:`CredentialEntry` with a valid (non-expired) value.

        Raises:
            KeyError: If *provider* is not registered.
            RuntimeError: If the fetcher fails.
        """
        with self._lock:
            if provider not in self._fetchers:
                msg = f"Provider '{provider}' is not registered"
                raise KeyError(msg)

            existing = self._store.load(provider)
            policy = self._policies.get(provider, self._policy)

            if existing and not self._needs_rotation(existing, policy):
                return existing

            return self._rotate_locked(provider, policy)

    def rotate(self, provider: str) -> CredentialEntry:
        """Force an immediate rotation for *provider*.

        Args:
            provider: Provider name.

        Returns:
            The newly fetched :class:`CredentialEntry`.

        Raises:
            KeyError: If *provider* is not registered.
        """
        with self._lock:
            if provider not in self._fetchers:
                msg = f"Provider '{provider}' is not registered"
                raise KeyError(msg)

            policy = self._policies.get(provider, self._policy)
            return self._rotate_locked(provider, policy)

    def invalidate(self, provider: str) -> bool:
        """Invalidate the cached credential for *provider*.

        Args:
            provider: Provider name.

        Returns:
            ``True`` if a credential was invalidated.
        """
        with self._lock:
            deleted = self._store.delete(provider)
            if deleted:
                self._audit.append(
                    AuditEvent(
                        provider=provider,
                        event_type="invalidate",
                        rotation_id="",
                        details="Manual invalidation",
                    )
                )
            return deleted

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _needs_rotation(
        self, entry: CredentialEntry, policy: RotationPolicy
    ) -> bool:
        """Check whether *entry* should be rotated under *policy*."""
        now = time.time()

        # Hard expiry
        if entry.is_expired:
            return True

        # TTL exceeded
        age = now - entry.created_at
        if age >= policy.ttl_seconds:
            return True

        # Max age exceeded
        if age >= policy.max_age_seconds:
            return True

        # Pre-emptive rotation buffer
        if entry.expires_at > 0:
            remaining = entry.expires_at - now
            if remaining <= policy.rotate_before_expiry_seconds:
                return True

        return False

    def _rotate_locked(
        self, provider: str, policy: RotationPolicy
    ) -> CredentialEntry:
        """Fetch a new credential and store it (must be called under lock)."""
        fetcher = self._fetchers[provider]
        rotation_id = uuid.uuid4().hex[:12]

        try:
            value = fetcher()
        except Exception as exc:
            self._audit.append(
                AuditEvent(
                    provider=provider,
                    event_type="error",
                    rotation_id=rotation_id,
                    details=str(exc),
                )
            )
            msg = f"Credential fetch failed for '{provider}': {exc}"
            raise RuntimeError(msg) from exc

        now = time.time()
        entry = CredentialEntry(
            key=f"{provider}_credential",
            value=value,
            provider=provider,
            created_at=now,
            expires_at=now + policy.ttl_seconds,
            rotation_id=rotation_id,
        )

        self._store.save(entry)
        self._audit.append(
            AuditEvent(
                provider=provider,
                event_type="rotate",
                rotation_id=rotation_id,
                details=f"TTL={policy.ttl_seconds}s",
            )
        )

        logger.info(
            "Rotated credential for %s (id=%s, ttl=%ss)",
            provider,
            rotation_id,
            policy.ttl_seconds,
        )
        return entry


__all__ = [
    "AuditEvent",
    "CredentialEntry",
    "CredentialRotator",
    "CredentialStore",
    "InMemoryCredentialStore",
    "RotationPolicy",
]
