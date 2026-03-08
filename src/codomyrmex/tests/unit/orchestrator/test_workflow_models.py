"""Tests for orchestrator.workflows._models."""

from codomyrmex.orchestrator.workflows._models import (
    CycleError,
    RetryPolicy,
    Task,
    TaskFailedError,
    TaskResult,
    TaskStatus,
    WorkflowError,
)


class TestTaskStatus:
    def test_all_values_present(self):
        values = {s.value for s in TaskStatus}
        assert "pending" in values
        assert "running" in values
        assert "completed" in values
        assert "failed" in values
        assert "skipped" in values
        assert "retrying" in values

    def test_construction_by_value(self):
        assert TaskStatus("completed") == TaskStatus.COMPLETED
        assert TaskStatus("failed") == TaskStatus.FAILED


class TestRetryPolicy:
    def test_defaults(self):
        rp = RetryPolicy()
        assert rp.max_attempts == 3
        assert rp.initial_delay == 1.0
        assert rp.max_delay == 60.0
        assert rp.exponential_base == 2.0

    def test_get_delay_first_attempt(self):
        rp = RetryPolicy(initial_delay=1.0, exponential_base=2.0)
        assert rp.get_delay(1) == 1.0  # 1.0 * 2^0

    def test_get_delay_second_attempt(self):
        rp = RetryPolicy(initial_delay=1.0, exponential_base=2.0)
        assert rp.get_delay(2) == 2.0  # 1.0 * 2^1

    def test_get_delay_third_attempt(self):
        rp = RetryPolicy(initial_delay=1.0, exponential_base=2.0)
        assert rp.get_delay(3) == 4.0  # 1.0 * 2^2

    def test_get_delay_capped_at_max(self):
        rp = RetryPolicy(initial_delay=1.0, exponential_base=2.0, max_delay=5.0)
        # attempt 10: 1.0 * 2^9 = 512, capped at 5
        assert rp.get_delay(10) == 5.0

    def test_custom_max_attempts(self):
        rp = RetryPolicy(max_attempts=5)
        assert rp.max_attempts == 5


class TestTaskResult:
    def test_success_result(self):
        r = TaskResult(success=True, value=42)
        assert r.success is True
        assert r.value == 42
        assert r.error is None

    def test_failure_result(self):
        r = TaskResult(success=False, error="timeout")
        assert r.success is False
        assert r.error == "timeout"
        assert r.value is None

    def test_defaults(self):
        r = TaskResult(success=True)
        assert r.execution_time == 0.0
        assert r.attempts == 1

    def test_with_execution_time_and_attempts(self):
        r = TaskResult(success=True, execution_time=1.5, attempts=3)
        assert r.execution_time == 1.5
        assert r.attempts == 3


class TestTask:
    def test_basic_construction(self):
        t = Task(name="my_task", action=lambda: None)
        assert t.name == "my_task"
        assert t.status == TaskStatus.PENDING
        assert t.attempts == 0

    def test_default_independent_lists(self):
        t1 = Task(name="a", action=lambda: None)
        t2 = Task(name="b", action=lambda: None)
        t1.args.append(1)
        assert t2.args == []

    def test_default_independent_sets(self):
        t1 = Task(name="a", action=lambda: None)
        t2 = Task(name="b", action=lambda: None)
        t1.dependencies.add("x")
        assert "x" not in t2.dependencies

    def test_hash_by_name(self):
        t1 = Task(name="task_a", action=lambda: None)
        t2 = Task(name="task_a", action=lambda: "other")
        assert hash(t1) == hash(t2)

    def test_hash_different_names(self):
        t1 = Task(name="a", action=lambda: None)
        t2 = Task(name="b", action=lambda: None)
        assert hash(t1) != hash(t2)

    def test_should_run_no_condition(self):
        t = Task(name="t", action=lambda: None)
        assert t.should_run({}) is True

    def test_should_run_condition_true(self):
        t = Task(name="t", action=lambda: None, condition=lambda results: True)
        assert t.should_run({}) is True

    def test_should_run_condition_false(self):
        t = Task(name="t", action=lambda: None, condition=lambda results: False)
        assert t.should_run({}) is False

    def test_should_run_condition_raises_returns_false(self):
        def bad_condition(results):
            raise RuntimeError("oops")

        t = Task(name="t", action=lambda: None, condition=bad_condition)
        # Should return False rather than propagating exception
        assert t.should_run({}) is False

    def test_get_result_completed(self):
        t = Task(name="t", action=lambda: None)
        t.status = TaskStatus.COMPLETED
        t.result = "done"
        t.execution_time = 0.5
        t.attempts = 2
        r = t.get_result()
        assert r.success is True
        assert r.value == "done"
        assert r.error is None
        assert r.execution_time == 0.5
        assert r.attempts == 2

    def test_get_result_failed(self):
        t = Task(name="t", action=lambda: None)
        t.status = TaskStatus.FAILED
        t.error = ValueError("bad input")
        r = t.get_result()
        assert r.success is False
        assert "bad input" in r.error

    def test_get_result_no_error(self):
        t = Task(name="t", action=lambda: None)
        t.status = TaskStatus.COMPLETED
        r = t.get_result()
        assert r.error is None

    def test_tags_are_set(self):
        t = Task(name="t", action=lambda: None, tags={"fast", "critical"})
        assert "fast" in t.tags
        assert "critical" in t.tags

    def test_timeout_default_none(self):
        t = Task(name="t", action=lambda: None)
        assert t.timeout is None


class TestWorkflowExceptions:
    def test_workflow_error_is_exception(self):
        e = WorkflowError("base error")
        assert isinstance(e, Exception)
        assert "base error" in str(e)

    def test_cycle_error_inherits_workflow_error(self):
        e = CycleError("cycle detected")
        assert isinstance(e, WorkflowError)
        assert "cycle" in str(e).lower()

    def test_task_failed_error_inherits_workflow_error(self):
        e = TaskFailedError("task X failed")
        assert isinstance(e, WorkflowError)
        assert "task X failed" in str(e)

    def test_all_raise_correctly(self):
        import pytest

        with pytest.raises(WorkflowError):
            raise CycleError("test")

        with pytest.raises(WorkflowError):
            raise TaskFailedError("test")
