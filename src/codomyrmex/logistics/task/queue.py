"""
Queue implementation for task management.
"""

import heapq
import time
from datetime import datetime
from typing import Optional

from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring.logger_config import get_logger

from .backends.in_memory_queue import InMemoryQueue
from .job import Job, JobStatus

logger = get_logger(__name__)


class QueueError(CodomyrmexError):
    """Raised when queue operations fail."""

    pass


class Queue:
    """Queue for task management."""

    def __init__(self, backend: str = "in_memory"):
        """Initialize queue.

        Args:
            backend: Queue backend (in_memory, redis)
        """
        self.backend = backend
        if backend == "in_memory":
            self._queue = InMemoryQueue()
        elif backend == "redis":
            try:
                from .backends.redis_queue import RedisQueue
                self._queue = RedisQueue()
            except ImportError:
                logger.warning("Redis not available, falling back to in-memory queue")
                self._queue = InMemoryQueue()
        else:
            logger.warning(f"Unknown backend {backend}, using in-memory queue")
            self._queue = InMemoryQueue()

    def enqueue(self, job: Job, priority: int = 0) -> str:
        """Add a job to the queue.

        Args:
            job: Job to enqueue
            priority: Job priority (higher = more priority)

        Returns:
            Job ID
        """
        job.priority = priority
        return self._queue.enqueue(job)

    def dequeue(self) -> Optional[Job]:
        """Remove and return the next job from the queue.

        Returns:
            Next job if available, None if queue is empty
        """
        return self._queue.dequeue()

    def schedule(self, job: Job, when: datetime) -> str:
        """Schedule a job for future execution.

        Args:
            job: Job to schedule
            when: When to execute the job

        Returns:
            Scheduled job ID
        """
        job.scheduled_for = when
        job.status = JobStatus.PENDING
        return self._queue.schedule(job, when)

    def get_status(self, job_id: str) -> JobStatus:
        """Get the status of a job.

        Args:
            job_id: Job identifier

        Returns:
            Job status
        """
        return self._queue.get_status(job_id)

    def cancel(self, job_id: str) -> bool:
        """Cancel a scheduled or queued job.

        Args:
            job_id: Job identifier

        Returns:
            True if cancellation successful
        """
        return self._queue.cancel(job_id)

    def get_stats(self) -> dict:
        """Get queue statistics.

        Returns:
            Statistics dictionary
        """
        return self._queue.get_stats()

