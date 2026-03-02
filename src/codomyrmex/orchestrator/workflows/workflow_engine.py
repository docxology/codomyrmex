"""Workflow engine for DAG-based task orchestration.

Defines workflow steps, dependencies, and a topological runner.
"""

from __future__ import annotations

import time
import uuid
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class StepStatus(Enum):
    """Status of a workflow step."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    """A single step in a workflow.

    Attributes:
        name: Step name.
        action: Callable to execute.
        depends_on: Step names this depends on.
        timeout: Max seconds.
        status: Current status.
        result: Step result.
        error: Error message if failed.
        duration_ms: Execution time.
    """

    name: str
    action: Callable[..., Any] | None = None
    depends_on: list[str] = field(default_factory=list)
    timeout: float = 300.0
    status: StepStatus = StepStatus.PENDING
    result: Any = None
    error: str = ""
    duration_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "name": self.name,
            "status": self.status.value,
            "depends_on": self.depends_on,
            "duration_ms": round(self.duration_ms, 2),
            "error": self.error,
        }


@dataclass
class WorkflowResult:
    """Result of running a workflow.

    Attributes:
        workflow_id: Unique ID.
        success: Whether all steps completed.
        steps: Step results.
        total_duration_ms: Total wall time.
    """

    workflow_id: str = ""
    success: bool = False
    steps: list[WorkflowStep] = field(default_factory=list)
    total_duration_ms: float = 0.0

    def __post_init__(self) -> None:
        """post Init ."""
        if not self.workflow_id:
            self.workflow_id = f"wf-{uuid.uuid4().hex[:8]}"

    @property
    def completed_count(self) -> int:
        """completed Count ."""
        return sum(1 for s in self.steps if s.status == StepStatus.COMPLETED)

    @property
    def failed_count(self) -> int:
        """failed Count ."""
        return sum(1 for s in self.steps if s.status == StepStatus.FAILED)

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "workflow_id": self.workflow_id,
            "success": self.success,
            "completed": self.completed_count,
            "failed": self.failed_count,
            "total_ms": round(self.total_duration_ms, 2),
        }


class WorkflowRunner:
    """Execute workflow DAGs in topological order.

    Usage::

        runner = WorkflowRunner()
        runner.add_step(WorkflowStep("build", action=build_fn))
        runner.add_step(WorkflowStep("test", action=test_fn, depends_on=["build"]))
        result = runner.run()
    """

    def __init__(self) -> None:
        """Initialize this instance."""
        self._steps: dict[str, WorkflowStep] = {}

    def add_step(self, step: WorkflowStep) -> None:
        """add Step ."""
        self._steps[step.name] = step

    def run(self, context: dict[str, Any] | None = None) -> WorkflowResult:
        """Execute all steps in dependency order.

        Args:
            context: Shared context dict passed to step actions.

        Returns:
            ``WorkflowResult`` with step outcomes.
        """
        ctx = context or {}
        start = time.time()

        order = self._topological_sort()
        result = WorkflowResult(steps=list(self._steps.values()))

        for step_name in order:
            step = self._steps[step_name]

            # Check dependencies
            deps_ok = all(
                self._steps[dep].status == StepStatus.COMPLETED
                for dep in step.depends_on
                if dep in self._steps
            )
            if not deps_ok:
                step.status = StepStatus.SKIPPED
                step.error = "dependency failed"
                continue

            step.status = StepStatus.RUNNING
            step_start = time.time()

            try:
                if step.action:
                    step.result = step.action(ctx)
                step.status = StepStatus.COMPLETED
            except Exception as exc:
                step.status = StepStatus.FAILED
                step.error = str(exc)

            step.duration_ms = (time.time() - step_start) * 1000

        result.total_duration_ms = (time.time() - start) * 1000
        result.success = all(
            s.status in (StepStatus.COMPLETED, StepStatus.SKIPPED)
            for s in self._steps.values()
        ) and result.failed_count == 0

        logger.info("Workflow complete", extra=result.to_dict())
        return result

    def _topological_sort(self) -> list[str]:
        """Kahn's algorithm for topological ordering."""
        in_degree: dict[str, int] = defaultdict(int)
        graph: dict[str, list[str]] = defaultdict(list)

        for name, step in self._steps.items():
            in_degree.setdefault(name, 0)
            for dep in step.depends_on:
                graph[dep].append(name)
                in_degree[name] += 1

        queue = deque(n for n, d in in_degree.items() if d == 0)
        order: list[str] = []

        while queue:
            node = queue.popleft()
            order.append(node)
            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(order) != len(self._steps):
            raise ValueError("Cycle detected in workflow DAG")

        return order

    @property
    def step_count(self) -> int:
        """step Count ."""
        return len(self._steps)

    def step_names(self) -> list[str]:
        """step Names ."""
        return list(self._steps.keys())


__all__ = ["StepStatus", "WorkflowResult", "WorkflowRunner", "WorkflowStep"]
