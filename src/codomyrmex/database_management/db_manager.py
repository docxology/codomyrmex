from datetime import datetime, timezone
from typing import Any, Optional
import os
import sys

from dataclasses import dataclass
from enum import Enum
import psycopg2
import pymysql
import sqlite3

from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring.logger_config import get_logger




























"""
Database Manager for Codomyrmex Database Management Module.

Provides comprehensive database connection management and administration.
"""


# Optional database drivers - import conditionally
try:
    POSTGRESQL_AVAILABLE = True
except ImportError:
    psycopg2 = None
    POSTGRESQL_AVAILABLE = False

try:
    MYSQL_AVAILABLE = True
except ImportError:
    pymysql = None
    MYSQL_AVAILABLE = False

# Add project root to Python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    pass
#     sys.path.insert(0, PROJECT_ROOT)  # Removed sys.path manipulation


logger = get_logger(__name__)


class DatabaseType(Enum):
    """Supported database types."""

    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    REDIS = "redis"


@dataclass
class DatabaseConnection:
    """Database connection configuration and management."""

    name: str
    db_type: DatabaseType
    database: str
    host: Optional[str] = None  # Not required for SQLite
    port: int = None  # Will be set based on db_type in __post_init__
    username: Optional[str] = None
    password: Optional[str] = None
    connection_string: Optional[str] = None
    ssl_mode: str = "prefer"
    connection_pool_size: int = 10
    connection_timeout: int = 30
    max_retries: int = 3

    # Runtime attributes
    _connection = None
    _pool = None
    created_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    connection_count: int = 0

    def __post_init__(self):
        self.created_at = datetime.now(timezone.utc)

        # Set default ports if not provided (not needed for SQLite)
        if self.port is None and self.db_type != DatabaseType.SQLITE:
            if self.db_type == DatabaseType.POSTGRESQL:
                self.port = 5432
            elif self.db_type == DatabaseType.MYSQL:
                self.port = 3306
            elif self.db_type == DatabaseType.MONGODB:
                self.port = 27017
            elif self.db_type == DatabaseType.REDIS:
                self.port = 6379
            else:
                self.port = 0  # Unknown type

        # Set default username if not provided
        if self.username is None:
            if self.db_type == DatabaseType.POSTGRESQL:
                self.username = "postgres"
            elif self.db_type == DatabaseType.MYSQL:
                self.username = "root"
            elif self.db_type == DatabaseType.MONGODB:
                self.username = "admin"
            elif self.db_type == DatabaseType.REDIS:
                self.username = "default"
            # SQLite doesn't need username

    def get_connection_string(self) -> str:
        """Generate connection string for the database."""
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
        """Establish database connection."""
        try:
            if self.db_type == DatabaseType.SQLITE:
                self._connection = sqlite3.connect(self.database)
                logger.info(f"Connected to SQLite database: {self.database}")

            elif self.db_type == DatabaseType.POSTGRESQL:
                if not POSTGRESQL_AVAILABLE:
                    raise CodomyrmexError("PostgreSQL driver (psycopg2) not available. Install with: pip install psycopg2-binary")
                self._connection = psycopg2.connect(
                    host=self.host,
                    port=self.port,
                    database=self.database,
                    user=self.username,
                    password=self.password,
                    connect_timeout=self.connection_timeout,
                )
                logger.info(f"Connected to PostgreSQL database: {self.database}")

            elif self.db_type == DatabaseType.MYSQL:
                if not MYSQL_AVAILABLE:
                    raise CodomyrmexError("MySQL driver (pymysql) not available. Install with: pip install pymysql")
                self._connection = pymysql.connect(
                    host=self.host,
                    port=self.port,
                    database=self.database,
                    user=self.username,
                    password=self.password,
                    connect_timeout=self.connection_timeout,
                )
                logger.info(f"Connected to MySQL database: {self.database}")

            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")

            self.last_used = datetime.now(timezone.utc)
            self.connection_count += 1

        except Exception as e:
            logger.error(f"Failed to connect to database {self.name}: {e}")
            raise

    def disconnect(self):
        """Close database connection."""
        try:
            if self._connection:
                self._connection.close()
                self._connection = None
                logger.info(f"Disconnected from database: {self.name}")
        except Exception as e:
            logger.error(f"Error disconnecting from database {self.name}: {e}")

    def execute_query(
        self, query: str, params: Optional[tuple] = None
    ) -> list[dict[str, Any]]:
        """
        Execute a database query.

        Args:
            query: SQL query to execute
            params: Query parameters

        Returns:
            List of query results
        """
        if not self._connection:
            self.connect()

        try:
            cursor = self._connection.cursor()

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            if query.strip().upper().startswith(("SELECT", "SHOW", "DESCRIBE")):
                columns = [desc[0] for desc in cursor.description]
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                return results
            else:
                self._connection.commit()
                return [{"affected_rows": cursor.rowcount}]

        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            self._connection.rollback()
            raise

    def get_database_info(self) -> dict[str, Any]:
        """Get database information and statistics."""
        info = {
            "name": self.name,
            "type": self.db_type.value,
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "connection_count": self.connection_count,
            "is_connected": self._connection is not None,
        }

        # Get database-specific information
        if self.db_type == DatabaseType.SQLITE and self._connection:
            try:
                cursor = self._connection.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                info["tables"] = [table[0] for table in tables]

                cursor.execute("PRAGMA database_list;")
                db_info = cursor.fetchone()
                if db_info:
                    info["file_path"] = db_info[2]

            except Exception as e:
                logger.warning(f"Failed to get SQLite info: {e}")

        return info

    def health_check(self) -> dict[str, Any]:
        """Perform database health check."""
        health = {
            "database": self.name,
            "status": "unknown",
            "response_time": None,
            "error": None,
        }

        try:
            start_time = datetime.now(timezone.utc)

            if self.db_type == DatabaseType.SQLITE:
                self.execute_query("SELECT 1;")
            elif self.db_type in [DatabaseType.POSTGRESQL, DatabaseType.MYSQL]:
                self.execute_query("SELECT 1 as health_check;")

            end_time = datetime.now(timezone.utc)
            health["status"] = "healthy"
            health["response_time"] = (end_time - start_time).total_seconds()

        except Exception as e:
            health["status"] = "unhealthy"
            health["error"] = str(e)

        return health


