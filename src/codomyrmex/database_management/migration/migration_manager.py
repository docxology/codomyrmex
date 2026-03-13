#!/usr/bin/env python3
"""Migration Management Module for Codomyrmex Database Management.

This module provides database migration management, schema versioning,
and migration execution capabilities with support for SQLite, PostgreSQL,
and MySQL databases.
"""

import hashlib
import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring import get_logger

from ._db_connector import DatabaseConnector

logger = get_logger(__name__)

__all__ = [
    "DatabaseConnector",
    "Migration",
    "MigrationManager",
    "MigrationResult",
    "run_migrations",
]


@dataclass
class Migration:
    """Database migration definition."""

    id: str
    name: str
    description: str
    sql: str
    rollback_sql: str | None = None
    dependencies: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    applied_at: datetime | None = None
    status: str = "pending"  # "pending", "applied", "failed", "rolled_back"
    checksum: str = ""

    def __post_init__(self):
        """Calculate checksum for migration SQL."""
        if not self.checksum:
            self.checksum = hashlib.sha256(self.sql.encode()).hexdigest()[:16]


@dataclass
class MigrationResult:
    """Result of a migration execution."""

    migration_id: str
    success: bool
    execution_time: float
    error_message: str | None = None
    rows_affected: int = 0
    statements_executed: int = 0


