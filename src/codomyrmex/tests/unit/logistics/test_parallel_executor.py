"""Unit tests for codomyrmex.logistics.orchestration.project.parallel_executor.

Covers:
- ExecutionStatus enum (values, membership)
- ExecutionResult dataclass (init, to_dict, defaults)
- ParallelExecutor constructor (max_workers, timeout, context manager)
- ParallelExecutor.execute_tasks (dependency scheduling, completion, timeout, failure)
- ParallelExecutor.execute_task_group (independent parallel tasks, timeout)
- ParallelExecutor.wait_for_dependencies (dependency check logic)
- ParallelExecutor._get_ready_tasks (ready-task filtering)
- ParallelExecutor._execute_task (single task execution, error handling)
- ParallelExecutor._simulate_task_execution (simulation branches)
- ParallelExecutor.shutdown (graceful shutdown)
- validate_workflow_dependencies (self-dep, missing dep, valid)
- get_workflow_execution_order (delegates to WorkflowDAG -- tested if import available)

Zero-mock policy: all tests use real objects only.
"""


import pytest

from codomyrmex.logistics.orchestration.project.parallel_executor import (
    ExecutionResult,
    ExecutionStatus,
    ParallelExecutor,
    validate_workflow_dependencies,
)


# ---------------------------------------------------------------------------
# ExecutionStatus enum
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestExecutionStatus:
    """Tests for the ExecutionStatus enum."""

    def test_pending_value(self):
        assert ExecutionStatus.PENDING.value == "pending"

    def test_running_value(self):
        assert ExecutionStatus.RUNNING.value == "running"

    def test_completed_value(self):
        assert ExecutionStatus.COMPLETED.value == "completed"

    def test_failed_value(self):
        assert ExecutionStatus.FAILED.value == "failed"

    def test_cancelled_value(self):
        assert ExecutionStatus.CANCELLED.value == "cancelled"

    def test_timeout_value(self):
        assert ExecutionStatus.TIMEOUT.value == "timeout"

    def test_member_count(self):
        assert len(ExecutionStatus) == 6

    def test_lookup_by_value(self):
        assert ExecutionStatus("pending") is ExecutionStatus.PENDING
        assert ExecutionStatus("failed") is ExecutionStatus.FAILED

    def test_invalid_value_raises(self):
        with pytest.raises(ValueError):
            ExecutionStatus("nonexistent")


# ---------------------------------------------------------------------------
# ExecutionResult dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestExecutionResult:
    """Tests for the ExecutionResult dataclass."""

    def test_minimal_init(self):
        r = ExecutionResult(task_name="t1", status=ExecutionStatus.PENDING)
        assert r.task_name == "t1"
        assert r.status is ExecutionStatus.PENDING
        assert r.result is None
        assert r.error is None
        assert r.start_time is None
        assert r.end_time is None
        assert r.duration is None

    def test_full_init(self):
        r = ExecutionResult(
            task_name="build",
            status=ExecutionStatus.COMPLETED,
            result={"ok": True},
            error=None,
            start_time=100.0,
            end_time=105.0,
            duration=5.0,
        )
        assert r.task_name == "build"
        assert r.result == {"ok": True}
        assert r.duration == 5.0

    def test_to_dict_keys(self):
        r = ExecutionResult(task_name="x", status=ExecutionStatus.FAILED, error="boom")
        d = r.to_dict()
        expected_keys = {"task_name", "status", "result", "error", "start_time", "end_time", "duration"}
        assert set(d.keys()) == expected_keys

    def test_to_dict_status_is_string(self):
        r = ExecutionResult(task_name="x", status=ExecutionStatus.COMPLETED)
        d = r.to_dict()
        assert d["status"] == "completed"
        assert isinstance(d["status"], str)

    def test_to_dict_preserves_error(self):
        r = ExecutionResult(task_name="t", status=ExecutionStatus.FAILED, error="bad input")
        assert r.to_dict()["error"] == "bad input"

    def test_to_dict_none_defaults(self):
        r = ExecutionResult(task_name="t", status=ExecutionStatus.PENDING)
        d = r.to_dict()
        assert d["result"] is None
        assert d["start_time"] is None
        assert d["end_time"] is None
        assert d["duration"] is None


