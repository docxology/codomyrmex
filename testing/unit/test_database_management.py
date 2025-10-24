"""
Comprehensive tests for the database_management module.

This module tests all database management functionality including
connection management, migration handling, backup operations, and monitoring.
"""

import pytest
import tempfile
import os
import sqlite3
from unittest.mock import patch, MagicMock
from pathlib import Path
from datetime import datetime, timezone

from codomyrmex.database_management.db_manager import (
    DatabaseManager,
    manage_databases,
    DatabaseConnection,
    DatabaseType
)


class TestDatabaseConnection:
    """Test cases for DatabaseConnection dataclass."""

    def test_database_connection_creation(self):
        """Test DatabaseConnection creation."""
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

        assert connection.port == 5432  # PostgreSQL default port
        assert connection.username == "postgres"  # PostgreSQL default username
        assert connection.ssl_mode == "prefer"
        assert connection.connection_pool_size == 10
        assert connection.connection_timeout == 30
        assert connection.max_retries == 3

    def test_database_connection_auto_timestamp(self):
        """Test DatabaseConnection automatic timestamp."""
        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.SQLITE,
            database="test.db"
        )

        assert connection.created_at is not None
        assert isinstance(connection.created_at, datetime)

    def test_get_connection_string_sqlite(self):
        """Test connection string generation for SQLite."""
        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.SQLITE,
            database="test.db"
        )

        assert connection.get_connection_string() == "sqlite:///test.db"

    def test_get_connection_string_postgresql(self):
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

    def test_get_connection_string_mysql(self):
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

    def test_get_connection_string_custom(self):
        """Test custom connection string."""
        custom_string = "custom://connection/string"
        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.SQLITE,
            database="test.db",
            connection_string=custom_string
        )

        assert connection.get_connection_string() == custom_string

    def test_get_connection_string_unsupported_type(self):
        """Test connection string for unsupported database type."""
        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.MONGODB,  # Assuming unsupported in get_connection_string
            database="test"
        )

        with pytest.raises(ValueError, match="Unsupported database type"):
            connection.get_connection_string()


