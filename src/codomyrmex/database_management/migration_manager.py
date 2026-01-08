from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Union
import json
import os
import re
import time

from dataclasses import dataclass, field
import hashlib
import psycopg2
import pymysql
import sqlite3

from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring.logger_config import get_logger






#!/usr/bin/env python3
"""
Migration Management Module for Codomyrmex Database Management.

This module provides database migration management, schema versioning,
and migration execution capabilities with support for SQLite, PostgreSQL,
and MySQL databases.
"""



logger = get_logger(__name__)

# Optional database drivers
try:
    POSTGRESQL_AVAILABLE = True
except ImportError:
    psycopg2 = None
    POSTGRESQL_AVAILABLE = False

try:
    MYSQL_AVAILABLE = True
except ImportError:
    pymysql = None
    MYSQL_AVAILABLE = False


@dataclass
class Migration:
    """Database migration definition."""
    id: str
    name: str
    description: str
    sql: str
    rollback_sql: Optional[str] = None
    dependencies: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    applied_at: Optional[datetime] = None
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
    error_message: Optional[str] = None
    rows_affected: int = 0
    statements_executed: int = 0


class DatabaseConnector:
    """Handles database connections for migrations."""

    def __init__(self, database_url: str):
        """Initialize database connector from URL.

        Args:
            database_url: Database connection URL
                SQLite: sqlite:///path/to/db.sqlite
                PostgreSQL: postgresql://user:pass@host:port/database
                MySQL: mysql://user:pass@host:port/database
        """
        self.database_url = database_url
        self._connection = None
        self._db_type = self._parse_db_type(database_url)

    def _parse_db_type(self, url: str) -> str:
        """Parse database type from URL."""
        if url.startswith("sqlite"):
            return "sqlite"
        elif url.startswith("postgresql") or url.startswith("postgres"):
            return "postgresql"
        elif url.startswith("mysql"):
            return "mysql"
        else:
            raise CodomyrmexError(f"Unsupported database URL format: {url}")

    def _parse_connection_params(self) -> dict[str, Any]:
        """Parse connection parameters from URL."""
        url = self.database_url

        if self._db_type == "sqlite":
            # sqlite:///path/to/db.sqlite or sqlite:///:memory:
            match = re.match(r'sqlite:///(.+)', url)
            if match:
                return {"database": match.group(1)}
            raise CodomyrmexError(f"Invalid SQLite URL: {url}")

        # PostgreSQL or MySQL: protocol://user:pass@host:port/database
        pattern = r'(?:postgresql|postgres|mysql)://(?:([^:]+):([^@]+)@)?([^:\/]+)(?::(\d+))?/(.+)'
        match = re.match(pattern, url)
        if match:
            return {
                "user": match.group(1) or ("postgres" if self._db_type == "postgresql" else "root"),
                "password": match.group(2) or "",
                "host": match.group(3),
                "port": int(match.group(4)) if match.group(4) else (5432 if self._db_type == "postgresql" else 3306),
                "database": match.group(5)
            }
        raise CodomyrmexError(f"Invalid database URL: {url}")

    def connect(self):
        """Establish database connection."""
        params = self._parse_connection_params()

        if self._db_type == "sqlite":
            self._connection = sqlite3.connect(params["database"])
            # Enable foreign keys
            self._connection.execute("PRAGMA foreign_keys = ON")
            logger.info(f"Connected to SQLite database: {params['database']}")

        elif self._db_type == "postgresql":
            if not POSTGRESQL_AVAILABLE:
                raise CodomyrmexError(
                    "PostgreSQL driver not available. Install with: pip install psycopg2-binary"
                )
            self._connection = psycopg2.connect(
                host=params["host"],
                port=params["port"],
                database=params["database"],
                user=params["user"],
                password=params["password"]
            )
            logger.info(f"Connected to PostgreSQL database: {params['database']}")

        elif self._db_type == "mysql":
            if not MYSQL_AVAILABLE:
                raise CodomyrmexError(
                    "MySQL driver not available. Install with: pip install pymysql"
                )
            self._connection = pymysql.connect(
                host=params["host"],
                port=params["port"],
                database=params["database"],
                user=params["user"],
                password=params["password"]
            )
            logger.info(f"Connected to MySQL database: {params['database']}")

    def disconnect(self):
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("Database connection closed")

    def execute(self, sql: str, params: Optional[tuple] = None) -> tuple[int, Any]:
        """Execute SQL statement.

        Args:
            sql: SQL statement to execute
            params: Optional query parameters

        Returns:
            Tuple of (rows_affected, cursor)
        """
        if not self._connection:
            raise CodomyrmexError("Not connected to database")

        cursor = self._connection.cursor()
        try:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)

            rows_affected = cursor.rowcount if cursor.rowcount >= 0 else 0
            return rows_affected, cursor
        except Exception as e:
            raise CodomyrmexError(f"SQL execution failed: {e}")

    def execute_script(self, sql_script: str) -> tuple[int, int]:
        """Execute multiple SQL statements.

        Args:
            sql_script: SQL script with multiple statements

        Returns:
            Tuple of (total_rows_affected, statements_executed)
        """
        if not self._connection:
            raise CodomyrmexError("Not connected to database")

        # Split script into individual statements
        statements = self._split_sql_statements(sql_script)
        total_rows = 0
        statements_executed = 0

        for statement in statements:
            statement = statement.strip()
            if statement and not statement.startswith("--"):
                rows, _ = self.execute(statement)
                total_rows += rows
                statements_executed += 1

        return total_rows, statements_executed

    def _split_sql_statements(self, sql_script: str) -> list[str]:
        """Split SQL script into individual statements."""
        # Handle simple semicolon-separated statements
        statements = []
        current = []

        for line in sql_script.split('\n'):
            line = line.strip()
            if line.startswith('--'):
                continue
            current.append(line)
            if line.endswith(';'):
                statements.append('\n'.join(current))
                current = []

        if current:
            statements.append('\n'.join(current))

        return [s for s in statements if s.strip()]

    def commit(self):
        """Commit transaction."""
        if self._connection:
            self._connection.commit()

    def rollback(self):
        """Rollback transaction."""
        if self._connection:
            self._connection.rollback()

    @property
    def connection(self):
        """Get raw connection."""
        return self._connection


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
        self,
        workspace_dir: Optional[str] = None,
        database_url: Optional[str] = None
    ):
        """Initialize migration manager.

        Args:
            workspace_dir: Directory for storing migration files
            database_url: Database connection URL (optional, can be set later)
        """
        self.workspace_dir = Path(workspace_dir) if workspace_dir else Path.cwd()
        self.migrations_dir = self.workspace_dir / "migrations"
        self.migration_history_dir = self.workspace_dir / "migration_history"
        self._ensure_directories()

        self._migrations: dict[str, Migration] = {}
        self._applied_migrations: dict[str, MigrationResult] = {}
        self._database_url = database_url
        self._connector: Optional[DatabaseConnector] = None

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
            raise CodomyrmexError("Database URL not set. Call set_database_url() first.")

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
                with open(migration_file, 'r') as f:
                    data = json.load(f)

                migration = Migration(
                    id=data["id"],
                    name=data["name"],
                    description=data.get("description", ""),
                    sql=data["sql"],
                    rollback_sql=data.get("rollback_sql"),
                    dependencies=data.get("dependencies", []),
                    created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
                    status=data.get("status", "pending"),
                    checksum=data.get("checksum", "")
                )

                self._migrations[migration.id] = migration

            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Failed to load migration {migration_file}: {e}")

        logger.info(f"Loaded {len(self._migrations)} migrations from {self.migrations_dir}")

    def create_migration(
        self,
        name: str,
        description: str,
        sql: str,
        rollback_sql: Optional[str] = None,
        dependencies: Optional[list[str]] = None
    ) -> Migration:
        """Create a new migration.

        Args:
            name: Migration name
            description: Migration description
            sql: SQL to execute for the migration
            rollback_sql: SQL to execute for rollback (optional)
            dependencies: List of migration IDs this depends on

        Returns:
            Created migration
        """
        migration_id = f"migration_{int(time.time())}_{name.replace(' ', '_').lower()}"

        migration = Migration(
            id=migration_id,
            name=name,
            description=description,
            sql=sql,
            rollback_sql=rollback_sql,
            dependencies=dependencies or []
        )

        self._migrations[migration_id] = migration

        # Save migration to file
        migration_file = self.migrations_dir / f"{migration_id}.json"
        with open(migration_file, 'w') as f:
            json.dump({
                "id": migration.id,
                "name": migration.name,
                "description": migration.description,
                "sql": migration.sql,
                "rollback_sql": migration.rollback_sql,
                "dependencies": migration.dependencies,
                "created_at": migration.created_at.isoformat(),
                "status": migration.status,
                "checksum": migration.checksum
            }, f, indent=2)

        logger.info(f"Created migration: {migration_id}")
        return migration

    def apply_migration(
        self,
        migration_id: str,
        dry_run: bool = False
    ) -> MigrationResult:
        """Apply a migration to the database.

        Args:
            migration_id: ID of the migration to apply
            dry_run: If True, validate but don't execute

        Returns:
            Migration execution result
        """
        if migration_id not in self._migrations:
            raise CodomyrmexError(f"Migration not found: {migration_id}")

        migration = self._migrations[migration_id]

        # Check if already applied
        if self._is_migration_applied(migration_id):
            logger.info(f"Migration already applied: {migration_id}")
            return MigrationResult(
                migration_id=migration_id,
                success=True,
                execution_time=0.0,
                error_message="Already applied"
            )

        # Check dependencies
        for dep_id in migration.dependencies:
            if not self._is_migration_applied(dep_id):
                raise CodomyrmexError(f"Dependency migration not applied: {dep_id}")

        if dry_run:
            logger.info(f"[DRY RUN] Would apply migration: {migration_id}")
            return MigrationResult(
                migration_id=migration_id,
                success=True,
                execution_time=0.0,
                error_message="Dry run - not executed"
            )

        connector = self._get_connector()
        start_time = time.time()

        try:
            # Execute migration SQL
            rows_affected, statements_executed = connector.execute_script(migration.sql)
            execution_time = time.time() - start_time

            # Record migration in tracking table
            connector.execute(
                """INSERT INTO _migrations (id, name, description, checksum, execution_time_ms, status)
                   VALUES (?, ?, ?, ?, ?, 'applied')""",
                (migration.id, migration.name, migration.description,
                 migration.checksum, int(execution_time * 1000))
            )

            connector.commit()

            # Update migration object
            migration.applied_at = datetime.now()
            migration.status = "applied"

            result = MigrationResult(
                migration_id=migration_id,
                success=True,
                execution_time=execution_time,
                rows_affected=rows_affected,
                statements_executed=statements_executed
            )

            self._applied_migrations[migration_id] = result
            self._save_migration_history(migration, result)

            logger.info(
                f"Applied migration {migration_id}: {statements_executed} statements, "
                f"{rows_affected} rows affected in {execution_time:.3f}s"
            )

            return result

        except Exception as e:
            connector.rollback()
            execution_time = time.time() - start_time

            result = MigrationResult(
                migration_id=migration_id,
                success=False,
                execution_time=execution_time,
                error_message=str(e)
            )

            migration.status = "failed"
            logger.error(f"Failed to apply migration {migration_id}: {e}")

            return result

    def rollback_migration(self, migration_id: str) -> MigrationResult:
        """Rollback a migration.

        Args:
            migration_id: ID of the migration to rollback

        Returns:
            Rollback result
        """
        if not self._is_migration_applied(migration_id):
            raise CodomyrmexError(f"Migration not applied: {migration_id}")

        migration = self._migrations.get(migration_id)
        if not migration:
            raise CodomyrmexError(f"Migration not found: {migration_id}")

        if not migration.rollback_sql:
            raise CodomyrmexError(f"No rollback SQL defined for migration: {migration_id}")

        connector = self._get_connector()
        start_time = time.time()

        try:
            # Execute rollback SQL
            rows_affected, statements_executed = connector.execute_script(migration.rollback_sql)
            execution_time = time.time() - start_time

            # Remove from tracking table
            connector.execute("DELETE FROM _migrations WHERE id = ?", (migration_id,))
            connector.commit()

            # Update migration object
            migration.status = "rolled_back"
            migration.applied_at = None

            # Remove from applied migrations
            if migration_id in self._applied_migrations:
                del self._applied_migrations[migration_id]

            result = MigrationResult(
                migration_id=f"rollback_{migration_id}",
                success=True,
                execution_time=execution_time,
                rows_affected=rows_affected,
                statements_executed=statements_executed
            )

            logger.info(
                f"Rolled back migration {migration_id}: {statements_executed} statements, "
                f"{rows_affected} rows affected in {execution_time:.3f}s"
            )

            return result

        except Exception as e:
            connector.rollback()
            execution_time = time.time() - start_time

            result = MigrationResult(
                migration_id=f"rollback_{migration_id}",
                success=False,
                execution_time=execution_time,
                error_message=str(e)
            )

            logger.error(f"Failed to rollback migration {migration_id}: {e}")
            return result

    def _is_migration_applied(self, migration_id: str) -> bool:
        """Check if a migration has been applied."""
        try:
            connector = self._get_connector()
            _, cursor = connector.execute(
                "SELECT 1 FROM _migrations WHERE id = ? AND status = 'applied'",
                (migration_id,)
            )
            return cursor.fetchone() is not None
        except Exception:
            return False

    def _save_migration_history(self, migration: Migration, result: MigrationResult):
        """Save migration result to history file."""
        history_file = self.migration_history_dir / f"{migration.id}_history.json"
        with open(history_file, 'w') as f:
            json.dump({
                "migration_id": migration.id,
                "name": migration.name,
                "applied_at": migration.applied_at.isoformat() if migration.applied_at else None,
                "success": result.success,
                "execution_time": result.execution_time,
                "rows_affected": result.rows_affected,
                "statements_executed": result.statements_executed,
                "error_message": result.error_message
            }, f, indent=2)

    def get_migration_status(self, migration_id: str) -> Optional[dict[str, Any]]:
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
            "applied_at": migration.applied_at.isoformat() if migration.applied_at else None,
            "dependencies": migration.dependencies,
            "checksum": migration.checksum
        }

    def list_migrations(self) -> list[dict[str, Any]]:
        """List all migrations with their status."""
        migrations = []

        for migration in self._migrations.values():
            is_applied = self._is_migration_applied(migration.id)
            migrations.append({
                "id": migration.id,
                "name": migration.name,
                "description": migration.description,
                "status": "applied" if is_applied else migration.status,
                "applied_at": migration.applied_at.isoformat() if migration.applied_at else None,
                "dependencies": migration.dependencies,
                "checksum": migration.checksum
            })

        # Sort by ID (which includes timestamp)
        migrations.sort(key=lambda m: m["id"])
        return migrations

    def get_pending_migrations(self) -> list[Migration]:
        """Get list of migrations that haven't been applied yet."""
        pending = []
        for migration in self._migrations.values():
            if not self._is_migration_applied(migration.id):
                pending.append(migration)
        return sorted(pending, key=lambda m: m.id)

    def apply_pending_migrations(self) -> list[MigrationResult]:
        """Apply all pending migrations in order."""
        pending = self.get_pending_migrations()
        results = []

        for migration in pending:
            result = self.apply_migration(migration.id)
            results.append(result)
            if not result.success:
                logger.warning(f"Stopping migration due to failure: {migration.id}")
                break

        return results

    def close(self):
        """Close database connection."""
        if self._connector:
            self._connector.disconnect()
            self._connector = None


