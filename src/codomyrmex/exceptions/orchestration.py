from __future__ import annotations
"""
Orchestration and Project Management Exceptions

Errors related to orchestration, workflows, and task execution.
"""

from .base import CodomyrmexError


class OrchestrationError(CodomyrmexError):
    """Raised when orchestration operations fail."""
    pass


class WorkflowError(CodomyrmexError):
    """Raised when workflow execution fails."""
    pass


class ProjectManagementError(CodomyrmexError):
    """Raised when project management operations fail."""
    pass


class TaskExecutionError(CodomyrmexError):
    """Raised when task execution fails."""
    pass