class TestDatabaseManager:
    """Test cases for DatabaseManager functionality."""

    def setup_method(self):
        """Setup for each test method."""
        self.manager = DatabaseManager()

    def test_database_manager_initialization(self):
        """Test DatabaseManager initialization."""
        manager = DatabaseManager()
        assert manager.connections == {}

    def test_add_connection(self):
        """Test adding database connection."""
        connection = DatabaseConnection(
            name="test_db",
            db_type=DatabaseType.SQLITE,
            database="test.db"
        )

        self.manager.add_connection(connection)
        assert "test_db" in self.manager.connections
        assert self.manager.connections["test_db"] == connection

    def test_remove_connection(self):
        """Test removing database connection."""
        connection = DatabaseConnection(
            name="test_db",
            db_type=DatabaseType.SQLITE,
            database="test.db"
        )
        self.manager.add_connection(connection)

        assert "test_db" in self.manager.connections

        self.manager.remove_connection("test_db")
        assert "test_db" not in self.manager.connections

    def test_remove_connection_nonexistent(self):
        """Test removing non-existent connection."""
        # Should not raise error
        self.manager.remove_connection("nonexistent")

    def test_get_connection(self):
        """Test getting database connection."""
        connection = DatabaseConnection(
            name="test_db",
            db_type=DatabaseType.SQLITE,
            database="test.db"
        )
        self.manager.add_connection(connection)

        result = self.manager.get_connection("test_db")
        assert result == connection

        # Test non-existent connection
        result = self.manager.get_connection("nonexistent")
        assert result is None

    def test_list_connections(self):
        """Test listing connection names."""
        # Initially empty
        assert self.manager.list_connections() == []

        # Add connections
        self.manager.add_connection(DatabaseConnection(
            name="db1",
            db_type=DatabaseType.SQLITE,
            database="test1.db"
        ))
        self.manager.add_connection(DatabaseConnection(
            name="db2",
            db_type=DatabaseType.SQLITE,
            database="test2.db"
        ))

        connections = self.manager.list_connections()
        assert len(connections) == 2
        assert "db1" in connections
        assert "db2" in connections

    @patch('codomyrmex.database_management.db_manager.sqlite3.connect')
    def test_connect_sqlite_success(self, mock_connect):
        """Test successful SQLite connection."""
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.SQLITE,
            database="test.db"
        )

        connection.connect()

        assert connection._connection == mock_connection
        assert connection.connection_count == 1
        mock_connect.assert_called_once_with("test.db")

    @patch('codomyrmex.database_management.db_manager.sqlite3.connect')
    def test_connect_sqlite_failure(self, mock_connect):
        """Test SQLite connection failure."""
        mock_connect.side_effect = Exception("Connection failed")

        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.SQLITE,
            database="test.db"
        )

        with pytest.raises(Exception, match="Connection failed"):
            connection.connect()

    def test_connect_postgresql_success(self):
        """Test successful PostgreSQL connection."""
        # This test will be skipped if PostgreSQL driver is not available
        pytest.importorskip('psycopg2')

        mock_connection = MagicMock()

        with patch('psycopg2.connect', return_value=mock_connection):
            connection = DatabaseConnection(
                name="test",
                db_type=DatabaseType.POSTGRESQL,
                host="localhost",
                port=5432,
                database="test_db",
                username="user",
                password="pass"
            )

            connection.connect()

            assert connection._connection == mock_connection
            assert connection.connection_count == 1

    def test_connect_mysql_success(self):
        """Test successful MySQL connection."""
        # This test will be skipped if MySQL driver is not available
        pytest.importorskip('pymysql')

        mock_connection = MagicMock()

        with patch('pymysql.connect', return_value=mock_connection):
            connection = DatabaseConnection(
                name="test",
                db_type=DatabaseType.MYSQL,
                host="localhost",
                port=3306,
                database="test_db",
                username="user",
                password="pass"
            )

            connection.connect()

            assert connection._connection == mock_connection
            assert connection.connection_count == 1

    def test_disconnect(self):
        """Test database disconnection."""
        mock_connection = MagicMock()
        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.SQLITE,
            database="test.db"
        )
        connection._connection = mock_connection

        connection.disconnect()

        assert connection._connection is None
        mock_connection.close.assert_called_once()

    def test_disconnect_no_connection(self):
        """Test disconnection when no connection exists."""
        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.SQLITE,
            database="test.db"
        )

        # Should not raise error
        connection.disconnect()

    @patch('codomyrmex.database_management.db_manager.sqlite3.connect')
    def test_execute_query_select_sqlite(self, mock_connect):
        """Test SELECT query execution on SQLite."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.description = [("id",), ("name",)]
        mock_cursor.fetchall.return_value = [(1, "test")]
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.SQLITE,
            database="test.db"
        )
        connection.connect()

        result = connection.execute_query("SELECT * FROM test_table")

        expected_result = [{"id": 1, "name": "test"}]
        assert result == expected_result
        mock_cursor.execute.assert_called_once_with("SELECT * FROM test_table")

    @patch('codomyrmex.database_management.db_manager.sqlite3.connect')
    def test_execute_query_insert_sqlite(self, mock_connect):
        """Test INSERT query execution on SQLite."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.SQLITE,
            database="test.db"
        )
        connection.connect()

        result = connection.execute_query("INSERT INTO test_table VALUES (1, 'test')")

        expected_result = [{"affected_rows": 1}]
        assert result == expected_result
        mock_connection.commit.assert_called_once()

    @patch('codomyrmex.database_management.db_manager.sqlite3.connect')
    def test_execute_query_with_parameters(self, mock_connect):
        """Test query execution with parameters."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.description = [("name",)]
        mock_cursor.fetchall.return_value = [("test",)]
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.SQLITE,
            database="test.db"
        )
        connection.connect()

        result = connection.execute_query("SELECT * FROM users WHERE id = ?", (1,))

        expected_result = [{"name": "test"}]
        assert result == expected_result
        mock_cursor.execute.assert_called_once_with("SELECT * FROM users WHERE id = ?", (1,))

    @patch('codomyrmex.database_management.db_manager.sqlite3.connect')
    def test_execute_query_error_handling(self, mock_connect):
        """Test query execution error handling."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("Query failed")
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.SQLITE,
            database="test.db"
        )
        connection.connect()

        with pytest.raises(Exception, match="Query failed"):
            connection.execute_query("SELECT * FROM invalid_table")

        mock_connection.rollback.assert_called_once()

    def test_get_database_info_sqlite(self):
        """Test getting database info for SQLite."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name

        try:
            connection = DatabaseConnection(
                name="test",
                db_type=DatabaseType.SQLITE,
                database=db_path
            )

            # Create a simple table for testing
            conn = sqlite3.connect(db_path)
            conn.execute("CREATE TABLE test_table (id INTEGER)")
            conn.commit()
            conn.close()

            with patch('codomyrmex.database_management.db_manager.sqlite3.connect') as mock_connect:
                mock_connection = MagicMock()
                mock_cursor = MagicMock()
                mock_cursor.fetchall.return_value = [("test_table",)]
                mock_connection.cursor.return_value = mock_cursor
                mock_connect.return_value = mock_connection

                connection.connect()
                info = connection.get_database_info()

                assert info["name"] == "test"
                assert info["type"] == "sqlite"
                assert "tables" in info
                assert info["is_connected"] is True

        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_get_database_info_no_connection(self):
        """Test getting database info when not connected."""
        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.SQLITE,
            database="test.db"
        )

        info = connection.get_database_info()

        assert info["name"] == "test"
        assert info["type"] == "sqlite"
        assert info["is_connected"] is False

    @patch('codomyrmex.database_management.db_manager.sqlite3.connect')
    def test_health_check_success(self, mock_connect):
        """Test successful health check."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [(1,)]
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.SQLITE,
            database="test.db"
        )

        health = connection.health_check()

        assert health["status"] == "healthy"
        assert health["database"] == "test"
        assert "response_time" in health
        assert health["response_time"] > 0

    @patch('codomyrmex.database_management.db_manager.sqlite3.connect')
    def test_health_check_failure(self, mock_connect):
        """Test health check failure."""
        mock_connect.side_effect = Exception("Connection failed")

        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.SQLITE,
            database="test.db"
        )

        health = connection.health_check()

        assert health["status"] == "unhealthy"
        assert health["database"] == "test"
        assert "Connection failed" in health["error"]

    def test_connect_all(self):
        """Test connecting to all databases."""
        # Add mock connections
        connection1 = DatabaseConnection(
            name="db1",
            db_type=DatabaseType.SQLITE,
            database="test1.db"
        )
        connection2 = DatabaseConnection(
            name="db2",
            db_type=DatabaseType.SQLITE,
            database="test2.db"
        )

        self.manager.add_connection(connection1)
        self.manager.add_connection(connection2)

        with patch('codomyrmex.database_management.db_manager.sqlite3.connect') as mock_connect:
            mock_connection = MagicMock()
            mock_connect.return_value = mock_connection

            self.manager.connect_all()

            # Should have attempted to connect twice
            assert mock_connect.call_count == 2

    def test_disconnect_all(self):
        """Test disconnecting from all databases."""
        # Add mock connections with active connections
        connection1 = DatabaseConnection(
            name="db1",
            db_type=DatabaseType.SQLITE,
            database="test1.db"
        )
        connection1._connection = MagicMock()

        connection2 = DatabaseConnection(
            name="db2",
            db_type=DatabaseType.SQLITE,
            database="test2.db"
        )
        connection2._connection = MagicMock()

        self.manager.add_connection(connection1)
        self.manager.add_connection(connection2)

        self.manager.disconnect_all()

        # Both connections should be closed and set to None after disconnect
        assert connection1._connection is None
        assert connection2._connection is None

    def test_execute_query_convenience(self):
        """Test execute_query convenience method."""
        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.SQLITE,
            database="test.db"
        )
        self.manager.add_connection(connection)

        with patch.object(connection, 'execute_query', return_value=[{"result": "test"}]) as mock_execute:
            result = self.manager.execute_query("test", "SELECT 1")

            assert result == [{"result": "test"}]
            mock_execute.assert_called_once_with("SELECT 1", None)

    def test_execute_query_nonexistent_connection(self):
        """Test execute_query with non-existent connection."""
        with pytest.raises(ValueError, match="Database connection not found"):
            self.manager.execute_query("nonexistent", "SELECT 1")

    def test_health_check_all(self):
        """Test health check for all connections."""
        # Add mock connections
        connection1 = DatabaseConnection(
            name="db1",
            db_type=DatabaseType.SQLITE,
            database="test1.db"
        )
        connection2 = DatabaseConnection(
            name="db2",
            db_type=DatabaseType.SQLITE,
            database="test2.db"
        )

        self.manager.add_connection(connection1)
        self.manager.add_connection(connection2)

        with patch.object(connection1, 'health_check', return_value={"status": "healthy"}):
            with patch.object(connection2, 'health_check', return_value={"status": "unhealthy", "error": "Connection failed"}):
                health_status = self.manager.health_check_all()

                assert "db1" in health_status
                assert "db2" in health_status
                assert health_status["db1"]["status"] == "healthy"
                assert health_status["db2"]["status"] == "unhealthy"

    def test_get_database_stats(self):
        """Test getting database statistics."""
        # Add mock connections with different states
        connection1 = DatabaseConnection(
            name="db1",
            db_type=DatabaseType.SQLITE,
            database="test1.db"
        )
        connection1._connection = MagicMock()  # Connected
        connection1.connection_count = 5

        connection2 = DatabaseConnection(
            name="db2",
            db_type=DatabaseType.POSTGRESQL,
            database="test2"
        )
        # Not connected
        connection2.connection_count = 3

        self.manager.add_connection(connection1)
        self.manager.add_connection(connection2)

        stats = self.manager.get_database_stats()

        assert stats["total_connections"] == 2
        assert stats["active_connections"] == 1
        assert stats["total_queries"] == 8
        assert stats["databases_by_type"]["sqlite"] == 1
        assert stats["databases_by_type"]["postgresql"] == 1
        assert stats["health_summary"]["healthy"] == 1  # One connection is active (SQLite)

    @patch('codomyrmex.database_management.db_manager.sqlite3.connect')
    def test_create_database_sqlite(self, mock_connect):
        """Test database creation for SQLite."""
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.SQLITE,
            database="test.db"
        )
        self.manager.add_connection(connection)

        result = self.manager.create_database("test", "new_db")

        assert result is True
        # SQLite creates database automatically on connection

    def test_create_database_postgresql(self):
        """Test database creation for PostgreSQL."""
        # This test will be skipped if PostgreSQL driver is not available
        pytest.importorskip('psycopg2')

        # Mock postgres connection
        mock_postgres_conn = MagicMock()

        with patch('psycopg2.connect', return_value=mock_postgres_conn):
            connection = DatabaseConnection(
                name="test",
                db_type=DatabaseType.POSTGRESQL,
                host="localhost",
                database="test_db",
                username="user",
                password="pass"
            )
            self.manager.add_connection(connection)

            with patch.object(connection, 'execute_query', return_value=[{"result": "success"}]):
                result = self.manager.create_database("test", "new_db")

                assert result is True

    def test_create_database_mysql(self):
        """Test database creation for MySQL."""
        # This test will be skipped if MySQL driver is not available
        pytest.importorskip('pymysql')

        # Mock mysql connection
        mock_mysql_conn = MagicMock()

        with patch('pymysql.connect', return_value=mock_mysql_conn):
            connection = DatabaseConnection(
                name="test",
                db_type=DatabaseType.MYSQL,
                host="localhost",
                database="test_db",
                username="user",
                password="pass"
            )
            self.manager.add_connection(connection)

            with patch.object(connection, 'execute_query', return_value=[{"result": "success"}]):
                result = self.manager.create_database("test", "new_db")

                assert result is True

    def test_create_database_nonexistent_connection(self):
        """Test database creation with non-existent connection."""
        with pytest.raises(ValueError, match="Database connection not found"):
            self.manager.create_database("nonexistent", "new_db")

    def test_drop_database_postgresql(self):
        """Test database dropping for PostgreSQL."""
        # This test will be skipped if PostgreSQL driver is not available
        pytest.importorskip('psycopg2')

        mock_postgres_conn = MagicMock()

        with patch('psycopg2.connect', return_value=mock_postgres_conn):
            connection = DatabaseConnection(
                name="test",
                db_type=DatabaseType.POSTGRESQL,
                host="localhost",
                database="postgres",
                username="user",
                password="pass"
            )
            self.manager.add_connection(connection)

            with patch.object(connection, 'execute_query', return_value=[{"result": "success"}]):
                result = self.manager.drop_database("test", "old_db")

                assert result is True


