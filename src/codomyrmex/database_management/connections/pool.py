"""Thread-safe database connection pool."""

import queue
import threading
import time
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Generic, TypeVar

from codomyrmex.logging_monitoring import get_logger

from .base import Connection, ConnectionFactory
from .models import ConnectionState, ConnectionStats, PoolConfig

logger = get_logger(__name__)
T = TypeVar("T")


class ConnectionPool(Generic[T]):
    """Thread-safe database connection pool.

    Usage:
        factory = InMemoryConnectionFactory()
        pool = ConnectionPool(factory, config=PoolConfig(max_connections=20))

        with pool.connection() as conn:
            result = conn.execute("SELECT * FROM users")
    """

    def __init__(
        self, factory: ConnectionFactory[T], config: PoolConfig | None = None
    ) -> None:
        self.factory = factory
        self.config = config or PoolConfig()
        self._pool: queue.Queue = queue.Queue()
        self._all_connections: list[Connection[T]] = []
        self._lock = threading.Lock()
        self._closed = False
        self._wait_times: list[float] = []
        self._total_checkouts = 0
        self._total_timeouts = 0
        self._initialize_pool()

    def _initialize_pool(self) -> None:
        for _ in range(self.config.min_connections):
            self._create_connection()

    def _create_connection(self) -> Connection[T]:
        conn = self.factory.create()
        with self._lock:
            self._all_connections.append(conn)
        self._pool.put(conn)
        return conn

    def _create_connection_unlocked(self) -> Connection[T]:
        """Create a connection while ``_lock`` is already held by the caller."""
        conn = self.factory.create()
        self._all_connections.append(conn)
        return conn

    def _validate_connection(self, conn: Connection[T]) -> bool:
        if conn.age_seconds > self.config.max_lifetime_s:
            return False
        try:
            return conn.is_valid()
        except Exception as e:
            logger.warning("Connection validity check failed: %s", e)
            return False

    def _remove_connection(self, conn: Connection[T]) -> None:
        try:
            conn.close()
        except Exception as e:
            logger.debug("Error closing connection during removal: %s", e)
        with self._lock:
            if conn in self._all_connections:
                self._all_connections.remove(conn)

    def acquire(self, timeout: float | None = None) -> Connection[T]:
        """Acquire a connection from the pool."""
        if self._closed:
            raise RuntimeError("Pool is closed")
        timeout = timeout if timeout is not None else self.config.acquire_timeout_s
        start_time = time.time()
        while True:
            try:
                remaining = timeout - (time.time() - start_time)
                if remaining <= 0:
                    self._total_timeouts += 1
                    raise TimeoutError("No connection available")
                conn = self._pool.get(timeout=min(remaining, 0.1))
                if not self._validate_connection(conn):
                    self._remove_connection(conn)
                    continue
                conn.mark_used()
                self._total_checkouts += 1
                self._wait_times.append((time.time() - start_time) * 1000)
                return conn
            except queue.Empty:
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
        if not self._validate_connection(conn):
            self._remove_connection(conn)
            with self._lock:
                replenish = len(self._all_connections) < self.config.min_connections
            if replenish:
                self._create_connection()
            return
        conn.mark_idle()
        self._pool.put(conn)

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
        with self._lock:
            active = sum(
                1 for c in self._all_connections if c.state == ConnectionState.IN_USE
            )
            idle = sum(
                1 for c in self._all_connections if c.state == ConnectionState.IDLE
            )
            return ConnectionStats(
                total_connections=len(self._all_connections),
                active_connections=active,
                idle_connections=idle,
                waiting_requests=0,
                total_checkouts=self._total_checkouts,
                total_timeouts=self._total_timeouts,
                avg_wait_time_ms=sum(self._wait_times[-100:])
                / max(len(self._wait_times[-100:]), 1),
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
            self._all_connections.clear()
        try:
            while True:
                self._pool.get_nowait()
        except queue.Empty:
            pass
