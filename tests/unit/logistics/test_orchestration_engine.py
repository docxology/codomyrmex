"""Unit tests for codomyrmex.logistics.orchestration.project.orchestration_engine.

Covers:
- OrchestrationEngine constructor and component wiring
- OrchestrationEngine methods (sessions, events, workflow/task/project execution,
  status, health, metrics, shutdown)
- create_orchestration_mcp_tools (if MCP available)
- get_orchestration_engine module-level function

Dataclass tests (OrchestrationMode, SessionStatus, OrchestrationSession) live in
test_orchestration_session.py.

Zero-mock policy: all tests use real objects only. Workflow steps and tasks run
real functions registered on the engine's task orchestrator under the ``test``
module name.
"""

import time

import pytest

from codomyrmex.logistics.orchestration.project.orchestration_engine import (
    MCP_AVAILABLE,
    OrchestrationEngine,
    OrchestrationMode,
    SessionStatus,
    get_orchestration_engine,
)
from codomyrmex.logistics.orchestration.project.project_manager import ProjectType
from codomyrmex.logistics.orchestration.project.workflow_manager import WorkflowStep


def _echo(message: str = "") -> str:
    return message


def _sleep(duration: float = 0.1) -> float:
    time.sleep(duration)
    return duration


def _fail(reason: str = "boom") -> None:
    raise RuntimeError(reason)


@pytest.fixture
def engine(tmp_path):
    """A real OrchestrationEngine on temporary directories with test actions."""
    eng = OrchestrationEngine(
        config={
            "workflows_dir": tmp_path / "wf",
            "projects_dir": tmp_path / "proj",
            "max_workers": 2,
        }
    )
    eng.task_orchestrator.register_action("test", "echo", _echo)
    eng.task_orchestrator.register_action("test", "sleep", _sleep)
    eng.task_orchestrator.register_action("test", "fail", _fail)
    yield eng
    eng.shutdown()


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

    def test_components_share_orchestrator_and_resources(self, engine, tmp_path):
        """Workflows run on the engine's orchestrator, which allocates from the
        engine's resource manager; config paths are honoured."""
        assert engine.workflow_manager.task_orchestrator is engine.task_orchestrator
        assert engine.task_orchestrator.resource_manager is engine.resource_manager
        assert engine.workflow_manager.config_dir == tmp_path / "wf"
        assert engine.project_manager.projects_root == tmp_path / "proj"
        assert engine.task_orchestrator.max_workers == 2

    def test_shutdown_leaves_injected_orchestrator_running(self, tmp_path):
        """An engine built on shared components must not stop them."""
        from codomyrmex.logistics.orchestration.project.task_orchestrator import (
            TaskOrchestrator,
        )

        shared = TaskOrchestrator(max_workers=1)
        shared.start_processing()
        try:
            engine = OrchestrationEngine(
                config={"workflows_dir": tmp_path / "wf"}, task_orchestrator=shared
            )
            assert engine.workflow_manager.task_orchestrator is shared
            engine.shutdown()
            assert not shared._stop_event.is_set()
        finally:
            shared.stop_execution()


# ---------------------------------------------------------------------------
# Session management
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestOrchestrationEngineSessionManagement:
    """Tests for session create/get/close."""

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

    def test_close_session_existing_releases_and_removes_session(self, engine):
        """close_session releases resources, emits the close event, and removes state."""
        events = []
        engine.register_event_handler("session_closed", lambda e, d: events.append(d))
        sid = engine.create_session()
        assert engine.close_session(sid) is True
        assert sid not in engine.active_sessions
        assert events == [{"session_id": sid}]

    def test_close_session_nonexistent(self, engine):
        result = engine.close_session("nonexistent-id")
        assert result is False

    def test_close_session_sets_completion_before_removal(self, engine):
        """close_session marks the session completed before removing it."""
        sid = engine.create_session()
        session = engine.active_sessions[sid]
        assert session.completed_at is None
        assert engine.close_session(sid) is True
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

    def test_register_event_handler(self, engine):
        def handler(event, data):
            return None

        engine.register_event_handler("test_event", handler)
        assert "test_event" in engine.event_handlers
        assert handler in engine.event_handlers["test_event"]

    def test_register_multiple_handlers(self, engine):
        def h1(e, d):
            return None

        def h2(e, d):
            return None

        engine.register_event_handler("evt", h1)
        engine.register_event_handler("evt", h2)
        assert len(engine.event_handlers["evt"]) == 2

    def test_register_handlers_different_events(self, engine):
        def h1(e, d):
            return None

        def h2(e, d):
            return None

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
        engine.register_event_handler("session_created", lambda e, d: events.append(d))
        sid = engine.create_session(user_id="eve")
        assert len(events) == 1
        assert events[0]["session_id"] == sid
        assert events[0]["user_id"] == "eve"

    def test_session_closed_event_fired(self, engine):
        """close_session emits a session_closed event after cleanup."""
        events = []
        engine.register_event_handler("session_closed", lambda e, d: events.append(d))
        sid = engine.create_session()
        assert engine.close_session(sid) is True
        assert events == [{"session_id": sid}]


