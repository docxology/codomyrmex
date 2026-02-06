
import asyncio

import pytest

from codomyrmex.orchestrator.workflow import (
    CycleError,
    TaskStatus,
    Workflow,
    WorkflowError,
)


@pytest.mark.asyncio
async def test_workflow_linear_execution():
    """Test simple linear dependency A -> B -> C."""
    execution_order = []

    async def task_a(_task_results=None):
        execution_order.append("A")
        return "result_a"

    async def task_b(_task_results=None):
        execution_order.append("B")
        return "result_b"

    async def task_c(_task_results=None):
        execution_order.append("C")
        return "result_c"

    wf = Workflow("test_linear")
    wf.add_task("A", task_a)
    wf.add_task("B", task_b, dependencies=["A"])
    wf.add_task("C", task_c, dependencies=["B"])

    results = await wf.run()

    assert execution_order == ["A", "B", "C"]
    assert results == {"A": "result_a", "B": "result_b", "C": "result_c"}

@pytest.mark.asyncio
async def test_workflow_parallel_execution():
    """Test parallel execution: A -> (B, C) -> D."""
    results_list = []

    async def task_a(_task_results=None):
        results_list.append("A")
        return "A"

    async def task_b(_task_results=None):
        await asyncio.sleep(0.05)
        results_list.append("B")
        return "B"

    async def task_c(_task_results=None):
        results_list.append("C")
        return "C"

    async def task_d(_task_results=None):
        results_list.append("D")
        return "D"

    wf = Workflow("test_parallel")
    wf.add_task("A", task_a)
    wf.add_task("B", task_b, dependencies=["A"])  # Slower
    wf.add_task("C", task_c, dependencies=["A"])  # Faster
    wf.add_task("D", task_d, dependencies=["B", "C"])

    await wf.run()

    # Sort results by the order they were appended to check relative ordering where deterministic
    # A MUST come before B and C
    assert results_list.index("A") < results_list.index("B")
    assert results_list.index("A") < results_list.index("C")

    # B and C MUST come before D
    assert results_list.index("B") < results_list.index("D")
    assert results_list.index("C") < results_list.index("D")

    # We cannot guarantee B vs C order due to small sleep diffs and scheduler,
    # but we know they are in between A and D.

    assert len(results_list) == 4
    assert set(results_list) == {"A", "B", "C", "D"}

@pytest.mark.asyncio
async def test_cycle_detection():
    """Test detection of circular dependencies."""
    wf = Workflow("test_cycle")
    wf.add_task("A", lambda: None, dependencies=["B"])
    wf.add_task("B", lambda: None, dependencies=["A"])

    with pytest.raises(CycleError):
        await wf.run()

@pytest.mark.asyncio
async def test_missing_dependency():
    """Test missing dependency validation."""
    wf = Workflow("test_missing")
    wf.add_task("A", lambda: None, dependencies=["NON_EXISTENT"])

    with pytest.raises(WorkflowError):
        await wf.run()

@pytest.mark.asyncio
async def test_task_failure_handling():
    """Test that downstream tasks are skipped/marked failed if dependency fails."""

    async def failing_task(_task_results=None):
        raise ValueError("Boom")

    success_run = False
    async def downstream_task(_task_results=None):
        nonlocal success_run
        success_run = True

    wf = Workflow("test_failure", fail_fast=False)  # Disable fail-fast to see proper skip behavior
    wf.add_task("Fail", failing_task)
    wf.add_task("Downstream", downstream_task, dependencies=["Fail"])

    results = await wf.run()

    # Downstream should not have run or should be skipped/failed in a specific way.
    # Implementation treats raising Exception as FAILED status.
    # Current implementation does NOT execute tasks with pending/failed dependencies.

    task_fail = wf.tasks["Fail"]
    task_down = wf.tasks["Downstream"]

    assert task_fail.status == TaskStatus.FAILED
    assert success_run is False
    # Downstream should be skipped because its dependency failed
    # It could be SKIPPED or PENDING depending on implementation
    assert task_down.status in (TaskStatus.SKIPPED, TaskStatus.PENDING)


# Additional tests for new workflow features