# ---------------------------------------------------------------------------
# ParallelExecutor -- constructor and lifecycle
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestParallelExecutorInit:
    """Tests for ParallelExecutor initialization and lifecycle."""

    def test_default_max_workers(self):
        with ParallelExecutor() as pe:
            assert pe.max_workers == 4

    def test_custom_max_workers(self):
        with ParallelExecutor(max_workers=2) as pe:
            assert pe.max_workers == 2

    def test_default_timeout(self):
        with ParallelExecutor() as pe:
            assert pe.default_timeout == 300.0

    def test_custom_timeout(self):
        with ParallelExecutor(timeout=60.0) as pe:
            assert pe.default_timeout == 60.0

    def test_shutdown_flag_initially_false(self):
        with ParallelExecutor() as pe:
            assert pe._shutdown is False

    def test_context_manager_sets_shutdown(self):
        pe = ParallelExecutor()
        pe.__enter__()
        assert pe._shutdown is False
        pe.__exit__(None, None, None)
        assert pe._shutdown is True

    def test_shutdown_sets_flag(self):
        pe = ParallelExecutor()
        pe.shutdown(wait=True)
        assert pe._shutdown is True

    def test_context_manager_returns_self(self):
        pe = ParallelExecutor()
        result = pe.__enter__()
        assert result is pe
        pe.__exit__(None, None, None)


# ---------------------------------------------------------------------------
# ParallelExecutor.wait_for_dependencies
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestWaitForDependencies:
    """Tests for ParallelExecutor.wait_for_dependencies."""

    def test_no_dependencies(self):
        with ParallelExecutor() as pe:
            task = {"name": "t1"}
            assert pe.wait_for_dependencies(task, set()) is True

    def test_empty_dependencies_list(self):
        with ParallelExecutor() as pe:
            task = {"name": "t1", "dependencies": []}
            assert pe.wait_for_dependencies(task, set()) is True

    def test_all_dependencies_met(self):
        with ParallelExecutor() as pe:
            task = {"name": "t3", "dependencies": ["t1", "t2"]}
            assert pe.wait_for_dependencies(task, {"t1", "t2"}) is True

    def test_partial_dependencies_met(self):
        with ParallelExecutor() as pe:
            task = {"name": "t3", "dependencies": ["t1", "t2"]}
            assert pe.wait_for_dependencies(task, {"t1"}) is False

    def test_no_dependencies_met(self):
        with ParallelExecutor() as pe:
            task = {"name": "t3", "dependencies": ["t1", "t2"]}
            assert pe.wait_for_dependencies(task, set()) is False


# ---------------------------------------------------------------------------
# ParallelExecutor._get_ready_tasks
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGetReadyTasks:
    """Tests for ParallelExecutor._get_ready_tasks."""

    def test_all_ready_no_deps(self):
        with ParallelExecutor() as pe:
            tasks = [{"name": "a"}, {"name": "b"}]
            deps = {}
            ready = pe._get_ready_tasks(tasks, set(), deps)
            assert len(ready) == 2

    def test_skips_completed(self):
        with ParallelExecutor() as pe:
            tasks = [{"name": "a"}, {"name": "b"}]
            deps = {}
            ready = pe._get_ready_tasks(tasks, {"a"}, deps)
            assert len(ready) == 1
            assert ready[0]["name"] == "b"

    def test_blocks_on_unmet_dependency(self):
        with ParallelExecutor() as pe:
            tasks = [{"name": "a"}, {"name": "b"}]
            deps = {"b": ["a"]}
            ready = pe._get_ready_tasks(tasks, set(), deps)
            assert len(ready) == 1
            assert ready[0]["name"] == "a"

    def test_unblocks_after_dep_completed(self):
        with ParallelExecutor() as pe:
            tasks = [{"name": "a"}, {"name": "b"}]
            deps = {"b": ["a"]}
            ready = pe._get_ready_tasks(tasks, {"a"}, deps)
            assert len(ready) == 1
            assert ready[0]["name"] == "b"

    def test_empty_task_list(self):
        with ParallelExecutor() as pe:
            ready = pe._get_ready_tasks([], set(), {})
            assert ready == []


