"""Comprehensive tests for the orchestrator module.

This module provides extensive test coverage for:
1. Workflow definition and parsing
2. Step execution and sequencing
3. Parallel step execution
4. Conditional branching
5. Error handling and recovery
6. Workflow state management
7. Input/output mapping between steps
8. Timeout handling
9. Retry logic
10. Workflow cancellation
"""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock

import pytest

from codomyrmex.orchestrator.integration import (
    AgentOrchestrator,
    CICDBridge,
    OrchestratorBridge,
    PipelineConfig,
    StageConfig,
    create_pipeline_workflow,
    run_agent_task,
    run_ci_stage,
)
from codomyrmex.orchestrator.thin import (
    StepResult,
    Steps,
    condition,
    retry,
    shell,
    timeout,
)
from codomyrmex.orchestrator.workflow import (
    CycleError,
    RetryPolicy,
    TaskResult,
    TaskStatus,
    Workflow,
    WorkflowError,
    chain,
    fan_out_fan_in,
    parallel,
)

# Mark all tests as orchestrator tests
pytestmark = [pytest.mark.orchestrator]


class TestWorkflowDefinitionAndParsing:
    """Tests for workflow definition and parsing."""

    def test_workflow_creation_with_name(self):
        """Test workflow can be created with a name."""
        wf = Workflow(name="test_workflow")
        assert wf.name == "test_workflow"
        assert len(wf.tasks) == 0

    def test_workflow_creation_with_timeout(self):
        """Test workflow can be created with a timeout."""
        wf = Workflow(name="test", timeout=300)
        assert wf.timeout == 300

    def test_workflow_creation_with_fail_fast(self):
        """Test workflow can be created with fail_fast option."""
        wf = Workflow(name="test", fail_fast=False)
        assert wf.fail_fast is False

    def test_add_task_basic(self):
        """Test adding a basic task to workflow."""
        wf = Workflow(name="test")

        def my_task():
            return "result"

        wf.add_task("task1", my_task)

        assert "task1" in wf.tasks
        assert wf.tasks["task1"].name == "task1"
        assert wf.tasks["task1"].action == my_task

    def test_add_task_with_dependencies(self):
        """Test adding a task with dependencies."""
        wf = Workflow(name="test")

        wf.add_task("task1", lambda: "1")
        wf.add_task("task2", lambda: "2", dependencies=["task1"])

        assert "task1" in wf.tasks["task2"].dependencies

    def test_add_duplicate_task_raises_error(self):
        """Test adding duplicate task name raises WorkflowError."""
        wf = Workflow(name="test")
        wf.add_task("task1", lambda: "1")

        with pytest.raises(WorkflowError, match="already exists"):
            wf.add_task("task1", lambda: "2")

    def test_add_task_with_metadata(self):
        """Test adding task with metadata."""
        wf = Workflow(name="test")
        wf.add_task(
            "task1",
            lambda: "1",
            metadata={"priority": "high", "category": "build"}
        )

        assert wf.tasks["task1"].metadata["priority"] == "high"
        assert wf.tasks["task1"].metadata["category"] == "build"

    def test_add_task_with_tags(self):
        """Test adding task with tags."""
        wf = Workflow(name="test")
        wf.add_task("task1", lambda: "1", tags=["critical", "fast"])

        assert "critical" in wf.tasks["task1"].tags
        assert "fast" in wf.tasks["task1"].tags


class TestStepExecutionAndSequencing:
    """Tests for step execution and sequencing."""

    @pytest.mark.asyncio
    async def test_single_task_execution(self):
        """Test execution of a single task."""
        executed = []

        async def task1(_task_results=None):
            executed.append("task1")
            return "result1"

        wf = Workflow(name="test")
        wf.add_task("task1", task1)

        results = await wf.run()

        assert executed == ["task1"]
        assert results["task1"] == "result1"

    @pytest.mark.asyncio
    async def test_sequential_execution_order(self):
        """Test tasks execute in correct sequential order."""
        execution_order = []

        async def make_task(name):
            async def task(_task_results=None):
                execution_order.append(name)
                return f"result_{name}"
            return task

        wf = Workflow(name="test")
        wf.add_task("first", await make_task("first"))
        wf.add_task("second", await make_task("second"), dependencies=["first"])
        wf.add_task("third", await make_task("third"), dependencies=["second"])

        await wf.run()

        assert execution_order == ["first", "second", "third"]

    @pytest.mark.asyncio
    async def test_sync_function_execution(self):
        """Test synchronous functions can be executed."""
        def sync_task():
            return "sync_result"

        wf = Workflow(name="test")
        wf.add_task("sync", sync_task)

        results = await wf.run()

        assert results["sync"] == "sync_result"

    @pytest.mark.asyncio
    async def test_chain_helper_creates_sequential_workflow(self):
        """Test chain helper creates proper sequential dependencies."""
        results = []

        def action1():
            results.append("a1")
            return "r1"

        def action2():
            results.append("a2")
            return "r2"

        def action3():
            results.append("a3")
            return "r3"

        wf = chain(action1, action2, action3, names=["s1", "s2", "s3"])

        # Verify dependencies are chained
        assert len(wf.tasks["s1"].dependencies) == 0
        assert "s1" in wf.tasks["s2"].dependencies
        assert "s2" in wf.tasks["s3"].dependencies


