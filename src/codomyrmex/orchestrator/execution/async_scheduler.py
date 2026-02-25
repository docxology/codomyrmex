"""Async-first scheduler using ``asyncio.TaskGroup`` (3.11+).

Provides ``AsyncScheduler`` as a replacement for the thread-based
:class:`Scheduler`, with priority-based execution and ``EventBus``
lifecycle event integration.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class AsyncJobStatus(Enum):
    """Status of an async scheduled job."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AsyncJob:
    """A single scheduled async job."""

    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = ""
    func: Callable[..., Coroutine[Any, Any, Any]] | None = None
    args: tuple[Any, ...] = ()
    kwargs: dict[str, Any] = field(default_factory=dict)
    priority: int = 0  # Lower = higher priority
    status: AsyncJobStatus = AsyncJobStatus.PENDING
    result: Any = None
    error: str | None = None
    scheduled_at: datetime = field(default_factory=datetime.now)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    max_runs: int | None = 1

    def __lt__(self, other: AsyncJob) -> bool:
        """Priority comparison for heapq (lower number = higher priority)."""
        return self.priority < other.priority


@dataclass
class SchedulerMetrics:
    """Runtime metrics for the async scheduler."""

    jobs_scheduled: int = 0
    jobs_completed: int = 0
    jobs_failed: int = 0
    jobs_cancelled: int = 0
    total_execution_time: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "jobs_scheduled": self.jobs_scheduled,
            "jobs_completed": self.jobs_completed,
            "jobs_failed": self.jobs_failed,
            "jobs_cancelled": self.jobs_cancelled,
            "total_execution_time": self.total_execution_time,
        }


# ---------------------------------------------------------------------------
# Lifecycle events
# ---------------------------------------------------------------------------


def _emit_scheduler_event(
    event_bus: Any,
    event_type_name: str,
    job: AsyncJob,
    **extra: Any,
) -> None:
    """Try to emit an EventBus event for scheduler lifecycle.

    Fails silently if EventBus or the event type is unavailable.
    """
    if event_bus is None:
        return
    try:
        from codomyrmex.events.core.event_schema import Event, EventType
        et = getattr(EventType, event_type_name, EventType.CUSTOM)
        event = Event(
            event_type=et,
            source=f"scheduler.{job.name}",
            data={"job_id": job.id, "job_name": job.name, **extra},
        )
        if hasattr(event_bus, "publish"):
            event_bus.publish(event)
        elif hasattr(event_bus, "emit"):
            event_bus.emit(event)
    except (ValueError, RuntimeError, AttributeError, OSError, TypeError):
        logger.debug("Failed to emit scheduler event %s", event_type_name)


# ---------------------------------------------------------------------------
# AsyncScheduler
# ---------------------------------------------------------------------------


class AsyncScheduler:
    """Async-first job scheduler with priority and EventBus integration.

    Parameters
    ----------
    max_concurrency:
        Maximum number of jobs running simultaneously.
    event_bus:
        Optional ``EventBus`` instance for lifecycle events.

    Usage::

        scheduler = AsyncScheduler(max_concurrency=4)

        async def my_job(x: int) -> int:
            return x * 2

        job_id = scheduler.schedule(my_job, args=(42,), priority=1, name="double")
        results = await scheduler.run_all()
    """

    def __init__(
        self,
        *,
        max_concurrency: int = 4,
        event_bus: Any = None,
    ) -> None:
        """Execute   Init   operations natively."""
        self._jobs: dict[str, AsyncJob] = {}
        self._max_concurrency = max_concurrency
        self._event_bus = event_bus
        self._semaphore = asyncio.Semaphore(max_concurrency)
        self._metrics = SchedulerMetrics()

    # ------------------------------------------------------------------
    # Public API — scheduling
    # ------------------------------------------------------------------

    def schedule(
        self,
        func: Callable[..., Coroutine[Any, Any, Any]],
        *,
        name: str | None = None,
        args: tuple[Any, ...] = (),
        kwargs: dict[str, Any] | None = None,
        priority: int = 0,
        max_runs: int | None = 1,
    ) -> str:
        """Schedule an async job.

        Returns
        -------
        str
            The job ID.
        """
        job = AsyncJob(
            name=name or func.__name__,
            func=func,
            args=args,
            kwargs=kwargs or {},
            priority=priority,
            max_runs=max_runs,
        )
        self._jobs[job.id] = job
        self._metrics.jobs_scheduled += 1

        _emit_scheduler_event(self._event_bus, "JOB_SCHEDULED", job)
        logger.debug("Scheduled job %s (priority=%d)", job.name, job.priority)
        return job.id

    def cancel(self, job_id: str) -> bool:
        """Cancel a pending job."""
        job = self._jobs.get(job_id)
        if job and job.status == AsyncJobStatus.PENDING:
            job.status = AsyncJobStatus.CANCELLED
            self._metrics.jobs_cancelled += 1
            return True
        return False

    def get_job(self, job_id: str) -> AsyncJob | None:
        """Retrieve a job by ID."""
        return self._jobs.get(job_id)

    def list_jobs(self, status: AsyncJobStatus | None = None) -> list[AsyncJob]:
        """List jobs, optionally filtered by status."""
        jobs = list(self._jobs.values())
        if status is not None:
            jobs = [j for j in jobs if j.status == status]
        return jobs

    @property
    def metrics(self) -> SchedulerMetrics:
        """Runtime metrics."""
        return self._metrics

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def run_all(self) -> dict[str, AsyncJob]:
        """Execute all pending jobs, respecting priority order.

        Returns
        -------
        dict[str, AsyncJob]
            Map of job_id → completed AsyncJob.
        """
        pending = sorted(
            (j for j in self._jobs.values() if j.status == AsyncJobStatus.PENDING),
            key=lambda j: j.priority,
        )

        if not pending:
            return {}

        async with asyncio.TaskGroup() as tg:
            for job in pending:
                tg.create_task(self._execute_job(job), name=job.name)

        return {j.id: j for j in pending}

    async def _execute_job(self, job: AsyncJob) -> None:
        """Execute a single job with semaphore bounds."""
        import time

        async with self._semaphore:
            job.status = AsyncJobStatus.RUNNING
            job.started_at = datetime.now()
            _emit_scheduler_event(self._event_bus, "JOB_STARTED", job)

            t0 = time.monotonic()
            try:
                assert job.func is not None
                job.result = await job.func(*job.args, **job.kwargs)
                job.status = AsyncJobStatus.COMPLETED
                job.completed_at = datetime.now()
                execution_time = time.monotonic() - t0
                self._metrics.jobs_completed += 1
                self._metrics.total_execution_time += execution_time

                _emit_scheduler_event(
                    self._event_bus, "JOB_COMPLETED", job,
                    execution_time=execution_time,
                )
                logger.debug("Job %s completed in %.2fs", job.name, execution_time)

            except Exception as exc:
                job.status = AsyncJobStatus.FAILED
                job.error = str(exc)
                job.completed_at = datetime.now()
                execution_time = time.monotonic() - t0
                self._metrics.jobs_failed += 1
                self._metrics.total_execution_time += execution_time

                _emit_scheduler_event(
                    self._event_bus, "JOB_FAILED", job,
                    error=str(exc),
                    execution_time=execution_time,
                )
                logger.warning("Job %s failed: %s", job.name, exc)


__all__ = [
    "AsyncScheduler",
    "AsyncJob",
    "AsyncJobStatus",
    "SchedulerMetrics",
]
