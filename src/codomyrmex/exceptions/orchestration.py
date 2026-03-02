"""Orchestration and Project Management Exceptions.

Errors related to orchestration, workflows, and task execution.
"""

from __future__ import annotations

from typing import Any

from .base import CodomyrmexError


class OrchestrationError(CodomyrmexError):
    """Raised when orchestration operations fail."""

    def __init__(
        self,
        message: str,
        orchestrator_id: str | None = None,
        strategy: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if orchestrator_id:
            self.context["orchestrator_id"] = orchestrator_id
        if strategy:
            self.context["strategy"] = strategy


class WorkflowError(CodomyrmexError):
    """Raised when workflow execution fails."""

    def __init__(
        self,
        message: str,
        workflow_name: str | None = None,
        step_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if workflow_name:
            self.context["workflow_name"] = workflow_name
        if step_name:
            self.context["step_name"] = step_name


class ProjectManagementError(CodomyrmexError):
    """Raised when project management operations fail."""

    def __init__(
        self,
        message: str,
        project_name: str | None = None,
        operation: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if project_name:
            self.context["project_name"] = project_name
        if operation:
            self.context["operation"] = operation


class TaskExecutionError(CodomyrmexError):
    """Raised when task execution fails."""

    def __init__(
        self,
        message: str,
        task_id: str | None = None,
        executor: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if task_id:
            self.context["task_id"] = task_id
        if executor:
            self.context["executor"] = executor