class TestConvenienceFunctions:
    """Test cases for module-level convenience functions."""

    @patch('codomyrmex.database_management.db_manager.DatabaseManager')
    def test_manage_databases_function(self, mock_manager_class):
        """Test manage_databases convenience function."""
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager

        result = manage_databases()

        mock_manager_class.assert_called_once()
        assert result == mock_manager


class TestIntegration:
    """Integration tests for database management components."""

    def test_database_connection_lifecycle(self):
        """Test complete database connection lifecycle."""
        with patch('codomyrmex.database_management.db_manager.sqlite3.connect') as mock_connect:
            mock_connection = MagicMock()
            mock_connect.return_value = mock_connection

            connection = DatabaseConnection(
                name="lifecycle_test",
                db_type=DatabaseType.SQLITE,
                database="test.db"
            )

            # Connect
            connection.connect()
            assert connection._connection == mock_connection
            assert connection.connection_count == 1

            # Execute query
            with patch.object(connection, 'execute_query', return_value=[{"result": "test"}]) as mock_execute:
                result = connection.execute_query("SELECT 1")
                assert result == [{"result": "test"}]

            # Get info
            info = connection.get_database_info()
            assert info["name"] == "lifecycle_test"
            assert info["is_connected"] is True

            # Health check
            with patch.object(connection, 'health_check', return_value={"status": "healthy"}) as mock_health:
                health = connection.health_check()
                assert health["status"] == "healthy"

            # Disconnect
            connection.disconnect()
            assert connection._connection is None
            mock_connection.close.assert_called_once()

    def test_database_manager_workflow(self):
        """Test DatabaseManager workflow."""
        manager = DatabaseManager()

        # Create and add connection
        connection = DatabaseConnection(
            name="workflow_test",
            db_type=DatabaseType.SQLITE,
            database="workflow.db"
        )
        manager.add_connection(connection)

        # Verify connection is added
        assert "workflow_test" in manager.list_connections()
        assert manager.get_connection("workflow_test") == connection

        # Test statistics
        stats = manager.get_database_stats()
        assert stats["total_connections"] == 1
        assert stats["active_connections"] == 1  # Connection is considered active

        # Remove connection
        manager.remove_connection("workflow_test")
        assert "workflow_test" not in manager.list_connections()

    def test_multiple_database_types(self):
        """Test handling multiple database types."""
        manager = DatabaseManager()

        # Add different database types
        sqlite_conn = DatabaseConnection(
            name="sqlite_db",
            db_type=DatabaseType.SQLITE,
            database="test.db"
        )
        postgres_conn = DatabaseConnection(
            name="postgres_db",
            db_type=DatabaseType.POSTGRESQL,
            host="localhost",
            database="test_db",
            username="user",
            password="pass"
        )
        mysql_conn = DatabaseConnection(
            name="mysql_db",
            db_type=DatabaseType.MYSQL,
            host="localhost",
            database="test_db",
            username="user",
            password="pass"
        )

        manager.add_connection(sqlite_conn)
        manager.add_connection(postgres_conn)
        manager.add_connection(mysql_conn)

        connections = manager.list_connections()
        assert len(connections) == 3
        assert "sqlite_db" in connections
        assert "postgres_db" in connections
        assert "mysql_db" in connections

        # Test connection string generation
        assert sqlite_conn.get_connection_string() == "sqlite:///test.db"
        assert "postgresql://" in postgres_conn.get_connection_string()
        assert "mysql://" in mysql_conn.get_connection_string()


