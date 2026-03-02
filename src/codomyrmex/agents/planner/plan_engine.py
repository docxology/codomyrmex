"""Hierarchical task planning with goal decomposition."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class TaskPriority(Enum):
    """Functional component: TaskPriority."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskState(Enum):
    """Functional component: TaskState."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"


@dataclass
class PlanTask:
    """A task in a plan.

    Attributes:
        name: Task name.
        description: What to do.
        subtasks: Child tasks.
        depends_on: Task names this depends on.
        priority: Task priority.
        state: Current state.
        estimate_minutes: Time estimate.
    """

    name: str
    description: str = ""
    subtasks: list[PlanTask] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)
    priority: TaskPriority = TaskPriority.MEDIUM
    state: TaskState = TaskState.PENDING
    estimate_minutes: float = 0.0

    @property
    def is_leaf(self) -> bool:
        return len(self.subtasks) == 0

    @property
    def subtask_count(self) -> int:
        return len(self.subtasks) + sum(s.subtask_count for s in self.subtasks)

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "name": self.name,
            "state": self.state.value,
            "priority": self.priority.value,
            "subtasks": [s.to_dict() for s in self.subtasks],
        }


@dataclass
class Plan:
    """A hierarchical plan.

    Attributes:
        goal: High-level goal.
        tasks: Top-level tasks.
        created_at: When created.
    """

    goal: str
    tasks: list[PlanTask] = field(default_factory=list)
    created_at: float = 0.0

    def __post_init__(self) -> None:
        if not self.created_at:
            self.created_at = time.time()

    @property
    def total_tasks(self) -> int:
        return sum(1 + t.subtask_count for t in self.tasks)

    @property
    def completion_rate(self) -> float:
        all_tasks = self._flatten()
        if not all_tasks:
            return 0.0
        done = sum(1 for t in all_tasks if t.state == TaskState.COMPLETED)
        return done / len(all_tasks)

    def _flatten(self) -> list[PlanTask]:
        """flatten ."""
        result: list[PlanTask] = []
        stack = list(self.tasks)
        while stack:
            task = stack.pop()
            result.append(task)
            stack.extend(task.subtasks)
        return result


class PlanEngine:
    """Decompose goals into hierarchical plans.

    Usage::

        engine = PlanEngine()
        plan = engine.decompose("Build a REST API")
    """

    def decompose(self, goal: str, max_depth: int = 2) -> Plan:
        """Decompose a goal into tasks.

        Uses keyword analysis to generate task structure.
        """
        tasks = self._analyze_goal(goal, depth=0, max_depth=max_depth)
        plan = Plan(goal=goal, tasks=tasks)

        logger.info("Plan created", extra={"goal": goal[:40], "tasks": plan.total_tasks})
        return plan

    def _analyze_goal(self, goal: str, depth: int, max_depth: int) -> list[PlanTask]:
        """Generate tasks from goal text."""
        goal_lower = goal.lower()

        # Phase-based decomposition
        phases = []
        if any(kw in goal_lower for kw in ("build", "create", "implement")):
            phases = ["design", "implement", "test", "deploy"]
        elif any(kw in goal_lower for kw in ("fix", "debug", "resolve")):
            phases = ["diagnose", "fix", "verify"]
        elif any(kw in goal_lower for kw in ("analyze", "audit", "review")):
            phases = ["gather_data", "analyze", "report"]
        else:
            phases = ["plan", "execute", "review"]

        tasks = []
        for i, phase in enumerate(phases):
            task = PlanTask(
                name=phase,
                description=f"{phase.replace('_', ' ').title()} phase for: {goal[:50]}",
                priority=TaskPriority.HIGH if i == 0 else TaskPriority.MEDIUM,
                depends_on=[phases[i - 1]] if i > 0 else [],
            )

            if depth < max_depth:
                task.subtasks = [
                    PlanTask(
                        name=f"{phase}_step_{j+1}",
                        description=f"Step {j+1} of {phase}",
                    )
                    for j in range(2)
                ]

            tasks.append(task)

        return tasks


__all__ = ["Plan", "PlanEngine", "PlanTask", "TaskPriority", "TaskState"]
