"""Tests for WorkflowManager.execute_workflow / execute_steps.

Covers dependency (topological) ordering independent of listing order,
explicit failure on invalid definitions, final status/end time, step failure
propagation, parameter merging, timeouts, and parallel workflows sharing the
orchestrator's registered actions.

Zero-mock policy: steps run real registered functions on a real
TaskOrchestrator.
"""

from __future__ import annotations

import threading
import time

import pytest

from codomyrmex.logistics.orchestration.project.resource_manager import (
    ResourceManager,
)
from codomyrmex.logistics.orchestration.project.task_orchestrator import (
    TaskOrchestrator,
)
from codomyrmex.logistics.orchestration.project.workflow_manager import (
    WorkflowManager,
    WorkflowStatus,
    WorkflowStep,
)

pytestmark = pytest.mark.unit


@pytest.fixture
def calls() -> list[tuple[str, dict]]:
    return []


@pytest.fixture
def manager(tmp_path, calls):
    lock = threading.Lock()
    orchestrator = TaskOrchestrator(max_workers=4, resource_manager=ResourceManager())

    def record(label: str, delay: float = 0.0, **kwargs):
        time.sleep(delay)
        with lock:
            calls.append((label, kwargs))
        return label

    def fail(label: str, **kwargs):
        with lock:
            calls.append((label, kwargs))
        raise RuntimeError(f"{label} failed")

    orchestrator.register_action("test", "record", record)
    orchestrator.register_action("test", "fail", fail)
    wm = WorkflowManager(
        persistence_dir=tmp_path / "persist",
        config_dir=tmp_path / "workflows",
        task_orchestrator=orchestrator,
    )
    yield wm
    orchestrator.stop_execution()


def step(name: str, *deps: str, action: str = "record", **params) -> WorkflowStep:
    return WorkflowStep(
        name=name,
        module="test",
        action=action,
        parameters={"label": name, **params},
        dependencies=list(deps),
    )


def labels(calls) -> list[str]:
    return [label for label, _ in calls]


class TestExecutionOrder:
    def test_dependency_listed_later_is_enforced(self, manager, calls):
        """Regression: deps on later-listed steps were silently dropped."""
        manager.create_workflow(
            "ordered",
            [step("second", "first"), step("first", delay=0.2)],
        )
        execution = manager.execute_workflow("ordered")

        assert labels(calls) == ["first", "second"]
        assert execution.status is WorkflowStatus.COMPLETED
        assert execution.success is True
        second = manager.task_orchestrator.get_task(
            execution.step_results["second"]["task_id"]
        )
        first_id = execution.step_results["first"]["task_id"]
        assert second.dependencies == [first_id]

    def test_diamond_respects_all_edges(self, manager, calls):
        manager.create_workflow(
            "diamond",
            [
                step("join", "left", "right"),
                step("right", "root", delay=0.1),
                step("left", "root"),
                step("root"),
            ],
        )
        execution = manager.execute_workflow("diamond")
        order = labels(calls)
        assert execution.status is WorkflowStatus.COMPLETED
        assert order[0] == "root"
        assert order[-1] == "join"
        assert set(order[1:3]) == {"left", "right"}

    def test_execution_finishes_with_end_time_and_results(self, manager):
        """Regression: the returned execution stayed RUNNING with no end time."""
        manager.create_workflow("single", [step("only")])
        execution = manager.execute_workflow("single")
        assert execution.status is WorkflowStatus.COMPLETED
        assert execution.end_time is not None
        assert execution.duration is not None and execution.duration >= 0
        assert execution.error is None
        assert execution.step_results["only"]["status"] == "completed"
        assert execution.step_results["only"]["result"] == "only"
        assert manager.get_execution_status(execution.execution_id) is execution

    def test_workflow_params_merged_into_step_parameters(self, manager, calls):
        manager.create_workflow("params", [step("a", extra=1)])
        manager.execute_workflow("params", extra=2, more="x")
        assert calls == [("a", {"extra": 2, "more": "x"})]

    def test_empty_workflow_completes(self, manager):
        manager.create_workflow("empty", [])
        execution = manager.execute_workflow("empty")
        assert execution.status is WorkflowStatus.COMPLETED
        assert execution.step_results == {}


