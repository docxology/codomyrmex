"""
Unit tests for collaboration.models — Zero-Mock compliant.

Covers: TaskPriority (enum values), TaskStatus (enum values),
Task (defaults, id auto-gen, to_dict, from_dict, is_ready),
TaskResult (defaults, to_dict, from_dict),
SwarmStatus (defaults, to_dict),
AgentStatus (defaults, to_dict, from_dict).
"""

import pytest

from codomyrmex.collaboration.models import (
    AgentStatus,
    SwarmStatus,
    Task,
    TaskPriority,
    TaskResult,
    TaskStatus,
)

# ── TaskPriority ───────────────────────────────────────────────────────


@pytest.mark.unit
class TestTaskPriority:
    def test_low_value(self):
        assert TaskPriority.LOW.value == 1

    def test_normal_value(self):
        assert TaskPriority.NORMAL.value == 5

    def test_high_value(self):
        assert TaskPriority.HIGH.value == 8

    def test_critical_value(self):
        assert TaskPriority.CRITICAL.value == 10


# ── TaskStatus ─────────────────────────────────────────────────────────


@pytest.mark.unit
class TestTaskStatus:
    def test_pending_value(self):
        assert TaskStatus.PENDING.value == "pending"

    def test_queued_value(self):
        assert TaskStatus.QUEUED.value == "queued"

    def test_running_value(self):
        assert TaskStatus.RUNNING.value == "running"

    def test_completed_value(self):
        assert TaskStatus.COMPLETED.value == "completed"

    def test_failed_value(self):
        assert TaskStatus.FAILED.value == "failed"

    def test_cancelled_value(self):
        assert TaskStatus.CANCELLED.value == "cancelled"


# ── Task ───────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestTask:
    def test_name_required(self):
        t = Task(name="my task")
        assert t.name == "my task"

    def test_id_auto_generated(self):
        t = Task(name="task")
        assert len(t.id) > 0

    def test_ids_unique(self):
        t1 = Task(name="task1")
        t2 = Task(name="task2")
        assert t1.id != t2.id

    def test_description_default_empty(self):
        t = Task(name="task")
        assert t.description == ""

    def test_required_capabilities_default_empty(self):
        t = Task(name="task")
        assert t.required_capabilities == []

    def test_priority_default_five(self):
        t = Task(name="task")
        assert t.priority == 5

    def test_dependencies_default_empty(self):
        t = Task(name="task")
        assert t.dependencies == []

    def test_status_default_pending(self):
        t = Task(name="task")
        assert t.status == TaskStatus.PENDING

    def test_assigned_agent_default_none(self):
        t = Task(name="task")
        assert t.assigned_agent_id is None

    def test_created_at_set(self):
        t = Task(name="task")
        assert t.created_at is not None

    def test_to_dict_has_required_keys(self):
        t = Task(name="build feature", description="build it")
        d = t.to_dict()
        for key in ("id", "name", "description", "status", "priority",
                    "dependencies", "required_capabilities", "metadata",
                    "created_at", "assigned_agent_id"):
            assert key in d

    def test_to_dict_name_stored(self):
        t = Task(name="my task")
        assert t.to_dict()["name"] == "my task"

    def test_to_dict_status_as_string(self):
        t = Task(name="task")
        assert t.to_dict()["status"] == "pending"

    def test_to_dict_created_at_isoformat(self):
        t = Task(name="task")
        iso = t.to_dict()["created_at"]
        assert "T" in iso  # ISO 8601 datetime

    def test_from_dict_round_trip(self):
        original = Task(
            name="test task",
            description="test desc",
            required_capabilities=["python"],
            priority=8,
        )
        d = original.to_dict()
        restored = Task.from_dict(d)
        assert restored.id == original.id
        assert restored.name == original.name
        assert restored.description == original.description
        assert restored.priority == original.priority
        assert restored.status == original.status

    def test_from_dict_minimal(self):
        """from_dict works with just 'name' key."""
        t = Task.from_dict({"name": "minimal task"})
        assert t.name == "minimal task"
        assert t.description == ""

    def test_from_dict_status_conversion(self):
        t = Task.from_dict({"name": "t", "status": "completed"})
        assert t.status == TaskStatus.COMPLETED

    def test_is_ready_no_dependencies(self):
        t = Task(name="task")
        assert t.is_ready([]) is True
        assert t.is_ready(["some-id"]) is True

    def test_is_ready_dependencies_satisfied(self):
        t = Task(name="task", dependencies=["dep1", "dep2"])
        assert t.is_ready(["dep1", "dep2", "dep3"]) is True

    def test_is_ready_dependencies_not_satisfied(self):
        t = Task(name="task", dependencies=["dep1", "dep2"])
        assert t.is_ready(["dep1"]) is False

    def test_is_ready_empty_completed_with_deps(self):
        t = Task(name="task", dependencies=["dep1"])
        assert t.is_ready([]) is False


# ── TaskResult ─────────────────────────────────────────────────────────


