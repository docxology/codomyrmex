"""Unified lock management and advanced synchronization primitives."""

import threading
import time
from dataclasses import dataclass, field

from codomyrmex.logging_monitoring import get_logger

from .distributed_lock import BaseLock

logger = get_logger(__name__)


@dataclass
class LockStats:
    """Statistics for lock manager telemetry.

    Attributes:
        total_locks: Total number of registered locks.
        total_acquisitions: Total number of successful acquisitions.
        total_releases: Total number of releases.
        active_locks: Number of locks currently held.
        lock_contention: Dictionary mapping lock names to failed acquisition counts.
    """

    total_locks: int = 0
    total_acquisitions: int = 0
    total_releases: int = 0
    active_locks: int = 0
    lock_contention: dict[str, int] = field(default_factory=dict)


class LockManager:
    """Orchestrates multiple locks and provides multi-resource acquisition."""

    def __init__(self):
        """Initialize the lock manager.

        Example:
            >>> manager = LockManager()
        """
        self._locks: dict[str, BaseLock] = {}
        self._total_acquisitions = 0
        self._total_releases = 0
        self._contention: dict[str, int] = {}
        self._manager_lock = threading.Lock()

    def register_lock(self, name: str, lock: BaseLock):
        """Register a lock with the manager.

        Args:
            name: Human-readable name for the lock.
            lock: The lock implementation to register.

        Example:
            >>> manager.register_lock("db", LocalLock("database"))
        """
        with self._manager_lock:
            self._locks[name] = lock

    def get_lock(self, name: str) -> BaseLock | None:
        """Retrieve a registered lock by name.

        Args:
            name: The name of the lock to retrieve.

        Returns:
            The lock instance if found, None otherwise.

        Example:
            >>> lock = manager.get_lock("db")
        """
        with self._manager_lock:
            return self._locks.get(name)

    @property
    def stats(self) -> LockStats:
        """Get lock manager statistics for telemetry.

        Returns:
            LockStats object with current metrics.

        Example:
            >>> stats = manager.stats
            >>> print(stats.total_locks)
        """
        with self._manager_lock:
            active = sum(
                1 for lock in self._locks.values() if getattr(lock, "is_held", False)
            )
            return LockStats(
                total_locks=len(self._locks),
                total_acquisitions=self._total_acquisitions,
                total_releases=self._total_releases,
                active_locks=active,
                lock_contention=self._contention.copy(),
            )

    def list_locks(self) -> list[str]:
        """list all registered lock names.

        Returns:
            list of registered lock names.

        Example:
            >>> manager.list_locks()
            ['db', 'file']
        """
        with self._manager_lock:
            return list(self._locks.keys())

    def acquire_all(self, names: list[str], timeout: float = 10.0) -> bool:
        """Acquire multiple locks safely to avoid deadlocks (sorts by name).

        Args:
            names: list of lock names to acquire.
            timeout: Maximum time to wait for all locks.

        Returns:
            True if all locks acquired, False if any failed (rolls back).

        Raises:
            ValueError: If a requested lock name is not registered.

        Example:
            >>> if manager.acquire_all(["db", "file"], timeout=5.0):
            ...     try:
            ...         pass
            ...     finally:
            ...         manager.release_all(["db", "file"])
        """
        sorted_names = sorted(names)
        acquired: list[BaseLock] = []
        start_time = time.time()

        try:
            for name in sorted_names:
                with self._manager_lock:
                    lock = self._locks.get(name)
                    if not lock:
                        raise ValueError(f"Lock '{name}' not registered")

                remaining_timeout = max(0.1, timeout - (time.time() - start_time))
                if lock.acquire(timeout=remaining_timeout):
                    acquired.append(lock)
                    with self._manager_lock:
                        self._total_acquisitions += 1
                else:
                    with self._manager_lock:
                        self._contention[name] = self._contention.get(name, 0) + 1
                    # Roll back on failure to acquire any lock in the set
                    for lock in reversed(acquired):
                        lock.release()
                        with self._manager_lock:
                            self._total_releases += 1
                    return False
            return True
        except Exception as e:
            logger.error("Failed to acquire multiple locks: %s", e)
            for lock in reversed(acquired):
                lock.release()
                with self._manager_lock:
                    self._total_releases += 1
            return False

    def release_all(self, names: list[str]):
        """Release multiple locks.

        Args:
            names: list of lock names to release.

        Example:
            >>> manager.release_all(["db", "file"])
        """
        for name in names:
            with self._manager_lock:
                lock = self._locks.get(name)
            if lock:
                lock.release()
                with self._manager_lock:
                    self._total_releases += 1


