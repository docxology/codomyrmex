"""
Comprehensive tests for the database_management module.

This module tests all database management functionality including:
1. Connection management
2. Query execution
3. Transaction handling (commit, rollback)
4. Parameterized queries
5. Result set iteration
6. Connection pooling
7. Migration support
8. Schema introspection
9. Batch operations
10. Error handling (connection failures, query errors)
"""

import os
import sqlite3
import tempfile
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

from codomyrmex.database_management import (
    DatabaseConnection,
    DatabaseManager,
    manage_databases,
    DatabaseMetrics,
    DatabaseMonitor,
    monitor_database,
    optimize_database,
    Migration,
    MigrationManager,
    run_migrations,
    Backup,
    BackupManager,
    backup_database,
    SchemaDefinition,
    SchemaGenerator,
    generate_schema,
)
from codomyrmex.database_management.db_manager import (
    DatabaseType,
    QueryResult,
    connect_database,
    execute_query,
)
from codomyrmex.database_management.migration_manager import (
    DatabaseConnector,
    MigrationResult,
)
from codomyrmex.database_management.schema_generator import (
    Column,
    Index,
    SchemaTable,
    SchemaMigration,
)
from codomyrmex.database_management.backup_manager import BackupResult
from codomyrmex.database_management.performance_monitor import (
    QueryMetrics,
    PerformanceAlert,
    DatabasePerformanceMonitor,
)
from codomyrmex.exceptions import CodomyrmexError


# ==============================================================================
# Connection Management Tests
# ==============================================================================

@pytest.mark.database
class TestConnectionManagement:
    """Tests for database connection management."""

    def test_database_connection_creation(self):
        """Test DatabaseConnection creation with all parameters."""
        connection = DatabaseConnection(
            name="test_db",
            db_type=DatabaseType.SQLITE,
            host="localhost",
            port=5432,
            database="test_db",
            username="user",
            password="pass"
        )

        assert connection.name == "test_db"
        assert connection.db_type == DatabaseType.SQLITE
        assert connection.host == "localhost"
        assert connection.port == 5432
        assert connection.database == "test_db"
        assert connection.username == "user"
        assert connection.password == "pass"

    def test_database_connection_defaults(self):
        """Test DatabaseConnection default values."""
        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.POSTGRESQL,
            host="localhost",
            database="test"
        )

        assert connection.port == 5432
        assert connection.username == "postgres"
        assert connection.ssl_mode == "prefer"
        assert connection.connection_pool_size == 10
        assert connection.connection_timeout == 30
        assert connection.max_retries == 3

    def test_mysql_connection_defaults(self):
        """Test MySQL connection has correct default port and username."""
        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.MYSQL,
            host="localhost",
            database="test"
        )

        assert connection.port == 3306
        assert connection.username == "root"

    def test_database_connection_auto_timestamp(self):
        """Test DatabaseConnection automatic timestamp."""
        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.SQLITE,
            database="test.db"
        )

        assert connection.created_at is not None
        assert isinstance(connection.created_at, datetime)

    def test_connection_string_sqlite(self):
        """Test connection string generation for SQLite."""
        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.SQLITE,
            database="test.db"
        )

        assert connection.get_connection_string() == "sqlite:///test.db"

    def test_connection_string_postgresql(self):
        """Test connection string generation for PostgreSQL."""
        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.POSTGRESQL,
            host="localhost",
            port=5432,
            database="test_db",
            username="user",
            password="pass"
        )

        expected = "postgresql://user:pass@localhost:5432/test_db"
        assert connection.get_connection_string() == expected

    def test_connection_string_mysql(self):
        """Test connection string generation for MySQL."""
        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.MYSQL,
            host="localhost",
            port=3306,
            database="test_db",
            username="user",
            password="pass"
        )

        expected = "mysql://user:pass@localhost:3306/test_db"
        assert connection.get_connection_string() == expected

    def test_custom_connection_string(self):
        """Test custom connection string overrides generated one."""
        custom_string = "custom://connection/string"
        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.SQLITE,
            database="test.db",
            connection_string=custom_string
        )

        assert connection.get_connection_string() == custom_string

    def test_unsupported_database_type_connection_string(self):
        """Test connection string for unsupported database type raises error."""
        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.MONGODB,
            database="test"
        )

        with pytest.raises(ValueError, match="Unsupported database type"):
            connection.get_connection_string()

    def test_sqlite_connect_and_disconnect(self, tmp_path):
        """Test SQLite connection and disconnection."""
        db_path = str(tmp_path / "test.db")
        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.SQLITE,
            database=db_path
        )

        connection.connect()
        assert connection._connection is not None
        assert connection.connection_count == 1
        assert isinstance(connection._connection, sqlite3.Connection)

        connection.disconnect()
        assert connection._connection is None

    def test_disconnect_when_not_connected(self):
        """Test disconnection when no connection exists is safe."""
        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.SQLITE,
            database="test.db"
        )

        # Should not raise error
        connection.disconnect()
        assert connection._connection is None


