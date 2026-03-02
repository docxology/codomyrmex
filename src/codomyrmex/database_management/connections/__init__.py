"""
Database Connections Module

Connection pooling, health checks, and connection management.
"""

__version__ = "0.1.0"

import queue
import threading
import time
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Generic, Optional, TypeVar

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)

T = TypeVar('T')

class ConnectionState(Enum):
    """State of a database connection."""
    IDLE = "idle"
    IN_USE = "in_use"
    CLOSED = "closed"
    ERROR = "error"

@dataclass
class ConnectionStats:
    """Statistics for connection pool."""
    total_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    waiting_requests: int = 0
    total_checkouts: int = 0
    total_timeouts: int = 0
    avg_wait_time_ms: float = 0.0

    @property
    def utilization(self) -> float:
        """Get pool utilization percentage."""
        if self.total_connections == 0:
            return 0.0
        return self.active_connections / self.total_connections

@dataclass
class PoolConfig:
    """Configuration for connection pool."""
    min_connections: int = 1
    max_connections: int = 10
    acquire_timeout_s: float = 30.0
    idle_timeout_s: float = 300.0  # 5 minutes
    max_lifetime_s: float = 3600.0  # 1 hour
    validation_interval_s: float = 60.0
    health_check_query: str = "SELECT 1"

class Connection(ABC, Generic[T]):
    """Base class for database connections."""

    def __init__(self):
        self.created_at: datetime = datetime.now()
        self.last_used_at: datetime = datetime.now()
        self.state: ConnectionState = ConnectionState.IDLE
        self._use_count: int = 0

    @property
    def age_seconds(self) -> float:
        """Get connection age in seconds."""
        return (datetime.now() - self.created_at).total_seconds()

    @property
    def idle_seconds(self) -> float:
        """Get idle time in seconds."""
        return (datetime.now() - self.last_used_at).total_seconds()

    @property
    def use_count(self) -> int:
        """Get number of times connection was used."""
        return self._use_count

    def mark_used(self) -> None:
        """Mark connection as used."""
        self.last_used_at = datetime.now()
        self._use_count += 1
        self.state = ConnectionState.IN_USE

    def mark_idle(self) -> None:
        """Mark connection as idle."""
        self.state = ConnectionState.IDLE

    @abstractmethod
    def execute(self, query: str, params: tuple | None = None) -> Any:
        """Execute a query."""
        pass

    @abstractmethod
    def is_valid(self) -> bool:
        """Check if connection is still valid."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the connection."""
        pass

class InMemoryConnection(Connection[dict]):
    """In-memory connection for lightweight or test usage."""

    def __init__(self, connection_id: int = 0):
        super().__init__()
        self.connection_id = connection_id
        self._closed = False
        self._queries: list[str] = []

    def execute(self, query: str, params: tuple | None = None) -> dict:
        """Execute mock query."""
        if self._closed:
            raise RuntimeError("Connection is closed")
        self._queries.append(query)
        return {"result": "in_memory", "query": query}

    def is_valid(self) -> bool:
        """Check if connection is valid."""
        return not self._closed

    def close(self) -> None:
        """Close the connection."""
        self._closed = True
        self.state = ConnectionState.CLOSED

class ConnectionFactory(ABC, Generic[T]):
    """Factory for creating database connections."""

    @abstractmethod
    def create(self) -> Connection[T]:
        """Create a new connection."""
        pass

class InMemoryConnectionFactory(ConnectionFactory[dict]):
    """Factory for in-memory connections."""

    def __init__(self):
        self._counter = 0
        self._lock = threading.Lock()

    def create(self) -> InMemoryConnection:
        """Create a new in-memory connection."""
        with self._lock:
            self._counter += 1
            return InMemoryConnection(self._counter)

