"""Database connection helpers for migration management."""

import re
import sqlite3
from typing import Any

from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

try:
    import psycopg2
    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False

try:
    import pymysql
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False


class DatabaseConnector:
    """Handles database connections for migrations."""

    def __init__(self, database_url: str):
        """Initialize database connector from URL."""
        self.database_url = database_url
        self._connection = None
        self._db_type = self._parse_db_type(database_url)

    def _parse_db_type(self, url: str) -> str:
        """Parse database type from URL."""
        if url.startswith("sqlite"):
            return "sqlite"
        if url.startswith(("postgresql", "postgres")):
            return "postgresql"
        if url.startswith("mysql"):
            return "mysql"
        raise CodomyrmexError(f"Unsupported database URL format: {url}")

    def _parse_connection_params(self) -> dict[str, Any]:
        """Parse connection parameters from URL."""
        url = self.database_url
        if self._db_type == "sqlite":
            match = re.match(r"sqlite:///(.+)", url)
            if match:
                return {"database": match.group(1)}
            raise CodomyrmexError(f"Invalid SQLite URL: {url}")
        pattern = r"(?:postgresql|postgres|mysql)://(?:([^:]+):([^@]+)@)?([^:\/]+)(?::(\d+))?/(.+)"
        match = re.match(pattern, url)
        if match:
            return {
                "user": match.group(1) or ("postgres" if self._db_type == "postgresql" else "root"),
                "password": match.group(2) or "",
                "host": match.group(3),
                "port": int(match.group(4)) if match.group(4) else (5432 if self._db_type == "postgresql" else 3306),
                "database": match.group(5),
            }
        raise CodomyrmexError(f"Invalid database URL: {url}")

    def connect(self):
        """Establish database connection."""
        params = self._parse_connection_params()
        if self._db_type == "sqlite":
            self._connection = sqlite3.connect(params["database"])
            self._connection.execute("PRAGMA foreign_keys = ON")
            logger.info("Connected to SQLite database: %s", params["database"])
        elif self._db_type == "postgresql":
            if not POSTGRESQL_AVAILABLE:
                raise CodomyrmexError("PostgreSQL driver not available. Install with: uv pip install psycopg2-binary")
            self._connection = psycopg2.connect(
                host=params["host"], port=params["port"], database=params["database"],
                user=params["user"], password=params["password"],
            )
            logger.info("Connected to PostgreSQL database: %s", params["database"])
        elif self._db_type == "mysql":
            if not MYSQL_AVAILABLE:
                raise CodomyrmexError("MySQL driver not available. Install with: uv pip install pymysql")
            self._connection = pymysql.connect(
                host=params["host"], port=params["port"], database=params["database"],
                user=params["user"], password=params["password"],
            )
            logger.info("Connected to MySQL database: %s", params["database"])

    def disconnect(self):
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("Database connection closed")

    def execute(self, sql: str, params: tuple | None = None) -> tuple[int, Any]:
        """Execute SQL statement. Returns (rows_affected, cursor)."""
        if not self._connection:
            raise CodomyrmexError("Not connected to database")
        cursor = self._connection.cursor()
        try:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            return max(cursor.rowcount, 0), cursor
        except Exception as e:
            raise CodomyrmexError(f"SQL execution failed: {e}") from e

    def execute_script(self, sql_script: str) -> tuple[int, int]:
        """Execute multiple SQL statements. Returns (total_rows_affected, statements_executed)."""
        if not self._connection:
            raise CodomyrmexError("Not connected to database")
        statements = self._split_sql_statements(sql_script)
        total_rows = 0
        statements_executed = 0
        for statement in statements:
            statement = statement.strip()
            if statement and not statement.startswith("--"):
                rows, _ = self.execute(statement)
                total_rows += rows
                statements_executed += 1
        return total_rows, statements_executed

    def _split_sql_statements(self, sql_script: str) -> list[str]:
        """Split SQL script into individual statements."""
        statements = []
        current = []
        for line in sql_script.split("\n"):
            line = line.strip()
            if line.startswith("--"):
                continue
            current.append(line)
            if line.endswith(";"):
                statements.append("\n".join(current))
                current = []
        if current:
            statements.append("\n".join(current))
        return [s for s in statements if s.strip()]

    def commit(self):
        """Commit transaction."""
        if self._connection:
            self._connection.commit()

    def rollback(self):
        """Rollback transaction."""
        if self._connection:
            self._connection.rollback()

    @property
    def connection(self):
        """Get raw connection."""
        return self._connection