class TestRetryPolicy:
    """Tests for RetryPolicy dataclass."""

    def test_retry_policy_defaults(self):
        """Test RetryPolicy default values."""
        from codomyrmex.orchestrator.workflow import RetryPolicy

        policy = RetryPolicy()

        assert policy.max_attempts == 3
        assert policy.initial_delay == 1.0
        assert policy.max_delay == 60.0
        assert policy.exponential_base == 2.0

    def test_retry_policy_custom_values(self):
        """Test RetryPolicy with custom values."""
        from codomyrmex.orchestrator.workflow import RetryPolicy

        policy = RetryPolicy(
            max_attempts=5,
            initial_delay=0.5,
            max_delay=30.0,
            exponential_base=3.0
        )

        assert policy.max_attempts == 5
        assert policy.initial_delay == 0.5

    def test_get_delay_exponential(self):
        """Test delay calculation with exponential backoff."""
        from codomyrmex.orchestrator.workflow import RetryPolicy

        policy = RetryPolicy(initial_delay=1.0, exponential_base=2.0)

        assert policy.get_delay(1) == 1.0
        assert policy.get_delay(2) == 2.0
        assert policy.get_delay(3) == 4.0

    def test_get_delay_max_cap(self):
        """Test delay is capped at max_delay."""
        from codomyrmex.orchestrator.workflow import RetryPolicy

        policy = RetryPolicy(initial_delay=10.0, max_delay=20.0, exponential_base=2.0)

        assert policy.get_delay(1) == 10.0
        assert policy.get_delay(2) == 20.0  # Capped at max


class TestTaskResult:
    """Tests for TaskResult dataclass."""

    def test_task_result_defaults(self):
        """Test TaskResult default values."""
        from codomyrmex.orchestrator.workflow import TaskResult

        result = TaskResult(success=True)

        assert result.success is True
        assert result.value is None
        assert result.error is None
        assert result.execution_time == 0.0
        assert result.attempts == 1

    def test_task_result_with_values(self):
        """Test TaskResult with all values."""
        from codomyrmex.orchestrator.workflow import TaskResult

        result = TaskResult(
            success=True,
            value={"data": "test"},
            error=None,
            execution_time=2.5,
            attempts=3
        )

        assert result.success is True
        assert result.value == {"data": "test"}
        assert result.attempts == 3


class TestWorkflowHelpers:
    """Tests for workflow helper functions."""

    def test_chain_helper(self):
        """Test chain helper function."""
        from codomyrmex.orchestrator.workflow import chain

        def action1(): return "1"
        def action2(): return "2"

        workflow = chain(action1, action2, names=["step1", "step2"])

        assert "step1" in workflow.tasks
        assert "step2" in workflow.tasks
        assert "step1" in workflow.tasks["step2"].dependencies

    def test_parallel_helper(self):
        """Test parallel helper function."""
        from codomyrmex.orchestrator.workflow import parallel

        def action1(): return "1"
        def action2(): return "2"

        workflow = parallel(action1, action2, names=["p1", "p2"])

        assert "p1" in workflow.tasks
        assert "p2" in workflow.tasks
        # Dependencies can be an empty set or list
        assert len(workflow.tasks["p1"].dependencies) == 0
        assert len(workflow.tasks["p2"].dependencies) == 0

    def test_fan_out_fan_in_helper(self):
        """Test fan_out_fan_in helper function."""
        from codomyrmex.orchestrator.workflow import fan_out_fan_in

        def initial(): return "start"
        def parallel1(): return "p1"
        def parallel2(): return "p2"
        def final(): return "end"

        workflow = fan_out_fan_in(
            initial=initial,
            parallel_tasks=[parallel1, parallel2],
            final=final
        )

        assert "initial" in workflow.tasks
        assert "final" in workflow.tasks


@pytest.mark.asyncio
async def test_workflow_with_timeout():
    """Test workflow task timeout."""
    from codomyrmex.orchestrator.workflow import Workflow

    async def slow_task():
        await asyncio.sleep(10)
        return "done"

    wf = Workflow("timeout_test")
    wf.add_task("slow", slow_task, timeout=0.1)

    await wf.run()

    # Task should be marked as failed due to timeout
    assert wf.tasks["slow"].status == TaskStatus.FAILED


@pytest.mark.asyncio
async def test_workflow_get_summary():
    """Test getting workflow summary."""
    async def success_task(_task_results=None):
        return "done"

    wf = Workflow("summary_test")
    wf.add_task("task1", success_task)
    wf.add_task("task2", success_task)

    await wf.run()
    summary = wf.get_summary()

    assert summary["success"] is True
    assert summary["total_tasks"] == 2
    assert summary["completed"] == 2
    assert summary["failed"] == 0


@pytest.mark.asyncio
async def test_workflow_progress_callback():
    """Test workflow progress callback."""
    progress_events = []

    def on_progress(task_name, status, details):
        progress_events.append((task_name, status))

    async def my_task(_task_results=None):
        return "result"

    wf = Workflow("callback_test", progress_callback=on_progress)
    wf.add_task("task1", my_task)

    await wf.run()

    # Should have received progress events
    assert len(progress_events) > 0
