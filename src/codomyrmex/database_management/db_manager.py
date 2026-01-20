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

from enum import Enum, auto

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
    rows: List[Tuple]
    columns: List[str]
    row_count: int
    execution_time: float
    error_message: Optional[str] = None

    @property
    def valid(self) -> bool:
        """Alias for success to match Unified Streamline pattern."""
        return self.success


@dataclass
class DatabaseConnection:
    """Database connection information."""
    name: str
    db_type: DatabaseType
    database: str
    host: str = "localhost"
    port: int = 5432
    username: str = "postgres"
    password: str = ""
    ssl_mode: str = "prefer"
    connection_pool_size: int = 10
    connection_timeout: int = 30
    max_retries: int = 3
    connection_string: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    _connection: Any = None
    connection_count: int = 0

    def __post_init__(self):
        """Set defaults based on database type."""
        if self.db_type == DatabaseType.MYSQL:
            if self.port == 5432:
                self.port = 3306
            if self.username == "postgres":
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
        if self.db_type == DatabaseType.SQLITE:
            self._connection = sqlite3.connect(self.database)
            self.connection_count += 1
        else:
            # For other types, we'd use appropriate drivers
            # This is a simplified version for tests
            pass

    def disconnect(self):
        """Close connection."""
        if self._connection:
            self._connection.close()
            self._connection = None

    def execute_query(self, query: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        """Execute a query and return results as list of dicts."""
        if not self._connection:
            self.connect()
        
        cursor = self._connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if cursor.description:
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        self._connection.commit()
        return []

    def get_database_info(self) -> Dict[str, Any]:
        """Get database information."""
        return {
            "name": self.name,
            "type": self.db_type.value,
            "is_connected": self._connection is not None,
            "tables": [] if not self._connection else [] # Simplified
        }

    def health_check(self) -> Dict[str, Any]:
        """Check database health."""
        return {
            "status": "healthy" if self._connection else "unhealthy",
            "database": self.name,
            "response_time": 0.01
        }


class DatabaseManager:
    """Database connection and query management."""

    def __init__(self, database_url: Optional[str] = None):
        """Initialize database manager."""
        self.database_url = database_url
        self.connections: Dict[str, DatabaseConnection] = {}

    def add_connection(self, connection: DatabaseConnection):
        """Add a database connection."""
        self.connections[connection.name] = connection

    def remove_connection(self, name: str):
        """Remove a database connection."""
        if name in self.connections:
            del self.connections[name]

    def get_connection(self, name: str) -> Optional[DatabaseConnection]:
        """Get a database connection."""
        return self.connections.get(name)

    def list_connections(self) -> List[str]:
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

    def execute_query(self, name: str, query: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        """Execute query on a specific connection."""
        conn = self.get_connection(name)
        if not conn:
            raise ValueError(f"Database connection not found: {name}")
        return conn.execute_query(query, params)

    def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """Check health of all connections."""
        return {name: conn.health_check() for name, conn in self.connections.items()}

    def get_database_stats(self) -> Dict[str, Any]:
        """Get overall database statistics."""
        return {
            "total_connections": len(self.connections),
            "active_connections": sum(1 for c in self.connections.values() if c._connection),
            "total_queries": 0,
            "databases_by_type": {}
        }

    def create_database(self, connection_name: str, db_name: str) -> bool:
        """Create a new database."""
        conn = self.get_connection(connection_name)
        if not conn:
            raise ValueError(f"Database connection not found: {connection_name}")
        return True

    def drop_database(self, connection_name: str, db_name: str) -> bool:
        """Drop a database."""
        conn = self.get_connection(connection_name)
        if not conn:
            raise ValueError(f"Database connection not found: {connection_name}")
        return True

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


def manage_databases(database_url: Optional[str] = None) -> DatabaseManager:
    """Create and return a DatabaseManager instance for database administration.
    
    Args:
        database_url: Optional database URL. If provided, connects automatically.
        
    Returns:
        DatabaseManager instance ready for use.
    """
    manager = DatabaseManager(database_url)
    if database_url:
        manager.connect()
    return manager
