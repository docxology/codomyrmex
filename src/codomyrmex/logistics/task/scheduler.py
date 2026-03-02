"""
Job scheduler for executing scheduled jobs.
"""

import threading
import time
from typing import Optional

from codomyrmex.logging_monitoring.core.logger_config import get_logger

from .job import Job, JobStatus
from .queue import Queue

logger = get_logger(__name__)


class JobScheduler:
    """Job scheduler for executing scheduled jobs."""

    def __init__(self, queue: Queue, check_interval: int = 1):
        """Initialize job scheduler.

        Args:
            queue: Queue instance
            check_interval: Interval in seconds to check for scheduled jobs
        """
        self.queue = queue
        self.check_interval = check_interval
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        """Start the scheduler."""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logger.info("Job scheduler started")

    def stop(self) -> None:
        """Stop the scheduler."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Job scheduler stopped")

    def _run(self) -> None:
        """Run the scheduler loop."""
        while self._running:
            try:
                # Check for jobs ready to execute
                job = self.queue.dequeue()
                if job:
                    logger.info(f"Executing job: {job.job_id}")
                    # Job execution would happen here
                    job.status = JobStatus.COMPLETED
            except Exception as e:
                logger.error(f"Error in scheduler: {e}")

            time.sleep(self.check_interval)

    def get_all_job_statuses(self) -> dict[str, str]:
        """
        Get status of all jobs in the queue.

        Returns:
            Dict mapping job_id to status string
        """
        statuses = {}
        # Access backend's job storage
        backend = self.queue._queue
        if hasattr(backend, '_jobs'):
            for job_id, job in backend._jobs.items():
                statuses[job_id] = job.status.value
        return statuses

    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a pending or running job.

        Args:
            job_id: ID of the job to cancel

        Returns:
            True if job was found and cancelled, False otherwise
        """
        # Use Queue's cancel method
        result = self.queue.cancel(job_id)
        if result:
            logger.info(f"Cancelled job: {job_id}")
        else:
            logger.warning(f"Failed to cancel job: {job_id}")
        return result

    def get_job(self, job_id: str) -> Optional["Job"]:
        """
        Get a job by its ID.

        Args:
            job_id: ID of the job

        Returns:
            Job instance or None if not found
        """
        backend = self.queue._queue
        if hasattr(backend, '_jobs'):
            return backend._jobs.get(job_id)
        return None