# ---------------------------------------------------------------------------
# get_system_status, health_check, get_metrics
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestOrchestrationEngineStatus:
    """Tests for status, health, and metrics methods."""

    def test_get_system_status_reports_real_component_state(self, engine):
        """Regression: get_system_status raised AttributeError because
        ProjectManager.get_projects_summary and
        ResourceManager.get_resource_usage did not exist."""
        engine.project_manager.create_project("p1", ProjectType.RESEARCH)
        engine.workflow_manager.create_workflow(
            "wf", [WorkflowStep(name="s", module="test", action="echo")]
        )
        engine.execute_workflow("wf")

        status = engine.get_system_status()

        assert status["workflow_manager"] == {
            "total_workflows": 1,
            "running_workflows": 0,
        }
        assert status["task_orchestrator"]["completed"] == 1
        assert status["project_manager"]["total_projects"] == 1
        assert status["project_manager"]["by_type"] == {"research": 1}
        assert status["resource_manager"]["total_resources"] == 3
        assert status["resource_manager"]["total_allocations"] == 0
        assert "sys-compute" in status["resource_manager"]["resources"]

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
        for comp_data in result["components"].values():
            assert "status" in comp_data

    def test_get_metrics_reports_real_component_state(self, engine):
        """Regression: get_metrics raised AttributeError (missing
        get_projects_summary / get_resource_usage)."""
        engine.create_session()
        engine.workflow_manager.create_workflow(
            "wf", [WorkflowStep(name="s", module="test", action="fail")]
        )
        engine.execute_workflow("wf")

        metrics = engine.get_metrics()

        assert metrics["sessions"]["by_status"] == {"pending": 1, "failed": 1}
        assert metrics["workflows"]["total_executions"] == 1
        assert metrics["workflows"]["failed_executions"] == 1
        assert metrics["tasks"]["failed"] == 1
        assert metrics["projects"]["total_projects"] == 0
        assert metrics["resources"]["total_resources"] == 3


# ---------------------------------------------------------------------------
# shutdown
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestOrchestrationEngineShutdown:
    """Tests for the shutdown method."""

    def test_shutdown_with_sessions_closes_all_sessions(self, engine):
        """shutdown closes active sessions and stops the task orchestrator."""
        engine.create_session()
        engine.create_session()
        assert len(engine.active_sessions) == 2
        engine.shutdown()
        assert engine.active_sessions == {}
        assert engine.task_orchestrator._stop_event.is_set()

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
# execute_workflow
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestOrchestrationEngineExecuteWorkflow:
    """Tests for execute_workflow."""

    def test_execute_workflow_invalid_session(self, engine):
        result = engine.execute_workflow("some_workflow", session_id="bad-id")
        assert result["success"] is False
        assert "not found" in result["error"]

    def test_execute_workflow_creates_session_then_fails(self, engine):
        """When no session_id, the engine creates one. The workflow
        execution returns a structured failure for an unknown workflow."""
        result = engine.execute_workflow("nonexistent_workflow")
        assert result["success"] is False
        assert "Workflow execution failed" in result["error"]

    def test_execute_workflow_runs_steps_and_reports_success(self, engine):
        """Regression: execute_workflow passed the synchronous
        WorkflowManager.execute_workflow to run_until_complete and therefore
        always returned success=False."""
        events = []
        engine.register_event_handler(
            "workflow_completed", lambda e, d: events.append(d)
        )
        engine.workflow_manager.create_workflow(
            "greet",
            [
                WorkflowStep(
                    name="second",
                    module="test",
                    action="echo",
                    parameters={"message": "two"},
                    dependencies=["first"],
                ),
                WorkflowStep(
                    name="first",
                    module="test",
                    action="sleep",
                    parameters={"duration": 0.1},
                ),
            ],
        )
        session_id = engine.create_session()

        result = engine.execute_workflow("greet", session_id=session_id)

        assert result["success"] is True
        assert result["status"] == "completed"
        assert result["error"] is None
        assert result["steps_executed"] == 2
        assert result["execution_time"] >= 0.1
        assert result["result"]["first"]["result"] == 0.1
        assert result["result"]["second"]["result"] == "two"
        assert engine.get_session(session_id).status is SessionStatus.COMPLETED
        assert events[0]["success"] is True

    def test_execute_workflow_reports_step_failure(self, engine):
        engine.workflow_manager.create_workflow(
            "broken",
            [
                WorkflowStep(
                    name="bad", module="test", action="fail", parameters={"reason": "x"}
                ),
                WorkflowStep(
                    name="after", module="test", action="echo", dependencies=["bad"]
                ),
            ],
        )
        session_id = engine.create_session()

        result = engine.execute_workflow("broken", session_id=session_id)

        assert result["success"] is False
        assert result["status"] == "failed"
        assert "bad: RuntimeError: x" in result["error"]
        assert result["steps_executed"] == 1  # "after" never ran
        assert engine.get_session(session_id).status is SessionStatus.FAILED

    def test_execute_workflow_rejects_invalid_dependencies(self, engine):
        engine.workflow_manager.create_workflow(
            "dangling",
            [WorkflowStep(name="a", module="test", action="echo", dependencies=["x"])],
        )
        result = engine.execute_workflow("dangling")
        assert result["success"] is False
        assert "missing task 'x'" in result["error"]


