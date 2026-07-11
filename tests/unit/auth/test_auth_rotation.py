"""Zero-mock tests for auth.rotation module.

Covers: CredentialEntry, RotationPolicy, AuditEvent, InMemoryCredentialStore,
CredentialRotator (register, get, rotate, invalidate, audit_log, TTL logic).

Zero-mock policy: no unittest.mock, no MagicMock, no monkeypatch.
"""

import time

import pytest

from codomyrmex.auth.rotation import (
    AuditEvent,
    CredentialEntry,
    CredentialRotator,
    CredentialStore,
    InMemoryCredentialStore,
    RotationPolicy,
)

# ==============================================================================
# CredentialEntry
# ==============================================================================


@pytest.mark.unit
class TestCredentialEntry:
    """Tests for CredentialEntry dataclass."""

    def test_creation_minimal(self):
        now = time.time()
        entry = CredentialEntry(key="k", value="secret", provider="prov")
        assert entry.key == "k"
        assert entry.value == "secret"
        assert entry.provider == "prov"
        assert entry.created_at >= now
        assert entry.expires_at == 0.0
        assert len(entry.rotation_id) == 12

    def test_no_expiry_never_expired(self):
        entry = CredentialEntry(key="k", value="s", provider="p", expires_at=0.0)
        assert entry.is_expired is False

    def test_future_expiry_not_expired(self):
        entry = CredentialEntry(
            key="k", value="s", provider="p", expires_at=time.time() + 9999
        )
        assert entry.is_expired is False

    def test_past_expiry_is_expired(self):
        entry = CredentialEntry(
            key="k", value="s", provider="p", expires_at=time.time() - 1
        )
        assert entry.is_expired is True

    def test_remaining_seconds_no_expiry(self):
        entry = CredentialEntry(key="k", value="s", provider="p", expires_at=0.0)
        assert entry.remaining_seconds == float("inf")

    def test_remaining_seconds_future(self):
        entry = CredentialEntry(
            key="k", value="s", provider="p", expires_at=time.time() + 100
        )
        assert 99 <= entry.remaining_seconds <= 101

    def test_remaining_seconds_expired(self):
        entry = CredentialEntry(
            key="k", value="s", provider="p", expires_at=time.time() - 5
        )
        assert entry.remaining_seconds == 0.0

    def test_rotation_id_is_unique(self):
        e1 = CredentialEntry(key="k", value="s", provider="p")
        e2 = CredentialEntry(key="k", value="s", provider="p")
        assert e1.rotation_id != e2.rotation_id


# ==============================================================================
# RotationPolicy
# ==============================================================================


@pytest.mark.unit
class TestRotationPolicy:
    """Tests for RotationPolicy frozen dataclass."""

    def test_defaults(self):
        policy = RotationPolicy()
        assert policy.ttl_seconds == 3600.0
        assert policy.max_age_seconds == 86400.0
        assert policy.rotate_before_expiry_seconds == 300.0

    def test_custom_values(self):
        policy = RotationPolicy(ttl_seconds=60.0, max_age_seconds=120.0)
        assert policy.ttl_seconds == 60.0
        assert policy.max_age_seconds == 120.0

    def test_frozen_immutable(self):
        policy = RotationPolicy()
        with pytest.raises((TypeError, AttributeError)):
            policy.ttl_seconds = 9999.0  # type: ignore[misc]


# ==============================================================================
# AuditEvent
# ==============================================================================


@pytest.mark.unit
class TestAuditEvent:
    """Tests for AuditEvent dataclass."""

    def test_creation(self):
        now = time.time()
        event = AuditEvent(provider="myprov", event_type="rotate", rotation_id="abc123")
        assert event.provider == "myprov"
        assert event.event_type == "rotate"
        assert event.rotation_id == "abc123"
        assert event.timestamp >= now
        assert event.details == ""

    def test_with_details(self):
        event = AuditEvent(
            provider="p",
            event_type="error",
            rotation_id="id",
            details="fetch failed",
        )
        assert event.details == "fetch failed"


# ==============================================================================
# InMemoryCredentialStore
# ==============================================================================


