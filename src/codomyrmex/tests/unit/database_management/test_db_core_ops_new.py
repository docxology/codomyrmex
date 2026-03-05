import os
import tempfile

import pytest

from codomyrmex.database_management import (
    DatabaseConnection,
    DatabaseManager,
    DatabaseType,
    manage_databases,
)


@pytest.fixture
def db_manager():
    """Provides a DatabaseManager with an in-memory SQLite connection."""
    manager = manage_databases("sqlite:///:memory:")
    return manager


@pytest.fixture
def temp_db_file():
    """Provides a temporary file path for a SQLite database."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)


def test_database_manager_init():
    """Test DatabaseManager initialization."""
    manager = DatabaseManager()
    assert len(manager.list_connections()) == 0
    assert manager.default_connection_name is None


def test_sqlite_in_memory_connection(db_manager):
    """Test connecting to and querying an in-memory SQLite database."""
    assert len(db_manager.list_connections()) == 1

    # Create table
    res = db_manager.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
    assert res.success

    # Insert
    res = db_manager.execute("INSERT INTO users (name) VALUES (?)", ("Alice",))
    assert res.success
    assert res.row_count == 1

    # Query
    res = db_manager.execute("SELECT * FROM users")
    assert res.success
    assert len(res.rows) == 1
    assert res.rows[0][1] == "Alice"
    assert "name" in res.columns


def test_sqlite_file_connection(temp_db_file):
    """Test connecting to a file-based SQLite database."""
    url = f"sqlite:///{temp_db_file}"
    manager = manage_databases(url)

    manager.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, val REAL)")
    manager.execute("INSERT INTO items (val) VALUES (?)", (42.0,))

    manager.disconnect_all()

    # Reconnect and verify data persists
    manager2 = manage_databases(url)
    res = manager2.execute("SELECT val FROM items")
    assert res.rows[0][0] == 42.0


def test_query_result_to_dict_list(db_manager):
    """Test QueryResult.to_dict_list() method."""
    db_manager.execute("CREATE TABLE test (a INTEGER, b TEXT)")
    db_manager.execute("INSERT INTO test VALUES (1, 'one'), (2, 'two')")

    res = db_manager.execute("SELECT * FROM test ORDER BY a")
    dicts = res.to_dict_list()

    assert len(dicts) == 2
    assert dicts[0] == {"a": 1, "b": "one"}
    assert dicts[1] == {"a": 2, "b": "two"}


def test_transaction_commit(db_manager):
    """Test successful transaction commit."""
    db_manager.execute("CREATE TABLE account (id INTEGER PRIMARY KEY, balance REAL)")
    db_manager.execute("INSERT INTO account VALUES (1, 100.0)")

    with db_manager.transaction():
        db_manager.execute("UPDATE account SET balance = balance - 20 WHERE id = 1")
        db_manager.execute("UPDATE account SET balance = balance + 20 WHERE id = 1")

    res = db_manager.execute("SELECT balance FROM account WHERE id = 1")
    assert res.rows[0][0] == 100.0


def test_transaction_rollback(db_manager):
    """Test transaction rollback on error."""
    db_manager.execute("CREATE TABLE account (id INTEGER PRIMARY KEY, balance REAL)")
    db_manager.execute("INSERT INTO account VALUES (1, 100.0)")

    try:
        with db_manager.transaction() as tx:
            tx.execute("UPDATE account SET balance = 50.0 WHERE id = 1", commit=False)
            raise ValueError("Something went wrong")
    except ValueError:
        pass

    res = db_manager.execute("SELECT balance FROM account WHERE id = 1")
    # Balance should still be 100.0 due to rollback
    assert res.rows[0][0] == 100.0


def test_get_tables_and_info(db_manager):
    """Test retrieving table list and column info."""
    db_manager.execute(
        "CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT NOT NULL UNIQUE)"
    )
    db_manager.execute(
        "CREATE TABLE posts (id INTEGER PRIMARY KEY, title TEXT, user_id INTEGER, FOREIGN KEY(user_id) REFERENCES users(id))"
    )

    tables = db_manager.get_tables()
    assert "users" in tables
    assert "posts" in tables

    info = db_manager.get_table_info("users")
    names = [c["name"] for c in info]
    assert "id" in names
    assert "email" in names

    email_col = next(c for c in info if c["name"] == "email")
    assert email_col["notnull"] is True


def test_health_check(db_manager):
    """Test health check functionality."""
    health = db_manager.health_check_all()
    assert len(health) == 1
    conn_name = next(iter(health.keys()))
    assert health[conn_name]["status"] == "healthy"


def test_multiple_connections():
    """Test managing multiple connections simultaneously."""
    manager = DatabaseManager()

    conn1 = DatabaseConnection(
        name="db1", db_type=DatabaseType.SQLITE, database=":memory:"
    )
    conn2 = DatabaseConnection(
        name="db2", db_type=DatabaseType.SQLITE, database=":memory:"
    )

    manager.add_connection(conn1)
    manager.add_connection(conn2)

    manager.execute("CREATE TABLE t1 (v TEXT)", connection_name="db1")
    manager.execute("CREATE TABLE t2 (v TEXT)", connection_name="db2")

    assert "t1" in manager.get_tables("db1")
    assert "t1" not in manager.get_tables("db2")
    assert "t2" in manager.get_tables("db2")
    assert "t2" not in manager.get_tables("db1")


def test_error_handling(db_manager):
    """Test handling of invalid queries."""
    res = db_manager.execute("SELECT * FROM non_existent_table")
    assert res.success is False
    assert res.error_message is not None
    assert "no such table" in res.error_message.lower()