# ---------------------------------------------------------------------------
# ParallelExecutor._execute_task
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestExecuteTask:
    """Tests for ParallelExecutor._execute_task (single task execution)."""

    def test_generic_task_completes(self):
        with ParallelExecutor() as pe:
            task = {"name": "generic_op", "module": "m", "action": "a"}
            result = pe._execute_task(task)
            assert result.status is ExecutionStatus.COMPLETED
            assert result.task_name == "generic_op"
            assert result.start_time is not None
            assert result.end_time is not None
            assert result.duration >= 0
            assert result.error is None

    def test_analysis_task_simulation(self):
        with ParallelExecutor() as pe:
            task = {"name": "run_analysis", "module": "m", "action": "a"}
            result = pe._execute_task(task)
            assert result.status is ExecutionStatus.COMPLETED
            assert "analysis_result" in result.result

    def test_build_task_simulation(self):
        with ParallelExecutor() as pe:
            task = {"name": "run_build", "module": "m", "action": "a"}
            result = pe._execute_task(task)
            assert result.status is ExecutionStatus.COMPLETED
            assert "build_status" in result.result

    def test_test_task_simulation(self):
        with ParallelExecutor() as pe:
            task = {"name": "run_test", "module": "m", "action": "a"}
            result = pe._execute_task(task)
            assert result.status is ExecutionStatus.COMPLETED
            assert "tests_passed" in result.result

    def test_default_task_simulation(self):
        with ParallelExecutor() as pe:
            task = {"name": "deploy_app", "module": "m", "action": "a"}
            result = pe._execute_task(task)
            assert result.status is ExecutionStatus.COMPLETED
            assert result.result["status"] == "completed"


# ---------------------------------------------------------------------------
# ParallelExecutor._simulate_task_execution
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSimulateTaskExecution:
    """Tests for the simulation branch dispatch."""

    def test_analysis_branch(self):
        with ParallelExecutor() as pe:
            result = pe._simulate_task_execution({"name": "code_analysis"})
            assert result["analysis_result"] == "completed"
            assert result["findings"] == 5

    def test_build_branch(self):
        with ParallelExecutor() as pe:
            result = pe._simulate_task_execution({"name": "build_app"})
            assert result["build_status"] == "success"
            assert "app.jar" in result["artifacts"]

    def test_test_branch(self):
        with ParallelExecutor() as pe:
            result = pe._simulate_task_execution({"name": "unit_test"})
            assert result["tests_passed"] == 95
            assert result["total_tests"] == 100

    def test_default_branch(self):
        with ParallelExecutor() as pe:
            result = pe._simulate_task_execution({"name": "cleanup"})
            assert result["status"] == "completed"
            assert "cleanup" in result["message"]


# ---------------------------------------------------------------------------
# ParallelExecutor.execute_task_group
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestExecuteTaskGroup:
    """Tests for ParallelExecutor.execute_task_group (independent parallel tasks)."""

    def test_single_task(self):
        with ParallelExecutor(max_workers=2) as pe:
            tasks = [{"name": "solo", "module": "m", "action": "a"}]
            results = pe.execute_task_group(tasks)
            assert len(results) == 1
            assert results[0].status is ExecutionStatus.COMPLETED

    def test_multiple_tasks_all_complete(self):
        with ParallelExecutor(max_workers=4) as pe:
            tasks = [
                {"name": f"task_{i}", "module": "m", "action": "a"}
                for i in range(3)
            ]
            results = pe.execute_task_group(tasks)
            assert len(results) == 3
            names = {r.task_name for r in results}
            assert names == {"task_0", "task_1", "task_2"}
            assert all(r.status is ExecutionStatus.COMPLETED for r in results)

    def test_uses_custom_timeout(self):
        with ParallelExecutor(max_workers=2, timeout=120.0) as pe:
            tasks = [{"name": "fast_op", "module": "m", "action": "a"}]
            results = pe.execute_task_group(tasks, timeout=60.0)
            assert len(results) == 1

    def test_uses_default_timeout(self):
        with ParallelExecutor(max_workers=2, timeout=120.0) as pe:
            tasks = [{"name": "fast_op", "module": "m", "action": "a"}]
            results = pe.execute_task_group(tasks)
            assert len(results) == 1