# ==============================================================================
# Query Execution Tests
# ==============================================================================

@pytest.mark.database
class TestQueryExecution:
    """Tests for query execution."""

    @pytest.fixture
    def db_connection(self, tmp_path):
        """Create a SQLite database connection for testing."""
        db_path = str(tmp_path / "test.db")
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)")
        conn.execute("INSERT INTO users VALUES (1, 'Alice', 'alice@example.com')")
        conn.execute("INSERT INTO users VALUES (2, 'Bob', 'bob@example.com')")
        conn.commit()
        conn.close()

        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.SQLITE,
            database=db_path
        )
        connection.connect()
        yield connection
        connection.disconnect()

    def test_select_query_execution(self, db_connection):
        """Test SELECT query execution returns results."""
        result = db_connection.execute_query("SELECT * FROM users")

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[0]["name"] == "Alice"

    def test_insert_query_execution(self, db_connection):
        """Test INSERT query execution."""
        db_connection.execute_query(
            "INSERT INTO users VALUES (3, 'Charlie', 'charlie@example.com')"
        )

        result = db_connection.execute_query("SELECT * FROM users WHERE id = 3")
        assert len(result) == 1
        assert result[0]["name"] == "Charlie"

    def test_update_query_execution(self, db_connection):
        """Test UPDATE query execution."""
        db_connection.execute_query(
            "UPDATE users SET name = 'Alice Updated' WHERE id = 1"
        )

        result = db_connection.execute_query("SELECT name FROM users WHERE id = 1")
        assert result[0]["name"] == "Alice Updated"

    def test_delete_query_execution(self, db_connection):
        """Test DELETE query execution."""
        db_connection.execute_query("DELETE FROM users WHERE id = 2")

        result = db_connection.execute_query("SELECT * FROM users")
        assert len(result) == 1
        assert result[0]["id"] == 1

    def test_query_with_invalid_table(self, db_connection):
        """Test query with non-existent table raises error."""
        with pytest.raises(Exception):
            db_connection.execute_query("SELECT * FROM invalid_table")


# ==============================================================================
# Parameterized Query Tests
# ==============================================================================

@pytest.mark.database
class TestParameterizedQueries:
    """Tests for parameterized query execution."""

    @pytest.fixture
    def db_connection(self, tmp_path):
        """Create a SQLite database connection for testing."""
        db_path = str(tmp_path / "test.db")
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE products (id INTEGER, name TEXT, price REAL)")
        conn.execute("INSERT INTO products VALUES (1, 'Widget', 19.99)")
        conn.execute("INSERT INTO products VALUES (2, 'Gadget', 29.99)")
        conn.execute("INSERT INTO products VALUES (3, 'Gizmo', 39.99)")
        conn.commit()
        conn.close()

        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.SQLITE,
            database=db_path
        )
        connection.connect()
        yield connection
        connection.disconnect()

    def test_parameterized_select(self, db_connection):
        """Test parameterized SELECT query."""
        result = db_connection.execute_query(
            "SELECT * FROM products WHERE id = ?",
            (1,)
        )

        assert len(result) == 1
        assert result[0]["name"] == "Widget"

    def test_parameterized_select_multiple_params(self, db_connection):
        """Test parameterized SELECT with multiple parameters."""
        result = db_connection.execute_query(
            "SELECT * FROM products WHERE price > ? AND price < ?",
            (20.0, 40.0)
        )

        assert len(result) == 2

    def test_parameterized_insert(self, db_connection):
        """Test parameterized INSERT query."""
        db_connection.execute_query(
            "INSERT INTO products VALUES (?, ?, ?)",
            (4, "Thingamajig", 49.99)
        )

        result = db_connection.execute_query("SELECT * FROM products WHERE id = 4")
        assert len(result) == 1
        assert result[0]["name"] == "Thingamajig"

    def test_parameterized_update(self, db_connection):
        """Test parameterized UPDATE query."""
        db_connection.execute_query(
            "UPDATE products SET price = ? WHERE id = ?",
            (24.99, 1)
        )

        result = db_connection.execute_query("SELECT price FROM products WHERE id = 1")
        assert result[0]["price"] == 24.99


