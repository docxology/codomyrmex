"""
Scheduler Module

Task scheduling and job queuing with support for cron and interval triggers.
"""

__version__ = "0.1.0"

import hashlib
import heapq
import re
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union
import concurrent.futures


class JobStatus(Enum):
    """Status of a scheduled job."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TriggerType(Enum):
    """Types of job triggers."""
    ONCE = "once"
    INTERVAL = "interval"
    CRON = "cron"


@dataclass
class Trigger(ABC):
    """Base class for job triggers."""
    
    @abstractmethod
    def get_next_run(self, from_time: Optional[datetime] = None) -> Optional[datetime]:
        """Get the next run time."""
        pass
    
    @abstractmethod
    def get_type(self) -> TriggerType:
        """Get trigger type."""
        pass


@dataclass
class OnceTrigger(Trigger):
    """Trigger that fires once at a specific time."""
    run_at: datetime
    
    def get_next_run(self, from_time: Optional[datetime] = None) -> Optional[datetime]:
        from_time = from_time or datetime.now()
        if self.run_at > from_time:
            return self.run_at
        return None
    
    def get_type(self) -> TriggerType:
        return TriggerType.ONCE


@dataclass
class IntervalTrigger(Trigger):
    """Trigger that fires at regular intervals."""
    seconds: int = 0
    minutes: int = 0
    hours: int = 0
    days: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    @property
    def interval_seconds(self) -> int:
        return (
            self.seconds +
            self.minutes * 60 +
            self.hours * 3600 +
            self.days * 86400
        )
    
    def get_next_run(self, from_time: Optional[datetime] = None) -> Optional[datetime]:
        from_time = from_time or datetime.now()
        start = self.start_time or datetime.now()
        
        if from_time < start:
            return start
        
        elapsed = (from_time - start).total_seconds()
        intervals_passed = int(elapsed / self.interval_seconds) + 1
        next_run = start + timedelta(seconds=intervals_passed * self.interval_seconds)
        
        if self.end_time and next_run > self.end_time:
            return None
        
        return next_run
    
    def get_type(self) -> TriggerType:
        return TriggerType.INTERVAL


@dataclass
class CronTrigger(Trigger):
    """Cron-style trigger (simplified)."""
    minute: str = "*"
    hour: str = "*"
    day_of_month: str = "*"
    month: str = "*"
    day_of_week: str = "*"
    
    def _match_field(self, field_pattern: str, value: int, max_val: int) -> bool:
        """Check if value matches cron pattern."""
        if field_pattern == "*":
            return True
        
        # Handle comma-separated values
        for part in field_pattern.split(","):
            # Handle ranges
            if "-" in part:
                low, high = map(int, part.split("-"))
                if low <= value <= high:
                    return True
            # Handle step values
            elif "/" in part:
                base, step = part.split("/")
                step = int(step)
                if base == "*":
                    if value % step == 0:
                        return True
            else:
                if int(part) == value:
                    return True
        
        return False
    
    def get_next_run(self, from_time: Optional[datetime] = None) -> Optional[datetime]:
        """Get next run time (simplified implementation)."""
        from_time = from_time or datetime.now()
        candidate = from_time.replace(second=0, microsecond=0) + timedelta(minutes=1)
        
        # Search up to 1 year ahead
        max_iterations = 525600  # minutes in a year
        
        for _ in range(max_iterations):
            if (
                self._match_field(self.minute, candidate.minute, 59) and
                self._match_field(self.hour, candidate.hour, 23) and
                self._match_field(self.day_of_month, candidate.day, 31) and
                self._match_field(self.month, candidate.month, 12) and
                self._match_field(self.day_of_week, candidate.weekday(), 6)
            ):
                return candidate
            candidate += timedelta(minutes=1)
        
        return None
    
    def get_type(self) -> TriggerType:
        return TriggerType.CRON
    
    @classmethod
    def from_expression(cls, expr: str) -> "CronTrigger":
        """Parse cron expression (minute hour day month weekday)."""
        parts = expr.strip().split()
        if len(parts) != 5:
            raise ValueError(f"Invalid cron expression: {expr}")
        
        return cls(
            minute=parts[0],
            hour=parts[1],
            day_of_month=parts[2],
            month=parts[3],
            day_of_week=parts[4],
        )


@dataclass
class Job:
    """A scheduled job."""
    id: str
    name: str
    func: Callable[..., Any]
    args: tuple = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    trigger: Trigger = field(default_factory=lambda: OnceTrigger(datetime.now()))
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    run_count: int = 0
    max_runs: Optional[int] = None
    result: Any = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.next_run is None:
            self.next_run = self.trigger.get_next_run()
    
    def __lt__(self, other: "Job") -> bool:
        if self.next_run is None:
            return False
        if other.next_run is None:
            return True
        return self.next_run < other.next_run
    
    def execute(self) -> Any:
        """Execute the job."""
        self.status = JobStatus.RUNNING
        self.last_run = datetime.now()
        
        try:
            self.result = self.func(*self.args, **self.kwargs)
            self.status = JobStatus.COMPLETED
            self.run_count += 1
            return self.result
        except Exception as e:
            self.error = str(e)
            self.status = JobStatus.FAILED
            raise
        finally:
            # Schedule next run
            if self.max_runs and self.run_count >= self.max_runs:
                self.next_run = None
            else:
                self.next_run = self.trigger.get_next_run(datetime.now())


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
        self._jobs: Dict[str, Job] = {}
        self._job_queue: List[Job] = []
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self._job_counter = 0
    
    def _generate_id(self) -> str:
        """Generate unique job ID."""
        self._job_counter += 1
        return f"job_{self._job_counter}_{int(time.time())}"
    
    def schedule(
        self,
        func: Callable[..., Any],
        name: Optional[str] = None,
        trigger: Optional[Trigger] = None,
        args: tuple = (),
        kwargs: Optional[Dict[str, Any]] = None,
        max_runs: Optional[int] = None,
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
    
    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID."""
        return self._jobs.get(job_id)
    
    def list_jobs(self, status: Optional[JobStatus] = None) -> List[Job]:
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
        except Exception:
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


__all__ = [
    # Core classes
    "Scheduler",
    "Job",
    "JobStatus",
    # Triggers
    "Trigger",
    "TriggerType",
    "OnceTrigger",
    "IntervalTrigger",
    "CronTrigger",
    # Convenience functions
    "every",
    "at",
    "cron",
]
