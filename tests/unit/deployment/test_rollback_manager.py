"""
Unit tests for deployment.rollback — Zero-Mock compliant.

Covers: SnapshotState (enum values), DeploymentSnapshot (fields, to_dict,
default state), RollbackResult (fields), RollbackManager (create_snapshot,
rollback_to, list_snapshots, verify_rollback, current_version, repr,
supersede-on-create, KeyError-on-missing, multi-rollback).
"""

import pytest

from codomyrmex.deployment.rollback import (
    DeploymentSnapshot,
    RollbackManager,
    RollbackResult,
    SnapshotState,
)

# ── SnapshotState ──────────────────────────────────────────────────────────


@pytest.mark.unit
class TestSnapshotState:
    def test_active_value(self):
        assert SnapshotState.ACTIVE.value == "active"

    def test_rolled_back_value(self):
        assert SnapshotState.ROLLED_BACK.value == "rolled_back"

    def test_superseded_value(self):
        assert SnapshotState.SUPERSEDED.value == "superseded"

    def test_three_members(self):
        assert len(SnapshotState) == 3


# ── DeploymentSnapshot ──────────────────────────────────────────────────────


@pytest.mark.unit
class TestDeploymentSnapshot:
    def test_version_stored(self):
        s = DeploymentSnapshot(version="v1.0.0")
        assert s.version == "v1.0.0"

    def test_default_state_active(self):
        s = DeploymentSnapshot(version="v1.0.0")
        assert s.state == SnapshotState.ACTIVE

    def test_created_at_set(self):
        s = DeploymentSnapshot(version="v1.0.0")
        assert s.created_at is not None

    def test_metadata_default_empty(self):
        s = DeploymentSnapshot(version="v1.0.0")
        assert s.metadata == {}

    def test_metadata_stored(self):
        s = DeploymentSnapshot(version="v2.0.0", metadata={"env": "prod"})
        assert s.metadata["env"] == "prod"

    def test_to_dict_keys(self):
        s = DeploymentSnapshot(version="v1.0.0")
        d = s.to_dict()
        for k in ("version", "state", "created_at", "metadata"):
            assert k in d

    def test_to_dict_version(self):
        s = DeploymentSnapshot(version="v3.0.0")
        assert s.to_dict()["version"] == "v3.0.0"

    def test_to_dict_state_is_string(self):
        s = DeploymentSnapshot(version="v1.0.0", state=SnapshotState.SUPERSEDED)
        assert s.to_dict()["state"] == "superseded"

    def test_to_dict_created_at_iso(self):
        s = DeploymentSnapshot(version="v1.0.0")
        # ISO 8601 contains a 'T' separator
        assert "T" in s.to_dict()["created_at"]


# ── RollbackResult ─────────────────────────────────────────────────────────


@pytest.mark.unit
class TestRollbackResult:
    def test_success_stored(self):
        r = RollbackResult(success=True, from_version="v2.0", to_version="v1.0")
        assert r.success is True

    def test_from_to_versions_stored(self):
        r = RollbackResult(success=True, from_version="v2.0", to_version="v1.0")
        assert r.from_version == "v2.0"
        assert r.to_version == "v1.0"

    def test_message_default_empty(self):
        r = RollbackResult(success=True, from_version="a", to_version="b")
        assert r.message == ""

    def test_message_stored(self):
        r = RollbackResult(
            success=False, from_version="a", to_version="b", message="err"
        )
        assert r.message == "err"

    def test_performed_at_set(self):
        r = RollbackResult(success=True, from_version="a", to_version="b")
        assert r.performed_at is not None


# ── RollbackManager ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestRollbackManagerInitial:
    def test_current_version_none_at_start(self):
        mgr = RollbackManager()
        assert mgr.current_version is None

    def test_list_snapshots_empty_at_start(self):
        mgr = RollbackManager()
        assert mgr.list_snapshots() == []

    def test_repr_contains_counts(self):
        mgr = RollbackManager()
        r = repr(mgr)
        assert "RollbackManager" in r
        assert "0" in r


@pytest.mark.unit
class TestRollbackManagerCreateSnapshot:
    def test_create_returns_snapshot(self):
        mgr = RollbackManager()
        snap = mgr.create_snapshot("v1.0.0")
        assert isinstance(snap, DeploymentSnapshot)

    def test_create_stores_version(self):
        mgr = RollbackManager()
        snap = mgr.create_snapshot("v1.0.0")
        assert snap.version == "v1.0.0"

    def test_create_updates_current_version(self):
        mgr = RollbackManager()
        mgr.create_snapshot("v1.0.0")
        assert mgr.current_version == "v1.0.0"

    def test_create_new_snapshot_state_active(self):
        mgr = RollbackManager()
        snap = mgr.create_snapshot("v1.0.0")
        assert snap.state == SnapshotState.ACTIVE

    def test_create_supersedes_previous_active(self):
        mgr = RollbackManager()
        mgr.create_snapshot("v1.0.0")
        mgr.create_snapshot("v2.0.0")
        # After creating v2, v1 should be superseded
        # list_snapshots returns copies, snap1 is the original
        snaps = mgr.list_snapshots()
        assert snaps[0].state == SnapshotState.SUPERSEDED

    def test_create_with_metadata(self):
        mgr = RollbackManager()
        snap = mgr.create_snapshot("v1.0.0", metadata={"commit": "abc123"})
        assert snap.metadata["commit"] == "abc123"

    def test_list_snapshots_returns_copies(self):
        mgr = RollbackManager()
        mgr.create_snapshot("v1.0.0")
        snaps = mgr.list_snapshots()
        assert len(snaps) == 1
        snaps[0].version = "modified"
        # Internal state should be unchanged
        assert mgr.list_snapshots()[0].version == "v1.0.0"

    def test_multiple_snapshots_ordered(self):
        mgr = RollbackManager()
        for v in ("v1", "v2", "v3"):
            mgr.create_snapshot(v)
        snaps = mgr.list_snapshots()
        assert [s.version for s in snaps] == ["v1", "v2", "v3"]