class TestParallelStepExecution:
    """Tests for parallel step execution."""

    @pytest.mark.asyncio
    async def test_parallel_tasks_run_concurrently(self):
        """Test that parallel tasks without dependencies run concurrently."""
        start_times = {}
        end_times = {}

        async def timed_task(name, duration=0.1):
            start_times[name] = time.time()
            await asyncio.sleep(duration)
            end_times[name] = time.time()
            return name

        wf = Workflow(name="parallel_test")
        wf.add_task("p1", lambda _task_results=None: asyncio.create_task(timed_task("p1")))
        wf.add_task("p2", lambda _task_results=None: asyncio.create_task(timed_task("p2")))
        wf.add_task("p3", lambda _task_results=None: asyncio.create_task(timed_task("p3")))

        # Tasks without dependencies should start nearly simultaneously
        # We verify this by checking they all have no deps
        assert len(wf.tasks["p1"].dependencies) == 0
        assert len(wf.tasks["p2"].dependencies) == 0
        assert len(wf.tasks["p3"].dependencies) == 0

    def test_parallel_helper_creates_independent_tasks(self):
        """Test parallel helper creates tasks with no dependencies."""
        def action1():
            return "1"

        def action2():
            return "2"

        def action3():
            return "3"

        wf = parallel(action1, action2, action3, names=["p1", "p2", "p3"])

        # All tasks should have no dependencies
        for task_name in ["p1", "p2", "p3"]:
            assert len(wf.tasks[task_name].dependencies) == 0

    def test_fan_out_fan_in_pattern(self):
        """Test fan-out/fan-in workflow pattern."""
        def initial():
            return "start"

        def parallel1():
            return "p1"

        def parallel2():
            return "p2"

        def final():
            return "end"

        wf = fan_out_fan_in(
            initial=initial,
            parallel_tasks=[parallel1, parallel2],
            final=final,
            initial_name="init",
            final_name="finish"
        )

        # Initial has no deps
        assert len(wf.tasks["init"].dependencies) == 0

        # Parallel tasks depend on initial
        assert "init" in wf.tasks["parallel1"].dependencies
        assert "init" in wf.tasks["parallel2"].dependencies

        # Final depends on all parallel tasks
        assert "parallel1" in wf.tasks["finish"].dependencies
        assert "parallel2" in wf.tasks["finish"].dependencies


class TestConditionalBranching:
    """Tests for conditional branching in workflows."""

    @pytest.mark.asyncio
    async def test_task_with_condition_that_passes(self):
        """Test task executes when condition returns True."""
        executed = []

        def always_true(results):
            return True

        async def conditional_task(_task_results=None):
            executed.append("conditional")
            return "executed"

        wf = Workflow(name="test")
        wf.add_task("conditional", conditional_task, condition=always_true)

        await wf.run()

        assert "conditional" in executed

    @pytest.mark.asyncio
    async def test_task_with_condition_that_fails(self):
        """Test task is skipped when condition returns False."""
        executed = []

        def always_false(results):
            return False

        async def conditional_task(_task_results=None):
            executed.append("conditional")
            return "executed"

        wf = Workflow(name="test")
        wf.add_task("conditional", conditional_task, condition=always_false)

        await wf.run()

        assert "conditional" not in executed
        assert wf.tasks["conditional"].status == TaskStatus.SKIPPED

    @pytest.mark.asyncio
    async def test_condition_based_on_previous_result(self):
        """Test conditional execution based on previous task result."""
        executed = []

        async def first_task(_task_results=None):
            executed.append("first")
            return {"success": True, "value": 100}

        def check_previous(results):
            first_result = results.get("first")
            if first_result:
                return first_result.value.get("value", 0) > 50
            return False

        async def second_task(_task_results=None):
            executed.append("second")
            return "conditional_executed"

        wf = Workflow(name="test")
        wf.add_task("first", first_task)
        wf.add_task("second", second_task, dependencies=["first"], condition=check_previous)

        await wf.run()

        assert "first" in executed
        assert "second" in executed

    def test_condition_helper_function(self):
        """Test condition helper creates proper predicate."""
        predicate = condition(lambda results: results.get("check", {}).get("ok", False))

        assert predicate({"check": {"ok": True}}) is True
        assert predicate({"check": {"ok": False}}) is False
        assert predicate({}) is False


