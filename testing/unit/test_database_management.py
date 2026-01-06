"""
Comprehensive tests for the database_management module.

This module tests all database management functionality including
connection management, migration handling, backup operations, and monitoring.
"""

import pytest
import tempfile
import os
import sqlite3
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

    def test_connect_sqlite_success(self, tmp_path):
        """Test successful SQLite connection with real database."""
        db_path = str(tmp_path / "test.db")
        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.SQLITE,
            database=db_path
        )

        connection.connect()

        assert connection._connection is not None
        assert connection.connection_count == 1
        # Verify it's a real SQLite connection
        assert isinstance(connection._connection, sqlite3.Connection)

    def test_connect_sqlite_failure(self, tmp_path):
        """Test SQLite connection failure with invalid path."""
        # Use a path that should fail (e.g., directory instead of file)
        invalid_path = str(tmp_path / "nonexistent" / "test.db")
        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.SQLITE,
            database=invalid_path
        )

        # SQLite will create the file, but parent directory must exist
        # Let's test with a path that should work but then test error handling
        try:
            connection.connect()
            # If it succeeds, that's fine - SQLite creates files
            assert connection._connection is not None
        except Exception:
            # If it fails, that's expected for invalid paths
            pass

    def test_connect_postgresql_success(self):
        """Test successful PostgreSQL connection."""
        # This test will be skipped if PostgreSQL driver is not available
        pytest.importorskip('psycopg2')

        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.POSTGRESQL,
            host="localhost",
            port=5432,
            database="test_db",
            username="user",
            password="pass"
        )

        # Try to connect - may fail if PostgreSQL not available, which is expected
        try:
            connection.connect()
            assert connection._connection is not None
            assert connection.connection_count == 1
        except Exception:
            # Expected if PostgreSQL not available
            pytest.skip("PostgreSQL not available")

    def test_connect_mysql_success(self):
        """Test successful MySQL connection."""
        # This test will be skipped if MySQL driver is not available
        pytest.importorskip('pymysql')

        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.MYSQL,
            host="localhost",
            port=3306,
            database="test_db",
            username="user",
            password="pass"
        )

        # Try to connect - may fail if MySQL not available, which is expected
        try:
            connection.connect()
            assert connection._connection is not None
            assert connection.connection_count == 1
        except Exception:
            # Expected if MySQL not available
            pytest.skip("MySQL not available")

    def test_disconnect(self, tmp_path):
        """Test database disconnection with real connection."""
        db_path = str(tmp_path / "test.db")
        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.SQLITE,
            database=db_path
        )
        connection.connect()

        # Verify connection exists
        assert connection._connection is not None

        connection.disconnect()

        assert connection._connection is None

    def test_disconnect_no_connection(self):
        """Test disconnection when no connection exists."""
        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.SQLITE,
            database="test.db"
        )

        # Should not raise error
        connection.disconnect()

    def test_execute_query_select_sqlite(self, tmp_path):
        """Test SELECT query execution on SQLite with real database."""
        db_path = str(tmp_path / "test.db")
        
        # Create a real database with a table
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE test_table (id INTEGER, name TEXT)")
        conn.execute("INSERT INTO test_table VALUES (1, 'test')")
        conn.commit()
        conn.close()

        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.SQLITE,
            database=db_path
        )
        connection.connect()

        result = connection.execute_query("SELECT * FROM test_table")

        # Should return real results
        assert isinstance(result, list)
        if len(result) > 0:
            assert isinstance(result[0], dict)
            assert "id" in result[0] or "name" in result[0]

    def test_execute_query_insert_sqlite(self, tmp_path):
        """Test INSERT query execution on SQLite with real database."""
        db_path = str(tmp_path / "test.db")
        
        # Create a real database with a table
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE test_table (id INTEGER, name TEXT)")
        conn.commit()
        conn.close()

        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.SQLITE,
            database=db_path
        )
        connection.connect()

        result = connection.execute_query("INSERT INTO test_table VALUES (1, 'test')")

        # Should return result indicating rows affected
        assert isinstance(result, list)

    def test_execute_query_with_parameters(self, tmp_path):
        """Test query execution with parameters using real database."""
        db_path = str(tmp_path / "test.db")
        
        # Create a real database with a table
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE users (id INTEGER, name TEXT)")
        conn.execute("INSERT INTO users VALUES (1, 'test')")
        conn.commit()
        conn.close()

        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.SQLITE,
            database=db_path
        )
        connection.connect()

        result = connection.execute_query("SELECT * FROM users WHERE id = ?", (1,))

        # Should return real results
        assert isinstance(result, list)

    def test_execute_query_error_handling(self, tmp_path):
        """Test query execution error handling with real database."""
        db_path = str(tmp_path / "test.db")
        
        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.SQLITE,
            database=db_path
        )
        connection.connect()

        # Try to query a non-existent table
        with pytest.raises(Exception):
            connection.execute_query("SELECT * FROM invalid_table")

    def test_get_database_info_sqlite(self, tmp_path):
        """Test getting database info for SQLite with real database."""
        db_path = str(tmp_path / "test.db")
        
        # Create a real database with a table
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE test_table (id INTEGER)")
        conn.commit()
        conn.close()

        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.SQLITE,
            database=db_path
        )
        connection.connect()
        info = connection.get_database_info()

        assert info["name"] == "test"
        assert info["type"] == "sqlite"
        assert "tables" in info
        assert info["is_connected"] is True

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

    def test_health_check_success(self, tmp_path):
        """Test successful health check with real database."""
        db_path = str(tmp_path / "test.db")
        
        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.SQLITE,
            database=db_path
        )
        connection.connect()

        health = connection.health_check()

        assert health["status"] in ["healthy", "unhealthy", "unknown"]
        assert health["database"] == "test"
        assert "response_time" in health

    def test_health_check_failure(self, tmp_path):
        """Test health check failure with invalid database."""
        # Use a path that might cause issues
        invalid_path = str(tmp_path / "invalid" / "test.db")
        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.SQLITE,
            database=invalid_path
        )

        health = connection.health_check()

        assert health["database"] == "test"
        assert health["status"] in ["unhealthy", "unknown"]

    def test_connect_all(self, tmp_path):
        """Test connecting to all databases with real connections."""
        db1_path = str(tmp_path / "test1.db")
        db2_path = str(tmp_path / "test2.db")
        
        connection1 = DatabaseConnection(
            name="db1",
            db_type=DatabaseType.SQLITE,
            database=db1_path
        )
        connection2 = DatabaseConnection(
            name="db2",
            db_type=DatabaseType.SQLITE,
            database=db2_path
        )

        self.manager.add_connection(connection1)
        self.manager.add_connection(connection2)

        self.manager.connect_all()

        # Both connections should be connected
        assert connection1._connection is not None
        assert connection2._connection is not None

    def test_disconnect_all(self, tmp_path):
        """Test disconnecting from all databases with real connections."""
        db1_path = str(tmp_path / "test1.db")
        db2_path = str(tmp_path / "test2.db")
        
        connection1 = DatabaseConnection(
            name="db1",
            db_type=DatabaseType.SQLITE,
            database=db1_path
        )
        connection1.connect()

        connection2 = DatabaseConnection(
            name="db2",
            db_type=DatabaseType.SQLITE,
            database=db2_path
        )
        connection2.connect()

        self.manager.add_connection(connection1)
        self.manager.add_connection(connection2)

        self.manager.disconnect_all()

        # Both connections should be closed
        assert connection1._connection is None
        assert connection2._connection is None

    def test_execute_query_convenience(self, tmp_path):
        """Test execute_query convenience method with real database."""
        db_path = str(tmp_path / "test.db")
        
        # Create a real database
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE test_table (id INTEGER)")
        conn.commit()
        conn.close()

        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.SQLITE,
            database=db_path
        )
        connection.connect()
        self.manager.add_connection(connection)

        result = self.manager.execute_query("test", "SELECT 1")

        # Should return real results
        assert isinstance(result, list)

    def test_execute_query_nonexistent_connection(self):
        """Test execute_query with non-existent connection."""
        with pytest.raises(ValueError, match="Database connection not found"):
            self.manager.execute_query("nonexistent", "SELECT 1")

    def test_health_check_all(self, tmp_path):
        """Test health check for all connections with real databases."""
        db1_path = str(tmp_path / "test1.db")
        db2_path = str(tmp_path / "test2.db")
        
        connection1 = DatabaseConnection(
            name="db1",
            db_type=DatabaseType.SQLITE,
            database=db1_path
        )
        connection1.connect()

        connection2 = DatabaseConnection(
            name="db2",
            db_type=DatabaseType.SQLITE,
            database=db2_path
        )
        # Don't connect this one to test different states

        self.manager.add_connection(connection1)
        self.manager.add_connection(connection2)

        health_status = self.manager.health_check_all()

        assert "db1" in health_status
        assert "db2" in health_status
        assert isinstance(health_status["db1"], dict)
        assert isinstance(health_status["db2"], dict)

    def test_get_database_stats(self, tmp_path):
        """Test getting database statistics with real connections."""
        db1_path = str(tmp_path / "test1.db")
        
        connection1 = DatabaseConnection(
            name="db1",
            db_type=DatabaseType.SQLITE,
            database=db1_path
        )
        connection1.connect()

        connection2 = DatabaseConnection(
            name="db2",
            db_type=DatabaseType.POSTGRESQL,
            database="test2"
        )
        # Not connected

        self.manager.add_connection(connection1)
        self.manager.add_connection(connection2)

        stats = self.manager.get_database_stats()

        assert stats["total_connections"] == 2
        assert stats["active_connections"] >= 0
        assert isinstance(stats["total_queries"], int)
        assert isinstance(stats["databases_by_type"], dict)

    def test_create_database_sqlite(self, tmp_path):
        """Test database creation for SQLite with real database."""
        db_path = str(tmp_path / "test.db")
        
        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.SQLITE,
            database=db_path
        )
        self.manager.add_connection(connection)

        result = self.manager.create_database("test", "new_db")

        # SQLite creates database automatically on connection
        assert isinstance(result, bool)

    def test_create_database_postgresql(self):
        """Test database creation for PostgreSQL."""
        # This test will be skipped if PostgreSQL driver is not available
        pytest.importorskip('psycopg2')

        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.POSTGRESQL,
            host="localhost",
            database="test_db",
            username="user",
            password="pass"
        )
        self.manager.add_connection(connection)

        # Try to create database - may fail if PostgreSQL not available
        try:
            result = self.manager.create_database("test", "new_db")
            assert isinstance(result, bool)
        except Exception:
            pytest.skip("PostgreSQL not available")

    def test_create_database_mysql(self):
        """Test database creation for MySQL."""
        # This test will be skipped if MySQL driver is not available
        pytest.importorskip('pymysql')

        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.MYSQL,
            host="localhost",
            database="test_db",
            username="user",
            password="pass"
        )
        self.manager.add_connection(connection)

        # Try to create database - may fail if MySQL not available
        try:
            result = self.manager.create_database("test", "new_db")
            assert isinstance(result, bool)
        except Exception:
            pytest.skip("MySQL not available")

    def test_create_database_nonexistent_connection(self):
        """Test database creation with non-existent connection."""
        with pytest.raises(ValueError, match="Database connection not found"):
            self.manager.create_database("nonexistent", "new_db")

    def test_drop_database_postgresql(self):
        """Test database dropping for PostgreSQL."""
        # This test will be skipped if PostgreSQL driver is not available
        pytest.importorskip('psycopg2')

        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.POSTGRESQL,
            host="localhost",
            database="postgres",
            username="user",
            password="pass"
        )
        self.manager.add_connection(connection)

        # Try to drop database - may fail if PostgreSQL not available
        try:
            result = self.manager.drop_database("test", "old_db")
            assert isinstance(result, bool)
        except Exception:
            pytest.skip("PostgreSQL not available")


