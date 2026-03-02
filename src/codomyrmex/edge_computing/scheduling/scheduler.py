"""Edge function scheduler.

Provides periodic and one-shot scheduling of edge function invocations.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any


class ScheduleType(Enum):
    """Types of schedules."""

    ONCE = "once"
    INTERVAL = "interval"
    CRON_LIKE = "cron_like"


@dataclass
class ScheduledJob:
    """A scheduled edge function invocation."""

    id: str
    function_id: str
    schedule_type: ScheduleType
    interval_seconds: float = 60.0
    next_run: datetime | None = None
    last_run: datetime | None = None
    run_count: int = 0
    max_runs: int | None = None
    enabled: bool = True
    args: tuple = ()
    kwargs: dict[str, Any] = field(default_factory=dict)

    @property
    def exhausted(self) -> bool:
        """Whether the job has reached its max run count."""
        if self.max_runs is None:
            return False
        return self.run_count >= self.max_runs


class EdgeScheduler:
    """Schedule edge function invocations.

    Uses a simple in-process timer. For production use, integrate with
    a distributed scheduler.
    """

    def __init__(self):
        self._jobs: dict[str, ScheduledJob] = {}
        self._running = False
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()

    def add_job(
        self,
        job_id: str,
        function_id: str,
        schedule_type: ScheduleType = ScheduleType.INTERVAL,
        interval_seconds: float = 60.0,
        max_runs: int | None = None,
        args: tuple = (),
        kwargs: dict[str, Any] | None = None,
    ) -> ScheduledJob:
        """Register a scheduled job."""
        job = ScheduledJob(
            id=job_id,
            function_id=function_id,
            schedule_type=schedule_type,
            interval_seconds=interval_seconds,
            next_run=datetime.now(UTC),
            max_runs=max_runs,
            args=args,
            kwargs=kwargs or {},
        )
        with self._lock:
            self._jobs[job_id] = job
        return job

    def remove_job(self, job_id: str) -> bool:
        """Remove a scheduled job."""
        with self._lock:
            if job_id in self._jobs:
                del self._jobs[job_id]
                return True
        return False

    def get_job(self, job_id: str) -> ScheduledJob | None:
        return self._jobs.get(job_id)

    def list_jobs(self, enabled_only: bool = False) -> list[ScheduledJob]:
        """List scheduled jobs."""
        jobs = list(self._jobs.values())
        if enabled_only:
            jobs = [j for j in jobs if j.enabled]
        return jobs

    def get_due_jobs(self) -> list[ScheduledJob]:
        """Return jobs that are due to run now."""
        now = datetime.now(UTC)
        due = []
        with self._lock:
            for job in self._jobs.values():
                if not job.enabled or job.exhausted:
                    continue
                if job.next_run and job.next_run <= now:
                    due.append(job)
        return due

    def execute_tick(self, cluster: Any) -> int:
        """Run one iteration of the scheduler, executing due jobs.

        Args:
            cluster: The EdgeCluster to run jobs on.

        Returns:
            Number of jobs executed.
        """
        due_jobs = self.get_due_jobs()
        executed_count = 0

        for job in due_jobs:
            # Simplistic execution: run on any node that has the function
            for node in cluster.list_nodes():
                runtime = cluster.get_runtime(node.id)
                if runtime and any(f.id == job.function_id for f in runtime.list_functions()):
                    try:
                        runtime.invoke(job.function_id, *job.args, **job.kwargs)
                        self.mark_executed(job.id)
                        executed_count += 1
                        break
                    except Exception:
                        continue
        return executed_count

    def mark_executed(self, job_id: str) -> None:
        """Mark a job as having just been executed."""
        job = self._jobs.get(job_id)
        if not job:
            return
        job.last_run = datetime.now(UTC)
        job.run_count += 1

        if job.schedule_type == ScheduleType.ONCE:
            job.enabled = False
        elif job.schedule_type == ScheduleType.INTERVAL:
            from datetime import timedelta

            job.next_run = datetime.now(UTC) + timedelta(seconds=job.interval_seconds)

    def summary(self) -> dict[str, Any]:
        """Summary of scheduler state."""
        jobs = list(self._jobs.values())
        return {
            "total_jobs": len(jobs),
            "enabled_jobs": sum(1 for j in jobs if j.enabled),
            "exhausted_jobs": sum(1 for j in jobs if j.exhausted),
            "total_runs": sum(j.run_count for j in jobs),
        }
