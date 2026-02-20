"""Pipeline data models — enums and dataclasses for pipeline orchestration."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class PipelineStatus(Enum):
    """Pipeline execution status."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class StageStatus(Enum):
    """Pipeline stage status."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class JobStatus(Enum):
    """Job execution status."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


@dataclass
class PipelineJob:
    """Individual job within a pipeline stage."""

    name: str
    commands: list[str]
    environment: dict[str, str] = field(default_factory=dict)
    artifacts: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    timeout: int = 3600  # 1 hour
    retry_count: int = 0
    allow_failure: bool = False
    status: JobStatus = JobStatus.PENDING
    start_time: datetime | None = None
    end_time: datetime | None = None
    output: str = ""
    error: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert job to dictionary format."""
        return {
            "name": self.name,
            "commands": self.commands,
            "environment": self.environment,
            "artifacts": self.artifacts,
            "dependencies": self.dependencies,
            "timeout": self.timeout,
            "retry_count": self.retry_count,
            "allow_failure": self.allow_failure,
            "status": self.status.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "output": self.output,
            "error": self.error,
        }


@dataclass
class PipelineStage:
    """Pipeline stage containing multiple jobs."""

    name: str
    jobs: list[PipelineJob] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    environment: dict[str, str] = field(default_factory=dict)
    allow_failure: bool = False
    parallel: bool = True
    status: StageStatus = StageStatus.PENDING
    start_time: datetime | None = None
    end_time: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert stage to dictionary format."""
        return {
            "name": self.name,
            "jobs": [job.to_dict() for job in self.jobs],
            "dependencies": self.dependencies,
            "environment": self.environment,
            "allow_failure": self.allow_failure,
            "parallel": self.parallel,
            "status": self.status.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
        }


@dataclass
class Pipeline:
    """Complete CI/CD pipeline definition."""

    name: str
    description: str = ""
    stages: list[PipelineStage] = field(default_factory=list)
    variables: dict[str, str] = field(default_factory=dict)
    triggers: dict[str, Any] = field(default_factory=dict)
    timeout: int = 7200  # 2 hours
    status: PipelineStatus = PipelineStatus.PENDING
    created_at: datetime | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    duration: float = 0.0

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict[str, Any]:
        """Convert pipeline to dictionary format."""
        return {
            "name": self.name,
            "description": self.description,
            "stages": [stage.to_dict() for stage in self.stages],
            "variables": self.variables,
            "triggers": self.triggers,
            "timeout": self.timeout,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "duration": self.duration,
        }
