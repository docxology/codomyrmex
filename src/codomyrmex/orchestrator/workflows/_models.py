"""Workflow dataclasses, enums, and exceptions."""

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class TaskStatus(Enum):
    """Task execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"


@dataclass
class RetryPolicy:
    """Retry configuration for tasks."""

    max_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    retry_on: tuple = (Exception,)

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for attempt using exponential backoff."""
        delay = self.initial_delay * (self.exponential_base ** (attempt - 1))
        return min(delay, self.max_delay)


@dataclass
class TaskResult:
    """Result of a task execution."""

    success: bool
    value: Any = None
    error: str | None = None
    execution_time: float = 0.0
    attempts: int = 1


@dataclass
class Task:
    """Represents a single unit of work in a workflow."""

    name: str
    action: Callable[..., Any]
    args: list[Any] = field(default_factory=list)
    kwargs: dict[str, Any] = field(default_factory=dict)
    dependencies: set[str] = field(default_factory=set)
    timeout: float | None = None
    retry_policy: RetryPolicy | None = None
    condition: Callable[[dict[str, TaskResult]], bool] | None = None
    transform_result: Callable[[Any], Any] | None = None
    tags: set[str] = field(default_factory=set)
    metadata: dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Exception | None = None
    attempts: int = 0
    execution_time: float = 0.0

    def __hash__(self):
        """Return the hash value."""
        return hash(self.name)

    def should_run(self, results: dict[str, TaskResult]) -> bool:
        """Check if task should run based on condition."""
        if self.condition is None:
            return True
        try:
            return self.condition(results)
        except Exception as e:
            logger.warning("Condition check failed for %s: %s", self.name, e)
            return False

    def get_result(self) -> TaskResult:
        """Get task result as TaskResult object."""
        return TaskResult(
            success=self.status == TaskStatus.COMPLETED,
            value=self.result,
            error=str(self.error) if self.error else None,
            execution_time=self.execution_time,
            attempts=self.attempts,
        )


class WorkflowError(Exception):
    """Base exception for workflow errors."""


class CycleError(WorkflowError):
    """Raised when a circular dependency is detected."""


class TaskFailedError(WorkflowError):
    """Raised when a required task fails."""


ProgressCallback = Callable[[str, str, dict[str, Any]], None]
