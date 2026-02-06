import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)
"""
Job data structures for queue module.
"""



class JobStatus(Enum):
    """Job status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Job:
    """Job data structure."""

    task: str
    args: dict = field(default_factory=dict)
    kwargs: dict = field(default_factory=dict)
    priority: int = 0
    retries: int = 0
    max_retries: int = 3
    job_id: str | None = None
    status: JobStatus = JobStatus.PENDING
    created_at: datetime | None = None
    scheduled_for: datetime | None = None

    def __post_init__(self):
        """Initialize job after creation."""
        if self.job_id is None:
            self.job_id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.now()

