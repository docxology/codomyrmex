"""Tests for orchestrator execution engines.

Sprint 2 coverage: targets SequentialEngine and ParallelEngine
from ``orchestrator.engines``.
"""

import time

import pytest

from codomyrmex.orchestrator.engines import (
    ParallelEngine,
    SequentialEngine,
    TaskState,
    WorkflowDefinition,
    create_engine,
)


@pytest.mark.unit
class TestSequentialEngine:
    """Tests for SequentialEngine execution."""

    def test_empty_workflow(self):
        """Engine handles a workflow with no tasks."""
        engine = SequentialEngine()
        wf = WorkflowDefinition(name="empty")
        result = engine.execute(wf)
        assert result.success is True
        assert result.task_results == {}

    def test_single_task(self):
        """Engine executes a single task and captures output."""
        engine = SequentialEngine()
        wf = WorkflowDefinition(name="single")
        wf.add_task("greet", action=lambda ctx: "hello")
        result = engine.execute(wf)
        assert result.success is True
        assert len(result.task_results) == 1
        task_result = list(result.task_results.values())[0]
        assert task_result.state == TaskState.COMPLETED
        assert task_result.output == "hello"

    def test_chained_tasks(self):
        """Tasks run in sequence and share context."""
        engine = SequentialEngine()
        wf = WorkflowDefinition(name="chain")
        t1 = wf.add_task("step1", action=lambda ctx: 10)
        wf.add_task("step2", action=lambda ctx: ctx.get("step1", 0) + 5, dependencies=[t1])
        result = engine.execute(wf)
        assert result.success is True
        task_results = list(result.task_results.values())
        assert task_results[0].output == 10
        assert task_results[1].output == 15

    def test_failing_task(self):
        """Engine reports failure when a task raises."""
        engine = SequentialEngine()
        wf = WorkflowDefinition(name="fail")
        wf.add_task("boom", action=lambda ctx: 1/0)
        result = engine.execute(wf)
        assert result.success is False
        assert "boom" in (result.error or "")

    def test_conditional_skip(self):
        """Task with false condition is skipped."""
        engine = SequentialEngine()
        wf = WorkflowDefinition(name="skip")
        wf.add_task(
            "maybe",
            action=lambda ctx: "ran",
            condition=lambda ctx: False,
        )
        result = engine.execute(wf)
        assert result.success is True
        task_result = list(result.task_results.values())[0]
        assert task_result.state == TaskState.SKIPPED

    def test_retry_on_failure(self):
        """Engine retries a task before declaring failure."""
        call_count = 0

        def flaky(ctx):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise RuntimeError("not yet")
            return "ok"

        engine = SequentialEngine()
        wf = WorkflowDefinition(name="retry")
        wf.add_task("flaky", action=flaky, retries=3, retry_delay=0.01)
        result = engine.execute(wf)
        assert result.success is True
        assert call_count == 3

    def test_duration_tracked(self):
        """Result captures timing information."""
        engine = SequentialEngine()
        wf = WorkflowDefinition(name="timed")
        wf.add_task("wait", action=lambda ctx: time.sleep(0.01))
        result = engine.execute(wf)
        assert result.duration_ms > 0


@pytest.mark.unit
class TestParallelEngine:
    """Tests for ParallelEngine execution."""

    def test_parallel_independent(self):
        """Independent tasks can run in parallel."""
        engine = ParallelEngine(max_workers=2)
        wf = WorkflowDefinition(name="parallel")
        wf.add_task("a", action=lambda ctx: "A")
        wf.add_task("b", action=lambda ctx: "B")
        result = engine.execute(wf)
        assert result.success is True
        assert len(result.task_results) == 2

    def test_parallel_with_dependency(self):
        """Dependent tasks execute after their dependencies."""
        engine = ParallelEngine(max_workers=2)
        wf = WorkflowDefinition(name="dep")
        t1 = wf.add_task("first", action=lambda ctx: 42)
        wf.add_task("second", action=lambda ctx: ctx.get("first", 0) * 2, dependencies=[t1])
        result = engine.execute(wf)
        assert result.success is True

    def test_parallel_failure(self):
        """Parallel engine fails fast on task error."""
        engine = ParallelEngine(max_workers=2)
        wf = WorkflowDefinition(name="fail")
        wf.add_task("ok", action=lambda ctx: "fine")
        wf.add_task("err", action=lambda ctx: 1/0)
        result = engine.execute(wf)
        assert result.success is False


@pytest.mark.unit
class TestEngineFactory:
    """Tests for engine factory function."""

    def test_create_sequential(self):
        engine = create_engine("sequential")
        assert isinstance(engine, SequentialEngine)

    def test_create_parallel(self):
        engine = create_engine("parallel")
        assert isinstance(engine, ParallelEngine)

    def test_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown engine type"):
            create_engine("quantum")