class MigrationManager:
    """Database migration management system."""

    MIGRATION_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS _migrations (
        id VARCHAR(255) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        checksum VARCHAR(64),
        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        execution_time_ms INTEGER,
        status VARCHAR(50) DEFAULT 'applied'
    )
    """

    def __init__(
        self, workspace_dir: str | None = None, database_url: str | None = None
    ):
        """Initialize migration manager."""
        self.workspace_dir = Path(workspace_dir) if workspace_dir else Path.cwd()
        self.migrations_dir = self.workspace_dir / "migrations"
        self.migration_history_dir = self.workspace_dir / "migration_history"
        self._ensure_directories()
        self._migrations: dict[str, Migration] = {}
        self._applied_migrations: dict[str, MigrationResult] = {}
        self._database_url = database_url
        self._connector: DatabaseConnector | None = None

    def _ensure_directories(self):
        """Ensure required directories exist."""
        self.migrations_dir.mkdir(parents=True, exist_ok=True)
        self.migration_history_dir.mkdir(parents=True, exist_ok=True)

    def set_database_url(self, database_url: str):
        """Set the database URL for migrations."""
        self._database_url = database_url
        self._connector = None

    def _get_connector(self) -> DatabaseConnector:
        """Get or create database connector."""
        if not self._database_url:
            raise CodomyrmexError(
                "Database URL not set. Call set_database_url() first."
            )
        if not self._connector:
            self._connector = DatabaseConnector(self._database_url)
            self._connector.connect()
            self._ensure_migration_table()
        return self._connector

    def _ensure_migration_table(self):
        """Ensure migration tracking table exists."""
        if self._connector:
            self._connector.execute(self.MIGRATION_TABLE_SQL)
            self._connector.commit()

    def load_migrations_from_directory(self):
        """Load all migrations from the migrations directory."""
        self._migrations.clear()
        for migration_file in sorted(self.migrations_dir.glob("*.json")):
            try:
                with open(migration_file) as f:
                    data = json.load(f)
                migration = Migration(
                    id=data["id"],
                    name=data["name"],
                    description=data.get("description", ""),
                    sql=data["sql"],
                    rollback_sql=data.get("rollback_sql"),
                    dependencies=data.get("dependencies", []),
                    created_at=datetime.fromisoformat(
                        data.get("created_at", datetime.now().isoformat())
                    ),
                    status=data.get("status", "pending"),
                    checksum=data.get("checksum", ""),
                )
                self._migrations[migration.id] = migration
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning("Failed to load migration %s: %s", migration_file, e)
        logger.info(
            "Loaded %s migrations from %s", len(self._migrations), self.migrations_dir
        )

    def _serialize_migration(self, migration: "Migration") -> dict[str, Any]:
        """Serialize a migration to a JSON-safe dict."""
        return {
            "id": migration.id,
            "name": migration.name,
            "description": migration.description,
            "sql": migration.sql,
            "rollback_sql": migration.rollback_sql,
            "dependencies": migration.dependencies,
            "created_at": migration.created_at.isoformat(),
            "status": migration.status,
            "checksum": migration.checksum,
        }

    def create_migration(
        self,
        name: str,
        description: str,
        sql: str,
        rollback_sql: str | None = None,
        dependencies: list[str] | None = None,
    ) -> "Migration":
        """Create a new migration and persist it to disk."""
        migration_id = f"migration_{int(time.time())}_{name.replace(' ', '_').lower()}"
        migration = Migration(
            id=migration_id,
            name=name,
            description=description,
            sql=sql,
            rollback_sql=rollback_sql,
            dependencies=dependencies or [],
        )
        self._migrations[migration_id] = migration
        migration_file = self.migrations_dir / f"{migration_id}.json"
        with open(migration_file, "w") as f:
            json.dump(self._serialize_migration(migration), f, indent=2)
        logger.info("Created migration: %s", migration_id)
        return migration

    def _check_apply_preconditions(
        self, migration_id: str, migration: "Migration", dry_run: bool
    ) -> "MigrationResult | None":
        """Return a short-circuit MigrationResult if apply should not proceed, else None."""
        if self._is_migration_applied(migration_id):
            logger.info("Migration already applied: %s", migration_id)
            return MigrationResult(
                migration_id=migration_id,
                success=True,
                execution_time=0.0,
                error_message="Already applied",
            )
        for dep_id in migration.dependencies:
            if not self._is_migration_applied(dep_id):
                raise CodomyrmexError(f"Dependency migration not applied: {dep_id}")
        if dry_run:
            logger.info("[DRY RUN] Would apply migration: %s", migration_id)
            return MigrationResult(
                migration_id=migration_id,
                success=True,
                execution_time=0.0,
                error_message="Dry run - not executed",
            )
        return None

    def _record_applied(
        self,
        connector: DatabaseConnector,
        migration: "Migration",
        execution_time: float,
    ):
        """Insert migration record into tracking table and commit."""
        connector.execute(
            "INSERT INTO _migrations (id, name, description, checksum, execution_time_ms, status) VALUES (?, ?, ?, ?, ?, 'applied')",
            (
                migration.id,
                migration.name,
                migration.description,
                migration.checksum,
                int(execution_time * 1000),
            ),
        )
        connector.commit()
        migration.applied_at = datetime.now()
        migration.status = "applied"

    def apply_migration(
        self, migration_id: str, dry_run: bool = False
    ) -> "MigrationResult":
        """Apply a migration to the database."""
        if migration_id not in self._migrations:
            raise CodomyrmexError(f"Migration not found: {migration_id}")
        migration = self._migrations[migration_id]
        early = self._check_apply_preconditions(migration_id, migration, dry_run)
        if early is not None:
            return early
        connector = self._get_connector()
        start_time = time.time()
        try:
            rows_affected, statements_executed = connector.execute_script(migration.sql)
            execution_time = time.time() - start_time
            self._record_applied(connector, migration, execution_time)
            result = MigrationResult(
                migration_id=migration_id,
                success=True,
                execution_time=execution_time,
                rows_affected=rows_affected,
                statements_executed=statements_executed,
            )
            self._applied_migrations[migration_id] = result
            self._save_migration_history(migration, result)
            logger.info(
                "Applied migration %s: %s stmts, %s rows in %.3fs",
                migration_id,
                statements_executed,
                rows_affected,
                execution_time,
            )
            return result
        except Exception as e:
            connector.rollback()
            execution_time = time.time() - start_time
            migration.status = "failed"
            logger.error("Failed to apply migration %s: %s", migration_id, e)
            return MigrationResult(
                migration_id=migration_id,
                success=False,
                execution_time=execution_time,
                error_message=str(e),
            )

    def rollback_migration(self, migration_id: str) -> "MigrationResult":
        """Rollback a migration."""
        if not self._is_migration_applied(migration_id):
            raise CodomyrmexError(f"Migration not applied: {migration_id}")
        migration = self._migrations.get(migration_id)
        if not migration:
            raise CodomyrmexError(f"Migration not found: {migration_id}")
        if not migration.rollback_sql:
            raise CodomyrmexError(
                f"No rollback SQL defined for migration: {migration_id}"
            )
        connector = self._get_connector()
        start_time = time.time()
        try:
            rows_affected, statements_executed = connector.execute_script(
                migration.rollback_sql
            )
            execution_time = time.time() - start_time
            connector.execute("DELETE FROM _migrations WHERE id = ?", (migration_id,))
            connector.commit()
            migration.status = "rolled_back"
            migration.applied_at = None
            self._applied_migrations.pop(migration_id, None)
            result = MigrationResult(
                migration_id=f"rollback_{migration_id}",
                success=True,
                execution_time=execution_time,
                rows_affected=rows_affected,
                statements_executed=statements_executed,
            )
            logger.info(
                "Rolled back migration %s: %s stmts, %s rows in %.3fs",
                migration_id,
                statements_executed,
                rows_affected,
                execution_time,
            )
            return result
        except Exception as e:
            connector.rollback()
            execution_time = time.time() - start_time
            logger.error("Failed to rollback migration %s: %s", migration_id, e)
            return MigrationResult(
                migration_id=f"rollback_{migration_id}",
                success=False,
                execution_time=execution_time,
                error_message=str(e),
            )

    def _is_migration_applied(self, migration_id: str) -> bool:
        """Check if a migration has been applied."""
        try:
            connector = self._get_connector()
            _, cursor = connector.execute(
                "SELECT 1 FROM _migrations WHERE id = ? AND status = 'applied'",
                (migration_id,),
            )
            return cursor.fetchone() is not None
        except Exception as e:
            logger.warning(
                "Failed to check migration applied status for %s: %s", migration_id, e
            )
            return False

    def _save_migration_history(
        self, migration: "Migration", result: "MigrationResult"
    ):
        """Save migration result to history file."""
        history_file = self.migration_history_dir / f"{migration.id}_history.json"
        with open(history_file, "w") as f:
            json.dump(
                {
                    "migration_id": migration.id,
                    "name": migration.name,
                    "applied_at": migration.applied_at.isoformat()
                    if migration.applied_at
                    else None,
                    "success": result.success,
                    "execution_time": result.execution_time,
                    "rows_affected": result.rows_affected,
                    "statements_executed": result.statements_executed,
                    "error_message": result.error_message,
                },
                f,
                indent=2,
            )

    def get_migration_status(self, migration_id: str) -> dict[str, Any] | None:
        """Get status of a migration."""
        if migration_id not in self._migrations:
            return None
        migration = self._migrations[migration_id]
        is_applied = self._is_migration_applied(migration_id)
        return {
            "id": migration.id,
            "name": migration.name,
            "description": migration.description,
            "status": "applied" if is_applied else migration.status,
            "applied_at": migration.applied_at.isoformat()
            if migration.applied_at
            else None,
            "dependencies": migration.dependencies,
            "checksum": migration.checksum,
        }

    def list_migrations(self) -> list[dict[str, Any]]:
        """List all migrations with their status."""
        migrations = []
        for migration in self._migrations.values():
            is_applied = self._is_migration_applied(migration.id)
            migrations.append(
                {
                    "id": migration.id,
                    "name": migration.name,
                    "description": migration.description,
                    "status": "applied" if is_applied else migration.status,
                    "applied_at": migration.applied_at.isoformat()
                    if migration.applied_at
                    else None,
                    "dependencies": migration.dependencies,
                    "checksum": migration.checksum,
                }
            )
        migrations.sort(key=lambda m: m["id"])
        return migrations

    def get_pending_migrations(self) -> list["Migration"]:
        """Get list of migrations that haven't been applied yet."""
        return sorted(
            [
                m
                for m in self._migrations.values()
                if not self._is_migration_applied(m.id)
            ],
            key=lambda m: m.id,
        )

    def apply_pending_migrations(self) -> list["MigrationResult"]:
        """Apply all pending migrations in order."""
        results = []
        for migration in self.get_pending_migrations():
            result = self.apply_migration(migration.id)
            results.append(result)
            if not result.success:
                logger.warning("Stopping migration due to failure: %s", migration.id)
                break
        return results

    def close(self):
        """Close database connection."""
        if self._connector:
            self._connector.disconnect()
            self._connector = None


