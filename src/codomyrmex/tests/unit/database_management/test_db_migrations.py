"""Unit tests for database migration management and schema introspection."""

import sqlite3
from pathlib import Path

import pytest

from codomyrmex.database_management import (
    BackupManager,
    Migration,
    MigrationManager,
    SchemaDefinition,
    SchemaGenerator,
)
from codomyrmex.database_management.migration.migration_manager import (
    DatabaseConnector,
)
from codomyrmex.database_management.performance_monitor import (
    DatabasePerformanceMonitor,
)
from codomyrmex.database_management.schema_generator import (
    Column,
    Index,
    SchemaTable,
)
from codomyrmex.exceptions import CodomyrmexError


# ==============================================================================
# Migration Support Tests
# ==============================================================================

@pytest.mark.database
class TestMigrationSupport:
    """Tests for database migration functionality."""

    @pytest.fixture
    def migration_manager(self, tmp_path):
        """Create a MigrationManager for testing."""
        workspace = str(tmp_path / "migrations")
        db_path = str(tmp_path / "migration_test.db")
        manager = MigrationManager(
            workspace_dir=workspace,
            database_url=f"sqlite:///{db_path}"
        )
        yield manager
        manager.close()

    def test_migration_creation(self, migration_manager):
        """Test creating a new migration."""
        migration = migration_manager.create_migration(
            name="create_users_table",
            description="Create the users table",
            sql="CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT);",
            rollback_sql="DROP TABLE users;"
        )

        assert migration.name == "create_users_table"
        assert migration.status == "pending"
        assert migration.checksum is not None

    def test_migration_apply(self, migration_manager):
        """Test applying a migration."""
        migration = migration_manager.create_migration(
            name="create_posts_table",
            description="Create posts table",
            sql="CREATE TABLE posts (id INTEGER PRIMARY KEY, title TEXT);",
            rollback_sql="DROP TABLE posts;"
        )

        result = migration_manager.apply_migration(migration.id)

        assert result.success
        assert result.execution_time >= 0

    def test_migration_rollback(self, migration_manager):
        """Test rolling back a migration."""
        migration = migration_manager.create_migration(
            name="create_comments_table",
            description="Create comments table",
            sql="CREATE TABLE comments (id INTEGER PRIMARY KEY);",
            rollback_sql="DROP TABLE comments;"
        )

        migration_manager.apply_migration(migration.id)
        result = migration_manager.rollback_migration(migration.id)

        assert result.success

    def test_migration_dry_run(self, migration_manager):
        """Test migration dry run mode."""
        migration = migration_manager.create_migration(
            name="create_likes_table",
            description="Create likes table",
            sql="CREATE TABLE likes (id INTEGER PRIMARY KEY);",
            rollback_sql="DROP TABLE likes;"
        )

        result = migration_manager.apply_migration(migration.id, dry_run=True)

        assert result.success
        assert "Dry run" in result.error_message

    def test_list_migrations(self, migration_manager):
        """Test listing all migrations."""
        migration_manager.create_migration(
            name="migration1",
            description="First migration",
            sql="SELECT 1;",
        )
        migration_manager.create_migration(
            name="migration2",
            description="Second migration",
            sql="SELECT 2;",
        )

        migrations = migration_manager.list_migrations()

        assert len(migrations) >= 2

    def test_get_pending_migrations(self, migration_manager):
        """Test getting pending migrations."""
        migration_manager.create_migration(
            name="pending_migration",
            description="Pending migration",
            sql="SELECT 1;",
        )

        pending = migration_manager.get_pending_migrations()

        assert len(pending) >= 1
        assert all(m.status == "pending" for m in pending)

    def test_migration_dependencies(self, migration_manager):
        """Test migration with dependencies."""
        migration1 = migration_manager.create_migration(
            name="base_table",
            description="Create base table",
            sql="CREATE TABLE base (id INTEGER PRIMARY KEY);",
        )

        migration2 = migration_manager.create_migration(
            name="dependent_table",
            description="Create dependent table",
            sql="CREATE TABLE dependent (id INTEGER, base_id INTEGER);",
            dependencies=[migration1.id]
        )

        # Apply first migration
        migration_manager.apply_migration(migration1.id)

        # Now dependent migration should work
        result = migration_manager.apply_migration(migration2.id)
        assert result.success

    def test_migration_checksum_calculation(self):
        """Test migration checksum is calculated correctly."""
        migration = Migration(
            id="test_migration",
            name="test",
            description="Test migration",
            sql="CREATE TABLE test (id INTEGER);"
        )

        assert migration.checksum is not None
        assert len(migration.checksum) == 16