class DatabaseManager:
    """
    Comprehensive database manager for multiple database types.

    Features:
    - Multi-database connection management
    - Connection pooling and optimization
    - Database health monitoring
    - Schema management and queries
    - Backup and restore operations
    """

    def __init__(self):
        """Initialize the database manager."""
        self.connections: dict[str, DatabaseConnection] = {}

    def add_connection(self, connection: DatabaseConnection):
        """Add a database connection."""
        self.connections[connection.name] = connection
        logger.info(f"Added database connection: {connection.name}")

    def remove_connection(self, name: str):
        """Remove a database connection."""
        if name in self.connections:
            self.connections[name].disconnect()
            del self.connections[name]
            logger.info(f"Removed database connection: {name}")

    def get_connection(self, name: str) -> Optional[DatabaseConnection]:
        """Get a database connection by name."""
        return self.connections.get(name)

    def list_connections(self) -> list[str]:
        """List all connection names."""
        return list(self.connections.keys())

    def connect_all(self):
        """Connect to all configured databases."""
        for name, connection in self.connections.items():
            try:
                connection.connect()
            except Exception as e:
                logger.error(f"Failed to connect to {name}: {e}")

    def disconnect_all(self):
        """Disconnect from all databases."""
        for connection in self.connections.values():
            connection.disconnect()

    def execute_query(
        self, connection_name: str, query: str, params: Optional[tuple] = None
    ) -> list[dict[str, Any]]:
        """
        Execute a query on a specific database connection.

        Args:
            connection_name: Name of the database connection
            query: SQL query to execute
            params: Query parameters

        Returns:
            Query results
        """
        connection = self.get_connection(connection_name)
        if not connection:
            raise ValueError(f"Database connection not found: {connection_name}")

        return connection.execute_query(query, params)

    def health_check_all(self) -> dict[str, dict[str, Any]]:
        """Perform health checks on all database connections."""
        health_status = {}

        for name, connection in self.connections.items():
            try:
                health_status[name] = connection.health_check()
            except Exception as e:
                health_status[name] = {
                    "database": name,
                    "status": "error",
                    "error": str(e),
                }

        return health_status

    def get_database_stats(self) -> dict[str, Any]:
        """Get statistics for all databases."""
        stats = {
            "total_connections": len(self.connections),
            "active_connections": 0,
            "total_queries": 0,
            "databases_by_type": {},
            "health_summary": {"healthy": 0, "unhealthy": 0, "unknown": 0},
        }

        health_checks = self.health_check_all()

        for name, connection in self.connections.items():
            if connection._connection:
                stats["active_connections"] += 1

            stats["total_queries"] += connection.connection_count

            db_type = connection.db_type.value
            if db_type not in stats["databases_by_type"]:
                stats["databases_by_type"][db_type] = 0
            stats["databases_by_type"][db_type] += 1

            # Health summary
            health = health_checks.get(name, {})
            status = health.get("status", "unknown")
            if status in stats["health_summary"]:
                stats["health_summary"][status] += 1

        return stats

    def create_database(self, connection_name: str, database_name: str) -> bool:
        """
        Create a new database.

        Args:
            connection_name: Name of the connection to use
            database_name: Name of the database to create

        Returns:
            bool: True if creation successful
        """
        connection = self.get_connection(connection_name)
        if not connection:
            raise ValueError(f"Database connection not found: {connection_name}")

        try:
            if connection.db_type == DatabaseType.SQLITE:
                # SQLite creates database automatically
                return True

            elif connection.db_type == DatabaseType.POSTGRESQL:
                # Connect to postgres database first
                postgres_conn = DatabaseConnection(
                    name="postgres_temp",
                    db_type=DatabaseType.POSTGRESQL,
                    host=connection.host,
                    port=connection.port,
                    database="postgres",
                    username=connection.username,
                    password=connection.password,
                )
                postgres_conn.connect()
                postgres_conn.execute_query(f"CREATE DATABASE {database_name};")
                postgres_conn.disconnect()

            elif connection.db_type == DatabaseType.MYSQL:
                # Connect without database first
                mysql_conn = DatabaseConnection(
                    name="mysql_temp",
                    db_type=DatabaseType.MYSQL,
                    host=connection.host,
                    port=connection.port,
                    database="",
                    username=connection.username,
                    password=connection.password,
                )
                mysql_conn.connect()
                mysql_conn.execute_query(f"CREATE DATABASE {database_name};")
                mysql_conn.disconnect()

            logger.info(f"Created database: {database_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to create database {database_name}: {e}")
            return False

    def drop_database(self, connection_name: str, database_name: str) -> bool:
        """
        Drop a database.

        Args:
            connection_name: Name of the connection to use
            database_name: Name of the database to drop

        Returns:
            bool: True if drop successful
        """
        connection = self.get_connection(connection_name)
        if not connection:
            raise ValueError(f"Database connection not found: {connection_name}")

        try:
            if connection.db_type == DatabaseType.POSTGRESQL:
                postgres_conn = DatabaseConnection(
                    name="postgres_temp",
                    db_type=DatabaseType.POSTGRESQL,
                    host=connection.host,
                    port=connection.port,
                    database="postgres",
                    username=connection.username,
                    password=connection.password,
                )
                postgres_conn.connect()
                postgres_conn.execute_query(f"DROP DATABASE IF EXISTS {database_name};")
                postgres_conn.disconnect()

            elif connection.db_type == DatabaseType.MYSQL:
                mysql_conn = DatabaseConnection(
                    name="mysql_temp",
                    db_type=DatabaseType.MYSQL,
                    host=connection.host,
                    port=connection.port,
                    database="",
                    username=connection.username,
                    password=connection.password,
                )
                mysql_conn.connect()
                mysql_conn.execute_query(f"DROP DATABASE IF EXISTS {database_name};")
                mysql_conn.disconnect()

            logger.info(f"Dropped database: {database_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to drop database {database_name}: {e}")
            return False


# Convenience functions
def manage_databases() -> DatabaseManager:
    """
    Convenience function to create database manager.

    Returns:
        DatabaseManager: Configured database manager
    """
    return DatabaseManager()
