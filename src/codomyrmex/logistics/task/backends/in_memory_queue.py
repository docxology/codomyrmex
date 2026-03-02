"""
In-memory queue backend.
"""

import heapq
import time
from datetime import datetime

from codomyrmex.logging_monitoring.core.logger_config import get_logger
from codomyrmex.logistics.task.job import Job, JobStatus

logger = get_logger(__name__)


class InMemoryQueue:
    """In-memory queue implementation."""

    def __init__(self):
        """Initialize in-memory queue."""
        # Priority queue: (-priority, timestamp, job)
        self._queue: list[tuple] = []
        self._jobs: dict[str, Job] = {}
        self._scheduled: list[tuple[datetime, Job]] = []

    def enqueue(self, job: Job) -> str:
        """Add a job to the queue."""
        heapq.heappush(self._queue, (-job.priority, time.time(), job))
        self._jobs[job.job_id] = job
        return job.job_id

    def dequeue(self) -> Job | None:
        """Remove and return the next job from the queue."""
        # Check scheduled jobs
        now = datetime.now()
        ready_jobs = [j for dt, j in self._scheduled if dt <= now]
        for dt, job in ready_jobs:
            self._scheduled.remove((dt, job))
            heapq.heappush(self._queue, (-job.priority, time.time(), job))

        if not self._queue:
            return None

        _, _, job = heapq.heappop(self._queue)
        job.status = JobStatus.RUNNING
        return job

    def schedule(self, job: Job, when: datetime) -> str:
        """Schedule a job for future execution."""
        self._scheduled.append((when, job))
        self._scheduled.sort(key=lambda x: x[0])
        self._jobs[job.job_id] = job
        return job.job_id

    def get_status(self, job_id: str) -> JobStatus:
        """Get the status of a job."""
        if job_id in self._jobs:
            return self._jobs[job_id].status
        return JobStatus.PENDING

    def cancel(self, job_id: str) -> bool:
        """Cancel a scheduled or queued job."""
        if job_id in self._jobs:
            job = self._jobs[job_id]
            job.status = JobStatus.CANCELLED
            # Remove from queue if present
            self._queue = [item for item in self._queue if item[2].job_id != job_id]
            heapq.heapify(self._queue)
            # Remove from scheduled
            self._scheduled = [(dt, j) for dt, j in self._scheduled if j.job_id != job_id]
            return True
        return False

    def get_stats(self) -> dict:
        """Get queue statistics."""
        return {
            "queue_length": len(self._queue),
            "scheduled_count": len(self._scheduled),
            "total_jobs": len(self._jobs),
        }