class ReadWriteLock:
    """In-process Read-Write lock (shared/exclusive).

    This implementation prioritizes writers to avoid starvation.
    """

    def __init__(self):
        """Initialize a read-write lock.

        Example:
            >>> rw = ReadWriteLock()
        """
        self._lock = threading.Lock()
        self._read_ready = threading.Condition(self._lock)
        self._readers = 0
        self._writers_waiting = 0
        self._writer_active = False

    def acquire_read(self, timeout: float | None = None) -> bool:
        """Acquire a read lock.

        Args:
            timeout: Maximum time to wait in seconds.

        Returns:
            True if acquired, False otherwise.

        Example:
            >>> rw.acquire_read(timeout=1.0)
            True
        """
        start_time = time.time()
        with self._lock:
            while self._writer_active or self._writers_waiting > 0:
                remaining = None
                if timeout is not None:
                    remaining = timeout - (time.time() - start_time)
                    if remaining <= 0:
                        return False
                if not self._read_ready.wait(timeout=remaining):
                    return False
            self._readers += 1
            return True

    def release_read(self):
        """Release a read lock.

        Example:
            >>> rw.release_read()
        """
        with self._lock:
            self._readers -= 1
            if self._readers == 0:
                self._read_ready.notify_all()

    def acquire_write(self, timeout: float | None = None) -> bool:
        """Acquire a write lock.

        Args:
            timeout: Maximum time to wait in seconds.

        Returns:
            True if acquired, False otherwise.

        Example:
            >>> rw.acquire_write(timeout=1.0)
            True
        """
        start_time = time.time()
        with self._lock:
            self._writers_waiting += 1
            try:
                while self._readers > 0 or self._writer_active:
                    remaining = None
                    if timeout is not None:
                        remaining = timeout - (time.time() - start_time)
                        if remaining <= 0:
                            return False
                    if not self._read_ready.wait(timeout=remaining):
                        return False
                self._writer_active = True
                return True
            finally:
                self._writers_waiting -= 1

    def release_write(self):
        """Release a write lock.

        Example:
            >>> rw.release_write()
        """
        with self._lock:
            self._writer_active = False
            self._read_ready.notify_all()

    def read_lock(self):
        """Return a context manager for the read lock.

        Returns:
            _ReadLockContext for use with 'with'.

        Example:
            >>> with rw.read_lock():
            ...     pass
        """
        return _ReadLockContext(self)

    def write_lock(self):
        """Return a context manager for the write lock.

        Returns:
            _WriteLockContext for use with 'with'.

        Example:
            >>> with rw.write_lock():
            ...     pass
        """
        return _WriteLockContext(self)


class _ReadLockContext:
    """Internal context manager for read locks."""

    def __init__(self, rw_lock: ReadWriteLock):
        """Initialize context.

        Args:
            rw_lock: The ReadWriteLock to use.
        """
        self._rw_lock = rw_lock

    def __enter__(self):
        """Enter context.

        Raises:
            TimeoutError: If lock acquisition fails.
        """
        if not self._rw_lock.acquire_read():
            raise TimeoutError("Failed to acquire read lock")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context and release lock."""
        self._rw_lock.release_read()


class _WriteLockContext:
    """Internal context manager for write locks."""

    def __init__(self, rw_lock: ReadWriteLock):
        """Initialize context.

        Args:
            rw_lock: The ReadWriteLock to use.
        """
        self._rw_lock = rw_lock

    def __enter__(self):
        """Enter context.

        Raises:
            TimeoutError: If lock acquisition fails.
        """
        if not self._rw_lock.acquire_write():
            raise TimeoutError("Failed to acquire write lock")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context and release lock."""
        self._rw_lock.release_write()