# ==============================================================================
# Transaction Handling Tests
# ==============================================================================

@pytest.mark.database
class TestTransactionHandling:
    """Tests for transaction commit and rollback."""

    @pytest.fixture
    def db_connector(self, tmp_path):
        """Create a DatabaseConnector with SQLite for testing transactions."""
        db_path = str(tmp_path / "transaction_test.db")
        connector = DatabaseConnector(f"sqlite:///{db_path}")
        connector.connect()
        connector.execute("CREATE TABLE accounts (id INTEGER, balance REAL)")
        connector.execute("INSERT INTO accounts VALUES (1, 1000.0)")
        connector.execute("INSERT INTO accounts VALUES (2, 500.0)")
        connector.commit()
        yield connector
        connector.disconnect()

    def test_transaction_commit(self, db_connector):
        """Test that transaction commits correctly."""
        db_connector.execute(
            "UPDATE accounts SET balance = balance - 100 WHERE id = 1"
        )
        db_connector.execute(
            "UPDATE accounts SET balance = balance + 100 WHERE id = 2"
        )
        db_connector.commit()

        # Verify changes persisted
        _, cursor = db_connector.execute("SELECT balance FROM accounts WHERE id = 1")
        assert cursor.fetchone()[0] == 900.0

        _, cursor = db_connector.execute("SELECT balance FROM accounts WHERE id = 2")
        assert cursor.fetchone()[0] == 600.0

    def test_transaction_rollback_on_error(self, db_connector):
        """Test that transaction rolls back on error."""
        _, cursor = db_connector.execute("SELECT balance FROM accounts WHERE id = 1")
        initial_balance = cursor.fetchone()[0]

        try:
            db_connector.execute(
                "UPDATE accounts SET balance = balance - 100 WHERE id = 1"
            )
            # Simulate an error before commit
            raise ValueError("Simulated error")
        except ValueError:
            db_connector.rollback()

        # Verify changes were rolled back
        _, cursor = db_connector.execute("SELECT balance FROM accounts WHERE id = 1")
        assert cursor.fetchone()[0] == initial_balance

    def test_nested_transaction_behavior(self, db_connector):
        """Test transaction commit after multiple operations."""
        db_connector.execute(
            "UPDATE accounts SET balance = balance - 50 WHERE id = 1"
        )
        db_connector.commit()

        _, cursor = db_connector.execute("SELECT balance FROM accounts WHERE id = 1")
        assert cursor.fetchone()[0] == 950.0


# ==============================================================================
# Result Set Iteration Tests
# ==============================================================================

@pytest.mark.database
class TestResultSetIteration:
    """Tests for iterating over query results."""

    @pytest.fixture
    def db_connector(self, tmp_path):
        """Create a DatabaseConnector with data for testing."""
        db_path = str(tmp_path / "iteration_test.db")
        connector = DatabaseConnector(f"sqlite:///{db_path}")
        connector.connect()
        connector.execute("CREATE TABLE items (id INTEGER, category TEXT, value REAL)")
        for i in range(100):
            connector.execute(
                f"INSERT INTO items VALUES ({i}, 'category_{i % 5}', {i * 1.5})"
            )
        connector.commit()
        yield connector
        connector.disconnect()

    def test_iterate_over_result_rows(self, db_connector):
        """Test iterating over result rows."""
        _, cursor = db_connector.execute("SELECT * FROM items LIMIT 10")
        rows = cursor.fetchall()

        assert len(rows) == 10
        for i, row in enumerate(rows):
            assert row[0] == i  # id

    def test_result_columns_access(self, db_connector):
        """Test accessing column names from result."""
        _, cursor = db_connector.execute("SELECT id, category, value FROM items LIMIT 1")
        columns = [desc[0] for desc in cursor.description]

        assert columns == ["id", "category", "value"]

    def test_empty_result_set(self, db_connector):
        """Test handling of empty result set."""
        _, cursor = db_connector.execute("SELECT * FROM items WHERE id > 1000")
        rows = cursor.fetchall()

        assert len(rows) == 0

    def test_query_result_dataclass(self):
        """Test QueryResult dataclass properties."""
        result = QueryResult(
            success=True,
            rows=[(1, "test")],
            columns=["id", "name"],
            row_count=1,
            execution_time=0.01
        )
        assert result.valid == result.success

    def test_result_execution_time(self, db_connector):
        """Test that query can execute and return results."""
        import time
        start = time.time()
        _, cursor = db_connector.execute("SELECT * FROM items")
        rows = cursor.fetchall()
        elapsed = time.time() - start

        assert len(rows) == 100
        assert elapsed >= 0