@pytest.mark.unit
class TestInMemoryCredentialStore:
    """Tests for InMemoryCredentialStore."""

    def _entry(self, provider: str = "test") -> CredentialEntry:
        return CredentialEntry(key=f"{provider}_cred", value="v", provider=provider)

    def test_save_and_load(self):
        store = InMemoryCredentialStore()
        entry = self._entry("aws")
        store.save(entry)
        loaded = store.load("aws")
        assert loaded is entry

    def test_load_missing_returns_none(self):
        store = InMemoryCredentialStore()
        assert store.load("nonexistent") is None

    def test_delete_existing(self):
        store = InMemoryCredentialStore()
        store.save(self._entry("azure"))
        result = store.delete("azure")
        assert result is True
        assert store.load("azure") is None

    def test_delete_missing_returns_false(self):
        store = InMemoryCredentialStore()
        assert store.delete("ghost") is False

    def test_overwrite_saves_new_entry(self):
        store = InMemoryCredentialStore()
        e1 = CredentialEntry(key="k", value="old", provider="p")
        e2 = CredentialEntry(key="k", value="new", provider="p")
        store.save(e1)
        store.save(e2)
        assert store.load("p").value == "new"

    def test_implements_protocol(self):
        store = InMemoryCredentialStore()
        assert isinstance(store, CredentialStore)


# ==============================================================================
# CredentialRotator
# ==============================================================================


@pytest.mark.unit
class TestCredentialRotatorBasic:
    """Basic CredentialRotator lifecycle tests."""

    def test_register_and_get(self):
        rotator = CredentialRotator()
        call_count = []
        rotator.register_provider("svc", lambda: (call_count.append(1), "key123")[1])
        entry = rotator.get_credential("svc")
        assert entry.value == "key123"
        assert entry.provider == "svc"
        assert len(call_count) == 1

    def test_get_unregistered_raises_key_error(self):
        rotator = CredentialRotator()
        with pytest.raises(KeyError, match="not registered"):
            rotator.get_credential("unknown")

    def test_registered_providers_list(self):
        rotator = CredentialRotator()
        rotator.register_provider("a", lambda: "va")
        rotator.register_provider("b", lambda: "vb")
        assert sorted(rotator.registered_providers) == ["a", "b"]

    def test_second_get_uses_cache(self):
        call_count = [0]

        def fetcher():
            call_count[0] += 1
            return "cached_key"

        rotator = CredentialRotator(policy=RotationPolicy(ttl_seconds=3600))
        rotator.register_provider("svc", fetcher)
        rotator.get_credential("svc")
        rotator.get_credential("svc")
        # Should only call fetcher once (TTL not expired)
        assert call_count[0] == 1

    def test_force_rotate_ignores_cache(self):
        call_count = [0]

        def fetcher():
            call_count[0] += 1
            return f"key_{call_count[0]}"

        rotator = CredentialRotator()
        rotator.register_provider("svc", fetcher)
        rotator.get_credential("svc")
        entry2 = rotator.rotate("svc")
        assert call_count[0] == 2
        assert entry2.value == "key_2"

    def test_rotate_unregistered_raises_key_error(self):
        rotator = CredentialRotator()
        with pytest.raises(KeyError, match="not registered"):
            rotator.rotate("ghost")

    def test_audit_log_populated_on_fetch(self):
        rotator = CredentialRotator()
        rotator.register_provider("svc", lambda: "v")
        rotator.get_credential("svc")
        log = rotator.audit_log
        assert len(log) >= 1
        event_types = {e.event_type for e in log}
        assert "rotate" in event_types

    def test_audit_log_is_copy(self):
        rotator = CredentialRotator()
        rotator.register_provider("svc", lambda: "v")
        rotator.get_credential("svc")
        log1 = rotator.audit_log
        log2 = rotator.audit_log
        assert log1 is not log2  # Different list objects
        assert len(log1) == len(log2)