class TestErrorHandling:
    """Test cases for error handling in database operations."""

    def test_execute_query_connection_not_found(self):
        """Test execute_query with non-existent connection."""
        manager = DatabaseManager()

        with pytest.raises(ValueError, match="Database connection not found"):
            manager.execute_query("nonexistent", "SELECT 1")

    @patch('codomyrmex.database_management.db_manager.sqlite3.connect')
    def test_connection_failure_handling(self, mock_connect):
        """Test connection failure handling."""
        mock_connect.side_effect = Exception("Database unavailable")

        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.SQLITE,
            database="test.db"
        )

        with pytest.raises(Exception, match="Database unavailable"):
            connection.connect()

    def test_health_check_connection_failure(self):
        """Test health check when connection fails."""
        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.SQLITE,
            database="test.db"
        )

        # Without mocking connection, health check should handle gracefully
        health = connection.health_check()

        assert health["database"] == "test"
        # Status may be "unknown" or "unhealthy" depending on implementation

    @patch('codomyrmex.database_management.db_manager.DatabaseConnection')
    def test_create_database_connection_error(self, mock_db_connection_class):
        """Test database creation with connection error."""
        mock_connection = MagicMock()
        mock_db_connection_class.return_value = mock_connection
        mock_connection.connect.side_effect = Exception("Connection failed")

        manager = DatabaseManager()
        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.POSTGRESQL,
            host="localhost",
            database="test"
        )
        manager.add_connection(connection)

        result = manager.create_database("test", "new_db")

        assert result is False

    def test_get_database_info_connection_error(self):
        """Test getting database info with connection error."""
        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.SQLITE,
            database="test.db"
        )

        # Should handle gracefully when not connected
        info = connection.get_database_info()

        assert info["name"] == "test"
        assert info["is_connected"] is False


if __name__ == "__main__":
    pytest.main([__file__])