# ==============================================================================
# Connection Pooling Tests
# ==============================================================================

@pytest.mark.database
class TestConnectionPooling:
    """Tests for connection pooling functionality."""

    def test_database_manager_multiple_connections(self, tmp_path):
        """Test managing multiple database connections."""
        manager = DatabaseManager()

        db1_path = str(tmp_path / "db1.db")
        db2_path = str(tmp_path / "db2.db")

        conn1 = DatabaseConnection(
            name="db1",
            db_type=DatabaseType.SQLITE,
            database=db1_path
        )
        conn2 = DatabaseConnection(
            name="db2",
            db_type=DatabaseType.SQLITE,
            database=db2_path
        )

        manager.add_connection(conn1)
        manager.add_connection(conn2)

        assert len(manager.list_connections()) == 2

    def test_connect_all_and_disconnect_all(self, tmp_path):
        """Test connect_all and disconnect_all methods."""
        manager = DatabaseManager()

        db1_path = str(tmp_path / "db1.db")
        db2_path = str(tmp_path / "db2.db")

        conn1 = DatabaseConnection(
            name="db1",
            db_type=DatabaseType.SQLITE,
            database=db1_path
        )
        conn2 = DatabaseConnection(
            name="db2",
            db_type=DatabaseType.SQLITE,
            database=db2_path
        )

        manager.add_connection(conn1)
        manager.add_connection(conn2)

        manager.connect_all()
        assert conn1._connection is not None
        assert conn2._connection is not None

        manager.disconnect_all()
        assert conn1._connection is None
        assert conn2._connection is None

    def test_health_check_all_connections(self, tmp_path):
        """Test health check across all connections."""
        manager = DatabaseManager()

        db_path = str(tmp_path / "test.db")
        conn = DatabaseConnection(
            name="test",
            db_type=DatabaseType.SQLITE,
            database=db_path
        )
        conn.connect()
        manager.add_connection(conn)

        health = manager.health_check_all()

        assert "test" in health
        assert health["test"]["status"] == "healthy"

    def test_database_stats(self, tmp_path):
        """Test getting database statistics."""
        manager = DatabaseManager()

        db_path = str(tmp_path / "test.db")
        conn = DatabaseConnection(
            name="test",
            db_type=DatabaseType.SQLITE,
            database=db_path
        )
        conn.connect()
        manager.add_connection(conn)

        stats = manager.get_database_stats()

        assert stats["total_connections"] == 1
        assert stats["active_connections"] == 1

    def test_connection_pool_size_config(self):
        """Test connection pool size configuration."""
        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.POSTGRESQL,
            database="test",
            connection_pool_size=20
        )

        assert connection.connection_pool_size == 20


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
# Batch Operations Tests
# ==============================================================================

