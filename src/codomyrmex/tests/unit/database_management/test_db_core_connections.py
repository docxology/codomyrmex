"""
Tests for database_management connections and migration manager:
DatabaseConnector URL parsing, SQLite operations, and MigrationManager
end-to-end workflows with in-memory SQLite.

Split from test_database_core.py to reduce file size.
"""

import sqlite3

import pytest

from codomyrmex.database_management.migration.migration_manager import (
    DatabaseConnector,
    MigrationManager,
)
from codomyrmex.exceptions import CodomyrmexError

# =============================================================================
# DatabaseConnector Tests
# =============================================================================

class TestDatabaseConnector:
    """Test DatabaseConnector URL parsing and SQLite operations."""

    @pytest.mark.unit
    def test_parse_sqlite_url(self, tmp_path):
        """SQLite URL is parsed correctly."""
        db_path = str(tmp_path / "test.db")
        connector = DatabaseConnector(f"sqlite:///{db_path}")
        assert connector._db_type == "sqlite"

    @pytest.mark.unit
    def test_parse_postgresql_url(self):
        """PostgreSQL URL is parsed correctly."""
        connector = DatabaseConnector("postgresql://user:pass@localhost:5432/mydb")
        assert connector._db_type == "postgresql"

    @pytest.mark.unit
    def test_parse_mysql_url(self):
        """MySQL URL is parsed correctly."""
        connector = DatabaseConnector("mysql://user:pass@localhost:3306/mydb")
        assert connector._db_type == "mysql"

    @pytest.mark.unit
    def test_parse_unsupported_url(self):
        """Unsupported URL scheme raises CodomyrmexError."""
        with pytest.raises(CodomyrmexError, match="Unsupported database URL"):
            DatabaseConnector("mongodb://localhost/db")

    @pytest.mark.unit
    def test_execute_without_connection_raises(self, tmp_path):
        """Execute without connecting raises CodomyrmexError."""
        db_path = str(tmp_path / "test.db")
        connector = DatabaseConnector(f"sqlite:///{db_path}")
        with pytest.raises(CodomyrmexError, match="Not connected"):
            connector.execute("SELECT 1")

    @pytest.mark.unit
    def test_connect_and_execute(self, tmp_path):
        """Connect to SQLite and execute a simple query."""
        db_path = str(tmp_path / "test.db")
        connector = DatabaseConnector(f"sqlite:///{db_path}")
        connector.connect()
        rows, cursor = connector.execute("SELECT 1 AS val")
        assert cursor.fetchone()[0] == 1
        connector.disconnect()

    @pytest.mark.unit
    def test_execute_script(self, tmp_path):
        """execute_script runs multiple statements and counts them."""
        db_path = str(tmp_path / "test.db")
        connector = DatabaseConnector(f"sqlite:///{db_path}")
        connector.connect()
        script = (
            "CREATE TABLE t (id INTEGER PRIMARY KEY);\n"
            "INSERT INTO t VALUES (1);\n"
            "INSERT INTO t VALUES (2);\n"
        )
        total_rows, stmts = connector.execute_script(script)
        connector.commit()
        assert stmts == 3

        _, cursor = connector.execute("SELECT COUNT(*) FROM t")
        assert cursor.fetchone()[0] == 2
        connector.disconnect()


# =============================================================================
# MigrationManager with In-Memory SQLite Tests
# =============================================================================