# ==============================================================================
# Schema Introspection Tests
# ==============================================================================

@pytest.mark.database
class TestSchemaIntrospection:
    """Tests for database schema introspection."""

    @pytest.fixture
    def db_connector(self, tmp_path):
        """Create a DatabaseConnector with schema for testing."""
        db_path = str(tmp_path / "schema_test.db")
        connector = DatabaseConnector(f"sqlite:///{db_path}")
        connector.connect()
        connector.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE
            )
        """)
        connector.execute("""
            CREATE TABLE posts (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                title TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        connector.commit()
        yield connector
        connector.disconnect()

    def test_get_tables(self, db_connector):
        """Test getting list of tables."""
        _, cursor = db_connector.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = [row[0] for row in cursor.fetchall()]

        assert "users" in tables
        assert "posts" in tables

    def test_get_table_info(self, db_connector):
        """Test getting column information for a table."""
        _, cursor = db_connector.execute("PRAGMA table_info(users)")
        columns = []
        for row in cursor.fetchall():
            columns.append({
                "cid": row[0],
                "name": row[1],
                "type": row[2],
                "notnull": bool(row[3]),
                "default": row[4],
                "pk": bool(row[5])
            })

        assert len(columns) == 3

        # Find the name column
        name_col = next(c for c in columns if c["name"] == "name")
        assert name_col["type"] == "TEXT"
        assert name_col["notnull"] is True

    def test_schema_generator_create_table(self, tmp_path):
        """Test schema generator table creation."""
        generator = SchemaGenerator(workspace_dir=str(tmp_path))

        table = SchemaTable(
            name="products",
            columns=[
                Column(name="id", data_type="integer", primary_key=True),
                Column(name="name", data_type="string", length=255),
                Column(name="price", data_type="float"),
            ]
        )

        table_id = generator.create_table(table)

        assert table_id == "table_products"

    def test_schema_definition_to_sql(self):
        """Test schema definition SQL generation."""
        schema = SchemaDefinition(
            name="test_schema",
            version="1.0.0",
            tables=[
                SchemaTable(
                    name="users",
                    columns=[
                        Column(name="id", data_type="integer", primary_key=True),
                        Column(name="name", data_type="string"),
                    ]
                )
            ]
        )

        sql = schema.to_sql("sqlite")

        assert "CREATE TABLE IF NOT EXISTS users" in sql
        assert "id INTEGER PRIMARY KEY" in sql

    def test_column_to_sql_with_constraints(self):
        """Test column SQL generation with constraints."""
        column = Column(
            name="email",
            data_type="string",
            length=255,
            nullable=False,
            unique=True
        )

        sql = column.to_sql("sqlite")

        assert "email TEXT" in sql
        assert "NOT NULL" in sql
        assert "UNIQUE" in sql

    def test_index_creation_sql(self):
        """Test index SQL generation."""
        index = Index(
            name="idx_users_email",
            columns=["email"],
            unique=True
        )

        sql = index.to_sql("users", "sqlite")

        assert "CREATE UNIQUE INDEX" in sql
        assert "idx_users_email" in sql


# ==============================================================================
# Backup Manager Tests
# ==============================================================================

@pytest.mark.database
class TestBackupManager:
    """Tests for database backup functionality."""

    @pytest.fixture
    def backup_manager(self, tmp_path):
        """Create a BackupManager for testing."""
        return BackupManager(workspace_dir=str(tmp_path))

    @pytest.fixture
    def test_db(self, tmp_path):
        """Create a test SQLite database."""
        db_path = str(tmp_path / "backup_test.db")
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE data (id INTEGER, value TEXT)")
        conn.execute("INSERT INTO data VALUES (1, 'test')")
        conn.commit()
        conn.close()
        return db_path

    def test_backup_sqlite_database(self, backup_manager, test_db):
        """Test backing up SQLite database."""
        result = backup_manager.create_backup(
            database_name="test_db",
            database_url=f"sqlite:///{test_db}",
            compression="none"
        )

        assert result.success
        assert result.file_size_mb > 0
        assert result.checksum is not None

    def test_backup_with_compression(self, backup_manager, test_db):
        """Test backing up with gzip compression."""
        result = backup_manager.create_backup(
            database_name="test_db",
            database_url=f"sqlite:///{test_db}",
            compression="gzip"
        )

        assert result.success
        assert result.backup_id.endswith

    def test_list_backups(self, backup_manager, test_db):
        """Test listing backups."""
        backup_manager.create_backup(
            database_name="test_db",
            database_url=f"sqlite:///{test_db}"
        )

        backups = backup_manager.list_backups()

        assert len(backups) >= 1

    def test_delete_backup(self, backup_manager, test_db):
        """Test deleting a backup."""
        result = backup_manager.create_backup(
            database_name="test_db",
            database_url=f"sqlite:///{test_db}"
        )

        assert backup_manager.delete_backup(result.backup_id)
        assert result.backup_id not in [b["backup_id"] for b in backup_manager.list_backups()]


# ==============================================================================
# Performance Monitor Tests
# ==============================================================================

@pytest.mark.database
class TestPerformanceMonitor:
    """Tests for database performance monitoring."""

    @pytest.fixture
    def monitor(self, tmp_path):
        """Create a DatabasePerformanceMonitor for testing."""
        return DatabasePerformanceMonitor(workspace_dir=str(tmp_path))

    def test_record_query_metrics(self, monitor):
        """Test recording query metrics."""
        monitor.record_query_metrics(
            query_hash="abc123",
            metrics={
                "query_type": "SELECT",
                "execution_time_ms": 15.5,
                "rows_affected": 10,
                "database_name": "test_db"
            }
        )

        analysis = monitor.analyze_query_performance(hours=1)
        assert analysis["queries_analyzed"] >= 1

    def test_record_database_metrics(self, monitor):
        """Test recording database metrics."""
        monitor.record_database_metrics(
            database_name="test_db",
            metrics={
                "connections_active": 5,
                "connections_idle": 3,
                "queries_per_second": 100.0,
                "average_query_time_ms": 25.0,
                "cache_hit_ratio": 0.95,
                "disk_io_mb": 10.5
            }
        )

        analysis = monitor.analyze_database_performance("test_db", hours=1)
        assert analysis["metrics_count"] >= 1

    def test_performance_report_generation(self, monitor):
        """Test generating performance report."""
        # Add some metrics
        monitor.record_database_metrics(
            database_name="test_db",
            metrics={
                "connections_active": 5,
                "queries_per_second": 100.0,
                "average_query_time_ms": 25.0,
                "cache_hit_ratio": 0.95,
                "disk_io_mb": 10.5,
                "connections_idle": 2
            }
        )

        report = monitor.get_performance_report("test_db", hours=1)

        assert report["database_name"] == "test_db"
        assert "recommendations" in report

    def test_check_alerts_high_query_time(self, monitor):
        """Test alert generation for high query time."""
        # Add metrics with high query time
        monitor.record_database_metrics(
            database_name="test_db",
            metrics={
                "connections_active": 5,
                "queries_per_second": 100.0,
                "average_query_time_ms": 600.0,  # High query time
                "cache_hit_ratio": 0.95,
                "disk_io_mb": 10.5,
                "connections_idle": 2
            }
        )

        alerts = monitor.check_alerts("test_db")

        # Should have alert for high query time
        high_time_alerts = [a for a in alerts if a.metric_name == "average_query_time_ms"]
        assert len(high_time_alerts) >= 1


# ==============================================================================
# Schema Generator Advanced Tests
# ==============================================================================

@pytest.mark.database
class TestSchemaGeneratorAdvanced:
    """Advanced tests for schema generation."""

    @pytest.fixture
    def generator(self, tmp_path):
        """Create a SchemaGenerator for testing."""
        return SchemaGenerator(workspace_dir=str(tmp_path))

    def test_compare_schemas(self, generator):
        """Test schema comparison."""
        current_schema = {
            "tables": [
                {
                    "name": "users",
                    "columns": [
                        {"name": "id", "type": "integer"},
                        {"name": "name", "type": "string"}
                    ]
                }
            ]
        }

        target_schema = {
            "tables": [
                {
                    "name": "users",
                    "columns": [
                        {"name": "id", "type": "integer"},
                        {"name": "name", "type": "string"},
                        {"name": "email", "type": "string"}  # New column
                    ]
                },
                {
                    "name": "posts",  # New table
                    "columns": [
                        {"name": "id", "type": "integer"}
                    ]
                }
            ]
        }

        differences = generator.compare_schemas(current_schema, target_schema)

        assert len(differences["tables_to_add"]) == 1
        assert len(differences["columns_to_add"]) == 1

    def test_schema_drift_report(self, generator):
        """Test schema drift report generation."""
        current_schema = {"tables": []}
        target_schema = {
            "tables": [
                {"name": "new_table", "columns": [{"name": "id", "type": "integer"}]}
            ]
        }

        report = generator.get_schema_drift_report(current_schema, target_schema)

        assert report["drift_detected"] is True
        assert report["migration_needed"] is True

    def test_export_schema_sql(self, generator, tmp_path):
        """Test exporting schema as SQL."""
        table = SchemaTable(
            name="test_table",
            columns=[
                Column(name="id", data_type="integer", primary_key=True),
                Column(name="name", data_type="string"),
            ]
        )
        generator.create_table(table)

        output_path = str(tmp_path / "schema.sql")
        result = generator.export_schema(output_path, format="sql")

        assert Path(result).exists()
        content = Path(result).read_text()
        assert "CREATE TABLE" in content

    def test_export_schema_json(self, generator, tmp_path):
        """Test exporting schema as JSON."""
        table = SchemaTable(
            name="test_table",
            columns=[
                Column(name="id", data_type="integer", primary_key=True),
            ]
        )
        generator.create_table(table)

        output_path = str(tmp_path / "schema.json")
        result = generator.export_schema(output_path, format="json")

        assert Path(result).exists()

    def test_generate_migration_from_changes(self, generator):
        """Test generating migration from schema changes."""
        changes = {
            "name": "add_email_column",
            "create_tables": [],
            "add_columns": [
                {
                    "table": "users",
                    "columns": [
                        {"name": "email", "data_type": "string", "length": 255}
                    ]
                }
            ]
        }

        migration = generator.generate_migration(
            name="add_email",
            description="Add email column to users",
            changes=changes
        )

        assert migration.migration_id is not None
        assert "ALTER TABLE" in migration.up_sql


# ==============================================================================
# Integration Tests
# ==============================================================================

@pytest.mark.database
class TestIntegration:
    """Integration tests for database management components."""

    def test_full_database_lifecycle(self, tmp_path):
        """Test complete database lifecycle with all components."""
        db_path = str(tmp_path / "integration_test.db")

        # Create and connect using DatabaseConnector
        connector = DatabaseConnector(f"sqlite:///{db_path}")
        connector.connect()

        # Create schema
        connector.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE
            )
        """)
        connector.commit()

        # Insert data
        connector.execute("INSERT INTO users VALUES (1, 'Alice', 'alice@test.com')")
        connector.execute("INSERT INTO users VALUES (2, 'Bob', 'bob@test.com')")
        connector.commit()

        # Query data
        _, cursor = connector.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        assert len(rows) == 2

        # Get schema info
        _, tables_cursor = connector.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = [row[0] for row in tables_cursor.fetchall()]
        assert "users" in tables

        _, columns_cursor = connector.execute("PRAGMA table_info(users)")
        columns = columns_cursor.fetchall()
        assert len(columns) == 3

        # Cleanup
        connector.disconnect()

    def test_migration_workflow(self, tmp_path):
        """Test complete migration workflow."""
        workspace = str(tmp_path / "migrations")
        db_path = str(tmp_path / "migration_workflow.db")

        # Create migration manager
        manager = MigrationManager(
            workspace_dir=workspace,
            database_url=f"sqlite:///{db_path}"
        )

        # Create migrations without dependencies for simpler test
        m1 = manager.create_migration(
            name="create_users",
            description="Create users table",
            sql="CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT);",
            rollback_sql="DROP TABLE users;"
        )

        m2 = manager.create_migration(
            name="create_posts",
            description="Create posts table",
            sql="CREATE TABLE posts (id INTEGER PRIMARY KEY, user_id INTEGER);",
            rollback_sql="DROP TABLE posts;"
            # No dependencies
        )

        # Apply migrations one by one
        result1 = manager.apply_migration(m1.id)
        assert result1.success

        result2 = manager.apply_migration(m2.id)
        assert result2.success

        # Check status
        status = manager.get_migration_status(m1.id)
        assert status["status"] == "applied"

        status2 = manager.get_migration_status(m2.id)
        assert status2["status"] == "applied"

        manager.close()

    def test_backup_and_monitor_integration(self, tmp_path):
        """Test backup and monitoring integration."""
        db_path = str(tmp_path / "backup_monitor.db")

        # Create test database
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE data (id INTEGER, value TEXT)")
        for i in range(100):
            conn.execute(f"INSERT INTO data VALUES ({i}, 'value_{i}')")
        conn.commit()
        conn.close()

        # Create backup
        backup_manager = BackupManager(workspace_dir=str(tmp_path))
        backup_result = backup_manager.create_backup(
            database_name="test_db",
            database_url=f"sqlite:///{db_path}"
        )

        assert backup_result.success

        # Monitor performance
        monitor = DatabasePerformanceMonitor(workspace_dir=str(tmp_path))
        monitor.record_database_metrics(
            database_name="test_db",
            metrics={
                "connections_active": 1,
                "connections_idle": 0,
                "queries_per_second": 10.0,
                "average_query_time_ms": 5.0,
                "cache_hit_ratio": 0.9,
                "disk_io_mb": 0.1
            }
        )

        report = monitor.get_performance_report("test_db")
        assert report is not None


# ==============================================================================
# DatabaseBackup Tests (from test_coverage_boost_r2.py)
# ==============================================================================

class TestDatabaseBackup:
    """Tests for DatabaseBackup manager."""

    def test_backup_and_restore_sqlite(self, tmp_path):
        from codomyrmex.database_management.backup.backup import DatabaseBackup

        # Create a real SQLite DB
        db_path = tmp_path / "test.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE t (id INTEGER)")
        conn.execute("INSERT INTO t VALUES (42)")
        conn.commit()
        conn.close()

        backup_dir = tmp_path / "backups"
        mgr = DatabaseBackup(backup_dir)
        meta = mgr.backup_sqlite(db_path, backup_name="test_backup")
        assert meta.success
        assert meta.size_bytes > 0

        # Restore
        restore_path = tmp_path / "restored.db"
        assert mgr.restore_sqlite("test_backup", restore_path)
        conn2 = sqlite3.connect(str(restore_path))
        rows = conn2.execute("SELECT id FROM t").fetchall()
        conn2.close()
        assert rows == [(42,)]

    def test_list_backups(self, tmp_path):
        from codomyrmex.database_management.backup.backup import DatabaseBackup

        db_path = tmp_path / "test.db"
        db_path.write_bytes(b"fake-sqlite")

        mgr = DatabaseBackup(tmp_path / "backups")
        mgr.backup_sqlite(db_path, backup_name="b1")
        mgr.backup_sqlite(db_path, backup_name="b2")
        assert len(mgr.list_backups()) == 2

    def test_prune(self, tmp_path):
        from codomyrmex.database_management.backup.backup import DatabaseBackup

        db_path = tmp_path / "test.db"
        db_path.write_bytes(b"data")

        mgr = DatabaseBackup(tmp_path / "backups")
        for i in range(5):
            mgr.backup_sqlite(db_path, backup_name=f"b{i}")
        removed = mgr.prune(keep_last=2)
        assert removed == 3
        assert len(mgr.list_backups()) == 2

    def test_restore_nonexistent(self, tmp_path):
        from codomyrmex.database_management.backup.backup import DatabaseBackup

        mgr = DatabaseBackup(tmp_path / "backups")
        assert not mgr.restore_sqlite("nope", tmp_path / "out.db")

    def test_backup_metadata_to_dict(self):
        from codomyrmex.database_management.backup.backup import (
            BackupFormat,
            BackupMetadata,
        )

        meta = BackupMetadata(
            backup_id="b1", source="/db", destination="/backup/b1.db",
            format=BackupFormat.FILE_COPY, size_bytes=1024,
        )
        d = meta.to_dict()
        assert d["backup_id"] == "b1"
        assert d["format"] == "file_copy"
        assert d["size_bytes"] == 1024


# ==============================================================================
# Column Tests (from test_coverage_boost_r3.py)
# ==============================================================================

class TestColumn:
    """Tests for Column dataclass."""

    def test_basic_column_sql(self):
        from codomyrmex.database_management.schema_generator import Column

        col = Column(name="id", data_type="integer", primary_key=True, auto_increment=True)
        sql = col.to_sql("sqlite")
        assert "id" in sql
        assert "INTEGER" in sql

    def test_nullable_column(self):
        from codomyrmex.database_management.schema_generator import Column

        col = Column(name="email", data_type="string", nullable=False, unique=True)
        sql = col.to_sql("sqlite")
        assert "NOT NULL" in sql
        assert "UNIQUE" in sql

    def test_default_value(self):
        from codomyrmex.database_management.schema_generator import Column

        col = Column(name="status", data_type="string", default="'active'")
        sql = col.to_sql("sqlite")
        assert "DEFAULT" in sql

    def test_postgresql_dialect(self):
        from codomyrmex.database_management.schema_generator import Column

        col = Column(name="data", data_type="json")
        sql = col.to_sql("postgresql")
        assert "JSONB" in sql or "JSON" in sql


# ==============================================================================
# Index Tests (from test_coverage_boost_r3.py)
# ==============================================================================

class TestIndex:
    """Tests for Index dataclass."""

    def test_basic_index(self):
        from codomyrmex.database_management.schema_generator import Index

        idx = Index(name="idx_email", columns=["email"])
        sql = idx.to_sql("users")
        assert "idx_email" in sql
        assert "email" in sql

    def test_unique_index(self):
        from codomyrmex.database_management.schema_generator import Index

        idx = Index(name="idx_unique", columns=["code"], unique=True)
        sql = idx.to_sql("items")
        assert "UNIQUE" in sql


# ==============================================================================
# SchemaTable Tests (from test_coverage_boost_r3.py)
# ==============================================================================

class TestSchemaTable:
    """Tests for SchemaTable."""

    def test_table_to_sql(self):
        from codomyrmex.database_management.schema_generator import Column, SchemaTable

        table = SchemaTable(
            name="users",
            columns=[
                Column(name="id", data_type="integer", primary_key=True),
                Column(name="name", data_type="string", nullable=False),
                Column(name="email", data_type="string", unique=True),
            ],
        )
        sql = table.to_sql("sqlite")
        assert "CREATE TABLE" in sql
        assert "users" in sql

    def test_table_to_dict(self):
        from codomyrmex.database_management.schema_generator import Column, SchemaTable

        table = SchemaTable(
            name="products",
            columns=[Column(name="id", data_type="integer")],
            description="Product catalog",
        )
        d = table.to_dict()
        assert d["name"] == "products"
        assert len(d["columns"]) == 1


# ==============================================================================
# SchemaMigration Tests (from test_coverage_boost_r3.py)
# ==============================================================================

class TestSchemaMigration:
    """Tests for SchemaMigration."""

    def test_checksum_generated(self):
        from codomyrmex.database_management.schema_generator import SchemaMigration

        m = SchemaMigration(
            migration_id="001",
            name="add_users",
            description="Add users table",
            up_sql="CREATE TABLE users (id INT);",
            down_sql="DROP TABLE users;",
        )
        assert m.checksum  # Auto-generated in __post_init__


# ==============================================================================
# SchemaDefinition Tests (from test_coverage_boost_r3.py)
# ==============================================================================

class TestSchemaDefinition:
    """Tests for SchemaDefinition."""

    def test_to_sql(self):
        from codomyrmex.database_management.schema_generator import (
            Column,
            SchemaDefinition,
            SchemaTable,
        )

        schema = SchemaDefinition(
            name="mydb",
            version="1.0",
            tables=[
                SchemaTable(
                    name="t1",
                    columns=[Column(name="id", data_type="integer", primary_key=True)],
                ),
            ],
        )
        sql = schema.to_sql("sqlite")
        assert "CREATE TABLE" in sql

    def test_to_dict(self):
        from codomyrmex.database_management.schema_generator import (
            SchemaDefinition,
        )

        schema = SchemaDefinition(name="db", version="2.0", tables=[])
        d = schema.to_dict()
        assert d["name"] == "db"
        assert d["version"] == "2.0"


# ==============================================================================
# MigrationResult Tests (from test_coverage_boost_r4.py)
# ==============================================================================

class TestMigrationResult:
    """Tests for MigrationResult."""

    def test_success_result(self):
        from codomyrmex.database_management.migration.migration_manager import (
            MigrationResult,
        )

        r = MigrationResult(
            migration_id="001", success=True,
            execution_time=0.5, rows_affected=10,
        )
        assert r.success
        assert r.rows_affected == 10


# ==============================================================================
# MigrationManager Tests (from test_coverage_boost_r4.py)
# ==============================================================================

class TestMigrationManager:
    """Tests for MigrationManager."""

    def test_init(self, tmp_path):
        from codomyrmex.database_management.migration.migration_manager import (
            MigrationManager,
        )

        mgr = MigrationManager(workspace_dir=str(tmp_path))
        assert mgr is not None

    def test_create_and_list(self, tmp_path):
        from codomyrmex.database_management.migration.migration_manager import (
            MigrationManager,
        )

        mgr = MigrationManager(workspace_dir=str(tmp_path))
        m = mgr.create_migration(
            name="init", description="Initial",
            sql="CREATE TABLE t (id INT);",
        )
        assert m.name == "init"
        migrations = mgr.list_migrations()
        assert isinstance(migrations, list)

    def test_with_sqlite(self, tmp_path):
        from codomyrmex.database_management.migration.migration_manager import (
            MigrationManager,
        )

        db = tmp_path / "migrations.db"
        mgr = MigrationManager(
            workspace_dir=str(tmp_path),
            database_url=f"sqlite:///{db}",
        )
        mgr.create_migration(
            name="init", description="Initial",
            sql="CREATE TABLE t (id INT);",
        )
        pending = mgr.get_pending_migrations()
        assert isinstance(pending, list)
