"""
Scheduler Models

Data classes and enums for the scheduling system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from collections.abc import Callable

from .triggers import OnceTrigger, Trigger


class JobStatus(Enum):
    """Status of a scheduled job."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Job:
    """A scheduled job."""
    id: str
    name: str
    func: Callable[..., Any]
    args: tuple = field(default_factory=tuple)
    kwargs: dict[str, Any] = field(default_factory=dict)
    trigger: Trigger = field(default_factory=lambda: OnceTrigger(datetime.now()))
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    last_run: datetime | None = None
    next_run: datetime | None = None
    run_count: int = 0
    max_runs: int | None = None
    result: Any = None
    error: str | None = None

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
