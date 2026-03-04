"""Tests for Sprint 29: Workflow Journaling & Analytics.

Covers WorkflowJournal lifecycle events, MemoryStore persistence,
and WorkflowAnalytics (failure hotspots, duration trends, success
rates, insight generation).
"""

import pytest

from codomyrmex.agents.memory.store import MemoryStore
from codomyrmex.orchestrator.workflows.workflow_analytics import (
    WorkflowAnalytics,
    WorkflowInsight,
)
from codomyrmex.orchestrator.workflows.workflow_engine import (
    StepStatus,
    WorkflowResult,
    WorkflowRunner,
    WorkflowStep,
)
from codomyrmex.orchestrator.workflows.workflow_journal import (
    WorkflowJournal,
)


def _make_result(success: bool = True, step_count: int = 2, wf_id: str = "wf-1") -> WorkflowResult:
    """Helper to create a WorkflowResult for testing."""
    steps = []
    for i in range(step_count):
        status = StepStatus.COMPLETED if success or i == 0 else StepStatus.FAILED
        steps.append(WorkflowStep(
            name=f"step_{i}",
            status=status,
            duration_ms=50.0 + i * 10,
            error="" if status == StepStatus.COMPLETED else "simulated",
        ))
    return WorkflowResult(
        workflow_id=wf_id,
        success=success,
        steps=steps,
        total_duration_ms=sum(s.duration_ms for s in steps),
    )


# ─── WorkflowJournal ────────────────────────────────────────────────

class TestWorkflowJournal:
    """Test suite for WorkflowJournal."""

    def test_record_start(self):
        """Verify record start behavior."""
        journal = WorkflowJournal()
        runner = WorkflowRunner()
        runner.add_step(WorkflowStep("a"))
        journal.on_workflow_start(runner, "wf-1")
        assert journal.entry_count == 1
        entries = journal.by_event_type("start")
        assert len(entries) == 1

    def test_record_step(self):
        """Verify record step behavior."""
        journal = WorkflowJournal()
        step = WorkflowStep(name="build", status=StepStatus.COMPLETED, duration_ms=100.0)
        journal.on_step_complete("wf-1", step)
        entries = journal.by_event_type("step")
        assert len(entries) == 1
        assert entries[0].step_name == "build"
        assert entries[0].status == "completed"

    def test_record_complete(self):
        """Verify record complete behavior."""
        journal = WorkflowJournal()
        result = _make_result(success=True)
        journal.on_workflow_complete(result)
        entries = journal.by_event_type("complete")
        assert len(entries) == 1
        assert entries[0].status == "success"

    def test_record_full_workflow(self):
        """Verify record full workflow behavior."""
        journal = WorkflowJournal()
        runner = WorkflowRunner()
        runner.add_step(WorkflowStep("a"))
        runner.add_step(WorkflowStep("b"))
        result = _make_result(step_count=2)
        journal.record_full_workflow(runner, result)
        # 1 start + 2 steps + 1 complete = 4
        assert journal.entry_count == 4

    def test_by_workflow_id(self):
        """Verify by workflow id behavior."""
        journal = WorkflowJournal()
        result1 = _make_result(wf_id="wf-1")
        result2 = _make_result(wf_id="wf-2")
        journal.on_workflow_complete(result1)
        journal.on_workflow_complete(result2)
        assert len(journal.by_workflow_id("wf-1")) == 1

    def test_memory_persistence(self):
        """Verify memory persistence behavior."""
        memory = MemoryStore()
        journal = WorkflowJournal(memory=memory)
        result = _make_result()
        journal.on_workflow_complete(result)
        entries = memory.search_by_tag("journal")
        assert len(entries) >= 1


# ─── WorkflowAnalytics ───────────────────────────────────────────────

class TestWorkflowAnalytics:
    """Test suite for WorkflowAnalytics."""

    def _populated_journal(self) -> WorkflowJournal:
        journal = WorkflowJournal()
        runner = WorkflowRunner()
        runner.add_step(WorkflowStep("build"))
        runner.add_step(WorkflowStep("test"))

        # Two successful workflows
        for wf_id in ("wf-1", "wf-2"):
            journal.record_full_workflow(runner, _make_result(success=True, wf_id=wf_id))

        # One failed workflow
        journal.record_full_workflow(runner, _make_result(success=False, wf_id="wf-3"))
        return journal

    def test_failure_hotspots(self):
        """Verify failure hotspots behavior."""
        journal = self._populated_journal()
        analytics = WorkflowAnalytics(journal)
        hotspots = analytics.failure_hotspots(n=3)
        # wf-3 has 1 failed step (step_1)
        assert len(hotspots) >= 1

    def test_duration_trend(self):
        """Verify duration trend behavior."""
        journal = self._populated_journal()
        analytics = WorkflowAnalytics(journal)
        trend = analytics.duration_trend(window=2)
        assert len(trend) == 3  # 3 workflows

    def test_success_rate(self):
        """Verify success rate behavior."""
        journal = self._populated_journal()
        analytics = WorkflowAnalytics(journal)
        rate = analytics.success_rate("step_0")
        assert rate == 1.0  # step_0 always succeeds

    def test_generate_insight(self):
        """Verify generate insight behavior."""
        journal = self._populated_journal()
        analytics = WorkflowAnalytics(journal)
        insight = analytics.generate_insight()
        assert isinstance(insight, WorkflowInsight)
        assert insight.total_workflows == 3
        assert insight.overall_success_rate == pytest.approx(2 / 3, abs=0.01)

    def test_empty_journal(self):
        """Verify empty journal behavior."""
        journal = WorkflowJournal()
        analytics = WorkflowAnalytics(journal)
        insight = analytics.generate_insight()
        assert insight.total_workflows == 0
        assert insight.overall_success_rate == 0.0
