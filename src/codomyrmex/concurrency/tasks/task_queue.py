"""Distributed task queue with priority and deduplication.

Priority queue supporting task deduplication, deadline-based
ordering, dead-letter handling, and at-least-once delivery.
"""

from __future__ import annotations

import heapq
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TaskPriority(Enum):
    """Task priority levels (lower value = higher priority)."""

    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4


class TaskStatus(Enum):
    """Task lifecycle status."""

    PENDING = "pending"
    IN_FLIGHT = "in_flight"
    COMPLETED = "completed"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"


@dataclass(order=True)
class QueueEntry:
    """Internal priority queue entry.

    Sorted by (priority, deadline, sequence).
    """

    priority: int
    deadline: float
    sequence: int
    task: Task = field(compare=False)


@dataclass
class Task:
    """A distributable task.

    Attributes:
        task_id: Unique task identifier.
        task_type: Task type for routing.
        payload: Task data.
        priority: Execution priority.
        deadline: Deadline timestamp (0 = no deadline).
        max_retries: Maximum retry attempts.
        retry_count: Current retry count.
        status: Current status.
        created_at: Creation timestamp.
    """

    task_id: str = ""
    task_type: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    deadline: float = 0.0
    max_retries: int = 3
    retry_count: int = 0
    status: TaskStatus = TaskStatus.PENDING
    created_at: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        if not self.task_id:
            self.task_id = f"task-{uuid.uuid4().hex[:10]}"


class TaskQueue:
    """Priority queue with deduplication and dead-letter support.

    Example::

        queue = TaskQueue()
        queue.enqueue(Task(task_type="analyze", priority=TaskPriority.HIGH))
        task = queue.dequeue()
        queue.ack(task.task_id)
    """

    def __init__(self, max_retries: int = 3) -> None:
        self._heap: list[QueueEntry] = []
        self._sequence = 0
        self._in_flight: dict[str, Task] = {}
        self._dead_letters: list[Task] = []
        self._seen_ids: set[str] = set()
        self._max_retries = max_retries

    @property
    def pending_count(self) -> int:
        """Number of tasks waiting in the queue."""
        return len(self._heap)

    @property
    def in_flight_count(self) -> int:
        """Number of tasks currently being processed."""
        return len(self._in_flight)

    @property
    def dead_letter_count(self) -> int:
        """Number of tasks in the dead-letter queue."""
        return len(self._dead_letters)

    def enqueue(self, task: Task) -> bool:
        """Add a task to the queue.

        Deduplicates by task_id. Returns False if already seen.

        Args:
            task: Task to enqueue.

        Returns:
            True if enqueued, False if duplicate.
        """
        if task.task_id in self._seen_ids:
            return False

        self._seen_ids.add(task.task_id)
        task.status = TaskStatus.PENDING
        entry = QueueEntry(
            priority=task.priority.value,
            deadline=task.deadline if task.deadline > 0 else float("inf"),
            sequence=self._sequence,
            task=task,
        )
        self._sequence += 1
        heapq.heappush(self._heap, entry)
        return True

    def dequeue(self) -> Task | None:
        """Pull the highest-priority task.

        Returns:
            Next task, or None if queue is empty.
        """
        while self._heap:
            entry = heapq.heappop(self._heap)
            task = entry.task

            # Skip expired tasks
            if task.deadline > 0 and time.time() > task.deadline:
                task.status = TaskStatus.DEAD_LETTER
                self._dead_letters.append(task)
                continue

            task.status = TaskStatus.IN_FLIGHT
            self._in_flight[task.task_id] = task
            return task

        return None

    def ack(self, task_id: str) -> bool:
        """Acknowledge successful processing.

        Args:
            task_id: ID of the completed task.

        Returns:
            True if acknowledged.
        """
        task = self._in_flight.pop(task_id, None)
        if task is not None:
            task.status = TaskStatus.COMPLETED
            return True
        return False

    def nack(self, task_id: str) -> bool:
        """Negative-acknowledge: retry or dead-letter.

        Args:
            task_id: ID of the failed task.

        Returns:
            True if requeued, False if dead-lettered.
        """
        task = self._in_flight.pop(task_id, None)
        if task is None:
            return False

        task.retry_count += 1
        if task.retry_count >= task.max_retries:
            task.status = TaskStatus.DEAD_LETTER
            self._dead_letters.append(task)
            return False

        # Requeue with same priority
        task.status = TaskStatus.PENDING
        self._seen_ids.discard(task.task_id)
        self.enqueue(task)
        return True

    def requeue_dead_letters(self) -> int:
        """Move dead-letter tasks back to the main queue.

        Returns:
            Number of tasks requeued.
        """
        count = 0
        for task in self._dead_letters:
            task.retry_count = 0
            task.status = TaskStatus.PENDING
            self._seen_ids.discard(task.task_id)
            if self.enqueue(task):
                count += 1
        self._dead_letters.clear()
        return count


__all__ = ["Task", "TaskPriority", "TaskQueue", "TaskStatus"]
