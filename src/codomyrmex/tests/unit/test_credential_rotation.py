"""Tests for auth.rotation — CredentialRotator with TTL caching.

Zero-Mock: All tests use real in-memory credential stores and
real time-based expiry logic.
"""

from __future__ import annotations

import time

import pytest

from codomyrmex.auth.rotation import (
    AuditEvent,
    CredentialEntry,
    CredentialRotator,
    InMemoryCredentialStore,
    RotationPolicy,
)

# ── CredentialEntry ───────────────────────────────────────────────────


class TestCredentialEntry:
    """Verify credential lifecycle metadata."""

    def test_not_expired_by_default(self) -> None:
        entry = CredentialEntry(key="k", value="v", provider="p")
        assert entry.is_expired is False
        assert entry.remaining_seconds == float("inf")

    def test_expired_when_past_expiry(self) -> None:
        entry = CredentialEntry(
            key="k", value="v", provider="p",
            expires_at=time.time() - 10,
        )
        assert entry.is_expired is True
        assert entry.remaining_seconds == 0.0

    def test_remaining_seconds_positive(self) -> None:
        entry = CredentialEntry(
            key="k", value="v", provider="p",
            expires_at=time.time() + 100,
        )
        assert entry.remaining_seconds > 90

    def test_rotation_id_assigned(self) -> None:
        entry = CredentialEntry(key="k", value="v", provider="p")
        assert len(entry.rotation_id) == 12


# ── RotationPolicy ───────────────────────────────────────────────────


class TestRotationPolicy:
    """Verify default policy values."""

    def test_defaults(self) -> None:
        policy = RotationPolicy()
        assert policy.ttl_seconds == 3600.0
        assert policy.max_age_seconds == 86400.0
        assert policy.rotate_before_expiry_seconds == 300.0


# ── InMemoryCredentialStore ──────────────────────────────────────────


class TestInMemoryCredentialStore:
    """Verify the in-memory backend."""

    def test_save_and_load(self) -> None:
        store = InMemoryCredentialStore()
        entry = CredentialEntry(key="k", value="secret", provider="aws")
        store.save(entry)
        loaded = store.load("aws")
        assert loaded is not None
        assert loaded.value == "secret"

    def test_load_missing_returns_none(self) -> None:
        store = InMemoryCredentialStore()
        assert store.load("nonexistent") is None

    def test_delete(self) -> None:
        store = InMemoryCredentialStore()
        entry = CredentialEntry(key="k", value="v", provider="gcp")
        store.save(entry)
        assert store.delete("gcp") is True
        assert store.load("gcp") is None

    def test_delete_nonexistent_returns_false(self) -> None:
        store = InMemoryCredentialStore()
        assert store.delete("nope") is False


# ── CredentialRotator ─────────────────────────────────────────────────


class TestCredentialRotator:
    """Test the full rotation lifecycle."""

    def _make_rotator(
        self,
        ttl: float = 0.2,
        fetcher_value: str = "my-secret",
    ) -> tuple[CredentialRotator, list[str]]:
        """Create a rotator with a simple counter-based fetcher."""
        call_log: list[str] = []

        def fetcher() -> str:
            call_log.append("fetched")
            return fetcher_value

        rotator = CredentialRotator(policy=RotationPolicy(ttl_seconds=ttl))
        rotator.register_provider("test", fetcher)
        return rotator, call_log

    def test_get_credential_fetches_on_first_call(self) -> None:
        rotator, log = self._make_rotator()
        cred = rotator.get_credential("test")
        assert cred.value == "my-secret"
        assert len(log) == 1

    def test_get_credential_caches_within_ttl(self) -> None:
        rotator, log = self._make_rotator(ttl=600)
        cred1 = rotator.get_credential("test")
        cred2 = rotator.get_credential("test")
        # Same credential returned — only one fetch
        assert cred1.value == cred2.value
        assert len(log) == 1  # Only one fetch

    def test_get_credential_rotates_after_ttl(self) -> None:
        rotator, log = self._make_rotator(ttl=0.05)
        cred1 = rotator.get_credential("test")
        time.sleep(0.1)  # Exceed TTL
        cred2 = rotator.get_credential("test")
        assert cred1.rotation_id != cred2.rotation_id
        assert len(log) == 2

    def test_force_rotate(self) -> None:
        rotator, log = self._make_rotator(ttl=3600)
        cred1 = rotator.get_credential("test")
        cred2 = rotator.rotate("test")
        assert cred1.rotation_id != cred2.rotation_id
        assert len(log) == 2

    def test_unregistered_provider_raises(self) -> None:
        rotator = CredentialRotator()
        with pytest.raises(KeyError, match="not registered"):
            rotator.get_credential("nonexistent")

    def test_fetcher_failure_raises_runtime_error(self) -> None:
        rotator = CredentialRotator()

        def bad_fetcher() -> str:
            msg = "network down"
            raise ConnectionError(msg)

        rotator.register_provider("broken", bad_fetcher)

        with pytest.raises(RuntimeError, match="network down"):
            rotator.get_credential("broken")

    def test_fetcher_failure_logged_in_audit(self) -> None:
        rotator = CredentialRotator()
        rotator.register_provider("broken", lambda: (_ for _ in ()).throw(ValueError("oops")))

        with pytest.raises(RuntimeError):
            rotator.get_credential("broken")

        error_events = [e for e in rotator.audit_log if e.event_type == "error"]
        assert len(error_events) == 1
        assert "oops" in error_events[0].details

    def test_audit_log_records_rotations(self) -> None:
        rotator, _ = self._make_rotator(ttl=60)
        rotator.get_credential("test")
        rotator.rotate("test")

        rotate_events = [e for e in rotator.audit_log if e.event_type == "rotate"]
        assert len(rotate_events) == 2

    def test_invalidate(self) -> None:
        rotator, log = self._make_rotator(ttl=60)
        rotator.get_credential("test")
        assert rotator.invalidate("test") is True
        # Next get should re-fetch
        rotator.get_credential("test")
        assert len(log) == 2

    def test_registered_providers(self) -> None:
        rotator = CredentialRotator()
        rotator.register_provider("a", lambda: "x")
        rotator.register_provider("b", lambda: "y")
        assert sorted(rotator.registered_providers) == ["a", "b"]

    def test_per_provider_policy(self) -> None:
        rotator = CredentialRotator(policy=RotationPolicy(ttl_seconds=3600))
        fast_policy = RotationPolicy(ttl_seconds=0.05)

        rotator.register_provider("fast", lambda: "secret", policy=fast_policy)
        cred1 = rotator.get_credential("fast")
        time.sleep(0.1)
        cred2 = rotator.get_credential("fast")
        assert cred1.rotation_id != cred2.rotation_id