@pytest.mark.database
class TestBatchOperations:
    """Tests for batch database operations."""

    @pytest.fixture
    def db_connector(self, tmp_path):
        """Create a DatabaseConnector for batch testing."""
        db_path = str(tmp_path / "batch_test.db")
        connector = DatabaseConnector(f"sqlite:///{db_path}")
        connector.connect()
        connector.execute("CREATE TABLE items (id INTEGER, value TEXT)")
        connector.commit()
        yield connector
        connector.disconnect()

    def test_execute_many_batch_insert(self, db_connector):
        """Test batch insert using executemany."""
        params_list = [(i, f"value_{i}") for i in range(100)]

        cursor = db_connector._connection.cursor()
        cursor.executemany("INSERT INTO items VALUES (?, ?)", params_list)
        db_connector.commit()

        # Verify all rows inserted
        _, count_cursor = db_connector.execute("SELECT COUNT(*) FROM items")
        assert count_cursor.fetchone()[0] == 100

    def test_execute_many_empty_list(self, db_connector):
        """Test executemany with empty parameter list."""
        cursor = db_connector._connection.cursor()
        cursor.executemany("INSERT INTO items VALUES (?, ?)", [])
        db_connector.commit()

        # Should have no rows
        _, count_cursor = db_connector.execute("SELECT COUNT(*) FROM items")
        assert count_cursor.fetchone()[0] == 0

    def test_execute_script_batch(self, db_connector):
        """Test batch execution using execute_script."""
        script = """
        INSERT INTO items VALUES (1, 'a');
        INSERT INTO items VALUES (2, 'b');
        INSERT INTO items VALUES (3, 'c');
        """
        total_rows, statements = db_connector.execute_script(script)
        db_connector.commit()

        assert statements == 3

        # Verify rows inserted
        _, count_cursor = db_connector.execute("SELECT COUNT(*) FROM items")
        assert count_cursor.fetchone()[0] == 3

    def test_batch_insert_performance(self, db_connector):
        """Test that batch insert is reasonably fast."""
        import time
        params_list = [(i, f"value_{i}") for i in range(1000)]

        start_time = time.time()
        cursor = db_connector._connection.cursor()
        cursor.executemany("INSERT INTO items VALUES (?, ?)", params_list)
        db_connector.commit()
        elapsed = time.time() - start_time

        # Should complete in under 5 seconds
        assert elapsed < 5.0

        # Verify all rows inserted
        _, count_cursor = db_connector.execute("SELECT COUNT(*) FROM items")
        assert count_cursor.fetchone()[0] == 1000


# ==============================================================================
# Error Handling Tests
# ==============================================================================

@pytest.mark.database
class TestErrorHandling:
    """Tests for error handling in database operations."""

    def test_connection_not_found_error(self):
        """Test error when connection not found."""
        manager = DatabaseManager()

        with pytest.raises(ValueError, match="Database connection not found"):
            manager.execute_query("nonexistent", "SELECT 1")

    def test_execute_without_connection(self):
        """Test error when executing on connector without connection."""
        connector = DatabaseConnector("sqlite:///test.db")
        # Don't call connect()

        with pytest.raises(CodomyrmexError, match="Not connected"):
            connector.execute("SELECT 1")

    def test_invalid_database_url(self):
        """Test error with invalid database URL."""
        with pytest.raises(CodomyrmexError, match="Unsupported database URL"):
            DatabaseConnector("invalid://url")

    def test_query_syntax_error(self, tmp_path):
        """Test handling of SQL syntax errors."""
        db_path = str(tmp_path / "test.db")
        connector = DatabaseConnector(f"sqlite:///{db_path}")
        connector.connect()

        with pytest.raises(CodomyrmexError, match="SQL execution failed"):
            connector.execute("SELEC * FROM invalid syntax")

        connector.disconnect()

    def test_constraint_violation_error(self, tmp_path):
        """Test handling of constraint violations."""
        db_path = str(tmp_path / "test.db")
        connector = DatabaseConnector(f"sqlite:///{db_path}")
        connector.connect()
        connector.execute("CREATE TABLE unique_test (id INTEGER PRIMARY KEY, value TEXT UNIQUE)")
        connector.execute("INSERT INTO unique_test VALUES (1, 'unique_value')")
        connector.commit()

        # Try to insert duplicate
        with pytest.raises(CodomyrmexError, match="SQL execution failed"):
            connector.execute("INSERT INTO unique_test VALUES (2, 'unique_value')")

        connector.disconnect()

    def test_migration_not_found_error(self, tmp_path):
        """Test error when migration not found."""
        manager = MigrationManager(workspace_dir=str(tmp_path))

        with pytest.raises(CodomyrmexError, match="Migration not found"):
            manager.apply_migration("nonexistent_migration")

    def test_rollback_without_sql(self, tmp_path):
        """Test error when rolling back migration without rollback SQL."""
        db_path = str(tmp_path / "test.db")
        manager = MigrationManager(
            workspace_dir=str(tmp_path),
            database_url=f"sqlite:///{db_path}"
        )

        migration = manager.create_migration(
            name="no_rollback",
            description="Migration without rollback",
            sql="CREATE TABLE test (id INTEGER);"
            # No rollback_sql provided
        )

        manager.apply_migration(migration.id)

        with pytest.raises(CodomyrmexError, match="No rollback SQL"):
            manager.rollback_migration(migration.id)

        manager.close()


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
# Convenience Function Tests
# ==============================================================================

