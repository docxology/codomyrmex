"""Tests for security/audit/audit_trail.py — AuditEntry and AuditTrail."""

import json

from codomyrmex.security.audit.audit_trail import AuditEntry, AuditTrail


class TestAuditEntryDataclass:
    """Tests for the AuditEntry dataclass."""

    def test_create_minimal(self):
        """AuditEntry with only action sets sensible defaults."""
        entry = AuditEntry(action="deploy")
        assert entry.action == "deploy"
        assert entry.actor == ""
        assert entry.resource == ""
        assert entry.previous_hash == ""
        assert entry.entry_hash == ""
        assert entry.timestamp > 0  # auto-set via __post_init__

    def test_create_full(self):
        """AuditEntry stores all provided fields."""
        entry = AuditEntry(
            action="read",
            actor="alice",
            resource="db/users",
            metadata={"row_id": 42},
            previous_hash="abc123",
        )
        assert entry.action == "read"
        assert entry.actor == "alice"
        assert entry.resource == "db/users"
        assert entry.metadata == {"row_id": 42}
        assert entry.previous_hash == "abc123"

    def test_timestamp_auto_set(self):
        """Timestamp is populated when not provided."""
        entry = AuditEntry(action="x")
        assert isinstance(entry.timestamp, float)
        assert entry.timestamp > 0.0

    def test_timestamp_explicit(self):
        """Explicit timestamp is preserved."""
        entry = AuditEntry(action="x", timestamp=12345.0)
        assert entry.timestamp == 12345.0

    def test_to_dict_has_all_keys(self):
        """to_dict includes action, actor, resource, timestamp, hashes."""
        entry = AuditEntry(action="login", actor="bob", resource="auth")
        d = entry.to_dict()
        for key in ("action", "actor", "resource", "timestamp", "previous_hash", "entry_hash"):
            assert key in d, f"Missing key: {key}"

    def test_to_dict_values(self):
        """to_dict values match the entry fields."""
        entry = AuditEntry(action="logout", actor="carol", timestamp=9999.0)
        d = entry.to_dict()
        assert d["action"] == "logout"
        assert d["actor"] == "carol"
        assert d["timestamp"] == 9999.0

    def test_payload_is_json(self):
        """payload() returns valid JSON string."""
        entry = AuditEntry(action="create", actor="svc", resource="bucket")
        payload = entry.payload()
        parsed = json.loads(payload)
        assert parsed["action"] == "create"
        assert parsed["actor"] == "svc"
        assert parsed["resource"] == "bucket"

    def test_payload_includes_previous_hash(self):
        """payload() includes previous_hash for chain integrity."""
        entry = AuditEntry(action="delete", previous_hash="deadbeef")
        payload = entry.payload()
        parsed = json.loads(payload)
        assert parsed["previous_hash"] == "deadbeef"

    def test_payload_is_sorted(self):
        """payload() uses sort_keys so output is deterministic."""
        e1 = AuditEntry(action="a", actor="x", resource="r", timestamp=1.0)
        e2 = AuditEntry(action="a", actor="x", resource="r", timestamp=1.0)
        assert e1.payload() == e2.payload()


class TestAuditTrailRecord:
    """Tests for AuditTrail.record() behaviour."""

    def test_record_returns_entry(self):
        """record() returns an AuditEntry object."""
        trail = AuditTrail()
        entry = trail.record("deploy")
        assert isinstance(entry, AuditEntry)
        assert entry.action == "deploy"

    def test_record_increments_size(self):
        """Each record() call increases size by 1."""
        trail = AuditTrail()
        assert trail.size == 0
        trail.record("a")
        assert trail.size == 1
        trail.record("b")
        assert trail.size == 2

    def test_record_sets_entry_hash(self):
        """record() computes and stores an entry_hash (non-empty string)."""
        trail = AuditTrail()
        entry = trail.record("action")
        assert len(entry.entry_hash) > 0

    def test_record_first_entry_previous_hash_is_genesis(self):
        """First entry previous_hash is 'genesis'."""
        trail = AuditTrail()
        entry = trail.record("first")
        assert entry.previous_hash == "genesis"

    def test_record_second_entry_links_to_first(self):
        """Second entry previous_hash matches first entry's hash."""
        trail = AuditTrail()
        e1 = trail.record("first")
        e2 = trail.record("second")
        assert e2.previous_hash == e1.entry_hash

    def test_record_with_all_params(self):
        """record() stores actor, resource, and metadata."""
        trail = AuditTrail()
        entry = trail.record("write", actor="agent-1", resource="file.py", metadata={"size": 100})
        assert entry.actor == "agent-1"
        assert entry.resource == "file.py"
        assert entry.metadata == {"size": 100}

    def test_record_chain_three_entries(self):
        """Three-entry chain links correctly."""
        trail = AuditTrail()
        e1 = trail.record("a")
        e2 = trail.record("b")
        e3 = trail.record("c")
        assert e2.previous_hash == e1.entry_hash
        assert e3.previous_hash == e2.entry_hash


