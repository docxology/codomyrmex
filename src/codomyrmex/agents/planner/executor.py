"""Execute plans with progress tracking and re-planning."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any
from collections.abc import Callable

from codomyrmex.agents.planner.plan_engine import Plan, PlanTask, TaskState
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class ExecutionResult:
    """Result of plan execution.

    Attributes:
        plan: The executed plan.
        success: Overall success.
        completed_tasks: Number completed.
        failed_tasks: Number failed.
        replanned: Whether re-planning occurred.
        duration_ms: Total execution time.
    """

    plan: Plan | None = None
    success: bool = False
    completed_tasks: int = 0
    failed_tasks: int = 0
    replanned: bool = False
    duration_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "success": self.success,
            "completed": self.completed_tasks,
            "failed": self.failed_tasks,
            "replanned": self.replanned,
            "duration_ms": round(self.duration_ms, 2),
        }


class PlanExecutor:
    """Execute a plan with progress tracking.

    Usage::

        executor = PlanExecutor()
        result = executor.execute(plan, actions={"implement": my_impl_fn})
    """

    def __init__(self, max_retries: int = 1) -> None:
        """Execute   Init   operations natively."""
        self._max_retries = max_retries

    def execute(
        self,
        plan: Plan,
        actions: dict[str, Callable[..., Any]] | None = None,
    ) -> ExecutionResult:
        """Execute all tasks in a plan.

        Args:
            plan: The plan to execute.
            actions: Map task name → action callable.

        Returns:
            ``ExecutionResult`` with outcomes.
        """
        actions = actions or {}
        start = time.time()
        result = ExecutionResult(plan=plan)

        flat = self._flatten(plan.tasks)

        for task in flat:
            action = actions.get(task.name)
            task.state = TaskState.IN_PROGRESS

            try:
                if action:
                    action(task)
                task.state = TaskState.COMPLETED
                result.completed_tasks += 1
            except Exception as exc:
                task.state = TaskState.FAILED
                result.failed_tasks += 1
                logger.warning("Task failed", extra={"task": task.name, "error": str(exc)[:80]})

        result.duration_ms = (time.time() - start) * 1000
        result.success = result.failed_tasks == 0

        logger.info("Plan executed", extra=result.to_dict())
        return result

    @staticmethod
    def _flatten(tasks: list[PlanTask]) -> list[PlanTask]:
        """Flatten task tree to execution order."""
        result: list[PlanTask] = []
        for task in tasks:
            result.append(task)
            result.extend(PlanExecutor._flatten(task.subtasks))
        return result


__all__ = ["ExecutionResult", "PlanExecutor"]