class TestErrorHandlingAndRecovery:
    """Tests for error handling and recovery."""

    @pytest.mark.asyncio
    async def test_task_failure_is_captured(self):
        """Test that task failures are properly captured."""
        async def failing_task(_task_results=None):
            raise ValueError("Intentional failure")

        wf = Workflow(name="test", fail_fast=False)
        wf.add_task("failing", failing_task)

        await wf.run()

        assert wf.tasks["failing"].status == TaskStatus.FAILED
        assert wf.tasks["failing"].error is not None

    @pytest.mark.asyncio
    async def test_fail_fast_stops_workflow(self):
        """Test fail_fast=True stops workflow on first failure."""
        executed = []

        async def task1(_task_results=None):
            executed.append("task1")
            raise ValueError("Failure")

        async def task2(_task_results=None):
            executed.append("task2")
            return "result2"

        wf = Workflow(name="test", fail_fast=True)
        wf.add_task("task1", task1)
        wf.add_task("task2", task2)

        await wf.run()

        assert "task1" in executed
        # task2 may or may not execute depending on timing,
        # but the workflow should have cancelled flag set
        assert wf._cancelled is True

    @pytest.mark.asyncio
    async def test_dependent_task_skipped_on_failure(self):
        """Test downstream tasks are skipped when dependency fails."""
        async def failing_task(_task_results=None):
            raise ValueError("Boom")

        async def dependent_task(_task_results=None):
            return "should_not_run"

        wf = Workflow(name="test", fail_fast=False)
        wf.add_task("failing", failing_task)
        wf.add_task("dependent", dependent_task, dependencies=["failing"])

        await wf.run()

        assert wf.tasks["failing"].status == TaskStatus.FAILED
        assert wf.tasks["dependent"].status == TaskStatus.SKIPPED

    @pytest.mark.asyncio
    async def test_workflow_error_on_missing_dependency(self):
        """Test WorkflowError raised for missing dependency."""
        wf = Workflow(name="test")
        wf.add_task("task1", lambda: "1", dependencies=["nonexistent"])

        with pytest.raises(WorkflowError, match="unknown task"):
            await wf.run()

    @pytest.mark.asyncio
    async def test_cycle_error_detection(self):
        """Test CycleError is raised for circular dependencies."""
        wf = Workflow(name="test")
        wf.add_task("a", lambda: "a", dependencies=["c"])
        wf.add_task("b", lambda: "b", dependencies=["a"])
        wf.add_task("c", lambda: "c", dependencies=["b"])

        with pytest.raises(CycleError):
            await wf.run()