class ConnectionPool(Generic[T]):
    """
    Thread-safe database connection pool.

    Usage:
        factory = PostgresConnectionFactory(dsn="...")
        pool = ConnectionPool(factory, config=PoolConfig(max_connections=20))

        # Acquire and release
        conn = pool.acquire()
        try:
            result = conn.execute("SELECT * FROM users")
        finally:
            pool.release(conn)

        # Or use context manager
        with pool.connection() as conn:
            result = conn.execute("SELECT * FROM users")
    """

    def __init__(
        self,
        factory: ConnectionFactory[T],
        config: PoolConfig | None = None,
    ):
        self.factory = factory
        self.config = config or PoolConfig()
        self._pool: queue.Queue = queue.Queue()
        self._all_connections: list[Connection[T]] = []
        self._lock = threading.Lock()
        self._closed = False
        self._wait_times: list[float] = []

        # Stats
        self._total_checkouts = 0
        self._total_timeouts = 0

        # Initialize minimum connections
        self._initialize_pool()

    def _initialize_pool(self) -> None:
        """Initialize pool with minimum connections."""
        for _ in range(self.config.min_connections):
            self._create_connection()

    def _create_connection(self) -> Connection[T]:
        """Create a new connection and add to pool.

        Thread-safe: acquires ``_lock`` internally.
        """
        conn = self.factory.create()
        with self._lock:
            self._all_connections.append(conn)
        self._pool.put(conn)
        return conn

    def _create_connection_unlocked(self) -> Connection[T]:
        """Create a connection while ``_lock`` is already held by the caller.

        The caller **must** be holding ``self._lock`` when calling this.
        """
        conn = self.factory.create()
        self._all_connections.append(conn)
        return conn

    def _validate_connection(self, conn: Connection[T]) -> bool:
        """Validate a connection is still usable."""
        # Check lifetime
        if conn.age_seconds > self.config.max_lifetime_s:
            return False

        # Check validity
        try:
            return conn.is_valid()
        except Exception as e:
            logger.warning("Connection validity check failed: %s", e)
            return False

    def acquire(self, timeout: float | None = None) -> Connection[T]:
        """
        Acquire a connection from the pool.

        Args:
            timeout: Timeout in seconds (uses config default if None)

        Returns:
            A database connection

        Raises:
            TimeoutError: If no connection available within timeout
        """
        if self._closed:
            raise RuntimeError("Pool is closed")

        timeout = timeout if timeout is not None else self.config.acquire_timeout_s
        start_time = time.time()

        while True:
            try:
                # Try to get from pool
                remaining = timeout - (time.time() - start_time)
                if remaining <= 0:
                    self._total_timeouts += 1
                    raise TimeoutError("No connection available")

                conn = self._pool.get(timeout=min(remaining, 0.1))

                # Validate
                if not self._validate_connection(conn):
                    self._remove_connection(conn)
                    continue

                conn.mark_used()
                self._total_checkouts += 1
                self._wait_times.append((time.time() - start_time) * 1000)

                return conn

            except queue.Empty:
                # Try to create new connection if under limit
                with self._lock:
                    if len(self._all_connections) < self.config.max_connections:
                        conn = self._create_connection_unlocked()
                        conn.mark_used()
                        self._total_checkouts += 1
                        return conn

    def release(self, conn: Connection[T]) -> None:
        """Return a connection to the pool."""
        if conn.state == ConnectionState.CLOSED:
            self._remove_connection(conn)
            return

        # Check if still valid
        if not self._validate_connection(conn):
            self._remove_connection(conn)
            # Replenish if below minimum
            with self._lock:
                if len(self._all_connections) < self.config.min_connections:
                    replenish = True
                else:
                    replenish = False
            if replenish:
                self._create_connection()
            return

        conn.mark_idle()
        self._pool.put(conn)

    def _remove_connection(self, conn: Connection[T]) -> None:
        """Remove a connection from the pool."""
        try:
            conn.close()
        except Exception as e:
            logger.debug("Error closing connection during removal: %s", e)
            pass

        with self._lock:
            if conn in self._all_connections:
                self._all_connections.remove(conn)

    @contextmanager
    def connection(self) -> Iterator[Connection[T]]:
        """Context manager for connection checkout."""
        conn = self.acquire()
        try:
            yield conn
        finally:
            self.release(conn)

    @property
    def stats(self) -> ConnectionStats:
        """Get pool statistics."""
        with self._lock:
            active = sum(1 for c in self._all_connections if c.state == ConnectionState.IN_USE)
            idle = sum(1 for c in self._all_connections if c.state == ConnectionState.IDLE)

            return ConnectionStats(
                total_connections=len(self._all_connections),
                active_connections=active,
                idle_connections=idle,
                waiting_requests=0,  # Approximate
                total_checkouts=self._total_checkouts,
                total_timeouts=self._total_timeouts,
                avg_wait_time_ms=sum(self._wait_times[-100:]) / max(len(self._wait_times[-100:]), 1),
            )

    def close(self) -> None:
        """Close the pool and all connections."""
        self._closed = True

        with self._lock:
            for conn in self._all_connections:
                try:
                    conn.close()
                except Exception as e:
                    logger.debug("Error closing connection during pool shutdown: %s", e)
                    pass
            self._all_connections.clear()

        # Drain the queue
        try:
            while True:
                self._pool.get_nowait()
        except queue.Empty as e:
            logger.debug("Connection pool queue drained: %s", e)
            pass

class HealthChecker:
    """
    Health checker for database connections.

    Usage:
        checker = HealthChecker(pool, check_interval=60)
        checker.start()  # Background checking

        # Or manual check
        is_healthy = checker.check_health()
    """

    def __init__(
        self,
        pool: ConnectionPool,
        check_interval: float = 60.0,
        health_query: str = "SELECT 1",
    ):
        self.pool = pool
        self.check_interval = check_interval
        self.health_query = health_query
        self._running = False
        self._thread: threading.Thread | None = None
        self._last_check: datetime | None = None
        self._last_result: bool = True

    def check_health(self) -> bool:
        """Perform health check."""
        try:
            with self.pool.connection() as conn:
                conn.execute(self.health_query)
            self._last_result = True
        except Exception:
            self._last_result = False

        self._last_check = datetime.now()
        return self._last_result

    def start(self) -> None:
        """Start background health checking."""
        if self._running:
            return

        self._running = True

        def check_loop():
            while self._running:
                self.check_health()
                time.sleep(self.check_interval)

        self._thread = threading.Thread(target=check_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop background health checking."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)

    @property
    def is_healthy(self) -> bool:
        """Get last health check result."""
        return self._last_result

__all__ = [
    # Enums
    "ConnectionState",
    # Data classes
    "ConnectionStats",
    "PoolConfig",
    # Base classes
    "Connection",
    "ConnectionFactory",
    # In-memory implementations
    "InMemoryConnection",
    "InMemoryConnectionFactory",
    # Pool
    "ConnectionPool",
    # Health
    "HealthChecker",
]
