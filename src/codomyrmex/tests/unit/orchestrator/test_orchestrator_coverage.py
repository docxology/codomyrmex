"""Tests for the orchestrator module.

Covers:
- Scheduler: schedule, cancel, list_jobs, get_job, run_now, convenience triggers
- Workflow: add_task, validate, run, dependencies, conditional execution, retry
- RetryPolicy: compute_delay, should_retry, exponential backoff, jitter
- PipelineRetryExecutor: execute with policy, set_policy
- with_retry decorator: sync functions
- Orchestrator events, config
"""

import asyncio

import pytest

# ===================================================================
# Scheduler
# ===================================================================

@pytest.mark.unit
class TestScheduler:
    """Test the task Scheduler."""

    def test_schedule_basic(self):
        """Test functionality: schedule basic."""
        from codomyrmex.orchestrator.scheduler.scheduler import Scheduler
        scheduler = Scheduler()
        job_id = scheduler.schedule(func=lambda: "hello", name="test")
        assert job_id is not None
        assert isinstance(job_id, str)

    def test_get_job(self):
        """Test functionality: get job."""
        from codomyrmex.orchestrator.scheduler.scheduler import Scheduler
        scheduler = Scheduler()
        job_id = scheduler.schedule(func=lambda: 42, name="test")
        job = scheduler.get_job(job_id)
        assert job is not None
        assert job.name == "test"

    def test_cancel_job(self):
        """Test functionality: cancel job."""
        from codomyrmex.orchestrator.scheduler.models import JobStatus
        from codomyrmex.orchestrator.scheduler.scheduler import Scheduler
        scheduler = Scheduler()
        job_id = scheduler.schedule(func=lambda: None, name="to_cancel")
        result = scheduler.cancel(job_id)
        assert result is True
        job = scheduler.get_job(job_id)
        assert job.status == JobStatus.CANCELLED

    def test_cancel_nonexistent(self):
        """Test functionality: cancel nonexistent."""
        from codomyrmex.orchestrator.scheduler.scheduler import Scheduler
        scheduler = Scheduler()
        assert scheduler.cancel("nonexistent") is False

    def test_list_jobs(self):
        """Test functionality: list jobs."""
        from codomyrmex.orchestrator.scheduler.scheduler import Scheduler
        scheduler = Scheduler()
        scheduler.schedule(func=lambda: None, name="a")
        scheduler.schedule(func=lambda: None, name="b")
        jobs = scheduler.list_jobs()
        assert len(jobs) == 2

    def test_list_jobs_by_status(self):
        """Test functionality: list jobs by status."""
        from codomyrmex.orchestrator.scheduler.models import JobStatus
        from codomyrmex.orchestrator.scheduler.scheduler import Scheduler
        scheduler = Scheduler()
        j1 = scheduler.schedule(func=lambda: None, name="a")
        scheduler.schedule(func=lambda: None, name="b")
        scheduler.cancel(j1)
        cancelled = scheduler.list_jobs(status=JobStatus.CANCELLED)
        assert len(cancelled) == 1

    def test_run_now(self):
        """Test functionality: run now."""
        from codomyrmex.orchestrator.scheduler.scheduler import Scheduler
        scheduler = Scheduler()
        job_id = scheduler.schedule(func=lambda: 42, name="immediate")
        result = scheduler.run_now(job_id)
        assert result == 42

    def test_run_now_nonexistent_raises(self):
        """Test functionality: run now nonexistent raises."""
        from codomyrmex.orchestrator.scheduler.scheduler import Scheduler
        scheduler = Scheduler()
        with pytest.raises(ValueError):
            scheduler.run_now("nonexistent")


@pytest.mark.unit
class TestConvenienceTriggers:
    """Test scheduler convenience trigger functions."""

    def test_every(self):
        """Test functionality: every."""
        from codomyrmex.orchestrator.scheduler.scheduler import every
        from codomyrmex.orchestrator.scheduler.triggers import IntervalTrigger
        trigger = every(seconds=30)
        assert isinstance(trigger, IntervalTrigger)

    def test_at(self):
        """Test functionality: at."""
        from codomyrmex.orchestrator.scheduler.scheduler import at
        from codomyrmex.orchestrator.scheduler.triggers import OnceTrigger
        trigger = at("23:59")
        assert isinstance(trigger, OnceTrigger)

    def test_cron(self):
        """Test functionality: cron."""
        from codomyrmex.orchestrator.scheduler.scheduler import cron
        from codomyrmex.orchestrator.scheduler.triggers import CronTrigger
        trigger = cron("*/5 * * * *")
        assert isinstance(trigger, CronTrigger)


