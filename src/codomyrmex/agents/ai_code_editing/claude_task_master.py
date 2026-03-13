"""Claude Task Master Integration Module.

This module provides integration with Anthropic's Claude API for
advanced AI-powered task orchestration, code generation, and
task decomposition capabilities.

Features:
- Task execution with automatic retry logic
- Task decomposition into subtasks
- Task analysis for complexity and requirements
- Workflow planning with constraints
- Cost estimation and tracking
- Streaming support for long-running tasks

Reference: https://docs.anthropic.com/claude/docs
"""

import os
import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from anthropic import Anthropic

from codomyrmex.logging_monitoring import get_logger

from ._execution import ClaudeTaskExecutionMixin
from ._planning import ClaudeTaskPlanningMixin

logger = get_logger(__name__)

# Default configuration - using latest models
DEFAULT_MODEL = "claude-sonnet-4-20250514"
DEFAULT_TEMPERATURE = 0.3
MAX_TOKENS = 4096

# Cost per 1M tokens (update as pricing changes)
TASK_MASTER_PRICING = {
    "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
    "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
    "claude-3-5-haiku-20241022": {"input": 1.00, "output": 5.00},
    "claude-3-opus-20240229": {"input": 15.00, "output": 75.00},
    "claude-opus-4-5-20251101": {"input": 15.00, "output": 75.00},
}


class TaskPriority(Enum):
    """Task priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(Enum):
    """Task execution status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Task definition for Claude Task Master."""

    description: str
    priority: TaskPriority = TaskPriority.MEDIUM
    context: str | None = None
    dependencies: list[str] = field(default_factory=list)
    timeout: float | None = None
    tags: list[str] = field(default_factory=list)


@dataclass
class TaskResult:
    """Result of task execution."""

    task_id: str
    status: TaskStatus
    result: Any
    execution_time: float
    tokens_used: int
    cost_usd: float = 0.0
    error: str | None = None
    retries: int = 0


class ClaudeTaskMaster(ClaudeTaskExecutionMixin, ClaudeTaskPlanningMixin):
    """Claude Task Master for AI-powered task orchestration.

    A comprehensive task orchestration system that uses Claude for:
    - Executing complex tasks with automatic retries
    - Decomposing tasks into manageable subtasks
    - Analyzing task requirements and complexity
    - Planning multi-step workflows

    Example:
        ```python
        master = ClaudeTaskMaster()

        # Execute a task
        result = master.execute_task(
            "Generate a Python function for binary search",
            context="The function should work with sorted lists",
        )

        # Decompose a complex task
        subtasks = master.decompose_task("Build a REST API for user management")
        ```
    """

    # Retry configuration
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_INITIAL_DELAY = 1.0
    DEFAULT_BACKOFF_FACTOR = 2.0

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ):
        """Initialize Claude Task Master integration.

        Args:
            api_key: Anthropic API key (uses ANTHROPIC_API_KEY env var if not provided)
            model: Model to use (defaults to claude-sonnet-4-20250514)
            max_retries: Maximum retry attempts for failed requests

        Raises:
            ValueError: If no API key is available
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.model = model or DEFAULT_MODEL
        self.max_retries = max_retries
        self._client: Anthropic | None = None
        self._task_counter = 0
        self._total_cost = 0.0
        self._total_tokens = 0

        if not self.api_key:
            logger.warning(
                "ANTHROPIC_API_KEY not set - Task Master operations will fail"
            )

    def _get_client(self) -> Anthropic:
        """Lazily initialize Anthropic client."""
        if self._client is None:
            if not self.api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable not set")

            try:
                self._client = Anthropic(api_key=self.api_key)
            except ImportError as e:
                raise ImportError(
                    "Anthropic package not installed. Install with: pip install anthropic"
                ) from e
        return self._client

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost in USD based on token usage."""
        pricing = TASK_MASTER_PRICING.get(self.model, {"input": 3.00, "output": 15.00})
        cost = (input_tokens / 1_000_000 * pricing["input"]) + (
            output_tokens / 1_000_000 * pricing["output"]
        )
        return round(cost, 6)

    def _execute_with_retry(
        self,
        messages: list[dict],
        system: str,
        max_tokens: int = MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
        **kwargs: Any,
    ) -> tuple[Any, int]:
        """Execute API call with retry logic.

        Args:
            messages: Messages to send
            system: System prompt
            max_tokens: Maximum output tokens
            temperature: Sampling temperature
            **kwargs: Additional API arguments

        Returns:
            Tuple of (response, retry_count)
        """
        client = self._get_client()

        for attempt in range(self.max_retries + 1):
            try:
                response = client.messages.create(  # type: ignore
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system,
                    messages=messages,
                    **kwargs,
                )
                return response, attempt
            except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
                error_str = str(e).lower()
                is_retryable = (
                    "rate_limit" in error_str
                    or "overloaded" in error_str
                    or "503" in error_str
                    or "529" in error_str
                    or "timeout" in error_str
                )

                if not is_retryable or attempt >= self.max_retries:
                    raise

                delay = self.DEFAULT_INITIAL_DELAY * (
                    self.DEFAULT_BACKOFF_FACTOR**attempt
                )
                delay *= 0.75 + random.random() * 0.5  # Add jitter

                logger.warning(
                    "Retryable error, attempt %s/%s, retrying in %.1fs: %s",
                    attempt + 1,
                    self.max_retries + 1,
                    delay,
                    e,
                )
                time.sleep(delay)

        raise RuntimeError("Max retries exceeded")

    def get_usage_stats(self) -> dict[str, Any]:
        """Get cumulative usage statistics.

        Returns:
            Dictionary with total tokens, cost, and task count
        """
        return {
            "total_tasks": self._task_counter,
            "total_tokens": self._total_tokens,
            "total_cost_usd": round(self._total_cost, 6),
            "model": self.model,
        }

    def reset_usage_stats(self) -> None:
        """Reset cumulative usage statistics."""
        self._task_counter = 0
        self._total_tokens = 0
        self._total_cost = 0.0

    def is_available(self) -> bool:
        """Check if Claude Task Master is available and configured."""
        if not self.api_key:
            return False

        try:
            self._get_client()
            return True
        except (ImportError, ValueError) as e:
            logger.warning("Claude Task Master unavailable: %s", e)
            return False


# Module-level convenience functions


def execute_task(task: str, **kwargs: Any) -> dict[str, Any]:
    """Execute a task using Claude (module-level convenience function)."""
    master = ClaudeTaskMaster()
    return master.execute_task(task, **kwargs)


def decompose_task(task: str, **kwargs: Any) -> dict[str, Any]:
    """Decompose a task into subtasks."""
    master = ClaudeTaskMaster()
    return master.decompose_task(task, **kwargs)


def analyze_task(task: str, **kwargs: Any) -> dict[str, Any]:
    """Analyze a task."""
    master = ClaudeTaskMaster()
    return master.analyze_task(task, **kwargs)


def plan_workflow(goal: str, **kwargs: Any) -> dict[str, Any]:
    """Create a workflow plan."""
    master = ClaudeTaskMaster()
    return master.plan_workflow(goal, **kwargs)


def generate_code(
    description: str, language: str = "python", **kwargs: Any
) -> dict[str, Any]:
    """Generate code from description."""
    master = ClaudeTaskMaster()
    return master.generate_code(description, language, **kwargs)