class TestMigrationManagerSQLite:
    """Test MigrationManager end-to-end with in-memory SQLite."""

    @pytest.mark.unit
    def test_create_migration(self, tmp_path):
        """create_migration stores migration and saves JSON file."""
        mm = MigrationManager(workspace_dir=str(tmp_path))
        m = mm.create_migration(
            name="create users",
            description="Create users table",
            sql="CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT);",
            rollback_sql="DROP TABLE users;",
        )
        assert m.id in mm._migrations
        assert m.name == "create users"
        assert m.checksum  # non-empty
        # JSON file saved
        json_files = list((tmp_path / "migrations").glob("*.json"))
        assert len(json_files) == 1

    @pytest.mark.unit
    def test_apply_migration_to_sqlite(self, tmp_path):
        """apply_migration executes SQL against in-memory SQLite via connector."""
        db_path = str(tmp_path / "test.db")
        mm = MigrationManager(
            workspace_dir=str(tmp_path),
            database_url=f"sqlite:///{db_path}",
        )
        m = mm.create_migration(
            name="create table",
            description="Create users",
            sql="CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT);",
            rollback_sql="DROP TABLE users;",
        )
        result = mm.apply_migration(m.id)
        assert result.success is True
        assert result.statements_executed >= 1
        mm.close()

    @pytest.mark.unit
    def test_apply_migration_dry_run(self, tmp_path):
        """apply_migration with dry_run=True does not execute SQL."""
        db_path = str(tmp_path / "test.db")
        mm = MigrationManager(
            workspace_dir=str(tmp_path),
            database_url=f"sqlite:///{db_path}",
        )
        m = mm.create_migration(
            name="create table",
            description="test",
            sql="CREATE TABLE users (id INTEGER PRIMARY KEY);",
        )
        result = mm.apply_migration(m.id, dry_run=True)
        assert result.success is True
        assert "Dry run" in (result.error_message or "")

        # Table should NOT exist
        conn = sqlite3.connect(db_path)
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        assert cursor.fetchone() is None
        conn.close()
        mm.close()

    @pytest.mark.unit
    def test_apply_migration_idempotent(self, tmp_path):
        """Applying same migration twice returns already-applied result."""
        db_path = str(tmp_path / "test.db")
        mm = MigrationManager(
            workspace_dir=str(tmp_path),
            database_url=f"sqlite:///{db_path}",
        )
        m = mm.create_migration(
            name="create table",
            description="test",
            sql="CREATE TABLE users (id INTEGER PRIMARY KEY);",
        )
        mm.apply_migration(m.id)
        result = mm.apply_migration(m.id)
        assert result.success is True
        assert "Already applied" in (result.error_message or "")
        mm.close()

    @pytest.mark.unit
    def test_rollback_migration(self, tmp_path):
        """rollback_migration reverts a previously applied migration."""
        db_path = str(tmp_path / "test.db")
        mm = MigrationManager(
            workspace_dir=str(tmp_path),
            database_url=f"sqlite:///{db_path}",
        )
        m = mm.create_migration(
            name="create table",
            description="test",
            sql="CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT);",
            rollback_sql="DROP TABLE users;",
        )
        mm.apply_migration(m.id)
        result = mm.rollback_migration(m.id)
        assert result.success is True

        # users table should be gone
        conn = sqlite3.connect(db_path)
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        assert cursor.fetchone() is None
        conn.close()
        mm.close()

    @pytest.mark.unit
    def test_dependency_check_blocks_migration(self, tmp_path):
        """Migration with unmet dependency raises CodomyrmexError."""
        db_path = str(tmp_path / "test.db")
        mm = MigrationManager(
            workspace_dir=str(tmp_path),
            database_url=f"sqlite:///{db_path}",
        )
        m = mm.create_migration(
            name="dependent",
            description="depends on missing",
            sql="SELECT 1;",
            dependencies=["nonexistent_migration"],
        )
        with pytest.raises(CodomyrmexError, match="Dependency migration not applied"):
            mm.apply_migration(m.id)
        mm.close()

    @pytest.mark.unit
    def test_apply_migration_not_found(self, tmp_path):
        """Applying a non-existent migration ID raises CodomyrmexError."""
        mm = MigrationManager(workspace_dir=str(tmp_path))
        with pytest.raises(CodomyrmexError, match="Migration not found"):
            mm.apply_migration("nonexistent")

    @pytest.mark.unit
    def test_rollback_not_applied_raises(self, tmp_path):
        """Rolling back a migration that was never applied raises error."""
        db_path = str(tmp_path / "test.db")
        mm = MigrationManager(
            workspace_dir=str(tmp_path),
            database_url=f"sqlite:///{db_path}",
        )
        m = mm.create_migration(
            name="not applied",
            description="test",
            sql="SELECT 1;",
            rollback_sql="SELECT 1;",
        )
        with pytest.raises(CodomyrmexError, match="Migration not applied"):
            mm.rollback_migration(m.id)
        mm.close()

    @pytest.mark.unit
    def test_rollback_no_rollback_sql_raises(self, tmp_path):
        """Rolling back a migration without rollback_sql raises error."""
        db_path = str(tmp_path / "test.db")
        mm = MigrationManager(
            workspace_dir=str(tmp_path),
            database_url=f"sqlite:///{db_path}",
        )
        m = mm.create_migration(
            name="no rollback",
            description="test",
            sql="CREATE TABLE t (id INTEGER);",
        )
        mm.apply_migration(m.id)
        with pytest.raises(CodomyrmexError, match="No rollback SQL defined"):
            mm.rollback_migration(m.id)
        mm.close()
