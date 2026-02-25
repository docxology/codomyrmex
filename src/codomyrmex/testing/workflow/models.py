"""
Workflow Testing Models

Data classes and enums for workflow testing.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class WorkflowStepType(Enum):
    """Types of workflow steps."""
    HTTP_REQUEST = "http_request"
    ASSERTION = "assertion"
    WAIT = "wait"
    SCRIPT = "script"
    CONDITIONAL = "conditional"


class StepStatus(Enum):
    """Status of a step execution."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class WorkflowStep:
    """A single step in a workflow test."""
    id: str
    name: str
    step_type: WorkflowStepType
    config: dict[str, Any] = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)
    retry_count: int = 0
    timeout_seconds: float = 30.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.step_type.value,
            "config": self.config,
        }


@dataclass
class StepResult:
    """Result of executing a step."""
    step_id: str
    status: StepStatus
    output: Any = None
    error: str | None = None
    duration_ms: float = 0.0
    retries: int = 0

    @property
    def passed(self) -> bool:
        """Check if step passed."""
        return self.status == StepStatus.PASSED

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "step_id": self.step_id,
            "status": self.status.value,
            "output": str(self.output) if self.output else None,
            "error": self.error,
            "duration_ms": self.duration_ms,
        }


@dataclass
class WorkflowResult:
    """Result of running a complete workflow."""
    workflow_id: str
    status: StepStatus
    step_results: list[StepResult] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None

    @property
    def total_steps(self) -> int:
        """Get total steps."""
        return len(self.step_results)

    @property
    def passed_steps(self) -> int:
        """Get passed steps."""
        return sum(1 for r in self.step_results if r.passed)

    @property
    def duration_ms(self) -> float:
        """Get total duration."""
        return sum(r.duration_ms for r in self.step_results)

    @property
    def pass_rate(self) -> float:
        """Get pass rate."""
        if self.total_steps == 0:
            return 0.0
        return self.passed_steps / self.total_steps

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "workflow_id": self.workflow_id,
            "status": self.status.value,
            "total_steps": self.total_steps,
            "passed_steps": self.passed_steps,
            "pass_rate": self.pass_rate,
            "duration_ms": self.duration_ms,
        }


@dataclass
class Workflow:
    """A workflow test definition."""
    id: str
    name: str
    description: str = ""
    steps: list[WorkflowStep] = field(default_factory=list)
    variables: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)

    def add_step(self, step: WorkflowStep) -> "Workflow":
        """Add a step to workflow."""
        self.steps.append(step)
        return self

    def add_assertion(
        self,
        id: str,
        name: str,
        assertion_type: str,
        expected: Any,
        actual_key: str | None = None,
    ) -> "Workflow":
        """Add an assertion step."""
        step = WorkflowStep(
            id=id,
            name=name,
            step_type=WorkflowStepType.ASSERTION,
            config={
                "type": assertion_type,
                "expected": expected,
                "actual_key": actual_key,
            },
        )
        return self.add_step(step)

    def add_wait(self, id: str, seconds: float) -> "Workflow":
        """Add a wait step."""
        step = WorkflowStep(
            id=id,
            name=f"Wait {seconds}s",
            step_type=WorkflowStepType.WAIT,
            config={"seconds": seconds},
        )
        return self.add_step(step)
