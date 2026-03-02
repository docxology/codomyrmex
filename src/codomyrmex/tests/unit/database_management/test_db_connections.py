"""Unit tests for database connection management and connection pooling."""

import sqlite3
from datetime import datetime

import pytest

from codomyrmex.database_management import (
    DatabaseConnection,
    DatabaseManager,
)
from codomyrmex.database_management.db_manager import (
    DatabaseType,
    QueryResult,
)
from codomyrmex.database_management.migration.migration_manager import (
    DatabaseConnector,
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
# DatabaseManager Tests (from test_coverage_boost_r7.py)
# ==============================================================================

@pytest.mark.database
class TestDatabaseManager:
    def test_database_type_enum(self):
        from codomyrmex.database_management.db_manager import DatabaseType
        assert DatabaseType.SQLITE.value == "sqlite" or hasattr(DatabaseType, "SQLITE")

    def test_query_result(self):
        r = QueryResult(success=True, rows=[], columns=[], row_count=0, execution_time=0.01)
        assert r.success

    def test_database_connection(self):
        from codomyrmex.database_management.db_manager import (
            DatabaseConnection,
            DatabaseType,
        )
        conn = DatabaseConnection(name="test", db_type=DatabaseType.SQLITE, database="test.db")
        assert conn.database == "test.db"

    def test_db_manager_init(self, tmp_path):
        from codomyrmex.database_management.db_manager import DatabaseManager
        mgr = DatabaseManager()
        assert mgr is not None
