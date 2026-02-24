"""Tests for Sprint 25 (Integration) and Sprint 26 (Planning)."""

from __future__ import annotations

import pytest

from codomyrmex.events.integration_bus import IntegrationBus, IntegrationEvent
from codomyrmex.orchestrator.module_connector import ModuleConnector, ServiceBinding
from codomyrmex.agents.planner.plan_engine import (
    Plan, PlanEngine, PlanTask, TaskPriority, TaskState,
)
from codomyrmex.agents.planner.executor import ExecutionResult, PlanExecutor


# ── IntegrationBus ───────────────────────────────────────────────


class TestIntegrationBus:
    """Test suite for IntegrationBus."""
    def test_emit_and_subscribe(self) -> None:
        """Test functionality: emit and subscribe."""
        bus = IntegrationBus()
        received: list[IntegrationEvent] = []
        bus.subscribe("build.done", lambda e: received.append(e))
        bus.emit("build.done", source="ci")
        assert len(received) == 1
        assert received[0].source == "ci"

    def test_no_subscriber(self) -> None:
        """Test functionality: no subscriber."""
        bus = IntegrationBus()
        event = bus.emit("orphan.topic")
        assert event.topic == "orphan.topic"

    def test_wildcard_subscriber(self) -> None:
        """Test functionality: wildcard subscriber."""
        bus = IntegrationBus()
        caught: list[str] = []
        bus.subscribe("*", lambda e: caught.append(e.topic))
        bus.emit("a")
        bus.emit("b")
        assert len(caught) == 2

    def test_history(self) -> None:
        """Test functionality: history."""
        bus = IntegrationBus()
        bus.emit("x")
        bus.emit("y")
        assert bus.history_size == 2
        assert len(bus.history_by_topic("x")) == 1

    def test_handler_error_isolation(self) -> None:
        """Test functionality: handler error isolation."""
        bus = IntegrationBus()
        bus.subscribe("err", lambda e: (_ for _ in ()).throw(RuntimeError("boom")))
        event = bus.emit("err")
        assert event.topic == "err"  # No crash


# ── ModuleConnector ──────────────────────────────────────────────


class TestModuleConnector:
    """Test suite for ModuleConnector."""
    def test_register_and_resolve(self) -> None:
        """Test functionality: register and resolve."""
        mc = ModuleConnector()
        mc.register("db", lambda: {"engine": "sqlite"})
        result = mc.resolve("db")
        assert result["engine"] == "sqlite"

    def test_singleton(self) -> None:
        """Test functionality: singleton."""
        mc = ModuleConnector()
        mc.register("svc", lambda: object())
        a = mc.resolve("svc")
        b = mc.resolve("svc")
        assert a is b

    def test_non_singleton(self) -> None:
        """Test functionality: non singleton."""
        mc = ModuleConnector()
        mc.register("svc", lambda: object(), singleton=False)
        a = mc.resolve("svc")
        b = mc.resolve("svc")
        assert a is not b

    def test_missing_service(self) -> None:
        """Test functionality: missing service."""
        mc = ModuleConnector()
        with pytest.raises(KeyError):
            mc.resolve("nope")

    def test_by_tag(self) -> None:
        """Test functionality: by tag."""
        mc = ModuleConnector()
        mc.register("a", lambda: 1, tags=["core"])
        mc.register("b", lambda: 2, tags=["ext"])
        assert mc.services_by_tag("core") == ["a"]

    def test_service_count(self) -> None:
        """Test functionality: service count."""
        mc = ModuleConnector()
        mc.register("x", lambda: 1)
        assert mc.service_count == 1


# ── PlanEngine ───────────────────────────────────────────────────


class TestPlanEngine:
    """Test suite for PlanEngine."""
    def test_decompose_build(self) -> None:
        """Test functionality: decompose build."""
        engine = PlanEngine()
        plan = engine.decompose("Build a REST API")
        assert len(plan.tasks) >= 3
        assert plan.total_tasks > 3  # Should have subtasks

    def test_decompose_fix(self) -> None:
        """Test functionality: decompose fix."""
        engine = PlanEngine()
        plan = engine.decompose("Fix the login bug")
        task_names = [t.name for t in plan.tasks]
        assert "diagnose" in task_names

    def test_decompose_analyze(self) -> None:
        """Test functionality: decompose analyze."""
        engine = PlanEngine()
        plan = engine.decompose("Analyze system performance")
        task_names = [t.name for t in plan.tasks]
        assert "analyze" in task_names

    def test_max_depth(self) -> None:
        """Test functionality: max depth."""
        engine = PlanEngine()
        shallow = engine.decompose("Do something", max_depth=0)
        deep = engine.decompose("Do something", max_depth=2)
        assert deep.total_tasks > shallow.total_tasks

    def test_task_dependencies(self) -> None:
        """Test functionality: task dependencies."""
        engine = PlanEngine()
        plan = engine.decompose("Build it")
        second_task = plan.tasks[1]
        assert len(second_task.depends_on) > 0


# ── PlanExecutor ─────────────────────────────────────────────────


class TestPlanExecutor:
    """Test suite for PlanExecutor."""
    def test_execute_all_succeed(self) -> None:
        """Test functionality: execute all succeed."""
        engine = PlanEngine()
        plan = engine.decompose("Build app", max_depth=0)
        executor = PlanExecutor()
        result = executor.execute(plan)
        assert result.success
        assert result.completed_tasks == len(plan.tasks)

    def test_execute_with_actions(self) -> None:
        """Test functionality: execute with actions."""
        plan = Plan(goal="test", tasks=[PlanTask("step1"), PlanTask("step2")])
        results: list[str] = []
        executor = PlanExecutor()
        result = executor.execute(plan, actions={
            "step1": lambda t: results.append(t.name),
        })
        assert result.success
        assert "step1" in results

    def test_execute_with_failure(self) -> None:
        """Test functionality: execute with failure."""
        plan = Plan(goal="test", tasks=[PlanTask("fail_step")])
        executor = PlanExecutor()
        result = executor.execute(plan, actions={
            "fail_step": lambda t: (_ for _ in ()).throw(RuntimeError("boom")),
        })
        assert not result.success
        assert result.failed_tasks == 1

    def test_completion_rate(self) -> None:
        """Test functionality: completion rate."""
        plan = Plan(goal="test", tasks=[PlanTask("a"), PlanTask("b")])
        executor = PlanExecutor()
        executor.execute(plan)
        assert plan.completion_rate == 1.0
