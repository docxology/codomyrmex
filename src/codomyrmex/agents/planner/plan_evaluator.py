"""Plan evaluation and scoring.

Scores plan execution quality based on success rate, time efficiency,
retry ratio, and memory relevance. Produces a composite PlanScore
used to decide whether to re-plan or accept the result.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from codomyrmex.agents.planner.feedback_config import FeedbackConfig
from codomyrmex.orchestrator.workflows.workflow_engine import StepStatus, WorkflowResult


@dataclass
class PlanScore:
    """Composite quality score for a plan execution.

    Attributes:
        overall: Weighted composite in [0, 1].
        success_rate: Fraction of steps completed.
        time_efficiency: Inverse of total duration, normalized.
        retry_ratio: Fraction of iterations used.
        memory_hits: Fraction of memory queries that returned data.
        iteration: Which feedback iteration produced this score.
        details: Additional scoring breakdown.
    """

    overall: float = 0.0
    success_rate: float = 0.0
    time_efficiency: float = 0.0
    retry_ratio: float = 0.0
    memory_hits: float = 0.0
    iteration: int = 0
    details: dict[str, Any] = field(default_factory=dict)


class PlanEvaluator:
    """Evaluate plan execution quality.

    Produces a weighted composite score from workflow results,
    supporting configurable weights and multi-iteration comparison.

    Example::

        evaluator = PlanEvaluator(config=FeedbackConfig())
        score = evaluator.evaluate(
            workflow_result=result,
            iteration=1,
            memory_hits=3,
            memory_queries=5,
        )
        if score.overall >= config.quality_floor:
            print("Plan quality acceptable")
    """

    def __init__(self, config: FeedbackConfig | None = None) -> None:
        self._config = config or FeedbackConfig()

    @property
    def config(self) -> FeedbackConfig:
        """Current scoring configuration."""
        return self._config

    def evaluate(
        self,
        workflow_result: WorkflowResult,
        iteration: int = 1,
        memory_hits: int = 0,
        memory_queries: int = 0,
        time_budget_ms: float = 10000.0,
    ) -> PlanScore:
        """Score a plan execution.

        Args:
            workflow_result: Result from WorkflowRunner.run().
            iteration: Current feedback iteration (1-based).
            memory_hits: Number of memory entries found relevant.
            memory_queries: Total memory queries attempted.
            time_budget_ms: Expected max duration in milliseconds.

        Returns:
            PlanScore with composite and component scores.
        """
        cfg = self._config
        total_steps = len(workflow_result.steps)

        # Success rate: fraction of steps that completed
        if total_steps > 0:
            completed = sum(
                1 for s in workflow_result.steps
                if s.status == StepStatus.COMPLETED
            )
            success_rate = completed / total_steps
        else:
            success_rate = 0.0

        # Time efficiency: how much of the budget was used
        # Lower is better → normalize to [0, 1] where 1 = fast
        if time_budget_ms > 0:
            time_ratio = workflow_result.total_duration_ms / time_budget_ms
            time_efficiency = max(0.0, 1.0 - min(time_ratio, 1.0))
        else:
            time_efficiency = 1.0

        # Retry ratio: how many iterations used out of max
        # Lower is better → 1.0 if first iteration
        max_iter = cfg.max_iterations
        if max_iter > 0:
            retry_ratio = 1.0 - ((iteration - 1) / max_iter)
        else:
            retry_ratio = 1.0

        # Memory hits: fraction of queries that returned data
        if memory_queries > 0:
            memory_hit_rate = memory_hits / memory_queries
        else:
            memory_hit_rate = 0.0

        # Weighted composite
        overall = (
            cfg.weight_success_rate * success_rate
            + cfg.weight_time_efficiency * time_efficiency
            + cfg.weight_retry_ratio * retry_ratio
            + cfg.weight_memory_hits * memory_hit_rate
        )

        return PlanScore(
            overall=min(1.0, max(0.0, overall)),
            success_rate=success_rate,
            time_efficiency=time_efficiency,
            retry_ratio=retry_ratio,
            memory_hits=memory_hit_rate,
            iteration=iteration,
            details={
                "total_steps": total_steps,
                "completed_steps": workflow_result.completed_count,
                "failed_steps": workflow_result.failed_count,
                "duration_ms": workflow_result.total_duration_ms,
                "time_budget_ms": time_budget_ms,
            },
        )

    def compare(self, score_a: PlanScore, score_b: PlanScore) -> float:
        """Compute improvement ratio between two scores.

        Args:
            score_a: Earlier score.
            score_b: Later score.

        Returns:
            Positive value if b > a (improvement), negative if regression.
        """
        if score_a.overall == 0:
            return score_b.overall
        return score_b.overall - score_a.overall

    def is_converging(self, scores: list[PlanScore]) -> bool:
        """Check if scores show convergence (diminishing improvement).

        Convergence is detected when the latest improvement is below
        the configured threshold.

        Args:
            scores: List of PlanScore objects across iterations.

        Returns:
            True if the improvement between last two scores is
            below convergence_threshold.
        """
        if len(scores) < 2:
            return False
        improvement = self.compare(scores[-2], scores[-1])
        return improvement < self._config.convergence_threshold


__all__ = ["PlanEvaluator", "PlanScore"]