# ---------------------------------------------------------------------------
# execute_task
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestOrchestrationEngineExecuteTask:
    """Tests for execute_task method."""

    def test_execute_task_invalid_session(self, engine):
        from codomyrmex.logistics.orchestration.project.task_orchestrator import Task

        task = Task(
            name="test", module="test", action="echo", parameters={"message": "hi"}
        )
        result = engine.execute_task(task, session_id="bad-session")
        assert result["success"] is False
        assert "not found" in result["error"]

    def test_execute_task_with_dict_succeeds(self, engine):
        """execute_task accepts dictionary task definitions."""
        task_dict = {
            "name": "t1",
            "module": "test",
            "action": "echo",
            "parameters": {"message": "hello"},
        }
        result = engine.execute_task(task_dict)
        assert result["success"] is True
        assert result["result"]["result"] == "hello"

    def test_execute_task_unknown_action_fails(self, engine):
        result = engine.execute_task(
            {"name": "t1", "module": "m", "action": "echo", "parameters": {}}
        )
        assert result["success"] is False
        assert "codomyrmex.m" in result["error"]

    def test_execute_task_unknown_dependency_fails_fast(self, engine):
        result = engine.execute_task(
            {"name": "t1", "module": "test", "action": "echo", "dependencies": ["x"]}
        )
        assert result["success"] is False
        assert "unknown task ids ['x']" in result["error"]

    def test_execute_task_session_timeout_cancels(self, engine):
        session_id = engine.create_session(timeout_seconds=0.2)
        result = engine.execute_task(
            {
                "name": "slow",
                "module": "test",
                "action": "sleep",
                "parameters": {"duration": 1.0},
            },
            session_id=session_id,
        )
        assert result["success"] is False
        assert "did not finish within 0.2s" in result["error"]
        task = engine.task_orchestrator.get_task(result["task_id"])
        assert task.status.value == "cancelled"


# ---------------------------------------------------------------------------
# execute_project_workflow
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestOrchestrationEngineProjectWorkflow:
    """Tests for execute_project_workflow."""

    def test_execute_project_workflow_invalid_session(self, engine):
        result = engine.execute_project_workflow("proj", "wf", session_id="bad-id")
        assert result["success"] is False
        assert "not found" in result["error"]

    def test_execute_project_workflow_unknown_project(self, engine):
        """Regression: it called the nonexistent
        ProjectManager.execute_project_workflow; now an unknown project is
        reported explicitly."""
        result = engine.execute_project_workflow("proj", "wf")
        assert result == {"success": False, "error": "Project proj not found"}

    def test_execute_project_workflow_runs_and_records_metrics(self, engine):
        engine.project_manager.create_project("proj", ProjectType.CUSTOM)
        engine.workflow_manager.create_workflow(
            "wf", [WorkflowStep(name="s", module="test", action="echo")]
        )
        engine.workflow_manager.create_workflow(
            "bad", [WorkflowStep(name="s", module="test", action="fail")]
        )

        ok = engine.execute_project_workflow("proj", "wf", message="hi")
        failed = engine.execute_project_workflow("proj", "bad")

        assert ok["success"] is True
        assert ok["project_name"] == "proj"
        assert ok["result"]["s"]["result"] == "hi"
        assert failed["success"] is False
        metrics = engine.project_manager.get_project("proj").metrics
        assert metrics["workflow_executions"] == 2
        assert metrics["successful_workflow_executions"] == 1
        assert metrics["last_workflow"] == "bad"
        assert metrics["last_workflow_success"] is False