# ===================================================================
# Workflow
# ===================================================================

@pytest.mark.unit
class TestWorkflow:
    """Test the Workflow DAG execution engine."""

    def test_add_task(self):
        """Test functionality: add task."""
        from codomyrmex.orchestrator.workflows.workflow import Workflow
        wf = Workflow("test_wf")
        wf.add_task("step1", action=lambda: "done")
        assert len(wf.tasks) >= 1

    def test_simple_run(self):
        """Test functionality: simple run."""
        from codomyrmex.orchestrator.workflows.workflow import Workflow
        wf = Workflow("test_wf")
        wf.add_task("step1", action=lambda: "done")
        results = asyncio.run(wf.run())
        assert "step1" in results
        # run() may return TaskResult objects or raw values
        r = results["step1"]
        if hasattr(r, 'success'):
            assert r.success is True
        else:
            assert r == "done"

    def test_dependency_chain(self):
        """Test functionality: dependency chain."""
        from codomyrmex.orchestrator.workflows.workflow import Workflow
        order = []
        wf = Workflow("test_wf")
        wf.add_task("a", action=lambda: order.append("a") or "a")
        wf.add_task("b", action=lambda: order.append("b") or "b", dependencies=["a"])
        wf.add_task("c", action=lambda: order.append("c") or "c", dependencies=["b"])
        asyncio.run(wf.run())
        assert order == ["a", "b", "c"]

    def test_validate_detects_missing_dep(self):
        """Test functionality: validate detects missing dep."""
        from codomyrmex.orchestrator.workflows.workflow import Workflow, WorkflowError
        wf = Workflow("test_wf")
        wf.add_task("a", action=lambda: None, dependencies=["nonexistent"])
        with pytest.raises(WorkflowError):
            wf.validate()

    def test_validate_detects_cycle(self):
        """Test functionality: validate detects cycle."""
        from codomyrmex.orchestrator.workflows.workflow import CycleError, Workflow
        wf = Workflow("test_wf")
        wf.add_task("a", action=lambda: None, dependencies=["b"])
        wf.add_task("b", action=lambda: None, dependencies=["a"])
        with pytest.raises(CycleError):
            wf.validate()

    def test_task_failure(self):
        """Test functionality: task failure."""
        from codomyrmex.orchestrator.workflows.workflow import Workflow
        def failing():
            raise RuntimeError("boom")
        wf = Workflow("test_wf", fail_fast=False)
        wf.add_task("fail", action=failing)
        results = asyncio.run(wf.run())
        # Failed tasks may return None, TaskResult, or error
        r = results.get("fail")
        if hasattr(r, 'success'):
            assert r.success is False
        else:
            # Failed tasks return None
            assert r is None

    def test_get_summary(self):
        """Test functionality: get summary."""
        from codomyrmex.orchestrator.workflows.workflow import Workflow
        wf = Workflow("test_wf")
        wf.add_task("step1", action=lambda: "ok")
        asyncio.run(wf.run())
        summary = wf.get_summary()
        assert isinstance(summary, dict)

    def test_get_task_result(self):
        """Test functionality: get task result."""
        from codomyrmex.orchestrator.workflows.workflow import Workflow
        wf = Workflow("test_wf")
        wf.add_task("step1", action=lambda: 42)
        asyncio.run(wf.run())
        result = wf.get_task_result("step1")
        assert result is not None


# ===================================================================
# RetryPolicy
# ===================================================================

@pytest.mark.unit
class TestRetryPolicy:
    """Test RetryPolicy from retry_policy module."""

    def test_compute_delay_exponential(self):
        """Test functionality: compute delay exponential."""
        from codomyrmex.orchestrator.resilience.retry_policy import RetryPolicy
        policy = RetryPolicy(base_delay=1.0, exponential_base=2.0, jitter=False)
        d1 = policy.compute_delay(1)
        d2 = policy.compute_delay(2)
        assert d2 > d1

    def test_compute_delay_capped(self):
        """Test functionality: compute delay capped."""
        from codomyrmex.orchestrator.resilience.retry_policy import RetryPolicy
        policy = RetryPolicy(base_delay=1.0, max_delay=10.0, exponential_base=2.0, jitter=False)
        delay = policy.compute_delay(100)
        assert delay <= 10.0

    def test_should_retry_within_attempts(self):
        """Test functionality: should retry within attempts."""
        from codomyrmex.orchestrator.resilience.retry_policy import (
            RetryOutcome,
            RetryPolicy,
        )
        policy = RetryPolicy(max_attempts=3)
        result = policy.should_retry(ValueError("test"), attempt=1)
        assert result == RetryOutcome.RETRY

    def test_should_retry_exceeded(self):
        """Test functionality: should retry exceeded."""
        from codomyrmex.orchestrator.resilience.retry_policy import (
            RetryOutcome,
            RetryPolicy,
        )
        policy = RetryPolicy(max_attempts=3)
        result = policy.should_retry(ValueError("test"), attempt=3)
        assert result in (RetryOutcome.ABORT, RetryOutcome.DEAD_LETTER)