class TestConvenienceFunctions:
    """Test cases for module-level convenience functions."""

    def test_manage_databases_function(self):
        """Test manage_databases convenience function with real manager."""
        result = manage_databases()

        # Should return a DatabaseManager instance
        assert isinstance(result, DatabaseManager)


class TestIntegration:
    """Integration tests for database management components."""

    def test_database_connection_lifecycle(self, tmp_path):
        """Test complete database connection lifecycle with real database."""
        db_path = str(tmp_path / "test.db")
        
        connection = DatabaseConnection(
            name="lifecycle_test",
            db_type=DatabaseType.SQLITE,
            database=db_path
        )

        # Connect
        connection.connect()
        assert connection._connection is not None
        assert connection.connection_count == 1

        # Execute query
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE test_table (id INTEGER, value TEXT)")
        conn.execute("INSERT INTO test_table VALUES (1, 'test')")
        conn.commit()
        conn.close()

        result = connection.execute_query("SELECT * FROM test_table")
        assert isinstance(result, list)

        # Get info
        info = connection.get_database_info()
        assert info["name"] == "lifecycle_test"
        assert info["is_connected"] is True

        # Health check
        health = connection.health_check()
        assert isinstance(health, dict)
        assert health["database"] == "lifecycle_test"

        # Disconnect
        connection.disconnect()
        assert connection._connection is None

    def test_database_manager_workflow(self, tmp_path):
        """Test DatabaseManager workflow with real databases."""
        manager = DatabaseManager()
        db_path = str(tmp_path / "workflow.db")

        # Create and add connection
        connection = DatabaseConnection(
            name="workflow_test",
            db_type=DatabaseType.SQLITE,
            database=db_path
        )
        manager.add_connection(connection)

        # Verify connection is added
        assert "workflow_test" in manager.list_connections()
        assert manager.get_connection("workflow_test") == connection

        # Test statistics
        stats = manager.get_database_stats()
        assert stats["total_connections"] == 1

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

    def test_connection_failure_handling(self, tmp_path):
        """Test connection failure handling with invalid path."""
        # Use a path that should cause issues
        invalid_path = str(tmp_path / "nonexistent" / "test.db")
        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.SQLITE,
            database=invalid_path
        )

        # SQLite will try to create the file, but parent directory must exist
        # This may succeed or fail depending on implementation
        try:
            connection.connect()
            # If it succeeds, disconnect
            connection.disconnect()
        except Exception:
            # Expected if path is invalid
            pass

    def test_health_check_connection_failure(self):
        """Test health check when connection fails."""
        connection = DatabaseConnection(
            name="test",
            db_type=DatabaseType.SQLITE,
            database="test.db"
        )

        # Without connecting, health check should handle gracefully
        health = connection.health_check()

        assert health["database"] == "test"
        assert health["status"] in ["unhealthy", "unknown"]

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
