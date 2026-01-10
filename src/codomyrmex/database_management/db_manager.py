"""Database Manager Module for Codomyrmex Database Management.

Provides database connection, query execution, and transaction management
for SQLite, PostgreSQL, and MySQL databases.
"""

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Generator, List, Optional, Tuple

from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)


@dataclass
class QueryResult:
    """Result of a query execution."""
    success: bool
    rows: List[Tuple]
    columns: List[str]
    row_count: int
    execution_time: float
    error_message: Optional[str] = None


@dataclass
class DatabaseConnection:
    """Database connection information."""
    connection_id: str
    database_type: str
    database_name: str
    connected_at: datetime
    active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


class DatabaseManager:
    """Database connection and query management."""

    def __init__(self, database_url: Optional[str] = None):
        """Initialize database manager."""
        self.database_url = database_url
        self._connection = None
        self._connections: Dict[str, DatabaseConnection] = {}

    def connect(self, database_url: Optional[str] = None) -> DatabaseConnection:
        """Establish a database connection."""
        url = database_url or self.database_url
        if not url:
            raise CodomyrmexError("No database URL provided")

        # Parse URL and connect
        if url.startswith("sqlite://"):
            db_path = url.replace("sqlite:///", "")
            self._connection = sqlite3.connect(db_path)
            db_type = "sqlite"
            db_name = db_path
        else:
            raise CodomyrmexError(f"Unsupported database URL: {url}")

        conn_id = f"conn_{datetime.now().timestamp()}"
        connection_info = DatabaseConnection(
            connection_id=conn_id,
            database_type=db_type,
            database_name=db_name,
            connected_at=datetime.now()
        )
        self._connections[conn_id] = connection_info
        logger.info(f"Connected to {db_type} database: {db_name}")
        return connection_info

    def disconnect(self, connection_id: Optional[str] = None):
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("Database connection closed")

    def execute(self, query: str, params: Optional[Tuple] = None) -> QueryResult:
        """Execute a query."""
        import time
        
        if not self._connection:
            raise CodomyrmexError("Not connected to database")

        start_time = time.time()
        try:
            cursor = self._connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            # Get results if any
            try:
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
            except Exception:
                rows = []
                columns = []

            self._connection.commit()
            execution_time = time.time() - start_time

            return QueryResult(
                success=True,
                rows=rows,
                columns=columns,
                row_count=len(rows),
                execution_time=execution_time
            )

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Query execution failed: {e}")
            return QueryResult(
                success=False,
                rows=[],
                columns=[],
                row_count=0,
                execution_time=execution_time,
                error_message=str(e)
            )

    def execute_many(self, query: str, params_list: List[Tuple]) -> QueryResult:
        """Execute a query with multiple parameter sets."""
        import time
        
        if not self._connection:
            raise CodomyrmexError("Not connected to database")

        start_time = time.time()
        try:
            cursor = self._connection.cursor()
            cursor.executemany(query, params_list)
            self._connection.commit()
            execution_time = time.time() - start_time

            return QueryResult(
                success=True,
                rows=[],
                columns=[],
                row_count=cursor.rowcount,
                execution_time=execution_time
            )

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Batch execution failed: {e}")
            return QueryResult(
                success=False,
                rows=[],
                columns=[],
                row_count=0,
                execution_time=execution_time,
                error_message=str(e)
            )

    @contextmanager
    def transaction(self) -> Generator[None, None, None]:
        """Context manager for transactions."""
        if not self._connection:
            raise CodomyrmexError("Not connected to database")

        try:
            yield
            self._connection.commit()
        except Exception as e:
            self._connection.rollback()
            logger.error(f"Transaction rolled back: {e}")
            raise

    def get_tables(self) -> List[str]:
        """Get list of tables in the database."""
        if not self._connection:
            raise CodomyrmexError("Not connected to database")

        result = self.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        return [row[0] for row in result.rows]

    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """Get column information for a table."""
        if not self._connection:
            raise CodomyrmexError("Not connected to database")

        result = self.execute(f"PRAGMA table_info({table_name})")
        columns = []
        for row in result.rows:
            columns.append({
                "cid": row[0],
                "name": row[1],
                "type": row[2],
                "notnull": bool(row[3]),
                "default": row[4],
                "pk": bool(row[5])
            })
        return columns


# Convenience functions
def connect_database(database_url: str) -> DatabaseManager:
    """Convenience function to connect to a database."""
    manager = DatabaseManager(database_url)
    manager.connect()
    return manager

def execute_query(database_url: str, query: str, params: Optional[Tuple] = None) -> QueryResult:
    """Convenience function to execute a single query."""
    manager = DatabaseManager(database_url)
    manager.connect()
    try:
        return manager.execute(query, params)
    finally:
        manager.disconnect()