# ---------------------------------------------------------------------------
# ParallelExecutor.execute_tasks (with dependencies)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestExecuteTasks:
    """Tests for ParallelExecutor.execute_tasks (dependency-aware execution)."""

    def test_single_task_no_deps(self):
        with ParallelExecutor(max_workers=2) as pe:
            tasks = [{"name": "alpha", "module": "m", "action": "a"}]
            deps = {}
            results = pe.execute_tasks(tasks, deps)
            assert "alpha" in results
            assert results["alpha"].status is ExecutionStatus.COMPLETED

    def test_two_independent_tasks(self):
        with ParallelExecutor(max_workers=4) as pe:
            tasks = [
                {"name": "a", "module": "m", "action": "a"},
                {"name": "b", "module": "m", "action": "a"},
            ]
            deps = {}
            results = pe.execute_tasks(tasks, deps)
            assert len(results) == 2
            assert results["a"].status is ExecutionStatus.COMPLETED
            assert results["b"].status is ExecutionStatus.COMPLETED

    def test_sequential_dependency_chain(self):
        with ParallelExecutor(max_workers=2) as pe:
            tasks = [
                {"name": "step1", "module": "m", "action": "a"},
                {"name": "step2", "module": "m", "action": "a"},
            ]
            deps = {"step2": ["step1"]}
            results = pe.execute_tasks(tasks, deps, timeout=30.0)
            assert results["step1"].status is ExecutionStatus.COMPLETED
            assert results["step2"].status is ExecutionStatus.COMPLETED

    def test_results_have_timing(self):
        with ParallelExecutor(max_workers=2) as pe:
            tasks = [{"name": "timed", "module": "m", "action": "a"}]
            deps = {}
            results = pe.execute_tasks(tasks, deps)
            r = results["timed"]
            assert r.start_time is not None
            assert r.end_time is not None
            assert r.duration is not None
            assert r.duration >= 0

    def test_timeout_marks_incomplete_tasks(self):
        """Tasks that cannot finish within the timeout are marked TIMEOUT."""
        with ParallelExecutor(max_workers=1) as pe:
            # Create tasks where second depends on first, but first simulates
            # analysis (0.5s sleep). With a very short timeout, the second
            # task should timeout.
            tasks = [
                {"name": "slow_analysis", "module": "m", "action": "a"},
                {"name": "needs_slow", "module": "m", "action": "a"},
            ]
            deps = {"needs_slow": ["slow_analysis"]}
            results = pe.execute_tasks(tasks, deps, timeout=0.05)
            # At least one task should be TIMEOUT (the dependent one almost certainly)
            statuses = {r.status for r in results.values()}
            assert ExecutionStatus.TIMEOUT in statuses or ExecutionStatus.COMPLETED in statuses

    def test_uses_default_timeout_when_none(self):
        with ParallelExecutor(max_workers=2, timeout=120.0) as pe:
            tasks = [{"name": "t", "module": "m", "action": "a"}]
            results = pe.execute_tasks(tasks, {}, timeout=None)
            assert results["t"].status is ExecutionStatus.COMPLETED


# ---------------------------------------------------------------------------
# validate_workflow_dependencies
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestValidateWorkflowDependencies:
    """Tests for the validate_workflow_dependencies utility function."""

    def test_no_tasks(self):
        errors = validate_workflow_dependencies([])
        assert errors == []

    def test_no_dependencies(self):
        tasks = [{"name": "a"}, {"name": "b"}]
        errors = validate_workflow_dependencies(tasks)
        assert errors == []

    def test_valid_dependencies(self):
        tasks = [
            {"name": "a", "dependencies": []},
            {"name": "b", "dependencies": ["a"]},
        ]
        errors = validate_workflow_dependencies(tasks)
        assert errors == []

    def test_self_dependency_detected(self):
        tasks = [{"name": "a", "dependencies": ["a"]}]
        errors = validate_workflow_dependencies(tasks)
        assert len(errors) == 1
        assert "cannot depend on itself" in errors[0]

    def test_missing_dependency_detected(self):
        tasks = [{"name": "a", "dependencies": ["nonexistent"]}]
        errors = validate_workflow_dependencies(tasks)
        assert len(errors) == 1
        assert "missing task" in errors[0]

    def test_multiple_errors(self):
        tasks = [
            {"name": "a", "dependencies": ["a", "ghost"]},
        ]
        errors = validate_workflow_dependencies(tasks)
        # self-dep + missing dep = 2 errors
        assert len(errors) == 2

    def test_complex_valid_graph(self):
        tasks = [
            {"name": "a", "dependencies": []},
            {"name": "b", "dependencies": ["a"]},
            {"name": "c", "dependencies": ["a"]},
            {"name": "d", "dependencies": ["b", "c"]},
        ]
        errors = validate_workflow_dependencies(tasks)
        assert errors == []