@pytest.mark.unit
class TestCredentialRotatorInvalidate:
    """Tests for invalidate() method."""

    def test_invalidate_removes_cached_credential(self):
        call_count = [0]

        def fetcher():
            call_count[0] += 1
            return f"v{call_count[0]}"

        rotator = CredentialRotator()
        rotator.register_provider("svc", fetcher)
        rotator.get_credential("svc")
        assert call_count[0] == 1

        rotator.invalidate("svc")
        rotator.get_credential("svc")  # Should fetch again
        assert call_count[0] == 2

    def test_invalidate_existing_returns_true(self):
        rotator = CredentialRotator()
        rotator.register_provider("svc", lambda: "v")
        rotator.get_credential("svc")
        assert rotator.invalidate("svc") is True

    def test_invalidate_missing_returns_false(self):
        rotator = CredentialRotator()
        rotator.register_provider("svc", lambda: "v")
        # Never fetched, nothing in store
        assert rotator.invalidate("svc") is False

    def test_invalidate_logs_audit_event(self):
        rotator = CredentialRotator()
        rotator.register_provider("svc", lambda: "v")
        rotator.get_credential("svc")
        initial_count = len(rotator.audit_log)
        rotator.invalidate("svc")
        assert len(rotator.audit_log) == initial_count + 1
        assert rotator.audit_log[-1].event_type == "invalidate"


@pytest.mark.unit
class TestCredentialRotatorTTL:
    """Tests for TTL-based rotation logic."""

    def test_expired_ttl_triggers_refetch(self):
        call_count = [0]

        def fetcher():
            call_count[0] += 1
            return f"v{call_count[0]}"

        # TTL of 0 means everything is expired
        rotator = CredentialRotator(policy=RotationPolicy(ttl_seconds=0))
        rotator.register_provider("svc", fetcher)
        rotator.get_credential("svc")
        rotator.get_credential("svc")
        assert call_count[0] == 2

    def test_per_provider_policy_overrides_default(self):
        call_count = [0]

        def fetcher():
            call_count[0] += 1
            return f"v{call_count[0]}"

        default_policy = RotationPolicy(ttl_seconds=0)  # Always rotate
        per_provider = RotationPolicy(ttl_seconds=9999)  # Never rotate

        rotator = CredentialRotator(policy=default_policy)
        rotator.register_provider("svc", fetcher, policy=per_provider)
        rotator.get_credential("svc")
        rotator.get_credential("svc")
        # Per-provider TTL should prevent second fetch
        assert call_count[0] == 1

    def test_fetcher_error_raises_runtime_error(self):
        def bad_fetcher():
            raise ValueError("network failure")

        rotator = CredentialRotator()
        rotator.register_provider("svc", bad_fetcher)
        with pytest.raises(RuntimeError, match="Credential fetch failed"):
            rotator.get_credential("svc")

    def test_fetcher_error_logs_audit_event(self):
        def bad_fetcher():
            raise ValueError("boom")

        rotator = CredentialRotator()
        rotator.register_provider("svc", bad_fetcher)
        with pytest.raises(RuntimeError):
            rotator.get_credential("svc")

        log = rotator.audit_log
        assert any(e.event_type == "error" for e in log)
        error_events = [e for e in log if e.event_type == "error"]
        assert "boom" in error_events[0].details

    def test_custom_store_is_used(self):
        stored = {}

        class TrackingStore:
            def save(self, entry):
                stored[entry.provider] = entry

            def load(self, provider):
                return stored.get(provider)

            def delete(self, provider):
                return stored.pop(provider, None) is not None

        rotator = CredentialRotator(store=TrackingStore())
        rotator.register_provider("svc", lambda: "tracked_value")
        entry = rotator.get_credential("svc")
        assert "svc" in stored
        assert stored["svc"].value == "tracked_value"
        assert entry.value == "tracked_value"

    def test_entry_key_format(self):
        rotator = CredentialRotator()
        rotator.register_provider("myservice", lambda: "val")
        entry = rotator.get_credential("myservice")
        assert entry.key == "myservice_credential"

    def test_rotation_id_in_entry(self):
        rotator = CredentialRotator()
        rotator.register_provider("svc", lambda: "v")
        entry = rotator.get_credential("svc")
        assert len(entry.rotation_id) == 12  # uuid4.hex[:12]

    def test_audit_event_rotation_id_matches_entry(self):
        rotator = CredentialRotator()
        rotator.register_provider("svc", lambda: "v")
        entry = rotator.get_credential("svc")
        log = rotator.audit_log
        rotate_events = [e for e in log if e.event_type == "rotate"]
        assert len(rotate_events) >= 1
        assert rotate_events[-1].rotation_id == entry.rotation_id