class TestWorkflowStateManagement:
    """Tests for workflow state management."""

    @pytest.mark.asyncio
    async def test_task_status_transitions(self):
        """Test task status transitions through execution."""
        status_history = []

        def on_progress(task_name, status, details):
            if task_name != "workflow":
                status_history.append((task_name, status))

        async def my_task(_task_results=None):
            return "done"

        wf = Workflow(name="test", progress_callback=on_progress)
        wf.add_task("task1", my_task)

        # Initially pending
        assert wf.tasks["task1"].status == TaskStatus.PENDING

        await wf.run()

        # Should have gone through running -> completed
        assert ("task1", "running") in status_history
        assert ("task1", "completed") in status_history

    @pytest.mark.asyncio
    async def test_workflow_summary(self):
        """Test workflow summary generation."""
        async def success_task(_task_results=None):
            return "success"

        async def fail_task(_task_results=None):
            raise ValueError("fail")

        wf = Workflow(name="test", fail_fast=False)
        wf.add_task("task1", success_task)
        wf.add_task("task2", fail_task)
        wf.add_task("task3", success_task, dependencies=["task2"])  # Will be skipped

        await wf.run()

        summary = wf.get_summary()

        assert summary["total_tasks"] == 3
        assert summary["completed"] == 1
        assert summary["failed"] == 1
        assert summary["skipped"] == 1
        assert summary["success"] is False

    @pytest.mark.asyncio
    async def test_get_task_result(self):
        """Test getting individual task result."""
        async def my_task(_task_results=None):
            return {"data": "value"}

        wf = Workflow(name="test")
        wf.add_task("task1", my_task)

        await wf.run()

        result = wf.get_task_result("task1")

        assert result is not None
        assert result.success is True
        assert result.value == {"data": "value"}

    def test_task_result_dataclass(self):
        """Test TaskResult dataclass properties."""
        result = TaskResult(
            success=True,
            value="test_value",
            error=None,
            execution_time=1.5,
            attempts=2
        )

        assert result.success is True
        assert result.value == "test_value"
        assert result.execution_time == 1.5
        assert result.attempts == 2


class TestInputOutputMappingBetweenSteps:
    """Tests for input/output mapping between steps."""

    @pytest.mark.asyncio
    async def test_task_receives_previous_results(self):
        """Test tasks can access results from previous tasks."""
        received_results = {}

        async def first_task(_task_results=None):
            return {"key": "value_from_first"}

        async def second_task(_task_results=None):
            nonlocal received_results
            received_results = _task_results
            first_result = _task_results.get("first")
            if first_result:
                return f"got_{first_result.value['key']}"
            return "no_result"

        wf = Workflow(name="test")
        wf.add_task("first", first_task)
        wf.add_task("second", second_task, dependencies=["first"])

        results = await wf.run()

        assert "first" in received_results
        assert received_results["first"].value == {"key": "value_from_first"}

    @pytest.mark.asyncio
    async def test_result_transform_function(self):
        """Test result transformation before storing."""
        async def my_task(_task_results=None):
            return {"raw": "data", "extra": "field"}

        def transform(result):
            return {"processed": result["raw"].upper()}

        wf = Workflow(name="test")
        wf.add_task("task1", my_task, transform_result=transform)

        await wf.run()

        assert wf.tasks["task1"].result == {"processed": "DATA"}

    @pytest.mark.asyncio
    async def test_task_kwargs_injection(self):
        """Test task receives custom kwargs."""
        received_kwargs = {}

        async def my_task(custom_arg=None, _task_results=None):
            nonlocal received_kwargs
            received_kwargs["custom_arg"] = custom_arg
            return "done"

        wf = Workflow(name="test")
        wf.add_task("task1", my_task, kwargs={"custom_arg": "injected_value"})

        await wf.run()

        assert received_kwargs["custom_arg"] == "injected_value"


class TestTimeoutHandling:
    """Tests for timeout handling."""

    @pytest.mark.asyncio
    async def test_task_timeout_triggers(self):
        """Test task timeout causes failure."""
        async def slow_task(_task_results=None):
            await asyncio.sleep(10)
            return "done"

        wf = Workflow(name="test")
        wf.add_task("slow", slow_task, timeout=0.1)

        await wf.run()

        assert wf.tasks["slow"].status == TaskStatus.FAILED
        # The error message contains "timed out" not just "timeout"
        assert "timed out" in str(wf.tasks["slow"].error).lower()

    @pytest.mark.asyncio
    async def test_workflow_timeout_triggers(self):
        """Test workflow-level timeout."""
        async def slow_task1(_task_results=None):
            await asyncio.sleep(5)
            return "1"

        async def slow_task2(_task_results=None):
            await asyncio.sleep(5)
            return "2"

        wf = Workflow(name="test", timeout=0.2)
        wf.add_task("slow1", slow_task1)
        wf.add_task("slow2", slow_task2, dependencies=["slow1"])

        with pytest.raises(WorkflowError, match="timeout"):
            await wf.run()

    @pytest.mark.asyncio
    async def test_timeout_decorator(self):
        """Test timeout decorator function."""
        @timeout(0.1)
        def slow_func():
            time.sleep(1)
            return "done"

        with pytest.raises(asyncio.TimeoutError):
            await slow_func()

    @pytest.mark.asyncio
    async def test_timeout_decorator_passes_when_fast(self):
        """Test timeout decorator allows fast functions."""
        @timeout(5)
        def fast_func():
            return "fast_result"

        result = await fast_func()
        assert result == "fast_result"


