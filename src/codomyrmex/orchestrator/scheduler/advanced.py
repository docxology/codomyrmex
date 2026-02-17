"""
Advanced Scheduler Features

Persistent scheduling and job dependencies.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any
from collections.abc import Callable

from . import JobStatus, Scheduler


class DependencyStatus(Enum):
    """Status of job dependencies."""
    WAITING = "waiting"
    READY = "ready"
    BLOCKED = "blocked"
    SATISFIED = "satisfied"


@dataclass
class JobDependency:
    """Dependency between jobs."""
    job_id: str
    depends_on: list[str] = field(default_factory=list)
    require_success: bool = True
    status: DependencyStatus = DependencyStatus.WAITING


class DependencyScheduler(Scheduler):
    """Scheduler with job dependency support."""

    def __init__(self, max_workers: int = 4):
        super().__init__(max_workers)
        self._dependencies: dict[str, JobDependency] = {}
        self._completed_jobs: set[str] = set()
        self._failed_jobs: set[str] = set()

    def add_dependency(self, job_id: str, depends_on: list[str]) -> None:
        """Add dependencies for a job."""
        self._dependencies[job_id] = JobDependency(
            job_id=job_id,
            depends_on=depends_on,
        )

    def _check_dependencies(self, job_id: str) -> DependencyStatus:
        """Check if job dependencies are satisfied."""
        if job_id not in self._dependencies:
            return DependencyStatus.READY

        dep = self._dependencies[job_id]

        for required_job in dep.depends_on:
            if required_job in self._failed_jobs:
                if dep.require_success:
                    return DependencyStatus.BLOCKED
            elif required_job not in self._completed_jobs:
                return DependencyStatus.WAITING

        return DependencyStatus.SATISFIED

    def _on_job_complete(self, job_id: str, success: bool) -> None:
        """Handle job completion."""
        if success:
            self._completed_jobs.add(job_id)
        else:
            self._failed_jobs.add(job_id)

        # Check if any waiting jobs can now run
        if job_id in self._dependencies:
            del self._dependencies[job_id]

    def schedule_with_deps(
        self,
        func: Callable[..., Any],
        depends_on: list[str] | None = None,
        **kwargs,
    ) -> str:
        """Schedule a job with dependencies."""
        job_id = self.schedule(func, **kwargs)

        if depends_on:
            self.add_dependency(job_id, depends_on)

        return job_id


class PersistentScheduler(Scheduler):
    """Scheduler with state persistence."""

    def __init__(
        self,
        max_workers: int = 4,
        state_path: str | None = None,
        auto_save: bool = True,
    ):
        super().__init__(max_workers)
        self._state_path = Path(state_path) if state_path else None
        self._auto_save = auto_save
        self._job_functions: dict[str, str] = {}  # job_id -> function name
        self._registered_functions: dict[str, Callable] = {}

        if self._state_path:
            self._load_state()

    def register_function(self, name: str, func: Callable) -> None:
        """Register a function for persistent scheduling."""
        self._registered_functions[name] = func

    def _load_state(self) -> None:
        """Load scheduler state from disk."""
        if not self._state_path or not self._state_path.exists():
            return

        try:
            with open(self._state_path) as f:
                state = json.load(f)

            for job_data in state.get("jobs", []):
                func_name = job_data.get("function")
                if func_name in self._registered_functions:
                    func = self._registered_functions[func_name]
                    job_id = self.schedule(
                        func,
                        name=job_data.get("name"),
                        args=tuple(job_data.get("args", [])),
                        kwargs=job_data.get("kwargs", {}),
                    )
                    self._job_functions[job_id] = func_name
        except (json.JSONDecodeError, KeyError):
            pass

    def _save_state(self) -> None:
        """Save scheduler state to disk."""
        if not self._state_path:
            return

        self._state_path.parent.mkdir(parents=True, exist_ok=True)

        jobs = []
        for job_id, job in self._jobs.items():
            if job.status not in (JobStatus.CANCELLED, JobStatus.COMPLETED):
                func_name = self._job_functions.get(job_id, "")
                jobs.append({
                    "id": job_id,
                    "name": job.name,
                    "function": func_name,
                    "status": job.status.value,
                })

        state = {
            "saved_at": datetime.now().isoformat(),
            "jobs": jobs,
        }

        with open(self._state_path, 'w') as f:
            json.dump(state, f, indent=2)

    def schedule(
        self,
        func: Callable[..., Any],
        function_name: str | None = None,
        **kwargs,
    ) -> str:
        """Schedule with optional persistence."""
        job_id = super().schedule(func, **kwargs)

        if function_name:
            self._job_functions[job_id] = function_name
            if self._auto_save:
                self._save_state()

        return job_id

    def stop(self) -> None:
        """Stop and save state."""
        super().stop()
        self._save_state()


class JobPipeline:
    """Define and run job pipelines."""

    def __init__(self, scheduler: Scheduler):
        self._scheduler = scheduler
        self._stages: list[list[Callable]] = []
        self._current_stage = 0
        self._results: list[list[Any]] = []

    def add_stage(self, *funcs: Callable) -> "JobPipeline":
        """Add a stage with one or more parallel jobs."""
        self._stages.append(list(funcs))
        return self

    async def run(self) -> list[list[Any]]:
        """Run all pipeline stages."""
        import asyncio

        for stage_funcs in self._stages:
            stage_results = []

            # Run all jobs in stage in parallel
            tasks = []
            for func in stage_funcs:
                job_id = self._scheduler.schedule(func)
                tasks.append(job_id)

            # Wait for all jobs in stage to complete
            while True:
                all_done = True
                for job_id in tasks:
                    job = self._scheduler.get_job(job_id)
                    if job and job.status not in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
                        all_done = False
                        break

                if all_done:
                    break

                await asyncio.sleep(0.1)

            # Collect results
            for job_id in tasks:
                job = self._scheduler.get_job(job_id)
                stage_results.append(job.result if job else None)

            self._results.append(stage_results)

        return self._results


@dataclass
class ScheduledRecurrence:
    """Recurrence specification for scheduled jobs."""
    every: int = 1
    unit: str = "days"  # seconds, minutes, hours, days, weeks
    at_time: str | None = None  # HH:MM format
    on_days: list[str] = field(default_factory=list)  # mon, tue, etc.
    until: datetime | None = None


def parse_cron(expression: str) -> dict[str, Any]:
    """Parse cron expression into components.

    Format: minute hour day_of_month month day_of_week
    """
    parts = expression.split()
    if len(parts) != 5:
        raise ValueError("Cron expression must have 5 parts")

    return {
        "minute": parts[0],
        "hour": parts[1],
        "day_of_month": parts[2],
        "month": parts[3],
        "day_of_week": parts[4],
    }


def describe_cron(expression: str) -> str:
    """Get human-readable description of cron expression."""
    parsed = parse_cron(expression)

    if expression == "* * * * *":
        return "Every minute"
    elif expression == "0 * * * *":
        return "Every hour"
    elif expression == "0 0 * * *":
        return "Every day at midnight"
    elif expression == "0 0 * * 0":
        return "Every Sunday at midnight"
    elif expression == "0 0 1 * *":
        return "First day of every month"

    return f"Custom: {expression}"
