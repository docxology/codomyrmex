"""Unit tests for database query execution, parameterized queries, and transactions."""

import sqlite3

import pytest

from codomyrmex.database_management import (
    DatabaseConnection,
    DatabaseManager,
    MigrationManager,
    manage_databases,
    monitor_database,
    optimize_database,
)
from codomyrmex.database_management.db_manager import (
    DatabaseType,
)
from codomyrmex.database_management.migration.migration_manager import (
    DatabaseConnector,
)
from codomyrmex.exceptions import CodomyrmexError

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
        with pytest.raises(sqlite3.OperationalError):
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
