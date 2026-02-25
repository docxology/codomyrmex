"""Planning-execution-feedback loop.

Wires PlanEngine → WorkflowRunner → MemoryStore into a convergent
cycle that decomposes goals, executes plans, evaluates quality,
stores outcomes, and re-plans if needed.
"""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from codomyrmex.agents.memory.store import MemoryStore
from codomyrmex.agents.planner.feedback_config import FeedbackConfig
from codomyrmex.agents.planner.plan_engine import Plan, PlanEngine, PlanTask, TaskState
from codomyrmex.agents.planner.plan_evaluator import PlanEvaluator, PlanScore
from codomyrmex.logging_monitoring import get_logger
from codomyrmex.orchestrator.workflows.workflow_engine import (
    WorkflowResult,
    WorkflowRunner,
    WorkflowStep,
)

logger = get_logger(__name__)


@dataclass
class FeedbackResult:
    """Result of a full feedback loop execution.

    Attributes:
        goal: The original goal.
        success: Whether the loop converged successfully.
        final_score: The best PlanScore achieved.
        iterations: Number of iterations executed.
        scores: Score history across iterations.
        final_plan: The last plan used.
        final_workflow_result: The last workflow execution result.
        memory_keys: Keys written to the MemoryStore.
        converged: Whether convergence was detected.
    """

    goal: str
    success: bool = False
    final_score: PlanScore = field(default_factory=PlanScore)
    iterations: int = 0
    scores: list[PlanScore] = field(default_factory=list)
    final_plan: Plan | None = None
    final_workflow_result: WorkflowResult | None = None
    memory_keys: list[str] = field(default_factory=list)
    converged: bool = False


def _goal_hash(goal: str) -> str:
    """Create a short hash for a goal string."""
    return hashlib.sha256(goal.encode()).hexdigest()[:12]


def _default_task_executor(task: PlanTask) -> Callable[..., Any]:
    """Create a default executor for a PlanTask.

    Returns a callable that marks the task as completed and returns
    a dict with the task name and state.
    """
    def executor(ctx: dict[str, Any]) -> dict[str, Any]:
        """Execute Executor operations natively."""
        task.state = TaskState.COMPLETED
        return {"task": task.name, "state": task.state.value}
    return executor