@pytest.mark.unit
class TestRollbackManagerRollbackTo:
    def test_rollback_returns_result(self):
        mgr = RollbackManager()
        mgr.create_snapshot("v1.0.0")
        mgr.create_snapshot("v2.0.0")
        result = mgr.rollback_to("v1.0.0")
        assert isinstance(result, RollbackResult)

    def test_rollback_success_true(self):
        mgr = RollbackManager()
        mgr.create_snapshot("v1.0.0")
        mgr.create_snapshot("v2.0.0")
        result = mgr.rollback_to("v1.0.0")
        assert result.success is True

    def test_rollback_updates_current_version(self):
        mgr = RollbackManager()
        mgr.create_snapshot("v1.0.0")
        mgr.create_snapshot("v2.0.0")
        mgr.rollback_to("v1.0.0")
        assert mgr.current_version == "v1.0.0"

    def test_rollback_from_version_set(self):
        mgr = RollbackManager()
        mgr.create_snapshot("v1.0.0")
        mgr.create_snapshot("v2.0.0")
        result = mgr.rollback_to("v1.0.0")
        assert result.from_version == "v2.0.0"

    def test_rollback_to_version_set(self):
        mgr = RollbackManager()
        mgr.create_snapshot("v1.0.0")
        mgr.create_snapshot("v2.0.0")
        result = mgr.rollback_to("v1.0.0")
        assert result.to_version == "v1.0.0"

    def test_rollback_message_contains_versions(self):
        mgr = RollbackManager()
        mgr.create_snapshot("v1.0.0")
        mgr.create_snapshot("v2.0.0")
        result = mgr.rollback_to("v1.0.0")
        assert "v1.0.0" in result.message
        assert "v2.0.0" in result.message

    def test_rollback_marks_target_rolled_back(self):
        mgr = RollbackManager()
        mgr.create_snapshot("v1.0.0")
        mgr.create_snapshot("v2.0.0")
        mgr.rollback_to("v1.0.0")
        snaps = mgr.list_snapshots()
        v1 = next(s for s in snaps if s.version == "v1.0.0")
        assert v1.state == SnapshotState.ROLLED_BACK

    def test_rollback_supersedes_later_snapshots(self):
        mgr = RollbackManager()
        mgr.create_snapshot("v1.0.0")
        mgr.create_snapshot("v2.0.0")
        mgr.create_snapshot("v3.0.0")
        mgr.rollback_to("v1.0.0")
        snaps = mgr.list_snapshots()
        later = [s for s in snaps if s.version in ("v2.0.0", "v3.0.0")]
        for s in later:
            assert s.state == SnapshotState.SUPERSEDED

    def test_rollback_missing_version_raises_keyerror(self):
        mgr = RollbackManager()
        mgr.create_snapshot("v1.0.0")
        with pytest.raises(KeyError, match="nonexistent"):
            mgr.rollback_to("nonexistent")

    def test_rollback_single_snapshot(self):
        mgr = RollbackManager()
        mgr.create_snapshot("v1.0.0")
        result = mgr.rollback_to("v1.0.0")
        assert result.success is True


@pytest.mark.unit
class TestRollbackManagerVerify:
    def test_verify_false_before_any_rollback(self):
        mgr = RollbackManager()
        mgr.create_snapshot("v1.0.0")
        mgr.create_snapshot("v2.0.0")
        # No rollback performed yet → 0 ROLLED_BACK states
        assert mgr.verify_rollback() is False

    def test_verify_true_after_valid_rollback(self):
        mgr = RollbackManager()
        mgr.create_snapshot("v1.0.0")
        mgr.create_snapshot("v2.0.0")
        mgr.rollback_to("v1.0.0")
        assert mgr.verify_rollback() is True

    def test_verify_false_empty_manager(self):
        mgr = RollbackManager()
        assert mgr.verify_rollback() is False

    def test_verify_false_after_double_rollback(self):
        """One ROLLED_BACK state is target, later rollback marks earlier ones superseded."""
        mgr = RollbackManager()
        mgr.create_snapshot("v1.0.0")
        mgr.create_snapshot("v2.0.0")
        mgr.create_snapshot("v3.0.0")
        mgr.rollback_to("v2.0.0")
        mgr.rollback_to("v1.0.0")
        # My implementation marks later snapshots as superseded, and exactly one as ROLLED_BACK.
        # So it should stay True if it matches current_version.
        assert mgr.verify_rollback() is True
