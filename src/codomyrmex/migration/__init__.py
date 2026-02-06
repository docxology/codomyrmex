"""
Migration Module

Provider and data migration tools.
"""

__version__ = "0.1.0"

import json
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, TypeVar
from collections.abc import Callable

T = TypeVar('T')


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
        step = MigrationStep(
            id=id,
            name=name,
            up_fn=up_fn,
            down_fn=down_fn,
        )
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
        for field, target_type in self.conversions.items():
            if field in result:
                try:
                    result[field] = target_type(result[field])
                except (ValueError, TypeError):
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


class MigrationRunner:
    """
    Runs migrations.

    Usage:
        runner = MigrationRunner()

        migration = Migration(id="v1_to_v2", name="Upgrade to V2", version="2.0")
        migration.add_simple_step(
            id="add_column",
            name="Add new column",
            up_fn=lambda: db.execute("ALTER TABLE..."),
            down_fn=lambda: db.execute("ALTER TABLE DROP..."),
        )

        result = runner.run(migration)
    """

    def __init__(self):
        self._completed: list[str] = []
        self._lock = threading.Lock()

    def run(
        self,
        migration: Migration,
        direction: MigrationDirection = MigrationDirection.UP,
    ) -> MigrationResult:
        """
        Run a migration.

        Args:
            migration: The migration to run
            direction: UP (migrate) or DOWN (rollback)

        Returns:
            MigrationResult with status
        """
        result = MigrationResult(
            migration_id=migration.id,
            status=MigrationStatus.RUNNING,
            steps_total=len(migration.steps),
        )

        steps = migration.steps if direction == MigrationDirection.UP else reversed(migration.steps)

        try:
            for step in steps:
                success = step.run_up() if direction == MigrationDirection.UP else step.run_down()

                if success:
                    result.steps_completed += 1
                else:
                    result.status = MigrationStatus.FAILED
                    result.error = f"Step '{step.id}' failed"
                    break

            if result.status == MigrationStatus.RUNNING:
                result.status = MigrationStatus.COMPLETED
                with self._lock:
                    if direction == MigrationDirection.UP:
                        self._completed.append(migration.id)
                    else:
                        if migration.id in self._completed:
                            self._completed.remove(migration.id)

        except Exception as e:
            result.status = MigrationStatus.FAILED
            result.error = str(e)

        result.completed_at = datetime.now()
        return result

    def rollback(self, migration: Migration) -> MigrationResult:
        """Rollback a migration."""
        return self.run(migration, direction=MigrationDirection.DOWN)

    def get_completed(self) -> list[str]:
        """Get list of completed migration IDs."""
        return list(self._completed)

    def is_completed(self, migration_id: str) -> bool:
        """Check if migration is completed."""
        return migration_id in self._completed


class DataMigrator:
    """
    Migrates data with transformations.

    Usage:
        migrator = DataMigrator()

        # Add transformers
        migrator.add_transformer(FieldRenameTransformer({"old_field": "new_field"}))

        # Migrate data
        old_data = [{"old_field": "value1"}, {"old_field": "value2"}]
        new_data = migrator.migrate(old_data)
    """

    def __init__(self):
        self._transformers: list[DataTransformer] = []

    def add_transformer(self, transformer: DataTransformer) -> "DataMigrator":
        """Add a transformer."""
        self._transformers.append(transformer)
        return self

    def migrate(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Migrate a list of records."""
        result = []
        transformer = CompositeTransformer(self._transformers)

        for record in data:
            transformed = transformer.transform(record)
            result.append(transformed)

        return result

    def migrate_single(self, record: dict[str, Any]) -> dict[str, Any]:
        """Migrate a single record."""
        transformer = CompositeTransformer(self._transformers)
        return transformer.transform(record)


__all__ = [
    # Enums
    "MigrationStatus",
    "MigrationDirection",
    # Data classes
    "MigrationStep",
    "MigrationResult",
    "Migration",
    # Transformers
    "DataTransformer",
    "FieldRenameTransformer",
    "FieldTypeTransformer",
    "CompositeTransformer",
    # Core
    "MigrationRunner",
    "DataMigrator",
]
