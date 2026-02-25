"""
Supervisor agent for orchestrating worker agents.

Provides delegation, result aggregation, and worker coordination
for complex multi-step workflows.
"""

import asyncio
import logging
from collections.abc import Callable
from typing import Any

from ..exceptions import (
    CapabilityMismatchError,
    TaskDependencyError,
    TaskExecutionError,
)
from ..models import Task, TaskResult
from ..protocols import AgentCapability, AgentState
from .base import CollaborativeAgent
from .worker import WorkerAgent

logger = logging.getLogger(__name__)


class SupervisorAgent(CollaborativeAgent):
    """
    A supervisor agent that delegates tasks to worker agents.

    Supervisors manage a pool of workers, delegate tasks based on
    capabilities, aggregate results, and handle failures with retry logic.

    Attributes:
        workers: List of managed worker agents.
        delegation_strategy: Strategy for selecting workers ("round_robin", "capability", "least_busy").
        max_retries: Maximum retries for failed tasks.
    """

    def __init__(
        self,
        agent_id: str | None = None,
        name: str = "Supervisor",
        delegation_strategy: str = "capability",
        max_retries: int = 3,
    ):
        """Execute   Init   operations natively."""
        super().__init__(
            agent_id,
            name,
            [AgentCapability(name="supervision", description="Supervise and delegate tasks")]
        )
        self._workers: dict[str, WorkerAgent] = {}
        self._delegation_strategy = delegation_strategy
        self._max_retries = max_retries
        self._round_robin_index = 0
        self._delegated_tasks: dict[str, str] = {}  # task_id -> worker_id

    def add_worker(self, worker: WorkerAgent) -> None:
        """Add a worker to the supervision pool."""
        self._workers[worker.agent_id] = worker
        logger.info(f"Supervisor {self.name} added worker: {worker.name}")

    def remove_worker(self, worker_id: str) -> bool:
        """Remove a worker from the supervision pool."""
        if worker_id in self._workers:
            del self._workers[worker_id]
            logger.info(f"Supervisor {self.name} removed worker: {worker_id}")
            return True
        return False

    def get_workers(self) -> list[WorkerAgent]:
        """Get all managed workers."""
        return list(self._workers.values())

    def get_idle_workers(self) -> list[WorkerAgent]:
        """Get all workers currently in idle state."""
        return [w for w in self._workers.values() if w.state == AgentState.IDLE]

    def find_capable_workers(self, task: Task) -> list[WorkerAgent]:
        """Find workers that can handle a specific task."""
        return [w for w in self._workers.values() if w.can_handle_task(task)]

    def _select_worker(self, task: Task) -> WorkerAgent:
        """
        Select a worker for a task based on delegation strategy.

        Raises:
            CapabilityMismatchError: If no worker can handle the task.
        """
        capable_workers = self.find_capable_workers(task)

        if not capable_workers:
            raise CapabilityMismatchError(
                task.required_capabilities,
                [cap for w in self._workers.values() for cap in w.get_capabilities()]
            )

        if self._delegation_strategy == "round_robin":
            worker = capable_workers[self._round_robin_index % len(capable_workers)]
            self._round_robin_index += 1
            return worker

        elif self._delegation_strategy == "least_busy":
            # Prefer idle workers
            idle_workers = [w for w in capable_workers if w.state == AgentState.IDLE]
            if idle_workers:
                return idle_workers[0]
            return capable_workers[0]

        else:  # capability (default)
            # Select worker with most matching capabilities
            best_worker = max(
                capable_workers,
                key=lambda w: len(set(w.get_capabilities()) & set(task.required_capabilities))
            )
            return best_worker

    async def delegate(self, task: Task) -> TaskResult:
        """
        Delegate a task to an appropriate worker.

        Selects a worker based on the delegation strategy and
        monitors task execution.
        """
        worker = self._select_worker(task)
        self._delegated_tasks[task.id] = worker.agent_id

        logger.info(f"Supervisor {self.name} delegating '{task.name}' to {worker.name}")

        for attempt in range(self._max_retries):
            try:
                result = await worker.process_task(task)
                if result.success:
                    return result

                if attempt < self._max_retries - 1:
                    logger.warning(
                        f"Task {task.id} failed (attempt {attempt + 1}), retrying..."
                    )
            except Exception as e:
                if attempt < self._max_retries - 1:
                    logger.warning(f"Task {task.id} error: {e}, retrying...")
                else:
                    raise TaskExecutionError(task.id, str(e), worker.agent_id)

        return TaskResult(
            task_id=task.id,
            success=False,
            error=f"Failed after {self._max_retries} attempts",
            agent_id=worker.agent_id,
        )

    async def delegate_batch(
        self,
        tasks: list[Task],
        parallel: bool = True,
    ) -> list[TaskResult]:
        """
        Delegate a batch of tasks to workers.

        Args:
            tasks: List of tasks to delegate.
            parallel: Whether to execute tasks in parallel.

        Returns:
            List of task results.
        """
        if parallel:
            results = await asyncio.gather(
                *[self.delegate(task) for task in tasks],
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
        else:
            return [await self.delegate(task) for task in tasks]

    async def execute_workflow(
        self,
        tasks: list[Task],
        on_progress: Callable[[Task, TaskResult], None] | None = None,
    ) -> dict[str, TaskResult]:
        """
        Execute a workflow with task dependencies.

        Tasks are executed in order respecting dependencies.
        Each task waits for its dependencies to complete.

        Args:
            tasks: List of tasks with dependencies.
            on_progress: Optional callback for progress updates.

        Returns:
            Dictionary mapping task IDs to results.
        """
        results: dict[str, TaskResult] = {}
        completed_ids: list[str] = []
        pending = list(tasks)

        while pending:
            # Find tasks ready to execute
            ready = [t for t in pending if t.is_ready(completed_ids)]

            if not ready:
                # Check for circular dependencies
                raise TaskDependencyError(
                    pending[0].id,
                    [d for d in pending[0].dependencies if d not in completed_ids]
                )

            # Execute ready tasks in parallel
            batch_results = await self.delegate_batch(ready)

            for task, result in zip(ready, batch_results):
                results[task.id] = result
                completed_ids.append(task.id)
                pending.remove(task)

                if on_progress:
                    on_progress(task, result)

        return results

    async def _execute_task(self, task: Task) -> Any:
        """Supervisors delegate tasks rather than executing directly."""
        result = await self.delegate(task)
        return result.output


__all__ = [
    "SupervisorAgent",
]
