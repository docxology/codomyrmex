"""
Scheduler Core

Task scheduler with support for various trigger types.
"""

import concurrent.futures
import heapq
import threading
import time
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any

from .models import Job, JobStatus
from .triggers import CronTrigger, IntervalTrigger, OnceTrigger, Trigger
from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


class Scheduler:
    """
    Task scheduler with support for various trigger types.

    Usage:
        scheduler = Scheduler()

        # Schedule a one-time job
        scheduler.schedule(
            name="backup",
            func=backup_database,
            trigger=OnceTrigger(datetime.now() + timedelta(hours=1)),
        )

        # Schedule a recurring job
        scheduler.schedule(
            name="cleanup",
            func=cleanup_temp_files,
            trigger=IntervalTrigger(hours=1),
        )

        # Start the scheduler
        scheduler.start()
    """

    def __init__(self, max_workers: int = 4):
        self._jobs: dict[str, Job] = {}
        self._job_queue: list[Job] = []
        self._lock = threading.Lock()
        self._running = False
        self._thread: threading.Thread | None = None
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self._job_counter = 0

    def _generate_id(self) -> str:
        """Generate unique job ID."""
        self._job_counter += 1
        return f"job_{self._job_counter}_{int(time.time())}"

    def schedule(
        self,
        func: Callable[..., Any],
        name: str | None = None,
        trigger: Trigger | None = None,
        args: tuple = (),
        kwargs: dict[str, Any] | None = None,
        max_runs: int | None = None,
    ) -> str:
        """
        Schedule a job.

        Args:
            func: Function to execute
            name: Optional job name
            trigger: Trigger defining when to run
            args: Positional arguments for func
            kwargs: Keyword arguments for func
            max_runs: Maximum number of executions

        Returns:
            Job ID
        """
        job_id = self._generate_id()
        job = Job(
            id=job_id,
            name=name or func.__name__,
            func=func,
            args=args,
            kwargs=kwargs or {},
            trigger=trigger or OnceTrigger(datetime.now()),
            max_runs=max_runs,
        )

        with self._lock:
            self._jobs[job_id] = job
            if job.next_run:
                heapq.heappush(self._job_queue, job)

        return job_id

    def cancel(self, job_id: str) -> bool:
        """Cancel a scheduled job."""
        with self._lock:
            if job_id in self._jobs:
                self._jobs[job_id].status = JobStatus.CANCELLED
                self._jobs[job_id].next_run = None
                return True
        return False

    def get_job(self, job_id: str) -> Job | None:
        """Get job by ID."""
        return self._jobs.get(job_id)

    def list_jobs(self, status: JobStatus | None = None) -> list[Job]:
        """List all jobs, optionally filtered by status."""
        jobs = list(self._jobs.values())
        if status:
            jobs = [j for j in jobs if j.status == status]
        return jobs

    def _run_loop(self):
        """Main scheduler loop."""
        while self._running:
            now = datetime.now()
            jobs_to_run = []

            with self._lock:
                # Find all jobs due to run
                while self._job_queue and self._job_queue[0].next_run and self._job_queue[0].next_run <= now:
                    job = heapq.heappop(self._job_queue)
                    if job.status != JobStatus.CANCELLED:
                        jobs_to_run.append(job)

            # Execute jobs
            for job in jobs_to_run:
                self._executor.submit(self._execute_job, job)

            time.sleep(0.1)  # Small sleep to prevent CPU spinning

    def _execute_job(self, job: Job):
        """Execute a job and reschedule if needed."""
        try:
            job.execute()
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.warning("Job '%s' execution failed: %s", job.name if hasattr(job, 'name') else job, e)
            pass  # Error already recorded in job

        # Reschedule if has next run
        with self._lock:
            if job.next_run and job.status != JobStatus.CANCELLED:
                job.status = JobStatus.PENDING
                heapq.heappush(self._job_queue, job)

    def start(self):
        """Start the scheduler."""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop the scheduler."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        self._executor.shutdown(wait=False)

    def run_now(self, job_id: str) -> Any:
        """Execute a job immediately."""
        job = self._jobs.get(job_id)
        if job:
            return job.execute()
        raise ValueError(f"Job not found: {job_id}")


# Convenience functions
def every(
    seconds: int = 0,
    minutes: int = 0,
    hours: int = 0,
    days: int = 0,
) -> IntervalTrigger:
    """Create an interval trigger."""
    return IntervalTrigger(
        seconds=seconds,
        minutes=minutes,
        hours=hours,
        days=days,
    )


def at(time_str: str) -> OnceTrigger:
    """Create a one-time trigger from time string (HH:MM)."""
    hour, minute = map(int, time_str.split(":"))
    now = datetime.now()
    run_at = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if run_at <= now:
        run_at += timedelta(days=1)
    return OnceTrigger(run_at=run_at)


def cron(expression: str) -> CronTrigger:
    """Create a cron trigger from expression."""
    return CronTrigger.from_expression(expression)
