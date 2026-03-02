"""
Migration Runner

Executes migrations and data transformations.
"""

import threading
from datetime import datetime
from typing import Any

from .models import (
    CompositeTransformer,
    DataTransformer,
    Migration,
    MigrationDirection,
    MigrationResult,
    MigrationStatus,
)


class MigrationRunner:
    """
    Runs migrations.

    Usage:
        runner = MigrationRunner()

        migration = Migration(id="v1_to_v2", name="Upgrade to V2", version="2.0")
        migration.add_simple_step(
            id="add_column",
            name="Add new column",
            up_fn=lambda: True,
            down_fn=lambda: True,
        )

        result = runner.run(migration)
    """

    def __init__(self):
        """Initialize this instance."""
        self._completed: list[str] = []
        self._lock = threading.Lock()

    def run(
        self,
        migration: Migration,
        direction: MigrationDirection = MigrationDirection.UP,
    ) -> MigrationResult:
        """Run a migration."""
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
        migrator.add_transformer(FieldRenameTransformer({"old_field": "new_field"}))
        new_data = migrator.migrate([{"old_field": "value1"}])
    """

    def __init__(self):
        """Initialize this instance."""
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
