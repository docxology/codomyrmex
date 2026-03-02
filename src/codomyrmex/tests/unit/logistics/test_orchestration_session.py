"""Tests for OrchestrationSession, OrchestrationMode, and SessionStatus dataclasses.

Zero-mock policy: all tests use real objects only.
"""

import uuid
from datetime import datetime, timezone

import pytest

from codomyrmex.logistics.orchestration.project.orchestration_engine import (
    OrchestrationMode,
    OrchestrationSession,
    SessionStatus,
)

# ---------------------------------------------------------------------------
# OrchestrationMode enum
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestOrchestrationMode:
    """Tests for the OrchestrationMode enum."""

    def test_sequential_value(self):
        assert OrchestrationMode.SEQUENTIAL.value == "sequential"

    def test_parallel_value(self):
        assert OrchestrationMode.PARALLEL.value == "parallel"

    def test_priority_value(self):
        assert OrchestrationMode.PRIORITY.value == "priority"

    def test_resource_aware_value(self):
        assert OrchestrationMode.RESOURCE_AWARE.value == "resource_aware"

    def test_all_members(self):
        expected = {"SEQUENTIAL", "PARALLEL", "PRIORITY", "RESOURCE_AWARE"}
        assert set(OrchestrationMode.__members__.keys()) == expected

    def test_from_value_roundtrip(self):
        for mode in OrchestrationMode:
            assert OrchestrationMode(mode.value) is mode

    def test_invalid_value_raises(self):
        with pytest.raises(ValueError):
            OrchestrationMode("nonexistent_mode")


# ---------------------------------------------------------------------------
# SessionStatus enum
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSessionStatus:
    """Tests for the SessionStatus enum."""

    def test_pending_value(self):
        assert SessionStatus.PENDING.value == "pending"

    def test_active_value(self):
        assert SessionStatus.ACTIVE.value == "active"

    def test_completed_value(self):
        assert SessionStatus.COMPLETED.value == "completed"

    def test_cancelled_value(self):
        assert SessionStatus.CANCELLED.value == "cancelled"

    def test_failed_value(self):
        assert SessionStatus.FAILED.value == "failed"

    def test_all_members(self):
        expected = {"PENDING", "ACTIVE", "COMPLETED", "CANCELLED", "FAILED"}
        assert set(SessionStatus.__members__.keys()) == expected

    def test_from_value_roundtrip(self):
        for status in SessionStatus:
            assert SessionStatus(status.value) is status

    def test_invalid_value_raises(self):
        with pytest.raises(ValueError):
            SessionStatus("bogus")