class TestFailures:
    def test_failed_step_fails_workflow_and_skips_dependents(self, manager, calls):
        manager.create_workflow(
            "broken",
            [
                step("boom", action="fail"),
                step("after", "boom"),
                step("independent"),
            ],
        )
        execution = manager.execute_workflow("broken")

        assert execution.status is WorkflowStatus.FAILED
        assert execution.end_time is not None
        assert "boom: RuntimeError: boom failed" in execution.error
        assert "after: Dependency 'boom'" in execution.error
        assert execution.step_results["after"]["status"] == "failed"
        assert execution.step_results["independent"]["status"] == "completed"
        assert sorted(labels(calls)) == ["boom", "independent"]

    def test_unknown_action_fails_workflow(self, manager):
        manager.create_workflow(
            "unknown",
            [WorkflowStep(name="s", module="no_such_module", action="nothing")],
        )
        execution = manager.execute_workflow("unknown")
        assert execution.status is WorkflowStatus.FAILED
        assert "codomyrmex.no_such_module" in execution.error

    def test_optional_step_failure_does_not_fail_workflow(self, manager):
        optional = step("optional", action="fail")
        optional.required = False
        manager.create_workflow("lenient", [optional, step("main")])
        execution = manager.execute_workflow("lenient")
        assert execution.status is WorkflowStatus.COMPLETED
        assert execution.step_results["optional"]["status"] == "failed"

    def test_timeout_cancels_unfinished_steps(self, manager, calls):
        execution = manager.execute_steps(
            "slow",
            [step("slow", delay=1.0), step("after", "slow")],
            timeout=0.2,
        )
        assert execution.status is WorkflowStatus.FAILED
        assert "timed out after 0.2s" in execution.error
        assert execution.step_results["after"]["status"] == "cancelled"
        time.sleep(1.2)
        assert "after" not in labels(calls)


class TestInvalidDefinitions:
    def test_unknown_workflow_raises(self, manager):
        with pytest.raises(ValueError, match="Workflow not found"):
            manager.execute_workflow("missing")

    def test_missing_dependency_raises(self, manager, calls):
        manager.create_workflow("dangling", [step("a", "ghost")])
        with pytest.raises(ValueError, match="missing task 'ghost'"):
            manager.execute_workflow("dangling")
        assert calls == []
        assert manager.executions == {}

    def test_cycle_raises(self, manager, calls):
        manager.create_workflow("cycle", [step("a", "b"), step("b", "a")])
        with pytest.raises(ValueError, match="Cycle detected"):
            manager.execute_workflow("cycle")
        assert calls == []

    def test_duplicate_step_names_raise(self, manager):
        manager.create_workflow("dupes", [step("a"), step("a")])
        with pytest.raises(ValueError, match="duplicate step names"):
            manager.execute_workflow("dupes")

    def test_run_if_is_not_silently_ignored(self, manager, calls):
        conditional = step("a")
        conditional.run_if = "a > 1"
        manager.create_workflow("conditional", [conditional])
        with pytest.raises(NotImplementedError, match="run_if"):
            manager.execute_workflow("conditional")
        assert calls == []


class TestSummariesAndParallel:
    def test_performance_summary_counts_outcomes(self, manager):
        manager.create_workflow("ok", [step("a")])
        manager.create_workflow("bad", [step("b", action="fail")])
        manager.execute_workflow("ok")
        manager.execute_workflow("bad")
        summary = manager.get_performance_summary()
        assert summary["total_executions"] == 2
        assert summary["successful_executions"] == 1
        assert summary["failed_executions"] == 1
        assert summary["running_executions"] == 0

    def test_parallel_workflow_uses_registered_actions(self, manager, calls):
        result = manager.execute_parallel_workflow(
            {
                "tasks": [
                    {
                        "name": "b",
                        "module": "test",
                        "action": "record",
                        "parameters": {"label": "b"},
                    },
                    {
                        "name": "a",
                        "module": "test",
                        "action": "record",
                        "parameters": {"label": "a", "delay": 0.1},
                    },
                ],
                "dependencies": {"b": ["a"]},
            }
        )
        assert result["status"] == "completed"
        assert result["completed_tasks"] == 2
        assert labels(calls) == ["a", "b"]
