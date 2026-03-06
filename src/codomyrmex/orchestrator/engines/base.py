"""Abstract ExecutionEngine base class."""

from abc import ABC, abstractmethod
from typing import Any

from .models import WorkflowDefinition, WorkflowResult


class ExecutionEngine(ABC):
    """Abstract base class for workflow execution engines."""

    @abstractmethod
    def execute(
        self,
        workflow: WorkflowDefinition,
        initial_context: dict[str, Any] | None = None,
    ) -> WorkflowResult:
        """Execute a workflow synchronously."""

    @abstractmethod
    async def execute_async(
        self,
        workflow: WorkflowDefinition,
        initial_context: dict[str, Any] | None = None,
    ) -> WorkflowResult:
        """Execute a workflow asynchronously."""