def run_migrations(
    migration_dir: str, database_url: str, direction: str = "up"
) -> dict[str, Any]:
    """Run database migrations. direction is 'up' or 'down'."""
    manager = MigrationManager(workspace_dir=migration_dir, database_url=database_url)
    try:
        manager.load_migrations_from_directory()
        all_migrations = manager.list_migrations()
        if direction == "up":
            results = manager.apply_pending_migrations()
            successful = sum(1 for r in results if r.success)
            return {
                "direction": "up",
                "migrations_processed": len(results),
                "successful": successful,
                "failed": len(results) - successful,
                "success": len(results) == successful,
                "results": [
                    {
                        "migration_id": r.migration_id,
                        "success": r.success,
                        "execution_time": r.execution_time,
                        "error_message": r.error_message,
                    }
                    for r in results
                ],
            }
        if direction == "down":
            applied = [m for m in all_migrations if m["status"] == "applied"]
            if not applied:
                return {
                    "direction": "down",
                    "migrations_processed": 0,
                    "success": True,
                    "message": "No migrations to rollback",
                }
            latest = max(applied, key=lambda m: m.get("applied_at") or "")
            result = manager.rollback_migration(latest["id"])
            return {
                "direction": "down",
                "migrations_processed": 1,
                "success": result.success,
                "result": {
                    "migration_id": result.migration_id,
                    "success": result.success,
                    "execution_time": result.execution_time,
                    "error_message": result.error_message,
                },
            }
        raise CodomyrmexError(f"Invalid migration direction: {direction}")
    finally:
        manager.close()
