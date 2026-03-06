"""Bulkhead: concurrency-limiting pattern using a semaphore."""

import threading
from typing import Self

from codomyrmex.exceptions import BulkheadFullError


class Bulkhead:
    """
    Bulkhead pattern for limiting concurrent executions.

    Usage:
        bulkhead = Bulkhead(name="api", max_concurrent=10)

        with bulkhead:
            result = make_api_call()
    """

    def __init__(
        self,
        name: str = "default",
        max_concurrent: int = 10,
        max_queue: int = 0,
        timeout_s: float = 0.0,
    ):
        self.name = name
        self.max_concurrent = max_concurrent
        self.max_queue = max_queue
        self.timeout_s = timeout_s
        self._semaphore = threading.Semaphore(max_concurrent)
        self._active = 0
        self._queued = 0
        self._lock = threading.Lock()

    @property
    def active_count(self) -> int:
        return self._active

    @property
    def available_slots(self) -> int:
        return max(0, self.max_concurrent - self._active)

    def acquire(self) -> bool:
        """Try to acquire a slot; returns False if bulkhead is full."""
        timeout = self.timeout_s if self.timeout_s > 0 else None

        with self._lock:
            if self._active >= self.max_concurrent:
                if self.max_queue > 0 and self._queued < self.max_queue:
                    self._queued += 1
                else:
                    return False

        acquired = self._semaphore.acquire(timeout=timeout)

        with self._lock:
            if self._queued > 0:
                self._queued -= 1
            if acquired:
                self._active += 1

        return acquired

    def release(self) -> None:
        """Release a slot."""
        with self._lock:
            self._active = max(0, self._active - 1)
        self._semaphore.release()

    def __enter__(self) -> Self:
        if not self.acquire():
            raise BulkheadFullError(f"Bulkhead '{self.name}' is full")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.release()
