"""
Migration Models

Data classes, enums, and transformers for data migration.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


class MigrationStatus(Enum):
    """Status of a migration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class MigrationDirection(Enum):
    """Direction of migration."""
    UP = "up"
    DOWN = "down"


@dataclass
class MigrationStep:
    """A single migration step."""
    id: str
    name: str
    description: str = ""
    up_fn: Callable[[], bool] | None = None
    down_fn: Callable[[], bool] | None = None
    dependencies: list[str] = field(default_factory=list)

    def run_up(self) -> bool:
        """Run migration up."""
        if self.up_fn:
            return self.up_fn()
        return True

    def run_down(self) -> bool:
        """Run migration down (rollback)."""
        if self.down_fn:
            return self.down_fn()
        return True


@dataclass
class MigrationResult:
    """Result of a migration."""
    migration_id: str
    status: MigrationStatus
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None
    steps_completed: int = 0
    steps_total: int = 0
    error: str | None = None

    @property
    def progress(self) -> float:
        """Get progress percentage."""
        if self.steps_total == 0:
            return 0.0
        return self.steps_completed / self.steps_total

    @property
    def duration_seconds(self) -> float:
        """Get duration in seconds."""
        end = self.completed_at or datetime.now()
        return (end - self.started_at).total_seconds()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "migration_id": self.migration_id,
            "status": self.status.value,
            "progress": self.progress,
            "steps_completed": self.steps_completed,
            "steps_total": self.steps_total,
            "duration_seconds": self.duration_seconds,
        }


@dataclass
class Migration:
    """A complete migration definition."""
    id: str
    name: str
    version: str
    description: str = ""
    steps: list[MigrationStep] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def add_step(self, step: MigrationStep) -> "Migration":
        """Add a step to migration."""
        self.steps.append(step)
        return self

    def add_simple_step(
        self,
        id: str,
        name: str,
        up_fn: Callable[[], bool],
        down_fn: Callable[[], bool] | None = None,
    ) -> "Migration":
        """Add a simple step with functions."""
        step = MigrationStep(id=id, name=name, up_fn=up_fn, down_fn=down_fn)
        return self.add_step(step)


class DataTransformer(ABC):
    """Base class for data transformation."""

    @abstractmethod
    def transform(self, data: Any) -> Any:
        """Transform data."""
        pass


class FieldRenameTransformer(DataTransformer):
    """Renames fields in dictionaries."""

    def __init__(self, mapping: dict[str, str]):
        self.mapping = mapping

    def transform(self, data: dict[str, Any]) -> dict[str, Any]:
        """Rename fields according to mapping."""
        result = {}
        for key, value in data.items():
            new_key = self.mapping.get(key, key)
            result[new_key] = value
        return result


class FieldTypeTransformer(DataTransformer):
    """Converts field types."""

    def __init__(self, conversions: dict[str, type]):
        self.conversions = conversions

    def transform(self, data: dict[str, Any]) -> dict[str, Any]:
        """Convert field types."""
        result = dict(data)
        for field_name, target_type in self.conversions.items():
            if field_name in result:
                try:
                    result[field_name] = target_type(result[field_name])
                except (ValueError, TypeError) as e:
                    logger.warning("Failed to convert field %r to %s: %s", field_name, target_type, e)
                    pass
        return result


class CompositeTransformer(DataTransformer):
    """Combines multiple transformers."""

    def __init__(self, transformers: list[DataTransformer]):
        self.transformers = transformers

    def transform(self, data: Any) -> Any:
        """Apply all transformers in sequence."""
        result = data
        for transformer in self.transformers:
            result = transformer.transform(result)
        return result
