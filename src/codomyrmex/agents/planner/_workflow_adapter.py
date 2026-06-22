"""Planner-local workflow primitives.

The planner layer only needs a small DAG runner for feedback-loop scoring.
Keeping that runner here avoids a direct dependency on the higher-level
orchestrator package while preserving the result shape expected by callers.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable


class StepStatus(Enum):
    """Status of a planner workflow step."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    """A single planner workflow step."""

    name: str
    action: Callable[..., Any] | None = None
    depends_on: list[str] = field(default_factory=list)
    status: StepStatus = StepStatus.PENDING
    result: Any = None
    error: str = ""
    duration_ms: float = 0.0


@dataclass
class WorkflowResult:
    """Result of running planner workflow steps."""

    workflow_id: str = ""
    success: bool = False
    steps: list[WorkflowStep] = field(default_factory=list)
    total_duration_ms: float = 0.0

    def __post_init__(self) -> None:
        if not self.workflow_id:
            self.workflow_id = f"planner-wf-{uuid.uuid4().hex[:8]}"

    @property
    def completed_count(self) -> int:
        """Number of completed steps."""
        return sum(1 for step in self.steps if step.status == StepStatus.COMPLETED)

    @property
    def failed_count(self) -> int:
        """Number of failed steps."""
        return sum(1 for step in self.steps if step.status == StepStatus.FAILED)


class WorkflowRunner:
    """Execute planner workflow steps in dependency order."""

    def __init__(self) -> None:
        self._steps: dict[str, WorkflowStep] = {}

    def add_step(self, step: WorkflowStep) -> None:
        """Register a step by name."""
        self._steps[step.name] = step

    def run(self, context: dict[str, Any] | None = None) -> WorkflowResult:
        """Execute all registered steps."""
        ctx = context or {}
        start = time.time()
        result = WorkflowResult(steps=list(self._steps.values()))

        for step_name in self._topological_order():
            step = self._steps[step_name]
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
        result.success = (
            result.completed_count > 0
            and result.failed_count == 0
            and all(
                step.status in (StepStatus.COMPLETED, StepStatus.SKIPPED)
                for step in self._steps.values()
            )
        )
        return result

    def _topological_order(self) -> list[str]:
        ordered: list[str] = []
        temporary: set[str] = set()
        permanent: set[str] = set()

        def visit(name: str) -> None:
            if name in permanent:
                return
            if name in temporary:
                msg = f"Cycle detected at workflow step {name!r}"
                raise ValueError(msg)
            temporary.add(name)
            for dep in self._steps[name].depends_on:
                if dep in self._steps:
                    visit(dep)
            temporary.remove(name)
            permanent.add(name)
            ordered.append(name)

        for step_name in self._steps:
            visit(step_name)
        return ordered


__all__ = ["StepStatus", "WorkflowResult", "WorkflowRunner", "WorkflowStep"]
