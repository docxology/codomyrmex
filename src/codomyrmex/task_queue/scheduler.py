"""
Job scheduler for executing scheduled jobs.
"""

import threading
import time
from datetime import datetime
from typing import Optional

from codomyrmex.logging_monitoring.logger_config import get_logger

from .job import JobStatus
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
        self._thread: Optional[threading.Thread] = None

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

