"""Security tests for DatabaseManager to ensure protection against SQL injection."""

import sqlite3
import pytest
from codomyrmex.database_management.db_manager import DatabaseManager

@pytest.mark.database
class TestDatabaseSecurity:
    """Tests for SQL injection protection in database operations."""

    @pytest.fixture
    def db_manager(self, tmp_path):
        """Create a DatabaseManager with a SQLite database for testing."""
        db_path = str(tmp_path / "security_test.db")
        manager = DatabaseManager(f"sqlite:///{db_path}")
        manager.connect()
        # Create a legitimate table
        manager.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
        yield manager
        manager.disconnect()

    def test_get_table_info_sql_injection_attempt(self, db_manager):
        """Verify that get_table_info is not vulnerable to SQL injection."""
        # Malicious table name attempting to execute a second statement
        malicious_name = 'users"); CREATE TABLE injection_test (id INTEGER); --'

        # This should not raise an error, but it should not execute the second statement either.
        # SQLite's PRAGMA will just not find a table with this name.
        info = db_manager.get_table_info(malicious_name)

        assert len(info) == 0

        # Verify that the injection table was NOT created
        result = db_manager.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='injection_test'"
        )
        assert len(result.rows) == 0

    def test_get_table_info_special_characters(self, db_manager):
        """Verify that get_table_info handles table names with special characters correctly."""
        # Table name with double quotes
        weird_name = 'weird"table'
        # Manually escape for creation (not the subject of this fix but needed for setup)
        db_manager.execute('CREATE TABLE "weird""table" (id INTEGER, data TEXT)')

        info = db_manager.get_table_info(weird_name)

        assert len(info) == 2
        names = [col['name'] for col in info]
        assert 'id' in names
        assert 'data' in names
