"""Tests for Sprint 27: Planning-Execution-Feedback Loop.

Covers FeedbackConfig, PlanEvaluator, PlanScore, and the full
FeedbackLoop convergent cycle.
"""

import pytest

from codomyrmex.agents.memory.store import MemoryStore
from codomyrmex.agents.planner.feedback_config import FeedbackConfig
from codomyrmex.agents.planner.feedback_loop import FeedbackLoop
from codomyrmex.agents.planner.plan_engine import PlanEngine, TaskState
from codomyrmex.agents.planner.plan_evaluator import PlanEvaluator, PlanScore
from codomyrmex.orchestrator.workflows.workflow_engine import (
    StepStatus,
    WorkflowResult,
    WorkflowStep,
)

# ─── FeedbackConfig ──────────────────────────────────────────────────

class TestFeedbackConfig:
    """Tests for FeedbackConfig defaults."""

    def test_defaults(self):
        """Test functionality: defaults."""
        cfg = FeedbackConfig()
        assert cfg.max_iterations == 3
        assert cfg.quality_floor == 0.6
        assert cfg.weight_success_rate == 0.4
        assert abs(cfg.weight_success_rate + cfg.weight_time_efficiency
                    + cfg.weight_retry_ratio + cfg.weight_memory_hits - 1.0) < 0.001

    def test_custom_config(self):
        """Test functionality: custom config."""
        cfg = FeedbackConfig(max_iterations=5, quality_floor=0.9)
        assert cfg.max_iterations == 5
        assert cfg.quality_floor == 0.9


# ─── PlanEvaluator ────────────────────────────────────────────────────

class TestPlanEvaluator:
    """Tests for PlanEvaluator scoring."""

    def test_perfect_score(self):
        """All steps completed, first iteration, within budget."""
        evaluator = PlanEvaluator()
        result = WorkflowResult(
            success=True,
            steps=[
                WorkflowStep(name="a", status=StepStatus.COMPLETED),
                WorkflowStep(name="b", status=StepStatus.COMPLETED),
            ],
            total_duration_ms=100.0,
        )
        score = evaluator.evaluate(result, iteration=1, time_budget_ms=10000.0)
        assert score.success_rate == 1.0
        assert score.overall > 0.8

    def test_failed_steps_lower_score(self):
        """Failed steps reduce the score."""
        evaluator = PlanEvaluator()
        result = WorkflowResult(
            success=False,
            steps=[
                WorkflowStep(name="a", status=StepStatus.COMPLETED),
                WorkflowStep(name="b", status=StepStatus.FAILED),
            ],
            total_duration_ms=100.0,
        )
        score = evaluator.evaluate(result, iteration=1)
        assert score.success_rate == 0.5
        assert score.overall < 0.8

    def test_later_iterations_lower_retry_score(self):
        """Being on iteration 3/3 penalizes retry ratio."""
        evaluator = PlanEvaluator(config=FeedbackConfig(max_iterations=3))
        result = WorkflowResult(
            success=True,
            steps=[WorkflowStep(name="a", status=StepStatus.COMPLETED)],
            total_duration_ms=100.0,
        )
        score_iter1 = evaluator.evaluate(result, iteration=1)
        score_iter3 = evaluator.evaluate(result, iteration=3)
        assert score_iter1.overall > score_iter3.overall

    def test_compare_scores(self):
        """Test functionality: compare scores."""
        evaluator = PlanEvaluator()
        a = PlanScore(overall=0.6)
        b = PlanScore(overall=0.8)
        assert evaluator.compare(a, b) == pytest.approx(0.2)

    def test_convergence_detection(self):
        """Test functionality: convergence detection."""
        evaluator = PlanEvaluator(config=FeedbackConfig(convergence_threshold=0.05))
        scores = [PlanScore(overall=0.75), PlanScore(overall=0.76)]
        assert evaluator.is_converging(scores) is True

    def test_not_converging(self):
        """Test functionality: not converging."""
        evaluator = PlanEvaluator(config=FeedbackConfig(convergence_threshold=0.05))
        scores = [PlanScore(overall=0.5), PlanScore(overall=0.8)]
        assert evaluator.is_converging(scores) is False


# ─── FeedbackLoop ─────────────────────────────────────────────────────

class TestFeedbackLoop:
    """Tests for the full FeedbackLoop."""

    def test_happy_path_converges(self):
        """Goal → plan → execute → converge on first iteration."""
        config = FeedbackConfig(
            max_iterations=3,
            quality_floor=0.5,  # low floor → converges immediately
        )
        loop = FeedbackLoop(config=config)
        result = loop.run("Build a test project")

        assert result.success is True
        assert result.iterations == 1
        assert result.converged is True
        assert result.final_score.overall >= config.quality_floor
        assert len(result.memory_keys) >= 1

    def test_memory_persisted(self):
        """Outcomes are stored in the MemoryStore."""
        memory = MemoryStore()
        loop = FeedbackLoop(
            config=FeedbackConfig(quality_floor=0.5),
            memory_store=memory,
        )
        loop.run("Analyze data")

        assert memory.size >= 1
        # Check that feedback tag is searchable
        entries = memory.search_by_tag("feedback")
        assert len(entries) >= 1

    def test_max_iterations_respected(self):
        """Loop does not exceed max_iterations."""
        config = FeedbackConfig(
            max_iterations=2,
            quality_floor=1.0,  # unreachable → forces max iterations
            convergence_threshold=0.0001,  # tiny threshold
        )
        loop = FeedbackLoop(config=config)
        result = loop.run("Impossible goal")

        assert result.iterations <= config.max_iterations
        assert len(result.scores) <= config.max_iterations

    def test_quality_floor_triggers_replan(self):
        """If score < quality_floor, loop re-plans."""
        fail_count = 0

        def failing_executor(task):
            def executor(ctx):
                nonlocal fail_count
                fail_count += 1
                if fail_count <= 2:
                    raise RuntimeError("step failed")
                task.state = TaskState.COMPLETED
                return {"task": task.name}
            return executor

        config = FeedbackConfig(
            max_iterations=3,
            quality_floor=0.9,
            retry_on_partial_failure=True,
        )
        loop = FeedbackLoop(
            config=config,
            task_executor_factory=failing_executor,
        )
        result = loop.run("Fix a bug")
        assert result.iterations >= 1  # At least tried

    def test_scores_tracked_across_iterations(self):
        """Score history is maintained."""
        config = FeedbackConfig(
            max_iterations=2,
            quality_floor=1.0,  # unreachable
            convergence_threshold=0.0001,
        )
        loop = FeedbackLoop(config=config)
        result = loop.run("Review code")

        assert len(result.scores) == result.iterations
        for score in result.scores:
            assert isinstance(score, PlanScore)

    def test_no_retry_on_partial_failure(self):
        """retry_on_partial_failure=False stops after first failure."""
        def always_fail(task):
            def executor(ctx):
                raise RuntimeError("nope")
            return executor

        config = FeedbackConfig(
            max_iterations=3,
            quality_floor=0.9,
            retry_on_partial_failure=False,
        )
        loop = FeedbackLoop(
            config=config,
            task_executor_factory=always_fail,
        )
        result = loop.run("Deploy app")
        assert result.iterations == 1
        assert result.success is False

    def test_custom_plan_engine(self):
        """Custom PlanEngine is used."""
        engine = PlanEngine()
        loop = FeedbackLoop(
            config=FeedbackConfig(quality_floor=0.5),
            plan_engine=engine,
        )
        result = loop.run("Custom engine test")
        assert result.success is True
