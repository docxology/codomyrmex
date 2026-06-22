"""Structural workflow result protocols for planner scoring."""

from __future__ import annotations

from typing import Any, Protocol


class WorkflowStepLike(Protocol):
    """Step object accepted by ``PlanEvaluator``."""

    status: Any


class WorkflowResultLike(Protocol):
    """Workflow result object accepted by planner scoring."""

    steps: list[WorkflowStepLike]
    total_duration_ms: float
    completed_count: int
    failed_count: int


__all__ = ["WorkflowResultLike", "WorkflowStepLike"]