# ---------------------------------------------------------------------------
# OrchestrationSession dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestOrchestrationSession:
    """Tests for the OrchestrationSession dataclass."""

    def test_default_construction(self):
        session = OrchestrationSession()
        assert isinstance(session.session_id, str)
        assert len(session.session_id) == 36  # UUID format
        assert session.name == ""
        assert session.description == ""
        assert session.user_id == "system"
        assert session.mode is OrchestrationMode.RESOURCE_AWARE
        assert session.max_parallel_tasks == 4
        assert session.max_parallel_workflows == 2
        assert session.timeout_seconds is None
        assert session.resource_requirements == {}
        assert session.metadata == {}
        assert session.status is SessionStatus.PENDING
        assert isinstance(session.created_at, datetime)
        assert session.started_at is None
        assert session.updated_at is None
        assert session.completed_at is None

    def test_custom_construction(self):
        sid = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        session = OrchestrationSession(
            session_id=sid,
            name="my-session",
            description="A test session",
            user_id="alice",
            mode=OrchestrationMode.PARALLEL,
            max_parallel_tasks=8,
            max_parallel_workflows=3,
            timeout_seconds=120,
            resource_requirements={"cpu": 2},
            metadata={"tag": "test"},
            created_at=now,
            started_at=now,
            status=SessionStatus.ACTIVE,
        )
        assert session.session_id == sid
        assert session.name == "my-session"
        assert session.description == "A test session"
        assert session.user_id == "alice"
        assert session.mode is OrchestrationMode.PARALLEL
        assert session.max_parallel_tasks == 8
        assert session.max_parallel_workflows == 3
        assert session.timeout_seconds == 120
        assert session.resource_requirements == {"cpu": 2}
        assert session.metadata == {"tag": "test"}
        assert session.status is SessionStatus.ACTIVE
        assert session.started_at == now

    def test_unique_session_ids(self):
        """Each default session gets a unique UUID."""
        ids = {OrchestrationSession().session_id for _ in range(50)}
        assert len(ids) == 50

    def test_resource_requirements_not_shared(self):
        """Default mutable fields should not be shared between instances."""
        s1 = OrchestrationSession()
        s2 = OrchestrationSession()
        s1.resource_requirements["cpu"] = 4
        assert "cpu" not in s2.resource_requirements

    def test_metadata_not_shared(self):
        s1 = OrchestrationSession()
        s2 = OrchestrationSession()
        s1.metadata["key"] = "val"
        assert "key" not in s2.metadata

    # --- to_dict ---

    def test_to_dict_keys(self):
        session = OrchestrationSession()
        d = session.to_dict()
        expected_keys = {
            "session_id", "name", "description", "user_id", "mode",
            "max_parallel_tasks", "max_parallel_workflows", "timeout_seconds",
            "resource_requirements", "metadata", "status",
            "created_at", "started_at", "updated_at", "completed_at",
        }
        assert set(d.keys()) == expected_keys

    def test_to_dict_mode_is_string(self):
        session = OrchestrationSession(mode=OrchestrationMode.SEQUENTIAL)
        d = session.to_dict()
        assert d["mode"] == "sequential"

    def test_to_dict_status_is_string(self):
        session = OrchestrationSession(status=SessionStatus.COMPLETED)
        d = session.to_dict()
        assert d["status"] == "completed"

    def test_to_dict_none_timestamps(self):
        session = OrchestrationSession()
        d = session.to_dict()
        assert d["started_at"] is None
        assert d["updated_at"] is None
        assert d["completed_at"] is None
        assert d["created_at"] is not None  # always set

    def test_to_dict_with_timestamps(self):
        now = datetime.now(timezone.utc)
        session = OrchestrationSession(
            started_at=now, completed_at=now, updated_at=now
        )
        d = session.to_dict()
        assert d["started_at"] == now.isoformat()
        assert d["completed_at"] == now.isoformat()
        assert d["updated_at"] == now.isoformat()

    def test_to_dict_preserves_nested_dicts(self):
        session = OrchestrationSession(
            resource_requirements={"cpu": 4, "mem": 1024},
            metadata={"owner": "test", "nested": {"a": 1}},
        )
        d = session.to_dict()
        assert d["resource_requirements"] == {"cpu": 4, "mem": 1024}
        assert d["metadata"]["nested"]["a"] == 1

    # --- from_dict ---

    def test_from_dict_minimal(self):
        """from_dict with empty dict uses sensible defaults."""
        session = OrchestrationSession.from_dict({})
        assert isinstance(session.session_id, str)
        assert session.name == ""
        assert session.user_id == "system"
        assert session.mode is OrchestrationMode.RESOURCE_AWARE
        assert session.status is SessionStatus.PENDING

    def test_from_dict_full_roundtrip(self):
        original = OrchestrationSession(
            name="roundtrip",
            description="Testing roundtrip",
            user_id="bob",
            mode=OrchestrationMode.PRIORITY,
            max_parallel_tasks=16,
            max_parallel_workflows=5,
            timeout_seconds=600,
            resource_requirements={"gpu": 2},
            metadata={"env": "prod"},
            status=SessionStatus.ACTIVE,
        )
        d = original.to_dict()
        restored = OrchestrationSession.from_dict(d)

        assert restored.session_id == original.session_id
        assert restored.name == original.name
        assert restored.description == original.description
        assert restored.user_id == original.user_id
        assert restored.mode is original.mode
        assert restored.max_parallel_tasks == original.max_parallel_tasks
        assert restored.max_parallel_workflows == original.max_parallel_workflows
        assert restored.timeout_seconds == original.timeout_seconds
        assert restored.resource_requirements == original.resource_requirements
        assert restored.metadata == original.metadata
        assert restored.status is original.status

    def test_from_dict_with_mode_string(self):
        session = OrchestrationSession.from_dict({"mode": "parallel"})
        assert session.mode is OrchestrationMode.PARALLEL

    def test_from_dict_with_none_mode(self):
        session = OrchestrationSession.from_dict({"mode": None})
        assert session.mode is OrchestrationMode.RESOURCE_AWARE

    def test_from_dict_with_missing_mode(self):
        session = OrchestrationSession.from_dict({"name": "no-mode"})
        assert session.mode is OrchestrationMode.RESOURCE_AWARE

    def test_from_dict_with_status_string(self):
        session = OrchestrationSession.from_dict({"status": "failed"})
        assert session.status is SessionStatus.FAILED

    def test_from_dict_invalid_status_falls_back_to_pending(self):
        session = OrchestrationSession.from_dict({"status": "not_a_real_status"})
        assert session.status is SessionStatus.PENDING

    def test_from_dict_with_valid_created_at(self):
        ts = "2025-06-15T10:30:00+00:00"
        session = OrchestrationSession.from_dict({"created_at": ts})
        assert session.created_at.year == 2025
        assert session.created_at.month == 6

    def test_from_dict_with_invalid_created_at(self):
        """Invalid created_at string should be silently ignored (keeps default)."""
        session = OrchestrationSession.from_dict({"created_at": "not-a-date"})
        # Should still have a valid created_at (the default)
        assert isinstance(session.created_at, datetime)

    def test_from_dict_preserves_custom_fields(self):
        data = {
            "session_id": "custom-id-123",
            "max_parallel_tasks": 32,
            "max_parallel_workflows": 10,
            "timeout_seconds": 999,
            "resource_requirements": {"disk": 500},
            "metadata": {"custom": True},
        }
        session = OrchestrationSession.from_dict(data)
        assert session.session_id == "custom-id-123"
        assert session.max_parallel_tasks == 32
        assert session.max_parallel_workflows == 10
        assert session.timeout_seconds == 999
        assert session.resource_requirements == {"disk": 500}
        assert session.metadata == {"custom": True}

    def test_from_dict_with_invalid_mode_raises(self):
        """An invalid mode value should raise ValueError (not caught by from_dict)."""
        with pytest.raises(ValueError):
            OrchestrationSession.from_dict({"mode": "invalid_mode_xyz"})