class FeedbackLoop:
    """Convergent planning-execution-feedback cycle.

    Orchestrates goal decomposition (PlanEngine), execution
    (WorkflowRunner), evaluation (PlanEvaluator), and memory
    persistence (MemoryStore) into a closed loop that iterates
    until quality converges or max iterations are reached.

    Example::

        loop = FeedbackLoop(
            config=FeedbackConfig(max_iterations=3, quality_floor=0.7),
        )
        result = loop.run("Build a REST API")
        if result.success:
            print(f"Converged in {result.iterations} iterations")
    """

    def __init__(
        self,
        config: FeedbackConfig | None = None,
        plan_engine: PlanEngine | None = None,
        memory_store: MemoryStore | None = None,
        task_executor_factory: Callable[[PlanTask], Callable[..., Any]] | None = None,
    ) -> None:
        """Execute   Init   operations natively."""
        self._config = config or FeedbackConfig()
        self._plan_engine = plan_engine or PlanEngine()
        self._memory = memory_store or MemoryStore()
        self._evaluator = PlanEvaluator(config=self._config)
        self._task_executor = task_executor_factory or _default_task_executor

    @property
    def config(self) -> FeedbackConfig:
        """Current feedback configuration."""
        return self._config

    @property
    def memory(self) -> MemoryStore:
        """Underlying memory store."""
        return self._memory

    def run(self, goal: str) -> FeedbackResult:
        """Execute the full feedback loop for a goal.

        1. Decompose goal → Plan (via PlanEngine)
        2. Convert PlanTasks → WorkflowSteps
        3. Run workflow (via WorkflowRunner)
        4. Evaluate result (via PlanEvaluator)
        5. Store outcomes in MemoryStore
        6. If score < quality_floor, re-plan with memory context
        7. Repeat until converged or max_iterations reached

        Args:
            goal: High-level goal to pursue.

        Returns:
            FeedbackResult with convergence status and history.
        """
        cfg = self._config
        goal_tag = f"{cfg.memory_tag_prefix}:{_goal_hash(goal)}"
        scores: list[PlanScore] = []
        memory_keys: list[str] = []
        best_score = PlanScore()
        best_plan: Plan | None = None
        best_result: WorkflowResult | None = None

        for iteration in range(1, cfg.max_iterations + 1):
            logger.info(
                "Feedback iteration %d/%d for goal: %s",
                iteration, cfg.max_iterations, goal[:50],
            )

            # 1. Check memory for prior context
            prior_entries = self._memory.search_by_tag(goal_tag)
            memory_queries = 1
            memory_hits = len(prior_entries)

            # 2. Decompose goal (optionally enriched with memory)
            enriched_goal = goal
            if prior_entries:
                prior_summary = "; ".join(
                    f"{e.key}={e.value}" for e in prior_entries[:3]
                )
                enriched_goal = f"{goal} [context: {prior_summary}]"

            plan = self._plan_engine.decompose(enriched_goal)

            # 3. Convert PlanTasks → WorkflowSteps
            runner = WorkflowRunner()
            flat_tasks = plan._flatten()
            for task in flat_tasks:
                step = WorkflowStep(
                    name=task.name,
                    action=self._task_executor(task),
                    depends_on=task.depends_on,
                )
                runner.add_step(step)

            # 4. Execute workflow
            workflow_result = runner.run()

            # 5. Evaluate
            score = self._evaluator.evaluate(
                workflow_result=workflow_result,
                iteration=iteration,
                memory_hits=memory_hits,
                memory_queries=memory_queries,
            )
            scores.append(score)

            # 6. Store outcomes in memory
            outcome_key = f"feedback:{_goal_hash(goal)}:iter{iteration}"
            self._memory.put(
                key=outcome_key,
                value={
                    "iteration": iteration,
                    "goal": goal[:100],
                    "score": score.overall,
                    "success": workflow_result.success,
                    "completed": workflow_result.completed_count,
                    "failed": workflow_result.failed_count,
                },
                ttl=cfg.memory_ttl,
                tags=[goal_tag, cfg.memory_tag_prefix, f"iter:{iteration}"],
            )
            memory_keys.append(outcome_key)

            # Track best
            if score.overall >= best_score.overall:
                best_score = score
                best_plan = plan
                best_result = workflow_result

            # 7. Check convergence
            if score.overall >= cfg.quality_floor:
                logger.info(
                    "Quality floor reached: %.3f >= %.3f",
                    score.overall, cfg.quality_floor,
                )
                return FeedbackResult(
                    goal=goal,
                    success=True,
                    final_score=best_score,
                    iterations=iteration,
                    scores=scores,
                    final_plan=best_plan,
                    final_workflow_result=best_result,
                    memory_keys=memory_keys,
                    converged=True,
                )

            # Check if improvement is too small (convergence)
            if self._evaluator.is_converging(scores):
                logger.info("Convergence detected (improvement below threshold)")
                return FeedbackResult(
                    goal=goal,
                    success=best_score.overall >= cfg.quality_floor,
                    final_score=best_score,
                    iterations=iteration,
                    scores=scores,
                    final_plan=best_plan,
                    final_workflow_result=best_result,
                    memory_keys=memory_keys,
                    converged=True,
                )

            # Check partial failure retry policy
            if not cfg.retry_on_partial_failure and workflow_result.failed_count > 0:
                logger.info("Partial failure — not retrying (config)")
                break

        # Max iterations exhausted
        return FeedbackResult(
            goal=goal,
            success=best_score.overall >= cfg.quality_floor,
            final_score=best_score,
            iterations=len(scores),
            scores=scores,
            final_plan=best_plan,
            final_workflow_result=best_result,
            memory_keys=memory_keys,
            converged=False,
        )


__all__ = ["FeedbackConfig", "FeedbackLoop", "FeedbackResult"]