@pytest.mark.unit
class TestPipelineRetryExecutor:
    """Test PipelineRetryExecutor."""

    def test_execute_success(self):
        """Test functionality: execute success."""
        from codomyrmex.orchestrator.resilience.retry_policy import (
            PipelineRetryExecutor,
            RetryOutcome,
        )
        executor = PipelineRetryExecutor()
        result = executor.execute("test_step", lambda: 42)
        assert result.outcome == RetryOutcome.SUCCESS
        assert result.result == 42

    def test_execute_failure_retried(self):
        """Test functionality: execute failure retried."""
        from codomyrmex.orchestrator.resilience.retry_policy import (
            PipelineRetryExecutor,
            RetryOutcome,
            RetryPolicy,
        )
        call_count = 0
        def flaky():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("transient")
            return "ok"
        executor = PipelineRetryExecutor(
            default_policy=RetryPolicy(max_attempts=5, base_delay=0.01, jitter=False)
        )
        result = executor.execute("flaky_step", flaky)
        assert result.outcome == RetryOutcome.SUCCESS
        assert call_count == 3

    def test_execute_exhausted(self):
        """Test functionality: execute exhausted."""
        from codomyrmex.orchestrator.resilience.retry_policy import (
            PipelineRetryExecutor,
            RetryOutcome,
            RetryPolicy,
        )
        executor = PipelineRetryExecutor(
            default_policy=RetryPolicy(max_attempts=2, base_delay=0.01, jitter=False)
        )
        def always_fail():
            raise ValueError("permanent")
        result = executor.execute("fail_step", always_fail)
        assert result.outcome in (RetryOutcome.ABORT, RetryOutcome.DEAD_LETTER)

    def test_set_custom_policy(self):
        """Test functionality: set custom policy."""
        from codomyrmex.orchestrator.resilience.retry_policy import (
            PipelineRetryExecutor,
            RetryPolicy,
        )
        executor = PipelineRetryExecutor()
        custom = RetryPolicy(max_attempts=10)
        executor.set_policy("special_step", custom)
        retrieved = executor.get_policy("special_step")
        assert retrieved.max_attempts == 10


# ===================================================================
# with_retry Decorator
# ===================================================================

@pytest.mark.unit
class TestWithRetryDecorator:
    """Test the @with_retry decorator."""

    def test_successful_function(self):
        """Test functionality: successful function."""
        from codomyrmex.orchestrator.resilience.retry_policy import with_retry
        @with_retry(max_attempts=3)
        def succeed():
            return 42
        assert succeed() == 42

    def test_retries_on_failure(self):
        """Test functionality: retries on failure."""
        from codomyrmex.orchestrator.resilience.retry_policy import with_retry
        counter = {"n": 0}
        @with_retry(max_attempts=5, base_delay=0.01)
        def flaky():
            counter["n"] += 1
            if counter["n"] < 3:
                raise ValueError("oops")
            return "ok"
        assert flaky() == "ok"
        assert counter["n"] == 3

    def test_exhausts_retries(self):
        """Test functionality: exhausts retries."""
        from codomyrmex.orchestrator.resilience.retry_policy import with_retry
        @with_retry(max_attempts=2, base_delay=0.01)
        def always_fail():
            raise RuntimeError("nope")
        with pytest.raises(RuntimeError):
            always_fail()


# ===================================================================
# Orchestrator Config
# ===================================================================

@pytest.mark.unit
class TestOrchestratorConfig:
    """Test orchestrator configuration loading."""

    def test_load_config_empty_dir(self, tmp_path):
        """Test functionality: load config empty dir."""
        from codomyrmex.orchestrator.config import load_config
        config = load_config(tmp_path)
        assert isinstance(config, dict)
        assert "skip" in config

    def test_get_script_config(self, tmp_path):
        """Test functionality: get script config."""
        from codomyrmex.orchestrator.config import get_script_config
        script = tmp_path / "test.py"
        script.touch()
        config = get_script_config(script, tmp_path, {"skip": [], "timeout_override": {}, "scripts": {}})
        assert isinstance(config, dict)