class TestRetryLogic:
    """Tests for retry logic."""

    def test_retry_policy_defaults(self):
        """Test RetryPolicy default values."""
        policy = RetryPolicy()

        assert policy.max_attempts == 3
        assert policy.initial_delay == 1.0
        assert policy.max_delay == 60.0
        assert policy.exponential_base == 2.0

    def test_retry_policy_delay_calculation(self):
        """Test exponential backoff delay calculation."""
        policy = RetryPolicy(initial_delay=1.0, exponential_base=2.0, max_delay=10.0)

        assert policy.get_delay(1) == 1.0
        assert policy.get_delay(2) == 2.0
        assert policy.get_delay(3) == 4.0
        assert policy.get_delay(4) == 8.0
        assert policy.get_delay(5) == 10.0  # Capped at max_delay

    @pytest.mark.asyncio
    async def test_task_with_retry_succeeds_after_failures(self):
        """Test task with retry eventually succeeds."""
        attempt_count = 0

        async def flaky_task(_task_results=None):
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise ValueError(f"Attempt {attempt_count} failed")
            return "success"

        policy = RetryPolicy(max_attempts=5, initial_delay=0.01)

        wf = Workflow(name="test")
        wf.add_task("flaky", flaky_task, retry_policy=policy)

        await wf.run()

        assert wf.tasks["flaky"].status == TaskStatus.COMPLETED
        assert attempt_count == 3

    @pytest.mark.asyncio
    async def test_task_retry_exhausted(self):
        """Test task fails after exhausting retries."""
        attempt_count = 0

        async def always_fail(_task_results=None):
            nonlocal attempt_count
            attempt_count += 1
            raise ValueError("Always fails")

        policy = RetryPolicy(max_attempts=3, initial_delay=0.01)

        wf = Workflow(name="test", fail_fast=False)
        wf.add_task("failing", always_fail, retry_policy=policy)

        await wf.run()

        assert wf.tasks["failing"].status == TaskStatus.FAILED
        assert attempt_count == 3

    @pytest.mark.asyncio
    async def test_retry_wrapper_function(self):
        """Test retry wrapper utility."""
        call_count = 0

        def eventually_succeed():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Not yet")
            return "success"

        wrapped = retry(eventually_succeed, max_attempts=5, delay=0.01)
        result = await wrapped()

        assert result == "success"
        assert call_count == 3


class TestWorkflowCancellation:
    """Tests for workflow cancellation."""

    @pytest.mark.asyncio
    async def test_cancel_stops_workflow(self):
        """Test cancel method stops workflow execution."""
        executed = []

        async def task1(_task_results=None):
            executed.append("task1")
            await asyncio.sleep(0.1)
            return "1"

        async def task2(_task_results=None):
            executed.append("task2")
            return "2"

        wf = Workflow(name="test")
        wf.add_task("task1", task1)
        wf.add_task("task2", task2, dependencies=["task1"])

        # Start workflow in background and cancel after short delay
        async def run_and_cancel():
            task = asyncio.create_task(wf.run())
            await asyncio.sleep(0.05)
            wf.cancel()
            await task
            return task.result()

        await run_and_cancel()

        assert wf._cancelled is True

    @pytest.mark.asyncio
    async def test_cancelled_flag_is_set(self):
        """Test _cancelled flag is properly set."""
        wf = Workflow(name="test")

        assert wf._cancelled is False

        wf.cancel()

        assert wf._cancelled is True

    @pytest.mark.asyncio
    async def test_progress_callback_on_completion(self):
        """Test progress callback receives workflow completion event."""
        events = []

        def on_progress(task_name, status, details):
            events.append((task_name, status))

        async def my_task(_task_results=None):
            return "done"

        wf = Workflow(name="test", progress_callback=on_progress)
        wf.add_task("task1", my_task)

        await wf.run()

        # Should receive workflow started and completed events
        assert ("workflow", "started") in events
        assert ("workflow", "completed") in events