# ---------------------------------------------------------------------------
# execute_complex_workflow
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestOrchestrationEngineComplexWorkflow:
    """Tests for execute_complex_workflow."""

    def test_execute_complex_workflow_invalid_session(self, engine):
        result = engine.execute_complex_workflow({}, session_id="bad")
        assert result["success"] is False
        assert "not found" in result["error"]

    def test_execute_complex_workflow_empty_steps(self, engine):
        """An empty workflow completes successfully with no step results."""
        result = engine.execute_complex_workflow({"steps": []})
        assert result["success"] is True
        assert result["results"] == {}

    def test_execute_complex_workflow_with_steps_succeeds(self, engine):
        """Steps are parsed into Tasks and executed through the task orchestrator."""
        definition = {
            "steps": [
                {
                    "name": "s1",
                    "module": "test",
                    "action": "echo",
                    "parameters": {"message": "one"},
                },
            ],
            "dependencies": {},
        }
        result = engine.execute_complex_workflow(definition)
        assert result["success"] is True
        assert result["results"]["s1"]["success"] is True
        assert result["results"]["s1"]["result"] == "one"

    def test_execute_complex_workflow_failed_step_is_not_success(self, engine):
        """Regression: success was True whenever all tasks finished, even if
        some failed, and dependencies on later-listed steps were dropped."""
        definition = {
            "steps": [
                {"name": "b", "module": "test", "action": "echo"},
                {"name": "a", "module": "test", "action": "fail"},
            ],
            "dependencies": {"b": ["a"]},
        }
        result = engine.execute_complex_workflow(definition)
        assert result["success"] is False
        assert result["results"]["a"]["status"] == "failed"
        assert result["results"]["b"]["status"] == "failed"
        assert result["results"]["b"]["start_time"] is None  # never ran
        assert "a: RuntimeError: boom" in result["error"]

    def test_execute_complex_workflow_invalid_definition(self, engine):
        result = engine.execute_complex_workflow(
            {
                "steps": [{"name": "a", "module": "test", "action": "echo"}],
                "dependencies": {"a": ["ghost"]},
            }
        )
        assert result["success"] is False
        assert "Invalid workflow definition" in result["error"]


# ---------------------------------------------------------------------------
# create_project_from_workflow
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestOrchestrationEngineCreateProjectFromWorkflow:
    """Tests for create_project_from_workflow."""

    def test_create_project_from_workflow_succeeds(self, engine, tmp_path):
        """Regression: it imported a nonexistent ``models`` module."""
        engine.workflow_manager.create_workflow(
            "wf1", [WorkflowStep(name="s", module="test", action="echo")]
        )
        result = engine.create_project_from_workflow(
            "proj1", "wf1", template_name="data_pipeline", description="d"
        )
        assert result["success"] is True
        assert result["project_created"] is True
        assert result["project"]["type"] == "data_pipeline"
        assert (tmp_path / "proj" / "proj1" / "src").is_dir()
        project = engine.project_manager.get_project("proj1")
        assert "workflow_wf1_completed" in project.milestones
        assert project.metrics["workflow_executions"] == 1

    def test_create_project_from_workflow_reports_workflow_failure(self, engine):
        """The project is created but a failed workflow is not reported as
        success (it used to return success=True regardless)."""
        result = engine.create_project_from_workflow("proj1", "missing_wf")
        assert result["success"] is False
        assert result["project_created"] is True
        assert "Workflow not found" in result["error"]
        assert engine.project_manager.get_project("proj1").milestones == {}

    def test_create_project_from_workflow_unknown_template(self, engine):
        result = engine.create_project_from_workflow("p", "wf", template_name="nope")
        assert result["success"] is False
        assert result["project_created"] is False
        assert "Unknown project template 'nope'" in result["error"]

    def test_create_project_from_workflow_existing_project(self, engine):
        engine.project_manager.create_project("dup", ProjectType.CUSTOM)
        result = engine.create_project_from_workflow("dup", "wf")
        assert result["success"] is False
        assert result["project_created"] is False
        assert "could not be created" in result["error"]


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
            assert "input_schema" in tool_def, (
                f"Tool {tool_name} missing 'input_schema'"
            )

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
        """TaskResult exposes a stable dictionary representation."""
        from codomyrmex.logistics.orchestration.project.task_orchestrator import (
            TaskResult,
            TaskStatus,
        )

        tr = TaskResult(task_id="t1", status=TaskStatus.COMPLETED, result="ok")
        assert tr.to_dict()["success"] is True
        assert tr.to_dict()["result"] == "ok"
