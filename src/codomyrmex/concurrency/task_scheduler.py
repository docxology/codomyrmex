"""Task scheduler with strategy-based routing.

Assigns tasks to workers using configurable strategies:
round-robin, least-loaded, and affinity-based routing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from codomyrmex.concurrency.task_queue import Task
from codomyrmex.concurrency.task_worker import TaskWorker


class SchedulingStrategy(Enum):
    """Task assignment strategy."""

    ROUND_ROBIN = "round_robin"
    LEAST_LOADED = "least_loaded"
    AFFINITY = "affinity"


@dataclass
class WorkerInfo:
    """Metadata about a registered worker.

    Attributes:
        worker_id: Worker identifier.
        capabilities: Task types this worker can handle.
        max_concurrent: Maximum concurrent tasks.
        current_load: Tasks currently assigned.
    """

    worker_id: str
    capabilities: list[str] = field(default_factory=list)
    max_concurrent: int = 10
    current_load: int = 0


class TaskScheduler:
    """Assign tasks to workers using configurable strategies.

    Example::

        scheduler = TaskScheduler(strategy=SchedulingStrategy.LEAST_LOADED)
        scheduler.register_worker("w-1", capabilities=["analyze"])
        worker_id = scheduler.assign(task)
    """

    def __init__(self, strategy: SchedulingStrategy = SchedulingStrategy.ROUND_ROBIN) -> None:
        """Execute   Init   operations natively."""
        self._strategy = strategy
        self._workers: dict[str, WorkerInfo] = {}
        self._round_robin_index = 0
        self._affinity_map: dict[str, str] = {}  # task_type → worker_id

    @property
    def worker_count(self) -> int:
        """Execute Worker Count operations natively."""
        return len(self._workers)

    @property
    def strategy(self) -> SchedulingStrategy:
        """Execute Strategy operations natively."""
        return self._strategy

    def register_worker(
        self,
        worker_id: str,
        capabilities: list[str] | None = None,
        max_concurrent: int = 10,
    ) -> None:
        """Register a worker with the scheduler.

        Args:
            worker_id: Worker identifier.
            capabilities: Task types this worker handles.
            max_concurrent: Max concurrent tasks.
        """
        self._workers[worker_id] = WorkerInfo(
            worker_id=worker_id,
            capabilities=capabilities or [],
            max_concurrent=max_concurrent,
        )

    def unregister_worker(self, worker_id: str) -> bool:
        """Remove a worker. Returns True if found."""
        return self._workers.pop(worker_id, None) is not None

    def set_affinity(self, task_type: str, worker_id: str) -> None:
        """Set affinity: route task_type to preferred worker.

        Args:
            task_type: Task type to route.
            worker_id: Preferred worker.
        """
        self._affinity_map[task_type] = worker_id

    def assign(self, task: Task) -> str:
        """Assign a task to a worker.

        Args:
            task: The task to assign.

        Returns:
            Worker ID, or empty string if no worker available.
        """
        if not self._workers:
            return ""

        eligible = self._eligible_workers(task)
        if not eligible:
            return ""

        if self._strategy == SchedulingStrategy.ROUND_ROBIN:
            return self._round_robin(eligible)
        elif self._strategy == SchedulingStrategy.LEAST_LOADED:
            return self._least_loaded(eligible)
        elif self._strategy == SchedulingStrategy.AFFINITY:
            return self._affinity(task, eligible)

        return eligible[0].worker_id

    def report_completion(self, worker_id: str) -> None:
        """Report that a worker completed a task.

        Args:
            worker_id: Worker that completed.
        """
        info = self._workers.get(worker_id)
        if info and info.current_load > 0:
            info.current_load -= 1

    def rebalance(self) -> list[tuple[str, str]]:
        """Redistribute load across workers.

        Returns:
            List of (from_worker, to_worker) reassignment suggestions.
        """
        if len(self._workers) < 2:
            return []

        workers = sorted(self._workers.values(), key=lambda w: w.current_load)
        suggestions: list[tuple[str, str]] = []

        lightest = workers[0]
        heaviest = workers[-1]
        if heaviest.current_load - lightest.current_load > 1:
            suggestions.append((heaviest.worker_id, lightest.worker_id))

        return suggestions

    def _eligible_workers(self, task: Task) -> list[WorkerInfo]:
        """Find workers that can handle a task."""
        eligible = []
        for w in self._workers.values():
            if w.current_load >= w.max_concurrent:
                continue
            if w.capabilities and task.task_type and task.task_type not in w.capabilities:
                continue
            eligible.append(w)
        return eligible

    def _round_robin(self, workers: list[WorkerInfo]) -> str:
        """Execute  Round Robin operations natively."""
        idx = self._round_robin_index % len(workers)
        self._round_robin_index += 1
        selected = workers[idx]
        selected.current_load += 1
        return selected.worker_id

    def _least_loaded(self, workers: list[WorkerInfo]) -> str:
        """Execute  Least Loaded operations natively."""
        selected = min(workers, key=lambda w: w.current_load)
        selected.current_load += 1
        return selected.worker_id

    def _affinity(self, task: Task, workers: list[WorkerInfo]) -> str:
        """Execute  Affinity operations natively."""
        preferred = self._affinity_map.get(task.task_type)
        if preferred:
            for w in workers:
                if w.worker_id == preferred:
                    w.current_load += 1
                    return w.worker_id
        # Fallback to least-loaded
        return self._least_loaded(workers)


__all__ = ["SchedulingStrategy", "TaskScheduler", "WorkerInfo"]