def run_migrations(
    migration_dir: str,
    database_url: str,
    direction: str = "up"
) -> dict[str, Any]:
    """Run database migrations.

    Args:
        migration_dir: Directory containing migration files
        database_url: Database connection URL
        direction: Migration direction ("up" or "down")

    Returns:
        Migration execution results
    """
    manager = MigrationManager(workspace_dir=migration_dir, database_url=database_url)

    try:
        # Load migrations from directory
        manager.load_migrations_from_directory()
        all_migrations = manager.list_migrations()

        if direction == "up":
            # Apply all pending migrations
            results = manager.apply_pending_migrations()

            successful = sum(1 for r in results if r.success)
            failed = len(results) - successful

            return {
                "direction": "up",
                "migrations_processed": len(results),
                "successful": successful,
                "failed": failed,
                "success": failed == 0,
                "results": [
                    {
                        "migration_id": r.migration_id,
                        "success": r.success,
                        "execution_time": r.execution_time,
                        "error_message": r.error_message
                    }
                    for r in results
                ]
            }

        elif direction == "down":
            # Rollback the most recently applied migration
            applied = [m for m in all_migrations if m["status"] == "applied"]
            if not applied:
                return {
                    "direction": "down",
                    "migrations_processed": 0,
                    "success": True,
                    "message": "No migrations to rollback"
                }

            # Get most recent migration
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
                    "error_message": result.error_message
                }
            }

        else:
            raise CodomyrmexError(f"Invalid migration direction: {direction}")

    finally:
        manager.close()
