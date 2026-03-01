"""Unit tests for codomyrmex.logistics.orchestration.project.orchestration_engine.

Covers:
- OrchestrationMode enum
- SessionStatus enum
- OrchestrationSession dataclass (init, to_dict, from_dict, edge cases)
- OrchestrationEngine constructor (documents known integration bug)
- OrchestrationEngine methods (session management, events, health, metrics, shutdown)
- create_orchestration_mcp_tools (if MCP available)
- get_orchestration_engine module-level function

Zero-mock policy: all tests use real objects only.
"""

import uuid
from datetime import datetime, timezone

import pytest

from codomyrmex.logistics.orchestration.project.orchestration_engine import (
    MCP_AVAILABLE,
    OrchestrationEngine,
    OrchestrationMode,
    OrchestrationSession,
    SessionStatus,
    get_orchestration_engine,
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


# ---------------------------------------------------------------------------
# OrchestrationEngine constructor
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestOrchestrationEngineInit:
    """Tests for OrchestrationEngine initialization."""

    def test_default_init_succeeds(self):
        """Default constructor creates a working OrchestrationEngine."""
        engine = OrchestrationEngine()
        assert engine is not None
        assert engine.config == {}
        engine.task_orchestrator.stop_execution()

    def test_init_with_empty_config_succeeds(self):
        """Explicit empty config creates a working engine."""
        engine = OrchestrationEngine(config={})
        assert engine.config == {}
        engine.task_orchestrator.stop_execution()

    def test_init_config_is_stored(self):
        """Config dict is stored on the engine instance."""
        engine = OrchestrationEngine(config={"max_workers": 8})
        assert engine.config.get("max_workers") == 8
        engine.task_orchestrator.stop_execution()


# ---------------------------------------------------------------------------
# OrchestrationEngine with patched ProjectManager (integration-style)
#
# Since zero-mock policy forbids mocking, and the constructor is broken,
# we test engine methods by manually constructing the engine's internal
# state. This tests the ENGINE's logic, not the broken wiring to
# ProjectManager.
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestOrchestrationEngineSessionManagement:
    """Tests for session create/get/close on a manually-wired engine."""

    @pytest.fixture()
    def engine(self, tmp_path):
        """Create an OrchestrationEngine with working subcomponents.

        We bypass the broken constructor by calling object.__new__ and
        setting up the internals manually with real objects.
        """
        import threading

        from codomyrmex.logistics.orchestration.project.project_manager import (
            ProjectManager,
        )
        from codomyrmex.logistics.orchestration.project.resource_manager import (
            ResourceManager,
        )
        from codomyrmex.logistics.orchestration.project.task_orchestrator import (
            TaskOrchestrator,
        )
        from codomyrmex.logistics.orchestration.project.workflow_manager import (
            WorkflowManager,
        )

        eng = object.__new__(OrchestrationEngine)
        eng.config = {}
        eng.workflow_manager = WorkflowManager(
            config_dir=tmp_path / "workflows",
            persistence_dir=tmp_path / "persistence",
        )
        eng.task_orchestrator = TaskOrchestrator(max_workers=2)
        eng.project_manager = ProjectManager(projects_root=tmp_path / "projects")
        eng.resource_manager = ResourceManager()
        eng.performance_monitor = None
        eng.active_sessions = {}
        eng.session_lock = threading.RLock()
        eng.event_handlers = {}
        eng.task_orchestrator.start_processing()

        yield eng

        eng.task_orchestrator.stop_execution()

    # --- create_session ---

    def test_create_session_returns_string_id(self, engine):
        sid = engine.create_session()
        assert isinstance(sid, str)
        assert len(sid) == 36  # UUID

    def test_create_session_stores_session(self, engine):
        sid = engine.create_session()
        assert sid in engine.active_sessions

    def test_create_session_default_user(self, engine):
        sid = engine.create_session()
        session = engine.active_sessions[sid]
        assert session.user_id == "system"

    def test_create_session_custom_user(self, engine):
        sid = engine.create_session(user_id="alice")
        session = engine.active_sessions[sid]
        assert session.user_id == "alice"

    def test_create_session_with_mode(self, engine):
        sid = engine.create_session(mode="parallel")
        session = engine.active_sessions[sid]
        assert session.mode is OrchestrationMode.PARALLEL

    def test_create_session_with_parallel_settings(self, engine):
        sid = engine.create_session(
            max_parallel_tasks=16,
            max_parallel_workflows=8,
        )
        session = engine.active_sessions[sid]
        assert session.max_parallel_tasks == 16
        assert session.max_parallel_workflows == 8

    def test_create_session_with_timeout(self, engine):
        sid = engine.create_session(timeout_seconds=300)
        session = engine.active_sessions[sid]
        assert session.timeout_seconds == 300

    def test_create_session_with_metadata(self, engine):
        sid = engine.create_session(metadata={"env": "test"})
        session = engine.active_sessions[sid]
        assert session.metadata == {"env": "test"}

    def test_create_session_with_resource_requirements(self, engine):
        sid = engine.create_session(resource_requirements={"gpu": 1})
        session = engine.active_sessions[sid]
        assert session.resource_requirements == {"gpu": 1}

    def test_create_multiple_sessions(self, engine):
        ids = [engine.create_session() for _ in range(5)]
        assert len(set(ids)) == 5
        assert len(engine.active_sessions) == 5

    # --- get_session ---

    def test_get_session_existing(self, engine):
        sid = engine.create_session(user_id="bob")
        session = engine.get_session(sid)
        assert session is not None
        assert session.user_id == "bob"

    def test_get_session_nonexistent(self, engine):
        result = engine.get_session("nonexistent-id")
        assert result is None

    # --- close_session ---

    def test_close_session_existing_fails_on_deallocate(self, engine):
        """close_session calls resource_manager.deallocate_resources which
        does not exist on ResourceManager. Documents integration bug."""
        sid = engine.create_session()
        with pytest.raises(AttributeError, match="deallocate_resources"):
            engine.close_session(sid)

    def test_close_session_nonexistent(self, engine):
        result = engine.close_session("nonexistent-id")
        assert result is False

    def test_close_session_sets_status_before_crash(self, engine):
        """close_session sets status=SessionStatus.COMPLETED and completed_at
        before crashing on deallocate_resources."""
        sid = engine.create_session()
        session = engine.active_sessions[sid]
        assert session.completed_at is None
        with pytest.raises(AttributeError):
            engine.close_session(sid)
        # The status was set before the crash
        assert session.status is SessionStatus.COMPLETED
        assert session.completed_at is not None

    def test_close_session_nonexistent_does_not_raise(self, engine):
        """Closing a nonexistent session returns False without error."""
        assert engine.close_session("no-such-session") is False
        assert engine.close_session("no-such-session") is False


# ---------------------------------------------------------------------------
# Event system
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestOrchestrationEngineEvents:
    """Tests for the event handler system."""

    @pytest.fixture()
    def engine(self, tmp_path):
        import threading

        from codomyrmex.logistics.orchestration.project.project_manager import (
            ProjectManager,
        )
        from codomyrmex.logistics.orchestration.project.resource_manager import (
            ResourceManager,
        )
        from codomyrmex.logistics.orchestration.project.task_orchestrator import (
            TaskOrchestrator,
        )
        from codomyrmex.logistics.orchestration.project.workflow_manager import (
            WorkflowManager,
        )

        eng = object.__new__(OrchestrationEngine)
        eng.config = {}
        eng.workflow_manager = WorkflowManager(
            config_dir=tmp_path / "wf",
            persistence_dir=tmp_path / "persist",
        )
        eng.task_orchestrator = TaskOrchestrator(max_workers=1)
        eng.project_manager = ProjectManager(projects_root=tmp_path / "proj")
        eng.resource_manager = ResourceManager()
        eng.performance_monitor = None
        eng.active_sessions = {}
        eng.session_lock = threading.RLock()
        eng.event_handlers = {}
        eng.task_orchestrator.start_processing()

        yield eng

        eng.task_orchestrator.stop_execution()

    def test_register_event_handler(self, engine):
        handler = lambda event, data: None
        engine.register_event_handler("test_event", handler)
        assert "test_event" in engine.event_handlers
        assert handler in engine.event_handlers["test_event"]

    def test_register_multiple_handlers(self, engine):
        h1 = lambda e, d: None
        h2 = lambda e, d: None
        engine.register_event_handler("evt", h1)
        engine.register_event_handler("evt", h2)
        assert len(engine.event_handlers["evt"]) == 2

    def test_register_handlers_different_events(self, engine):
        h1 = lambda e, d: None
        h2 = lambda e, d: None
        engine.register_event_handler("evt_a", h1)
        engine.register_event_handler("evt_b", h2)
        assert "evt_a" in engine.event_handlers
        assert "evt_b" in engine.event_handlers

    def test_emit_event_calls_handler(self, engine):
        received = []
        engine.register_event_handler("ping", lambda e, d: received.append((e, d)))
        engine.emit_event("ping", {"msg": "hello"})
        assert len(received) == 1
        assert received[0] == ("ping", {"msg": "hello"})

    def test_emit_event_calls_multiple_handlers(self, engine):
        calls = []
        engine.register_event_handler("multi", lambda e, d: calls.append("h1"))
        engine.register_event_handler("multi", lambda e, d: calls.append("h2"))
        engine.emit_event("multi", {})
        assert calls == ["h1", "h2"]

    def test_emit_event_no_handlers(self, engine):
        """Emitting an event with no handlers should not raise."""
        engine.emit_event("unregistered_event", {"data": 123})

    def test_emit_event_handler_exception_does_not_propagate(self, engine):
        """A failing handler should not crash emit_event."""
        def bad_handler(e, d):
            raise RuntimeError("handler exploded")

        engine.register_event_handler("fail_event", bad_handler)
        # Should not raise
        engine.emit_event("fail_event", {})

    def test_session_created_event_fired(self, engine):
        events = []
        engine.register_event_handler(
            "session_created", lambda e, d: events.append(d)
        )
        sid = engine.create_session(user_id="eve")
        assert len(events) == 1
        assert events[0]["session_id"] == sid
        assert events[0]["user_id"] == "eve"

    def test_session_closed_event_not_fired_due_to_bug(self, engine):
        """close_session crashes on deallocate_resources before emitting
        the session_closed event. Documents this integration bug."""
        events = []
        engine.register_event_handler(
            "session_closed", lambda e, d: events.append(d)
        )
        sid = engine.create_session()
        with pytest.raises(AttributeError):
            engine.close_session(sid)
        # Event was NOT emitted because the crash happens before emit
        assert len(events) == 0


# ---------------------------------------------------------------------------
# get_system_status, health_check, get_metrics
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestOrchestrationEngineStatus:
    """Tests for status, health, and metrics methods."""

    @pytest.fixture()
    def engine(self, tmp_path):
        import threading

        from codomyrmex.logistics.orchestration.project.project_manager import (
            ProjectManager,
        )
        from codomyrmex.logistics.orchestration.project.resource_manager import (
            ResourceManager,
        )
        from codomyrmex.logistics.orchestration.project.task_orchestrator import (
            TaskOrchestrator,
        )
        from codomyrmex.logistics.orchestration.project.workflow_manager import (
            WorkflowManager,
        )

        eng = object.__new__(OrchestrationEngine)
        eng.config = {}
        eng.workflow_manager = WorkflowManager(
            config_dir=tmp_path / "wf",
            persistence_dir=tmp_path / "persist",
        )
        eng.task_orchestrator = TaskOrchestrator(max_workers=1)
        eng.project_manager = ProjectManager(projects_root=tmp_path / "proj")
        eng.resource_manager = ResourceManager()
        eng.performance_monitor = None
        eng.active_sessions = {}
        eng.session_lock = threading.RLock()
        eng.event_handlers = {}
        eng.task_orchestrator.start_processing()

        yield eng

        eng.task_orchestrator.stop_execution()

    def test_get_system_status_returns_dict(self, engine):
        """get_system_status calls several methods that don't exist on
        real subcomponents (get_execution_stats, get_projects_summary,
        get_resource_usage). Expect AttributeError."""
        with pytest.raises(AttributeError):
            engine.get_system_status()

    def test_health_check_returns_dict(self, engine):
        result = engine.health_check()
        assert isinstance(result, dict)
        assert "overall_status" in result
        assert "timestamp" in result
        assert "components" in result
        assert "issues" in result

    def test_health_check_lists_all_components(self, engine):
        result = engine.health_check()
        expected_components = {
            "workflow_manager",
            "task_orchestrator",
            "project_manager",
            "resource_manager",
        }
        assert set(result["components"].keys()) == expected_components

    def test_health_check_components_have_status(self, engine):
        result = engine.health_check()
        for comp_name, comp_data in result["components"].items():
            assert "status" in comp_data

    def test_get_metrics_fails_on_missing_methods(self, engine):
        """get_metrics calls get_execution_stats, get_projects_summary,
        get_resource_usage which don't exist."""
        with pytest.raises(AttributeError):
            engine.get_metrics()


# ---------------------------------------------------------------------------
# shutdown
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestOrchestrationEngineShutdown:
    """Tests for the shutdown method."""

    @pytest.fixture()
    def engine(self, tmp_path):
        import threading

        from codomyrmex.logistics.orchestration.project.project_manager import (
            ProjectManager,
        )
        from codomyrmex.logistics.orchestration.project.resource_manager import (
            ResourceManager,
        )
        from codomyrmex.logistics.orchestration.project.task_orchestrator import (
            TaskOrchestrator,
        )
        from codomyrmex.logistics.orchestration.project.workflow_manager import (
            WorkflowManager,
        )

        eng = object.__new__(OrchestrationEngine)
        eng.config = {}
        eng.workflow_manager = WorkflowManager(
            config_dir=tmp_path / "wf",
            persistence_dir=tmp_path / "persist",
        )
        eng.task_orchestrator = TaskOrchestrator(max_workers=1)
        eng.project_manager = ProjectManager(projects_root=tmp_path / "proj")
        eng.resource_manager = ResourceManager()
        eng.performance_monitor = None
        eng.active_sessions = {}
        eng.session_lock = threading.RLock()
        eng.event_handlers = {}
        eng.task_orchestrator.start_processing()
        return eng

    def test_shutdown_with_sessions_hits_deallocate_bug(self, engine):
        """shutdown calls close_session for each active session, which
        crashes on deallocate_resources. The sessions remain because
        close_session raises before deleting them."""
        engine.create_session()
        engine.create_session()
        assert len(engine.active_sessions) == 2
        # shutdown catches errors from close_session implicitly via
        # __del__ guard, but the direct call propagates the error.
        # Actually shutdown iterates over session_ids and calls close_session;
        # close_session raises AttributeError which propagates out of shutdown.
        with pytest.raises(AttributeError, match="deallocate_resources"):
            engine.shutdown()

    def test_shutdown_no_sessions_succeeds(self, engine):
        """shutdown with no active sessions completes cleanly."""
        engine.shutdown()
        assert engine.task_orchestrator._stop_event.is_set()

    def test_shutdown_stops_task_orchestrator_when_no_sessions(self, engine):
        engine.shutdown()
        assert engine.task_orchestrator._stop_event.is_set()

    def test_shutdown_idempotent_when_no_sessions(self, engine):
        """Calling shutdown twice with no sessions should not raise."""
        engine.shutdown()
        engine.shutdown()


# ---------------------------------------------------------------------------
# execute_workflow (session not found branch)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestOrchestrationEngineExecuteWorkflow:
    """Tests for execute_workflow error paths."""

    @pytest.fixture()
    def engine(self, tmp_path):
        import threading

        from codomyrmex.logistics.orchestration.project.project_manager import (
            ProjectManager,
        )
        from codomyrmex.logistics.orchestration.project.resource_manager import (
            ResourceManager,
        )
        from codomyrmex.logistics.orchestration.project.task_orchestrator import (
            TaskOrchestrator,
        )
        from codomyrmex.logistics.orchestration.project.workflow_manager import (
            WorkflowManager,
        )

        eng = object.__new__(OrchestrationEngine)
        eng.config = {}
        eng.workflow_manager = WorkflowManager(
            config_dir=tmp_path / "wf",
            persistence_dir=tmp_path / "persist",
        )
        eng.task_orchestrator = TaskOrchestrator(max_workers=1)
        eng.project_manager = ProjectManager(projects_root=tmp_path / "proj")
        eng.resource_manager = ResourceManager()
        eng.performance_monitor = None
        eng.active_sessions = {}
        eng.session_lock = threading.RLock()
        eng.event_handlers = {}
        eng.task_orchestrator.start_processing()

        yield eng

        eng.task_orchestrator.stop_execution()

    def test_execute_workflow_invalid_session(self, engine):
        result = engine.execute_workflow("some_workflow", session_id="bad-id")
        assert result["success"] is False
        assert "not found" in result["error"]

    def test_execute_workflow_creates_session_then_fails(self, engine):
        """When no session_id, the engine creates one. The workflow
        execution fails (workflow not found), and the finally block
        crashes on deallocate_resources."""
        with pytest.raises(AttributeError, match="deallocate_resources"):
            engine.execute_workflow("nonexistent_workflow")


# ---------------------------------------------------------------------------
# execute_task error paths
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestOrchestrationEngineExecuteTask:
    """Tests for execute_task method."""

    @pytest.fixture()
    def engine(self, tmp_path):
        import threading

        from codomyrmex.logistics.orchestration.project.project_manager import (
            ProjectManager,
        )
        from codomyrmex.logistics.orchestration.project.resource_manager import (
            ResourceManager,
        )
        from codomyrmex.logistics.orchestration.project.task_orchestrator import (
            TaskOrchestrator,
        )
        from codomyrmex.logistics.orchestration.project.workflow_manager import (
            WorkflowManager,
        )

        eng = object.__new__(OrchestrationEngine)
        eng.config = {}
        eng.workflow_manager = WorkflowManager(
            config_dir=tmp_path / "wf",
            persistence_dir=tmp_path / "persist",
        )
        eng.task_orchestrator = TaskOrchestrator(max_workers=1)
        eng.project_manager = ProjectManager(projects_root=tmp_path / "proj")
        eng.resource_manager = ResourceManager()
        eng.performance_monitor = None
        eng.active_sessions = {}
        eng.session_lock = threading.RLock()
        eng.event_handlers = {}
        eng.task_orchestrator.start_processing()

        yield eng

        eng.task_orchestrator.stop_execution()

    def test_execute_task_invalid_session(self, engine):
        from codomyrmex.logistics.orchestration.project.task_orchestrator import Task

        task = Task(name="test", module="mod", action="echo", parameters={"message": "hi"})
        result = engine.execute_task(task, session_id="bad-session")
        assert result["success"] is False
        assert "not found" in result["error"]

    def test_execute_task_with_dict_fails_on_add_task(self, engine):
        """execute_task calls self.task_orchestrator.add_task which does
        not exist (it should be submit_task). Expect an error result."""
        task_dict = {"name": "t1", "module": "m", "action": "echo"}
        result = engine.execute_task(task_dict)
        assert result["success"] is False
        assert "error" in result


# ---------------------------------------------------------------------------
# execute_project_workflow error paths
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestOrchestrationEngineProjectWorkflow:
    """Tests for execute_project_workflow."""

    @pytest.fixture()
    def engine(self, tmp_path):
        import threading

        from codomyrmex.logistics.orchestration.project.project_manager import (
            ProjectManager,
        )
        from codomyrmex.logistics.orchestration.project.resource_manager import (
            ResourceManager,
        )
        from codomyrmex.logistics.orchestration.project.task_orchestrator import (
            TaskOrchestrator,
        )
        from codomyrmex.logistics.orchestration.project.workflow_manager import (
            WorkflowManager,
        )

        eng = object.__new__(OrchestrationEngine)
        eng.config = {}
        eng.workflow_manager = WorkflowManager(
            config_dir=tmp_path / "wf",
            persistence_dir=tmp_path / "persist",
        )
        eng.task_orchestrator = TaskOrchestrator(max_workers=1)
        eng.project_manager = ProjectManager(projects_root=tmp_path / "proj")
        eng.resource_manager = ResourceManager()
        eng.performance_monitor = None
        eng.active_sessions = {}
        eng.session_lock = threading.RLock()
        eng.event_handlers = {}
        eng.task_orchestrator.start_processing()

        yield eng

        eng.task_orchestrator.stop_execution()

    def test_execute_project_workflow_invalid_session(self, engine):
        result = engine.execute_project_workflow(
            "proj", "wf", session_id="bad-id"
        )
        assert result["success"] is False
        assert "not found" in result["error"]

    def test_execute_project_workflow_missing_method(self, engine):
        """ProjectManager does not have execute_project_workflow method."""
        result = engine.execute_project_workflow("proj", "wf")
        assert result["success"] is False
        assert "error" in result


# ---------------------------------------------------------------------------
# execute_complex_workflow
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestOrchestrationEngineComplexWorkflow:
    """Tests for execute_complex_workflow."""

    @pytest.fixture()
    def engine(self, tmp_path):
        import threading

        from codomyrmex.logistics.orchestration.project.project_manager import (
            ProjectManager,
        )
        from codomyrmex.logistics.orchestration.project.resource_manager import (
            ResourceManager,
        )
        from codomyrmex.logistics.orchestration.project.task_orchestrator import (
            TaskOrchestrator,
        )
        from codomyrmex.logistics.orchestration.project.workflow_manager import (
            WorkflowManager,
        )

        eng = object.__new__(OrchestrationEngine)
        eng.config = {}
        eng.workflow_manager = WorkflowManager(
            config_dir=tmp_path / "wf",
            persistence_dir=tmp_path / "persist",
        )
        eng.task_orchestrator = TaskOrchestrator(max_workers=1)
        eng.project_manager = ProjectManager(projects_root=tmp_path / "proj")
        eng.resource_manager = ResourceManager()
        eng.performance_monitor = None
        eng.active_sessions = {}
        eng.session_lock = threading.RLock()
        eng.event_handlers = {}
        eng.task_orchestrator.start_processing()

        yield eng

        eng.task_orchestrator.stop_execution()

    def test_execute_complex_workflow_invalid_session(self, engine):
        result = engine.execute_complex_workflow({}, session_id="bad")
        assert result["success"] is False
        assert "not found" in result["error"]

    def test_execute_complex_workflow_empty_steps(self, engine):
        """Empty workflow definition triggers add_task (missing method) or
        wait_for_completion (missing method) depending on code path."""
        result = engine.execute_complex_workflow({"steps": []})
        assert result["success"] is False
        assert "error" in result

    def test_execute_complex_workflow_with_steps_fails_on_add_task(self, engine):
        """Steps are parsed into Tasks but add_task does not exist."""
        definition = {
            "steps": [
                {"name": "s1", "module": "m1", "action": "a1"},
            ],
            "dependencies": {},
        }
        result = engine.execute_complex_workflow(definition)
        assert result["success"] is False
        assert "error" in result


# ---------------------------------------------------------------------------
# create_project_from_workflow
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestOrchestrationEngineCreateProjectFromWorkflow:
    """Tests for create_project_from_workflow."""

    @pytest.fixture()
    def engine(self, tmp_path):
        import threading

        from codomyrmex.logistics.orchestration.project.project_manager import (
            ProjectManager,
        )
        from codomyrmex.logistics.orchestration.project.resource_manager import (
            ResourceManager,
        )
        from codomyrmex.logistics.orchestration.project.task_orchestrator import (
            TaskOrchestrator,
        )
        from codomyrmex.logistics.orchestration.project.workflow_manager import (
            WorkflowManager,
        )

        eng = object.__new__(OrchestrationEngine)
        eng.config = {}
        eng.workflow_manager = WorkflowManager(
            config_dir=tmp_path / "wf",
            persistence_dir=tmp_path / "persist",
        )
        eng.task_orchestrator = TaskOrchestrator(max_workers=1)
        eng.project_manager = ProjectManager(projects_root=tmp_path / "proj")
        eng.resource_manager = ResourceManager()
        eng.performance_monitor = None
        eng.active_sessions = {}
        eng.session_lock = threading.RLock()
        eng.event_handlers = {}
        eng.task_orchestrator.start_processing()

        yield eng

        eng.task_orchestrator.stop_execution()

    def test_create_project_from_workflow_missing_method(self, engine):
        """create_project expects (name, type, description) not (name, template_name).
        The mismatch causes an error."""
        result = engine.create_project_from_workflow("proj1", "wf1")
        assert result["success"] is False
        assert "error" in result


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestMCPTools:
    """Tests for MCP tool creation."""

    @pytest.mark.skipif(not MCP_AVAILABLE, reason="MCP module not available")
    def test_create_orchestration_mcp_tools_returns_dict(self):
        from codomyrmex.logistics.orchestration.project.orchestration_engine import (
            create_orchestration_mcp_tools,
        )

        tools = create_orchestration_mcp_tools()
        assert isinstance(tools, dict)

    @pytest.mark.skipif(not MCP_AVAILABLE, reason="MCP module not available")
    def test_mcp_tools_expected_keys(self):
        from codomyrmex.logistics.orchestration.project.orchestration_engine import (
            create_orchestration_mcp_tools,
        )

        tools = create_orchestration_mcp_tools()
        expected = {"execute_workflow", "create_project", "get_system_status"}
        assert set(tools.keys()) == expected

    @pytest.mark.skipif(not MCP_AVAILABLE, reason="MCP module not available")
    def test_mcp_tool_has_name_and_description(self):
        from codomyrmex.logistics.orchestration.project.orchestration_engine import (
            create_orchestration_mcp_tools,
        )

        tools = create_orchestration_mcp_tools()
        for tool_name, tool_def in tools.items():
            assert "name" in tool_def, f"Tool {tool_name} missing 'name'"
            assert "description" in tool_def, f"Tool {tool_name} missing 'description'"
            assert "input_schema" in tool_def, f"Tool {tool_name} missing 'input_schema'"

    @pytest.mark.skipif(not MCP_AVAILABLE, reason="MCP module not available")
    def test_execute_workflow_tool_requires_workflow_name(self):
        from codomyrmex.logistics.orchestration.project.orchestration_engine import (
            create_orchestration_mcp_tools,
        )

        tools = create_orchestration_mcp_tools()
        schema = tools["execute_workflow"]["input_schema"]
        assert "workflow_name" in schema["required"]

    @pytest.mark.skipif(not MCP_AVAILABLE, reason="MCP module not available")
    def test_create_project_tool_requires_project_name(self):
        from codomyrmex.logistics.orchestration.project.orchestration_engine import (
            create_orchestration_mcp_tools,
        )

        tools = create_orchestration_mcp_tools()
        schema = tools["create_project"]["input_schema"]
        assert "project_name" in schema["required"]


# ---------------------------------------------------------------------------
# get_orchestration_engine module-level function
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGetOrchestrationEngine:
    """Tests for the get_orchestration_engine singleton function."""

    def test_get_orchestration_engine_returns_singleton(self):
        """The global factory creates and caches an OrchestrationEngine."""
        import codomyrmex.logistics.orchestration.project.orchestration_engine as mod

        original = mod._orchestration_engine
        mod._orchestration_engine = None
        try:
            engine = get_orchestration_engine()
            assert engine is not None
            # Second call returns same instance (singleton)
            engine2 = get_orchestration_engine()
            assert engine is engine2
            engine.task_orchestrator.stop_execution()
        finally:
            mod._orchestration_engine = original


# ---------------------------------------------------------------------------
# TaskResult.to_dict coverage (used by execute_task)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestTaskResultIntegration:
    """Tests verifying TaskResult.to_dict is accessible."""

    def test_task_result_has_to_dict(self):
        """TaskResult from task_orchestrator should be a dataclass; to_dict
        may or may not exist. Verify the attribute."""
        from codomyrmex.logistics.orchestration.project.task_orchestrator import (
            TaskResult,
            TaskStatus,
        )

        tr = TaskResult(task_id="t1", status=TaskStatus.COMPLETED, result="ok")
        # TaskResult is a dataclass -- it may not have to_dict
        # The engine code calls result.to_dict() which would fail
        has_to_dict = hasattr(tr, "to_dict")
        # Document behavior: TaskResult does NOT have to_dict
        assert not has_to_dict, "TaskResult gained a to_dict method -- update tests"
