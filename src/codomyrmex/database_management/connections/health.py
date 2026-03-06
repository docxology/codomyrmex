"""Health checker for database connections."""

import threading
import time
from datetime import datetime

from .pool import ConnectionPool


class HealthChecker:
    """Health checker for database connections.

    Usage:
        checker = HealthChecker(pool, check_interval=60)
        checker.start()

        is_healthy = checker.check_health()
    """

    def __init__(
        self,
        pool: ConnectionPool,
        check_interval: float = 60.0,
        health_query: str = "SELECT 1",
    ) -> None:
        self.pool = pool
        self.check_interval = check_interval
        self.health_query = health_query
        self._running = False
        self._thread: threading.Thread | None = None
        self._last_check: datetime | None = None
        self._last_result: bool = True

    def check_health(self) -> bool:
        """Perform a health check against the pool."""
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

        def check_loop() -> None:
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
        return self._last_result
