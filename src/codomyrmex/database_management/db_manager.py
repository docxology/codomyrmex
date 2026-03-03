"""Database Manager Module for Codomyrmex Database Management.

Provides database connection, query execution, and transaction management
for SQLite, PostgreSQL, and MySQL databases.
"""

import os
import sqlite3
import time
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from codomyrmex.config_management.defaults import (
    DEFAULT_POSTGRES_HOST,
    DEFAULT_POSTGRES_PORT,
    DEFAULT_POSTGRES_USER,
)
from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


class DatabaseType(Enum):
    """Supported database types."""

    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    REDIS = "redis"
    CUSTOM = "custom"


@dataclass
class QueryResult:
    """Result of a query execution."""

    success: bool
    rows: list[tuple]
    columns: list[str]
    row_count: int
    execution_time: float
    error_message: str | None = None

    @property
    def valid(self) -> bool:
        """Alias for success to match Unified Streamline pattern."""
        return self.success

    def to_dict_list(self) -> list[dict[str, Any]]:
        """Convert rows to list of dictionaries."""
        return [dict(zip(self.columns, row, strict=False)) for row in self.rows]


@dataclass
class DatabaseConnection:
    """Database connection information and low-level operations."""

    name: str
    db_type: DatabaseType
    database: str
    host: str = ""
    port: int = 0
    username: str = ""
    password: str = ""
    ssl_mode: str = "prefer"
    connection_pool_size: int = 10
    connection_timeout: int = 30
    max_retries: int = 3
    connection_string: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    _connection: Any = None
    connection_count: int = 0

    def __post_init__(self):
        """Set defaults based on database type."""
        if self.db_type != DatabaseType.SQLITE:
            self.host = self.host or os.getenv("DB_HOST", DEFAULT_POSTGRES_HOST)
            self.port = self.port or int(os.getenv("DB_PORT", DEFAULT_POSTGRES_PORT))
            self.username = self.username or os.getenv("DB_USER", DEFAULT_POSTGRES_USER)

            if self.db_type == DatabaseType.MYSQL:
                if self.port == int(DEFAULT_POSTGRES_PORT):
                    self.port = 3306
                if self.username == DEFAULT_POSTGRES_USER:
                    self.username = "root"

    def get_connection_string(self) -> str:
        """Get database connection string."""
        if self.connection_string:
            return self.connection_string

        if self.db_type == DatabaseType.SQLITE:
            return f"sqlite:///{self.database}"
        elif self.db_type == DatabaseType.POSTGRESQL:
            return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        elif self.db_type == DatabaseType.MYSQL:
            return f"mysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")

    def connect(self):
        """Establish connection."""
        if self._connection:
            return

        if self.db_type == DatabaseType.SQLITE:
            self._connection = sqlite3.connect(self.database)
            self.connection_count += 1
            logger.info(f"Connected to SQLite database: {self.database}")
        elif self.db_type in [DatabaseType.POSTGRESQL, DatabaseType.MYSQL]:
            # In a real implementation, we would use psycopg2 or pymysql here.
            # For this thin orchestrator, we'll keep it simple or raise if not available.
            raise NotImplementedError(
                f"Connection for {self.db_type.value} not fully implemented in this version"
            )
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")

    def disconnect(self):
        """Close connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info(f"Disconnected from database: {self.name}")

    def is_connected(self) -> bool:
        """Check if connected."""
        return self._connection is not None

    def execute(
        self, query: str, params: tuple | None = None, commit: bool = True
    ) -> QueryResult:
        """Execute a query and return QueryResult.

        Args:
            query: SQL query string.
            params: Optional tuple of parameters.
            commit: Whether to commit after execution if it's a DDL/DML query.
        """
        if not self._connection:
            self.connect()

        start_time = time.time()
        try:
            cursor = self._connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            rows = []
            columns = []
            row_count = 0

            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                row_count = len(rows)
            else:
                if commit:
                    self._connection.commit()
                row_count = cursor.rowcount

            execution_time = time.time() - start_time
            return QueryResult(
                success=True,
                rows=rows,
                columns=columns,
                row_count=row_count,
                execution_time=execution_time,
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
                error_message=str(e),
            )

    @contextmanager
    def transaction(self) -> Generator["DatabaseConnection", None, None]:
        """Context manager for transactions."""
        if not self._connection:
            self.connect()

        try:
            yield self
            self._connection.commit()
        except Exception as e:
            self._connection.rollback()
            logger.error(f"Transaction rolled back: {e}")
            raise


class DatabaseManager:
    """Database connection and query management."""

    def __init__(self, database_url: str | None = None):
        """Initialize database manager."""
        self.connections: dict[str, DatabaseConnection] = {}
        self.default_connection_name: str | None = None

        if database_url:
            self.connect(database_url)

    def add_connection(self, connection: DatabaseConnection):
        """Add a database connection."""
        self.connections[connection.name] = connection
        if not self.default_connection_name:
            self.default_connection_name = connection.name

    def remove_connection(self, name: str):
        """Remove a database connection."""
        if name in self.connections:
            self.connections[name].disconnect()
            del self.connections[name]
            if self.default_connection_name == name:
                self.default_connection_name = (
                    next(iter(self.connections.keys())) if self.connections else None
                )

    def get_connection(self, name: str | None = None) -> DatabaseConnection | None:
        """Get a database connection."""
        name = name or self.default_connection_name
        return self.connections.get(name) if name else None

    def list_connections(self) -> list[str]:
        """List all connection names."""
        return list(self.connections.keys())

    def connect_all(self):
        """Connect all databases."""
        for conn in self.connections.values():
            conn.connect()

    def disconnect_all(self):
        """Disconnect all databases."""
        for conn in self.connections.values():
            conn.disconnect()

    def connect(self, database_url: str) -> DatabaseConnection:
        """Establish a database connection from URL."""
        if database_url.startswith("sqlite://"):
            db_path = database_url.replace("sqlite:///", "")
            if not db_path:
                db_path = ":memory:"
            db_type = DatabaseType.SQLITE
            name = f"sqlite_{os.path.basename(db_path) or 'memory'}_{int(time.time())}"
        else:
            # Simple parsing for other types if needed, but primarily supporting SQLite for now
            raise CodomyrmexError(f"Unsupported database URL: {database_url}")

        conn = DatabaseConnection(name=name, db_type=db_type, database=db_path)
        conn.connect()
        self.add_connection(conn)
        return conn

    def execute(
        self,
        query: str,
        params: tuple | None = None,
        connection_name: str | None = None,
        commit: bool = True,
    ) -> QueryResult:
        """Execute a query on the specified or default connection."""
        conn = self.get_connection(connection_name)
        if not conn:
            raise CodomyrmexError("No database connection available")
        return conn.execute(query, params, commit=commit)

    def health_check_all(self) -> dict[str, dict[str, Any]]:
        """Check health of all connections."""
        health = {}
        for name, conn in self.connections.items():
            start = time.time()
            try:
                # Simple query to check health
                if conn.db_type == DatabaseType.SQLITE:
                    conn.execute("SELECT 1")
                health[name] = {
                    "status": "healthy",
                    "response_time": time.time() - start,
                }
            except Exception as e:
                health[name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "response_time": time.time() - start,
                }
        return health

    def get_database_stats(self) -> dict[str, Any]:
        """Get overall database statistics."""
        return {
            "total_connections": len(self.connections),
            "active_connections": sum(
                1 for c in self.connections.values() if c.is_connected()
            ),
            "databases_by_type": {
                t.value: sum(1 for c in self.connections.values() if c.db_type == t)
                for t in DatabaseType
            },
        }

    @contextmanager
    def transaction(
        self, connection_name: str | None = None
    ) -> Generator[DatabaseConnection, None, None]:
        """Context manager for transactions."""
        conn = self.get_connection(connection_name)
        if not conn:
            raise CodomyrmexError("No database connection available")

        with conn.transaction() as tx:
            yield tx

    def get_tables(self, connection_name: str | None = None) -> list[str]:
        """Get list of tables in the database."""
        conn = self.get_connection(connection_name)
        if not conn:
            raise CodomyrmexError("No database connection available")

        if conn.db_type == DatabaseType.SQLITE:
            result = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            return [row[0] for row in result.rows if not row[0].startswith("sqlite_")]
        return []

    def get_table_info(
        self, table_name: str, connection_name: str | None = None
    ) -> list[dict[str, Any]]:
        """Get column information for a table."""
        conn = self.get_connection(connection_name)
        if not conn:
            raise CodomyrmexError("No database connection available")

        if conn.db_type == DatabaseType.SQLITE:
            result = conn.execute(f"PRAGMA table_info({table_name})")
            columns = []
            for row in result.rows:
                columns.append(
                    {
                        "cid": row[0],
                        "name": row[1],
                        "type": row[2],
                        "notnull": bool(row[3]),
                        "default": row[4],
                        "pk": bool(row[5]),
                    }
                )
            return columns
        return []


# Convenience functions
def connect_database(database_url: str) -> DatabaseManager:
    """Convenience function to connect to a database."""
    return DatabaseManager(database_url)


def manage_databases(database_url: str | None = None) -> DatabaseManager:
    """Create and return a DatabaseManager instance."""
    return DatabaseManager(database_url)


def execute_query(
    database_url: str, query: str, params: tuple | None = None
) -> QueryResult:
    """Convenience function to execute a single query."""
    manager = DatabaseManager(database_url)
    try:
        return manager.execute(query, params)
    finally:
        manager.disconnect_all()
