"""Unit tests for database result set iteration and batch operations."""

import time

import pytest

from codomyrmex.database_management.db_manager import (
    QueryResult,
)
from codomyrmex.database_management.migration.migration_manager import (
    DatabaseConnector,
)

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
        start = time.time()
        _, cursor = db_connector.execute("SELECT * FROM items")
        rows = cursor.fetchall()
        elapsed = time.time() - start

        assert len(rows) == 100
        assert elapsed >= 0


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
