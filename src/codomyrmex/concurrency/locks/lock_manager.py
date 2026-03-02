"""Unified lock management and advanced synchronization primitives."""

import threading
from dataclasses import dataclass

from codomyrmex.logging_monitoring.core.logger_config import get_logger

from .distributed_lock import BaseLock

logger = get_logger(__name__)


@dataclass
class LockStats:
    """Statistics for lock manager telemetry."""
    total_locks: int
    total_acquisitions: int
    total_releases: int
    active_locks: int

class LockManager:
    """Orchestrates multiple locks and provides multi-resource acquisition."""

    def __init__(self):
        """Initialize this instance."""
        self._locks: dict[str, BaseLock] = {}
        self._total_acquisitions = 0
        self._total_releases = 0

    def register_lock(self, name: str, lock: BaseLock):
        """register Lock ."""
        self._locks[name] = lock

    @property
    def stats(self) -> LockStats:
        """Get lock manager statistics for telemetry."""
        return LockStats(
            total_locks=len(self._locks),
            total_acquisitions=self._total_acquisitions,
            total_releases=self._total_releases,
            active_locks=sum(1 for lock in self._locks.values() if getattr(lock, '_acquired', False))
        )

    def acquire_all(self, names: list[str], timeout: float = 10.0) -> bool:
        """Acquire multiple locks safely to avoid deadlocks (sorts by name)."""
        sorted_names = sorted(names)
        acquired = []
        try:
            for name in sorted_names:
                lock = self._locks.get(name)
                if not lock:
                    raise ValueError(f"Lock '{name}' not registered")
                if lock.acquire(timeout=timeout):
                    acquired.append(lock)
                    self._total_acquisitions += 1
                else:
                    return False
            return True
        except Exception as e:
            logger.error(f"Failed to acquire multiple locks: {e}")
            for lock in acquired:
                lock.release()
                self._total_releases += 1
            return False

    def release_all(self, names: list[str]):
        """Release multiple locks."""
        for name in names:
            if name in self._locks:
                self._locks[name].release()
                self._total_releases += 1

class ReadWriteLock:
    """In-process Read-Write lock (shared/exclusive)."""

    def __init__(self):
        """Initialize this instance."""
        self._read_ready = threading.Condition(threading.Lock())
        self._readers = 0
        self._writers = 0

    def acquire_read(self):
        """acquire Read ."""
        with self._read_ready:
            while self._writers > 0:
                self._read_ready.wait()
            self._readers += 1

    def release_read(self):
        """release Read ."""
        with self._read_ready:
            self._readers -= 1
            if self._readers == 0:
                self._read_ready.notify_all()

    def acquire_write(self):
        """acquire Write ."""
        with self._read_ready:
            while self._readers > 0 or self._writers > 0:
                self._read_ready.wait()
            self._writers += 1

    def release_write(self):
        """release Write ."""
        with self._read_ready:
            self._writers -= 1
            self._read_ready.notify_all()
