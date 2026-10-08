"""Tests for TaskOrchestrator task dispatch, dependencies, cancellation and resources.

Tasks name the code they run with ``module`` and ``action``. These tests check
that the orchestrator really calls that code (registered callables and
``codomyrmex.<module>.<action>`` resolved by import), that unknown code fails
the task instead of being reported as executed, and that resource requirements
are allocated around execution.

Zero-mock policy: actions are real functions; resources come from a real
ResourceManager.
"""

from __future__ import annotations

import threading
import time

import pytest

from codomyrmex.exceptions import TaskExecutionError
from codomyrmex.logistics.orchestration.project.resource_manager import (
    Resource,
    ResourceManager,
    ResourceStatus,
    ResourceType,
)
from codomyrmex.logistics.orchestration.project.task_orchestrator import (
    ActionRegistry,
    Task,
    TaskOrchestrator,
    TaskResource,
    TaskStatus,
    invoke_action,
    resolve_module_action,
)

pytestmark = pytest.mark.unit


class CallLog:
    """Thread-safe record of action calls."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []
        self._lock = threading.Lock()

    def add(self, name: str, **kwargs) -> None:
        with self._lock:
            self.calls.append((name, kwargs))

    @property
    def names(self) -> list[str]:
        with self._lock:
            return [name for name, _ in self.calls]


@pytest.fixture
def log() -> CallLog:
    return CallLog()


@pytest.fixture
def resources() -> ResourceManager:
    return ResourceManager()


@pytest.fixture
def orchestrator(log: CallLog, resources: ResourceManager):
    orch = TaskOrchestrator(max_workers=2, resource_manager=resources)

    def echo(message: str = "") -> str:
        log.add("echo", message=message)
        return message

    def sleep(duration: float = 0.1) -> float:
        log.add("sleep", duration=duration)
        time.sleep(duration)
        return duration

    def fail(reason: str = "boom") -> None:
        log.add("fail", reason=reason)
        raise ValueError(reason)

    orch.register_action("test", "echo", echo)
    orch.register_action("test", "sleep", sleep)
    orch.register_action("test", "fail", fail)
    orch.start_processing()
    yield orch
    orch.stop_execution()


# ---------------------------------------------------------------------------
# Resolution
# ---------------------------------------------------------------------------


class TestResolveModuleAction:
    def test_resolves_real_codomyrmex_function(self):
        from codomyrmex.logistics.orchestration.project import parallel_executor

        func = resolve_module_action(
            "logistics.orchestration.project.parallel_executor",
            "validate_workflow_dependencies",
        )
        assert func is parallel_executor.validate_workflow_dependencies

    def test_unknown_module_raises(self):
        with pytest.raises(TaskExecutionError, match="codomyrmex.no_such_module"):
            resolve_module_action("no_such_module", "run")

    def test_unknown_action_raises(self):
        with pytest.raises(TaskExecutionError, match="has no action 'no_such_action'"):
            resolve_module_action(
                "logistics.orchestration.project.parallel_executor", "no_such_action"
            )

    def test_non_callable_attribute_raises(self):
        with pytest.raises(TaskExecutionError, match="is not callable"):
            resolve_module_action(
                "logistics.orchestration.project.task_orchestrator",
                "TERMINAL_STATUSES",
            )

    @pytest.mark.parametrize("module", ["", "../etc", "os; rm", ".relative", "a..b"])
    def test_malformed_module_rejected(self, module):
        with pytest.raises(TaskExecutionError, match="Invalid task module"):
            resolve_module_action(module, "run")

    @pytest.mark.parametrize("action", ["", "_private", "__import__", "a.b", "a-b"])
    def test_non_public_action_rejected(self, action):
        with pytest.raises(TaskExecutionError, match="Invalid task action"):
            resolve_module_action("logistics", action)


class TestActionRegistry:
    def test_registered_action_wins_over_import(self):
        registry = ActionRegistry()

        def replacement(**kwargs):
            return ("registered", kwargs)

        registry.register(
            "logistics.orchestration.project.parallel_executor",
            "validate_workflow_dependencies",
            replacement,
        )
        assert (
            registry.resolve(
                "logistics.orchestration.project.parallel_executor",
                "validate_workflow_dependencies",
            )
            is replacement
        )

    def test_unregister(self):
        registry = ActionRegistry()
        registry.register("test", "echo", str)
        assert registry.unregister("test", "echo") is True
        assert registry.unregister("test", "echo") is False
        assert registry.get("test", "echo") is None

    def test_register_rejects_non_callable(self):
        with pytest.raises(TypeError):
            ActionRegistry().register("test", "x", 42)


class TestInvokeAction:
    def test_passes_parameters_as_keywords(self):
        def add(a, b):
            return a + b

        assert invoke_action(add, {"a": 2, "b": 3}) == 5

    def test_runs_coroutine_functions(self):
        async def double(value):
            return value * 2

        assert invoke_action(double, {"value": 21}) == 42


# ---------------------------------------------------------------------------
# Execution through the orchestrator
# ---------------------------------------------------------------------------


class TestDispatch:
    def test_registered_action_is_called_with_parameters(self, orchestrator, log):
        result = orchestrator.execute_task(
            Task(name="t", module="test", action="echo", parameters={"message": "hi"})
        )
        assert result.status is TaskStatus.COMPLETED
        assert result.result == "hi"
        assert log.calls == [("echo", {"message": "hi"})]

    def test_imported_action_is_really_called(self, orchestrator):
        task = Task(
            name="validate",
            module="logistics.orchestration.project.parallel_executor",
            action="validate_workflow_dependencies",
            parameters={"tasks": [{"name": "a", "dependencies": ["ghost"]}]},
        )
        result = orchestrator.execute_task(task)
        assert result.status is TaskStatus.COMPLETED
        assert result.result == ["Task 'a' depends on missing task 'ghost'"]

    def test_unknown_module_fails_instead_of_reporting_executed(self, orchestrator):
        """Regression: unknown module/action used to complete with a canned result."""
        result = orchestrator.execute_task(
            Task(name="t", module="no_such_module", action="whatever")
        )
        assert result.status is TaskStatus.FAILED
        assert result.success is False
        assert result.result is None
        assert "codomyrmex.no_such_module" in result.error

    def test_unknown_action_on_real_module_fails(self, orchestrator):
        result = orchestrator.execute_task(
            Task(name="t", module="logistics", action="no_such_action")
        )
        assert result.status is TaskStatus.FAILED
        assert "has no action 'no_such_action'" in result.error

    @pytest.mark.parametrize("action", ["echo", "sleep", "fail"])
    def test_former_builtin_names_are_not_special(self, orchestrator, log, action):
        """'echo'/'sleep'/'fail' on an unknown module are not simulated any more."""
        result = orchestrator.execute_task(Task(name="t", module="m", action=action))
        assert result.status is TaskStatus.FAILED
        assert log.calls == []

    def test_action_exception_fails_task(self, orchestrator):
        result = orchestrator.execute_task(
            Task(name="t", module="test", action="fail", parameters={"reason": "bad"})
        )
        assert result.status is TaskStatus.FAILED
        assert result.error == "ValueError: bad"

    def test_wrong_parameters_fail_task(self, orchestrator):
        result = orchestrator.execute_task(
            Task(name="t", module="test", action="echo", parameters={"nope": 1})
        )
        assert result.status is TaskStatus.FAILED
        assert "TypeError" in result.error

    def test_stats_count_real_outcomes(self, orchestrator):
        orchestrator.execute_task(Task(name="ok", module="test", action="echo"))
        orchestrator.execute_task(Task(name="bad", module="test", action="fail"))
        stats = orchestrator.get_execution_stats()
        assert stats["completed"] == 1
        assert stats["failed"] == 1
        assert stats["total_tasks"] == 2


class TestDependencies:
    def test_dependent_runs_after_dependency(self, orchestrator, log):
        first = Task(
            name="first", module="test", action="sleep", parameters={"duration": 0.2}
        )
        second = Task(
            name="second",
            module="test",
            action="echo",
            parameters={"message": "after"},
            dependencies=[first.id],
        )
        orchestrator.submit_task(first)
        orchestrator.submit_task(second)
        assert orchestrator.wait_for_tasks([first.id, second.id], timeout=10)
        assert log.names == ["sleep", "echo"]
        assert second.started_at is not None and first.completed_at is not None
        assert second.started_at >= first.completed_at

    def test_failed_dependency_fails_dependent_without_running_it(
        self, orchestrator, log
    ):
        """Dependents of a failed task used to stay BLOCKED forever."""
        first = Task(name="first", module="test", action="fail")
        second = Task(
            name="second", module="test", action="echo", dependencies=[first.id]
        )
        third = Task(
            name="third", module="test", action="echo", dependencies=[second.id]
        )
        for task in (first, second, third):
            orchestrator.submit_task(task)
        assert orchestrator.wait_for_tasks([first.id, second.id, third.id], timeout=10)
        assert first.status is TaskStatus.FAILED
        assert second.status is TaskStatus.FAILED
        assert third.status is TaskStatus.FAILED
        assert "Dependency 'first'" in (second.error or "")
        assert "Dependency 'second'" in (third.error or "")
        assert log.names == ["fail"]

    def test_unknown_dependency_stays_blocked(self, orchestrator):
        task = Task(name="t", module="test", action="echo", dependencies=["missing"])
        orchestrator.submit_task(task)
        assert orchestrator.wait_for_tasks([task.id], timeout=0.3) is False
        assert task.status is TaskStatus.BLOCKED


class TestCancellation:
    def test_cancelled_queued_task_never_runs(self, log, resources):
        orch = TaskOrchestrator(max_workers=1, resource_manager=resources)
        orch.register_action(
            "test", "sleep", lambda duration: (log.add("sleep"), time.sleep(duration))
        )
        orch.register_action("test", "echo", lambda: log.add("echo"))
        try:
            blocker = Task(
                name="blocker",
                module="test",
                action="sleep",
                parameters={"duration": 0.4},
            )
            queued = Task(name="queued", module="test", action="echo")
            orch.submit_task(blocker)
            deadline = time.monotonic() + 5
            while blocker.status is not TaskStatus.RUNNING:
                assert time.monotonic() < deadline
                time.sleep(0.01)
            orch.submit_task(queued)
            assert orch.cancel_task(queued.id) is True
            assert orch.wait_for_tasks([blocker.id, queued.id], timeout=5)
            time.sleep(0.3)  # give the processor a chance to (wrongly) run it
            assert queued.status is TaskStatus.CANCELLED
            assert log.names == ["sleep"]
            assert orch.get_task_result(queued.id).status is TaskStatus.CANCELLED
        finally:
            orch.stop_execution()

    def test_cancelled_running_task_is_not_reported_completed(self, orchestrator):
        task = Task(
            name="slow", module="test", action="sleep", parameters={"duration": 0.3}
        )
        orchestrator.submit_task(task)
        deadline = time.monotonic() + 5
        while task.status is not TaskStatus.RUNNING:
            assert time.monotonic() < deadline
            time.sleep(0.01)
        assert orchestrator.cancel_task(task.id) is True
        time.sleep(0.6)  # the thread finishes; its result must be discarded
        assert task.status is TaskStatus.CANCELLED
        assert task.result.status is TaskStatus.CANCELLED
        assert task.result.result is None
        assert orchestrator.running_tasks == {}

    def test_cancel_finished_task_returns_false(self, orchestrator):
        task = Task(name="t", module="test", action="echo")
        orchestrator.execute_task(task)
        assert orchestrator.cancel_task(task.id) is False


class TestWaitForTasks:
    def test_unknown_id_raises(self, orchestrator):
        with pytest.raises(KeyError):
            orchestrator.wait_for_tasks(["nope"])

    def test_empty_list_returns_true(self, orchestrator):
        assert orchestrator.wait_for_tasks([]) is True

    def test_stopped_orchestrator_raises_instead_of_hanging(self, orchestrator):
        task = Task(name="t", module="test", action="echo", dependencies=["missing"])
        orchestrator.submit_task(task)
        orchestrator.stop_execution()
        with pytest.raises(TaskExecutionError, match="was stopped"):
            orchestrator.wait_for_tasks([task.id])


class TestResources:
    def test_resources_held_during_execution_and_released(self, resources):
        observed: list[float] = []
        orch = TaskOrchestrator(max_workers=1, resource_manager=resources)
        orch.register_action(
            "test",
            "observe",
            lambda: observed.append(resources.get_resource("sys-memory").allocated),
        )
        try:
            task = Task(
                name="t",
                module="test",
                action="observe",
                resources=[TaskResource(resource_type="memory", amount=256)],
            )
            result = orch.execute_task(task)
            assert result.status is TaskStatus.COMPLETED
            assert observed == [256]
            assert resources.get_resource("sys-memory").allocated == 0
            assert len(result.metadata["allocations"]) == 1
            assert task.allocations == []
        finally:
            orch.stop_execution()

    def test_resources_released_when_action_fails(self, resources):
        orch = TaskOrchestrator(max_workers=1, resource_manager=resources)
        orch.register_action("test", "fail", lambda: 1 / 0)
        try:
            result = orch.execute_task(
                Task(
                    name="t",
                    module="test",
                    action="fail",
                    resources=[TaskResource(resource_type="compute", amount=10)],
                )
            )
            assert result.status is TaskStatus.FAILED
            assert resources.get_resource("sys-compute").allocated == 0
        finally:
            orch.stop_execution()

    def test_contended_resource_serialises_tasks(self, resources):
        resources.add_resource(
            Resource(id="gpu-0", name="GPU", type=ResourceType.CUSTOM, capacity=1)
        )
        active = 0
        peak = 0
        lock = threading.Lock()

        def use_gpu():
            nonlocal active, peak
            with lock:
                active += 1
                peak = max(peak, active)
            time.sleep(0.15)
            with lock:
                active -= 1

        orch = TaskOrchestrator(max_workers=3, resource_manager=resources)
        orch.register_action("test", "use_gpu", use_gpu)
        try:
            tasks = [
                Task(
                    name=f"t{i}",
                    module="test",
                    action="use_gpu",
                    resources=[
                        TaskResource(resource_type="custom", resource_id="gpu-0")
                    ],
                )
                for i in range(3)
            ]
            for task in tasks:
                orch.submit_task(task)
            assert orch.wait_for_tasks([t.id for t in tasks], timeout=10)
            assert all(t.status is TaskStatus.COMPLETED for t in tasks)
            assert peak == 1
            assert resources.get_resource("gpu-0").allocated == 0
        finally:
            orch.stop_execution()

    @pytest.mark.parametrize(
        ("requirement", "message"),
        [
            (TaskResource(resource_type="memory", amount=10**9), "cannot be satisfied"),
            (TaskResource(resource_type="quantum"), "Unknown resource type"),
            (TaskResource(resource_type="lock"), "No resource of type 'lock'"),
            (
                TaskResource(resource_type="memory", resource_id="nope"),
                "Unknown resource id",
            ),
            (
                TaskResource(resource_type="compute", resource_id="sys-memory"),
                "has type 'memory'",
            ),
            (TaskResource(resource_type="memory", amount=0), "must be positive"),
        ],
    )
    def test_unsatisfiable_requirement_fails_explicitly(
        self, orchestrator, log, requirement, message
    ):
        result = orchestrator.execute_task(
            Task(name="t", module="test", action="echo", resources=[requirement])
        )
        assert result.status is TaskStatus.FAILED
        assert message in result.error
        assert log.calls == []

    def test_offline_resource_fails_explicitly(self, orchestrator, resources, log):
        resources.get_resource("sys-memory").status = ResourceStatus.OFFLINE
        result = orchestrator.execute_task(
            Task(
                name="t",
                module="test",
                action="echo",
                resources=[TaskResource(resource_type="memory")],
            )
        )
        assert result.status is TaskStatus.FAILED
        assert "offline" in result.error
        assert log.calls == []