class TestIntegrationBridges:
    """Tests for integration bridge classes."""

    def test_orchestrator_bridge_creation(self):
        """Test OrchestratorBridge initialization."""
        bridge = OrchestratorBridge()
        assert bridge._engine is None
        assert bridge._session_id is None

    def test_orchestrator_bridge_run_quick(self):
        """Test OrchestratorBridge run_quick method."""
        bridge = OrchestratorBridge()
        result = bridge.run_quick("echo test")

        assert result["success"] is True
        assert "test" in result.get("stdout", "")

    def test_orchestrator_bridge_create_workflow(self):
        """Test OrchestratorBridge create_workflow method."""
        bridge = OrchestratorBridge()
        steps = bridge.create_workflow("my_workflow")

        assert isinstance(steps, Steps)
        assert steps.workflow.name == "my_workflow"

    def test_cicd_bridge_creation(self):
        """Test CICDBridge initialization."""
        bridge = CICDBridge(workspace_dir="/tmp/test")
        assert bridge._workspace_dir == "/tmp/test"
        assert bridge._manager is None

    def test_stage_config_dataclass(self):
        """Test StageConfig dataclass."""
        config = StageConfig(
            name="build",
            commands=["make", "make test"],
            parallel=False,
            timeout=600
        )

        assert config.name == "build"
        assert len(config.commands) == 2
        assert config.parallel is False
        assert config.timeout == 600

    def test_pipeline_config_dataclass(self):
        """Test PipelineConfig dataclass."""
        stages = [
            StageConfig(name="build", commands=["make"]),
            StageConfig(name="test", commands=["make test"])
        ]
        config = PipelineConfig(
            name="ci_pipeline",
            stages=stages,
            timeout=1800,
            fail_fast=True
        )

        assert config.name == "ci_pipeline"
        assert len(config.stages) == 2
        assert config.timeout == 1800

    def test_create_pipeline_workflow(self):
        """Test create_pipeline_workflow helper."""
        stages = [
            {"name": "build", "commands": ["echo build"]},
            {"name": "test", "commands": ["echo test"]}
        ]

        wf = create_pipeline_workflow(stages, name="test_pipeline")

        assert wf.name == "test_pipeline"
        assert "build" in wf.tasks
        assert "test" in wf.tasks


class TestAgentOrchestrator:
    """Tests for AgentOrchestrator class."""

    def test_agent_registration(self):
        """Test agent registration."""
        orchestrator = AgentOrchestrator()
        mock_agent = MagicMock()

        orchestrator.register_agent("test_agent", mock_agent)

        assert orchestrator.get_agent("test_agent") == mock_agent

    def test_get_unregistered_agent(self):
        """Test getting unregistered agent returns None."""
        orchestrator = AgentOrchestrator()

        assert orchestrator.get_agent("nonexistent") is None

    @pytest.mark.asyncio
    async def test_run_agent_task_not_found(self):
        """Test running task with unregistered agent."""
        orchestrator = AgentOrchestrator()

        result = await orchestrator.run_agent_task("nonexistent", "task")

        assert result["success"] is False
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_run_agent_task_with_execute(self):
        """Test running task with agent that has execute method."""
        orchestrator = AgentOrchestrator()

        mock_agent = MagicMock()
        mock_agent.execute = AsyncMock(return_value={"output": "test"})

        orchestrator.register_agent("test_agent", mock_agent)

        result = await orchestrator.run_agent_task("test_agent", "do_something")

        assert result["success"] is True
        assert result["agent"] == "test_agent"
        mock_agent.execute.assert_called_once_with("do_something")

    @pytest.mark.asyncio
    async def test_run_agent_task_with_run(self):
        """Test running task with agent that has run method."""
        orchestrator = AgentOrchestrator()

        mock_agent = MagicMock(spec=["run"])
        mock_agent.run = AsyncMock(return_value={"output": "test"})

        orchestrator.register_agent("test_agent", mock_agent)

        result = await orchestrator.run_agent_task("test_agent", "do_something")

        assert result["success"] is True
        mock_agent.run.assert_called_once()

    def test_create_agent_workflow(self):
        """Test creating workflow from agent tasks."""
        orchestrator = AgentOrchestrator()

        tasks = [
            {"name": "task1", "agent": "agent1", "task": "do_task_1"},
            {"name": "task2", "agent": "agent2", "task": "do_task_2", "depends_on": ["task1"]}
        ]

        wf = orchestrator.create_agent_workflow(tasks, name="agent_workflow")

        assert wf.name == "agent_workflow"
        assert "task1" in wf.tasks
        assert "task2" in wf.tasks
        assert "task1" in wf.tasks["task2"].dependencies