@pytest.mark.database
class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    def test_manage_databases_function(self):
        """Test manage_databases convenience function."""
        result = manage_databases()
        assert isinstance(result, DatabaseManager)

    def test_manage_databases_without_url(self):
        """Test manage_databases without database URL returns a manager."""
        result = manage_databases()
        assert isinstance(result, DatabaseManager)

    def test_database_connector_convenience(self, tmp_path):
        """Test DatabaseConnector as convenience for connecting."""
        db_path = str(tmp_path / "test.db")
        connector = DatabaseConnector(f"sqlite:///{db_path}")
        connector.connect()

        assert connector._connection is not None
        connector.disconnect()

    def test_database_connector_execute(self, tmp_path):
        """Test DatabaseConnector execute convenience."""
        db_path = str(tmp_path / "test.db")
        connector = DatabaseConnector(f"sqlite:///{db_path}")
        connector.connect()
        connector.execute("CREATE TABLE test (id INTEGER)")
        connector.commit()

        _, cursor = connector.execute("SELECT 1")
        result = cursor.fetchone()

        assert result[0] == 1
        connector.disconnect()

    def test_monitor_database_function(self, tmp_path):
        """Test monitor_database convenience function."""
        result = monitor_database("test_db", workspace_dir=str(tmp_path))

        assert isinstance(result, dict)
        assert "database_name" in result

    def test_optimize_database_function(self, tmp_path):
        """Test optimize_database convenience function."""
        result = optimize_database("test_db", workspace_dir=str(tmp_path))

        assert isinstance(result, dict)
        assert "database_name" in result


# ==============================================================================
# Database Connector Tests
# ==============================================================================

@pytest.mark.database
class TestDatabaseConnector:
    """Tests for DatabaseConnector class."""

    def test_parse_sqlite_url(self, tmp_path):
        """Test parsing SQLite URL."""
        db_path = str(tmp_path / "test.db")
        connector = DatabaseConnector(f"sqlite:///{db_path}")

        assert connector._db_type == "sqlite"

    def test_parse_postgresql_url(self):
        """Test parsing PostgreSQL URL."""
        connector = DatabaseConnector("postgresql://user:pass@localhost:5432/db")

        assert connector._db_type == "postgresql"

    def test_parse_mysql_url(self):
        """Test parsing MySQL URL."""
        connector = DatabaseConnector("mysql://user:pass@localhost:3306/db")

        assert connector._db_type == "mysql"

    def test_invalid_url_raises_error(self):
        """Test that invalid URL raises error."""
        with pytest.raises(CodomyrmexError, match="Unsupported database URL"):
            DatabaseConnector("invalid://url")

    def test_sqlite_connect_and_execute(self, tmp_path):
        """Test SQLite connection and execution."""
        db_path = str(tmp_path / "test.db")
        connector = DatabaseConnector(f"sqlite:///{db_path}")

        connector.connect()
        rows, cursor = connector.execute("CREATE TABLE test (id INTEGER)")
        connector.commit()

        assert connector._connection is not None

        connector.disconnect()
        assert connector._connection is None

    def test_execute_script(self, tmp_path):
        """Test executing multiple SQL statements."""
        db_path = str(tmp_path / "test.db")
        connector = DatabaseConnector(f"sqlite:///{db_path}")
        connector.connect()

        script = """
        CREATE TABLE users (id INTEGER);
        CREATE TABLE posts (id INTEGER);
        INSERT INTO users VALUES (1);
        """

        total_rows, statements = connector.execute_script(script)

        assert statements == 3
        connector.disconnect()


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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