class TestAuditTrailVerifyChain:
    """Tests for AuditTrail.verify_chain()."""

    def test_empty_chain_is_valid(self):
        """Empty chain verifies as True."""
        trail = AuditTrail()
        assert trail.verify_chain() is True

    def test_single_entry_chain_is_valid(self):
        """Single entry chain verifies correctly."""
        trail = AuditTrail()
        trail.record("action")
        assert trail.verify_chain() is True

    def test_multi_entry_chain_is_valid(self):
        """Multi-entry chain is valid after sequential records."""
        trail = AuditTrail()
        for i in range(5):
            trail.record(f"action_{i}", actor=f"agent_{i}")
        assert trail.verify_chain() is True

    def test_tampered_entry_hash_fails(self):
        """Manually tampering with entry_hash breaks chain verification."""
        trail = AuditTrail()
        trail.record("action")
        # Tamper with hash directly
        trail._entries[0].entry_hash = "tampered"
        assert trail.verify_chain() is False

    def test_tampered_previous_hash_fails(self):
        """Manually tampering with previous_hash breaks chain verification."""
        trail = AuditTrail()
        trail.record("a")
        trail.record("b")
        # The second entry's previous_hash should match first entry's hash
        trail._entries[1].previous_hash = "wrong"
        assert trail.verify_chain() is False

    def test_custom_signing_key_produces_different_hash(self):
        """Different signing keys produce different hashes."""
        t1 = AuditTrail(signing_key=b"key1")
        t2 = AuditTrail(signing_key=b"key2")
        e1 = t1.record("action", actor="x", resource="r")
        e2 = t2.record("action", actor="x", resource="r")
        # Hashes should differ due to different keys
        assert e1.entry_hash != e2.entry_hash


class TestAuditTrailQueries:
    """Tests for AuditTrail query methods."""

    def test_entries_returns_copy(self):
        """entries() returns a list (copy, not internal ref)."""
        trail = AuditTrail()
        trail.record("a")
        entries = trail.entries()
        assert isinstance(entries, list)
        assert len(entries) == 1

    def test_entries_by_actor_filters(self):
        """entries_by_actor() returns only matching actor entries."""
        trail = AuditTrail()
        trail.record("a", actor="alice")
        trail.record("b", actor="bob")
        trail.record("c", actor="alice")
        results = trail.entries_by_actor("alice")
        assert len(results) == 2
        assert all(e.actor == "alice" for e in results)

    def test_entries_by_actor_no_match(self):
        """entries_by_actor() returns empty list for unknown actor."""
        trail = AuditTrail()
        trail.record("x", actor="alice")
        results = trail.entries_by_actor("unknown")
        assert results == []

    def test_to_jsonl_format(self):
        """to_jsonl() produces one JSON object per line."""
        trail = AuditTrail()
        trail.record("a")
        trail.record("b")
        jsonl = trail.to_jsonl()
        lines = jsonl.strip().split("\n")
        assert len(lines) == 2
        for line in lines:
            obj = json.loads(line)
            assert "action" in obj

    def test_to_jsonl_empty_trail(self):
        """to_jsonl() on empty trail returns empty string."""
        trail = AuditTrail()
        assert trail.to_jsonl() == ""

    def test_size_property(self):
        """size property reflects number of recorded entries."""
        trail = AuditTrail()
        assert trail.size == 0
        trail.record("x")
        trail.record("y")
        trail.record("z")
        assert trail.size == 3