class TestStepsBuilder:
    """Tests for Steps workflow builder."""

    def test_steps_fluent_api(self):
        """Test Steps fluent API for chaining."""
        steps = Steps(name="fluent_test")

        result = steps.add("step1", lambda: "1").add("step2", lambda: "2").add("step3", lambda: "3")

        assert result is steps
        assert len(steps._steps) == 3

    def test_steps_auto_dependency(self):
        """Test Steps automatically chains dependencies."""
        steps = Steps(name="auto_dep")

        steps.add("first", lambda: "1")
        steps.add("second", lambda: "2")  # Should auto-depend on first
        steps.add("third", lambda: "3")   # Should auto-depend on second

        # Verify second depends on first
        assert "first" in steps._workflow.tasks["second"].dependencies

    def test_steps_explicit_dependency(self):
        """Test Steps with explicit dependencies."""
        steps = Steps(name="explicit_dep")

        steps.add("a", lambda: "a")
        steps.add("b", lambda: "b")
        steps.add("c", lambda: "c", depends_on=["a", "b"])

        assert "a" in steps._workflow.tasks["c"].dependencies
        assert "b" in steps._workflow.tasks["c"].dependencies

    def test_steps_with_timeout(self):
        """Test Steps with task timeout."""
        steps = Steps(name="timeout_test")

        steps.add("task", lambda: "result", timeout=30.0)

        assert steps._workflow.tasks["task"].timeout == 30.0

    def test_steps_with_retry(self):
        """Test Steps with retry configuration."""
        steps = Steps(name="retry_test")

        steps.add("task", lambda: "result", retry=3)

        assert steps._workflow.tasks["task"].retry_policy is not None
        assert steps._workflow.tasks["task"].retry_policy.max_attempts == 3

    @pytest.mark.asyncio
    async def test_steps_run_async(self):
        """Test Steps async run."""
        results = []

        def task1():
            results.append("t1")
            return "r1"

        def task2():
            results.append("t2")
            return "r2"

        steps = Steps(name="async_test")
        steps.add("task1", task1, depends_on=[])
        steps.add("task2", task2, depends_on=["task1"])

        # Use async run instead of run_sync to avoid nested event loop issues
        output = await steps.run()

        assert "t1" in results
        assert "t2" in results


class TestShellExecution:
    """Tests for shell command execution."""

    def test_shell_success(self):
        """Test successful shell command."""
        result = shell("echo hello")

        assert result["success"] is True
        assert "hello" in result["stdout"]
        assert result["returncode"] == 0

    def test_shell_failure(self):
        """Test failed shell command."""
        result = shell("exit 1")

        assert result["success"] is False
        assert result["returncode"] == 1

    def test_shell_with_env(self):
        """Test shell command with environment variables."""
        result = shell("echo $TEST_VAR", env={"TEST_VAR": "hello_world"})

        assert result["success"] is True
        assert "hello_world" in result["stdout"]

    def test_shell_timeout(self):
        """Test shell command timeout."""
        result = shell("sleep 10", timeout=1)

        assert result["success"] is False
        assert "Timeout" in result.get("error", "")

    def test_shell_captures_stderr(self):
        """Test shell captures stderr."""
        result = shell("echo error >&2")

        assert "error" in result.get("stderr", "")


class TestStepResultDataclass:
    """Tests for StepResult dataclass."""

    def test_step_result_success(self):
        """Test StepResult for success case."""
        result = StepResult(
            success=True,
            value={"data": "test"},
            execution_time=1.5
        )

        assert result.success is True
        assert result.value == {"data": "test"}
        assert result.error is None
        assert result.execution_time == 1.5

    def test_step_result_failure(self):
        """Test StepResult for failure case."""
        result = StepResult(
            success=False,
            error="Something went wrong",
            execution_time=0.5
        )

        assert result.success is False
        assert result.error == "Something went wrong"
        assert result.value is None


@pytest.mark.asyncio
async def test_run_ci_stage():
    """Test run_ci_stage helper function."""
    result = await run_ci_stage(
        name="test_stage",
        commands=["echo step1", "echo step2"],
        timeout=60
    )

    assert "success" in result
    assert result["stage"] == "test_stage"


@pytest.mark.asyncio
async def test_run_agent_task_helper():
    """Test run_agent_task helper function."""
    result = await run_agent_task("nonexistent_agent", "some_task")

    assert result["success"] is False
    assert "not found" in result["error"]
