"""
Worker agent implementation for task execution.

Provides a concrete agent implementation for executing tasks
with capability-based routing and configurable execution handlers.
"""

import asyncio
import logging
from collections.abc import Callable
from typing import Any

from ..exceptions import CapabilityMismatchError
from ..models import Task, TaskResult
from ..protocols import AgentCapability
from .base import CollaborativeAgent

logger = logging.getLogger(__name__)


class WorkerAgent(CollaborativeAgent):
    """
    A worker agent that executes tasks based on capabilities.

    Worker agents are the primary workhorses of a swarm. They register
    capabilities and execute tasks that match those capabilities.

    Attributes:
        task_handlers: Mapping of capability names to handler functions.
        max_concurrent_tasks: Maximum number of tasks to process concurrently.
    """

    def __init__(
        self,
        agent_id: str | None = None,
        name: str = "Worker",
        capabilities: list[AgentCapability] | None = None,
        max_concurrent_tasks: int = 1,
    ):
        """Initialize this instance."""
        super().__init__(agent_id, name, capabilities)
        self._task_handlers: dict[str, Callable[[Task], Any]] = {}
        self._max_concurrent_tasks = max_concurrent_tasks
        self._active_tasks: dict[str, asyncio.Task] = {}

    def register_handler(
        self,
        capability_name: str,
        handler: Callable[[Task], Any],
        description: str = "",
    ) -> None:
        """
        Register a handler for a capability.

        Args:
            capability_name: Name of the capability this handler provides.
            handler: Async or sync function that processes tasks.
            description: Human-readable description of the capability.
        """
        self._task_handlers[capability_name] = handler

        # Add capability if not already present
        if not self.has_capability(capability_name):
            self.add_capability(AgentCapability(
                name=capability_name,
                description=description,
            ))

        logger.info(f"Worker {self.name} registered handler for: {capability_name}")

    def can_handle_task(self, task: Task) -> bool:
        """Check if this worker can handle a task."""
        if not task.required_capabilities:
            return True
        return all(self.has_capability(cap) for cap in task.required_capabilities)

    async def _execute_task(self, task: Task) -> Any:
        """
        Execute a task using registered handlers.

        Finds the appropriate handler based on task capabilities
        and executes it.
        """
        # Find a matching handler
        handler = None
        for cap in task.required_capabilities:
            if cap in self._task_handlers:
                handler = self._task_handlers[cap]
                break

        # Fall back to default handler if no capability-specific one
        if handler is None:
            handler = self._task_handlers.get("default")

        if handler is None:
            raise CapabilityMismatchError(
                task.required_capabilities,
                self.get_capabilities()
            )

        # Execute the handler
        logger.info(f"Worker {self.name} executing task: {task.name}")

        if asyncio.iscoroutinefunction(handler):
            result = await handler(task)
        else:
            result = handler(task)

        logger.info(f"Worker {self.name} completed task: {task.name}")
        return result

    async def execute_batch(self, tasks: list[Task]) -> list[TaskResult]:
        """
        Execute a batch of tasks, respecting concurrency limits.

        Args:
            tasks: List of tasks to execute.

        Returns:
            List of task results in the same order as input tasks.
        """
        semaphore = asyncio.Semaphore(self._max_concurrent_tasks)

        async def execute_with_semaphore(task: Task) -> TaskResult:
            async with semaphore:
                return await self.process_task(task)

        results = await asyncio.gather(
            *[execute_with_semaphore(task) for task in tasks],
            return_exceptions=True
        )

        # Convert exceptions to TaskResults
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append(TaskResult(
                    task_id=tasks[i].id,
                    success=False,
                    error=str(result),
                    agent_id=self._agent_id,
                ))
            else:
                final_results.append(result)

        return final_results


class SpecializedWorker(WorkerAgent):
    """
    A worker specialized for a single capability.

    This is a convenience class for workers that only perform
    one type of task.
    """

    def __init__(
        self,
        capability_name: str,
        handler: Callable[[Task], Any],
        agent_id: str | None = None,
        name: str | None = None,
        description: str = "",
    ):
        """Initialize this instance."""
        name = name or f"{capability_name.title()}Worker"
        super().__init__(agent_id, name)
        self.register_handler(capability_name, handler, description)


__all__ = [
    "WorkerAgent",
    "SpecializedWorker",
]
