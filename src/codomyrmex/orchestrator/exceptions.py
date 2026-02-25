"""Orchestrator Exception Classes.

This module defines exceptions specific to orchestration operations
including workflows, steps, timeouts, and state management.
All exceptions inherit from CodomyrmexError for consistent error handling.

Note: Some base exceptions (WorkflowError, CycleError, TaskFailedError) are
defined in workflow.py and are re-exported here.
"""

from typing import Any

from codomyrmex.exceptions import OrchestrationError

# Re-export workflow exceptions for centralized access
from .workflows.workflow import CycleError, TaskFailedError, WorkflowError


class StepError(OrchestrationError):
    """Raised when a workflow step fails.

    This includes step execution errors, step validation failures,
    and step dependency issues.
    """

    def __init__(
        self,
        message: str,
        step_name: str | None = None,
        step_index: int | None = None,
        workflow_name: str | None = None,
        **kwargs: Any
    ):
        """Initialize StepError.

        Args:
            message: Error description
            step_name: Name of the failed step
            step_index: Index of the step in the workflow
            workflow_name: Name of the workflow containing the step
            **kwargs: Additional context passed to parent
        """
        super().__init__(message, **kwargs)
        if step_name:
            self.context["step_name"] = step_name
        if step_index is not None:
            self.context["step_index"] = step_index
        if workflow_name:
            self.context["workflow_name"] = workflow_name


class OrchestratorTimeoutError(OrchestrationError):
    """Raised when orchestration operations timeout.

    This includes workflow-level timeouts, step timeouts,
    and resource wait timeouts.

    Note: Named OrchestratorTimeoutError to avoid shadowing
    the built-in TimeoutError and the base TimeoutError from exceptions.
    """

    def __init__(
        self,
        message: str,
        timeout_seconds: float | None = None,
        operation: str | None = None,
        **kwargs: Any
    ):
        """Initialize OrchestratorTimeoutError.

        Args:
            message: Error description
            timeout_seconds: The timeout value that was exceeded
            operation: The operation that timed out
            **kwargs: Additional context passed to parent
        """
        super().__init__(message, **kwargs)
        if timeout_seconds is not None:
            self.context["timeout_seconds"] = timeout_seconds
        if operation:
            self.context["operation"] = operation


class StateError(OrchestrationError):
    """Raised when workflow state operations fail.

    This includes state persistence errors, state transitions,
    and state validation failures.
    """

    def __init__(
        self,
        message: str,
        current_state: str | None = None,
        expected_state: str | None = None,
        workflow_id: str | None = None,
        **kwargs: Any
    ):
        """Initialize StateError.

        Args:
            message: Error description
            current_state: The current state of the workflow
            expected_state: The expected state for the operation
            workflow_id: ID of the workflow with state error
            **kwargs: Additional context passed to parent
        """
        super().__init__(message, **kwargs)
        if current_state:
            self.context["current_state"] = current_state
        if expected_state:
            self.context["expected_state"] = expected_state
        if workflow_id:
            self.context["workflow_id"] = workflow_id


class DependencyResolutionError(OrchestrationError):
    """Raised when task dependencies cannot be resolved."""

    def __init__(
        self,
        message: str,
        task_name: str | None = None,
        missing_dependencies: list[str] | None = None,
        **kwargs: Any
    ):
        """Initialize DependencyResolutionError.

        Args:
            message: Error description
            task_name: Name of the task with unresolved dependencies
            missing_dependencies: List of missing dependency names
            **kwargs: Additional context passed to parent
        """
        super().__init__(message, **kwargs)
        if task_name:
            self.context["task_name"] = task_name
        if missing_dependencies:
            self.context["missing_dependencies"] = missing_dependencies


class ConcurrencyError(OrchestrationError):
    """Raised when concurrency-related issues occur.

    This includes resource contention, deadlocks,
    and parallel execution failures.
    """

    def __init__(
        self,
        message: str,
        resource_name: str | None = None,
        max_workers: int | None = None,
        **kwargs: Any
    ):
        """Initialize ConcurrencyError.

        Args:
            message: Error description
            resource_name: Name of the contested resource
            max_workers: Maximum number of workers configured
            **kwargs: Additional context passed to parent
        """
        super().__init__(message, **kwargs)
        if resource_name:
            self.context["resource_name"] = resource_name
        if max_workers is not None:
            self.context["max_workers"] = max_workers




__all__ = [
    # Re-exported from workflow.py
    "WorkflowError",
    "CycleError",
    "TaskFailedError",
    # Defined in this module
    "StepError",
    "OrchestratorTimeoutError",
    "StateError",
    "DependencyResolutionError",
    "ConcurrencyError",
]