@pytest.mark.unit
class TestTaskResult:
    def test_task_id_and_success_stored(self):
        r = TaskResult(task_id="task-1", success=True)
        assert r.task_id == "task-1"
        assert r.success is True

    def test_output_default_none(self):
        r = TaskResult(task_id="t", success=True)
        assert r.output is None

    def test_error_default_none(self):
        r = TaskResult(task_id="t", success=True)
        assert r.error is None

    def test_duration_default_zero(self):
        r = TaskResult(task_id="t", success=True)
        assert r.duration == pytest.approx(0.0)

    def test_agent_id_default_empty(self):
        r = TaskResult(task_id="t", success=True)
        assert r.agent_id == ""

    def test_to_dict_has_keys(self):
        r = TaskResult(task_id="t1", success=False, error="timeout")
        d = r.to_dict()
        for key in ("task_id", "success", "output", "error", "duration",
                    "agent_id", "completed_at"):
            assert key in d

    def test_to_dict_success_false(self):
        r = TaskResult(task_id="t", success=False)
        assert r.to_dict()["success"] is False

    def test_to_dict_completed_at_isoformat(self):
        r = TaskResult(task_id="t", success=True)
        iso = r.to_dict()["completed_at"]
        assert "T" in iso

    def test_from_dict_round_trip(self):
        original = TaskResult(
            task_id="task-123",
            success=True,
            output={"result": 42},
            duration=1.5,
            agent_id="agent-1",
        )
        d = original.to_dict()
        restored = TaskResult.from_dict(d)
        assert restored.task_id == "task-123"
        assert restored.success is True
        assert restored.output == {"result": 42}
        assert restored.duration == pytest.approx(1.5)

    def test_from_dict_minimal(self):
        r = TaskResult.from_dict({"task_id": "t1", "success": True})
        assert r.task_id == "t1"
        assert r.error is None

    def test_from_dict_failure(self):
        r = TaskResult.from_dict({
            "task_id": "t1",
            "success": False,
            "error": "timed out",
        })
        assert r.success is False
        assert r.error == "timed out"


# ── SwarmStatus ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestSwarmStatus:
    def test_defaults_zero(self):
        s = SwarmStatus()
        assert s.total_agents == 0
        assert s.active_agents == 0
        assert s.idle_agents == 0
        assert s.pending_tasks == 0
        assert s.running_tasks == 0
        assert s.completed_tasks == 0
        assert s.failed_tasks == 0
        assert s.uptime_seconds == pytest.approx(0.0)

    def test_custom_values(self):
        s = SwarmStatus(total_agents=5, active_agents=3, completed_tasks=100)
        assert s.total_agents == 5
        assert s.active_agents == 3
        assert s.completed_tasks == 100

    def test_to_dict_has_all_keys(self):
        s = SwarmStatus()
        d = s.to_dict()
        for key in ("total_agents", "active_agents", "idle_agents",
                    "pending_tasks", "running_tasks", "completed_tasks",
                    "failed_tasks", "uptime_seconds"):
            assert key in d

    def test_to_dict_values_match(self):
        s = SwarmStatus(total_agents=10, failed_tasks=2)
        d = s.to_dict()
        assert d["total_agents"] == 10
        assert d["failed_tasks"] == 2


# ── AgentStatus ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestAgentStatus:
    def test_agent_id_required(self):
        a = AgentStatus(agent_id="agent-1")
        assert a.agent_id == "agent-1"

    def test_name_default_empty(self):
        a = AgentStatus(agent_id="agent-1")
        assert a.name == ""

    def test_status_default_idle(self):
        a = AgentStatus(agent_id="agent-1")
        assert a.status == "idle"

    def test_current_task_id_default_none(self):
        a = AgentStatus(agent_id="agent-1")
        assert a.current_task_id is None

    def test_capabilities_default_empty(self):
        a = AgentStatus(agent_id="agent-1")
        assert a.capabilities == []

    def test_tasks_completed_default_zero(self):
        a = AgentStatus(agent_id="agent-1")
        assert a.tasks_completed == 0

    def test_tasks_failed_default_zero(self):
        a = AgentStatus(agent_id="agent-1")
        assert a.tasks_failed == 0

    def test_to_dict_has_keys(self):
        a = AgentStatus(agent_id="agent-1")
        d = a.to_dict()
        for key in ("agent_id", "name", "status", "current_task_id",
                    "capabilities", "tasks_completed", "tasks_failed",
                    "last_heartbeat"):
            assert key in d

    def test_to_dict_last_heartbeat_isoformat(self):
        a = AgentStatus(agent_id="agent-1")
        iso = a.to_dict()["last_heartbeat"]
        assert "T" in iso

    def test_from_dict_round_trip(self):
        original = AgentStatus(
            agent_id="agent-42",
            name="Worker",
            status="busy",
            capabilities=["python", "shell"],
            tasks_completed=5,
        )
        d = original.to_dict()
        restored = AgentStatus.from_dict(d)
        assert restored.agent_id == "agent-42"
        assert restored.name == "Worker"
        assert restored.status == "busy"
        assert restored.capabilities == ["python", "shell"]
        assert restored.tasks_completed == 5

    def test_from_dict_minimal(self):
        a = AgentStatus.from_dict({"agent_id": "a1"})
        assert a.agent_id == "a1"
        assert a.status == "idle"

    def test_from_dict_current_task_none_when_absent(self):
        a = AgentStatus.from_dict({"agent_id": "a1"})
        assert a.current_task_id is None
