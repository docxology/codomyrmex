"""
Core shared types for Codomyrmex.

Provides foundational types used across all layers: Result, Task, Config, ModuleInfo.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ResultStatus(Enum):
    """Status of an operation result."""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"


class TaskStatus(Enum):
    """Status of a task."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Result:
    """
    Standard result type for module operations.

    Every module operation should return a Result to enable
    consistent error handling and status checking.
    """
    status: ResultStatus
    data: Any = None
    message: str = ""
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    duration_ms: float | None = None

    @property
    def ok(self) -> bool:
        """Ok."""
        return self.status == ResultStatus.SUCCESS

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "status": self.status.value,
            "data": self.data,
            "message": self.message,
            "errors": self.errors,
            "metadata": self.metadata,
            "duration_ms": self.duration_ms,
        }


@dataclass
class Task:
    """
    Standard task type for work items across modules.

    Used by orchestrator, agents, and workflow systems to represent
    units of work.
    """
    id: str
    name: str
    status: TaskStatus = TaskStatus.PENDING
    description: str = ""
    module: str = ""
    input_data: dict[str, Any] = field(default_factory=dict)
    output_data: dict[str, Any] = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status.value,
            "description": self.description,
            "module": self.module,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "dependencies": self.dependencies,
            "metadata": self.metadata,
        }


@dataclass
class Config:
    """Standard configuration type for modules."""
    name: str
    values: dict[str, Any] = field(default_factory=dict)
    version: str = "1.0.0"
    module: str = ""

    def get(self, key: str, default: Any = None) -> Any:
        """Return the requested value."""
        return self.values.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set the value."""
        self.values[key] = value


@dataclass
class ModuleInfo:
    """Information about a codomyrmex module."""
    name: str
    version: str = "0.1.0"
    layer: str = ""  # foundation, core, service, application
    description: str = ""
    dependencies: list[str] = field(default_factory=list)
    has_cli: bool = False
    has_mcp: bool = False
    has_events: bool = False


@dataclass
class ToolDefinition:
    """Definition of a tool exposed via MCP or CLI."""
    name: str
    description: str
    module: str
    input_schema: dict[str, Any] = field(default_factory=dict)
    output_schema: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)


@dataclass
class Notification:
    """Standard notification type."""
    title: str
    message: str
    level: str = "info"  # info, warning, error, critical
    source: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


__all__ = [
    "Result",
    "ResultStatus",
    "Task",
    "TaskStatus",
    "Config",
    "ModuleInfo",
    "ToolDefinition",
    "Notification",
]
