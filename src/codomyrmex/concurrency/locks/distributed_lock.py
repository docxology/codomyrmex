"""Abstract base class and local implementation of distributed locks."""

import fcntl
import os
import threading
import time
from abc import ABC, abstractmethod

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class BaseLock(ABC):
    """Abstract base class for all lock implementations."""

    def __init__(self, name: str):
        """Initialize the base lock.

        Args:
            name: Unique identifier for the lock.

        Example:
            >>> lock = LocalLock("resource-1")
        """
        self.name = name
        self.is_held = False

    @abstractmethod
    def acquire(self, timeout: float = 10.0, retry_interval: float = 0.1) -> bool:
        """Acquire the lock.

        Args:
            timeout: Maximum time to wait for the lock in seconds.
            retry_interval: Time between acquisition attempts.

        Returns:
            True if acquired, False otherwise.

        Raises:
            RuntimeError: If there is an internal failure during acquisition.

        Example:
            >>> lock.acquire(timeout=5.0)
            True
        """

    @abstractmethod
    def release(self) -> None:
        """Release the lock.

        Raises:
            RuntimeError: If the lock cannot be released safely.

        Example:
            >>> lock.release()
        """

    def __enter__(self):
        """Enter the context manager.

        Returns:
            The lock instance.

        Raises:
            TimeoutError: If the lock could not be acquired within the default timeout.

        Example:
            >>> with LocalLock("resource-1") as lock:
            ...     pass
        """
        if not self.acquire():
            raise TimeoutError(f"Could not acquire lock: {self.name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager and clean up.

        Args:
            exc_type: Exception type if an exception occurred.
            exc_val: Exception value.
            exc_tb: Exception traceback.

        Example:
            >>> lock.__exit__(None, None, None)
        """
        self.release()


class LocalLock(BaseLock):
    """File-based lock for local multi-process synchronization.

    Now includes thread-safety via a re-entrant threading lock.
    """

    def __init__(self, name: str, lock_dir: str = "/tmp/codomyrmex/locks"):
        """Initialize a local file-based lock.

        Args:
            name: Unique identifier for the lock.
            lock_dir: Directory where lock files will be stored.

        Example:
            >>> lock = LocalLock("my-resource", lock_dir="/tmp/locks")
        """
        super().__init__(name)
        self.lock_path = os.path.join(lock_dir, f"{name}.lock")
        self._lock_dir = lock_dir
        os.makedirs(lock_dir, exist_ok=True)
        self._lock_file: int | None = None
        self._thread_lock = threading.RLock()
        self._nesting_level = 0

    def acquire(self, timeout: float = 10.0, retry_interval: float = 0.1) -> bool:
        """Acquire the lock with retry logic and thread safety.

        Args:
            timeout: Maximum time to wait for the lock in seconds.
            retry_interval: Time between acquisition attempts.

        Returns:
            True if acquired, False otherwise.

        Example:
            >>> lock = LocalLock("test")
            >>> lock.acquire(timeout=1.0)
            True
        """
        start_time = time.time()

        # First acquire the thread-level lock
        if not self._thread_lock.acquire(timeout=timeout):
            return False

        if self.is_held:
            self._nesting_level += 1
            return True

        while True:
            try:
                # Open the file and try to get an exclusive lock
                fd = os.open(self.lock_path, os.O_CREAT | os.O_WRONLY)
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    self._lock_file = fd
                    self.is_held = True
                    self._nesting_level = 1
                    return True
                except OSError:
                    os.close(fd)
            except Exception as e:
                logger.debug("Error opening lock file %s: %s", self.lock_path, e)

            if time.time() - start_time >= timeout:
                self._thread_lock.release()
                return False

            time.sleep(retry_interval)

    def release(self) -> None:
        """Release the lock and clean up.

        Example:
            >>> lock.release()
        """
        with self._thread_lock:
            if not self.is_held:
                return

            self._nesting_level -= 1
            if self._nesting_level > 0:
                return

            if self._lock_file is not None:
                try:
                    fcntl.flock(self._lock_file, fcntl.LOCK_UN)
                    os.close(self._lock_file)
                except Exception as e:
                    logger.debug("Error releasing lock file %s: %s", self.lock_path, e)
                finally:
                    self._lock_file = None
                    self.is_held = False

            try:
                if os.path.exists(self.lock_path):
                    os.remove(self.lock_path)
            except OSError as e:
                logger.debug("Failed to remove lock file %s: %s", self.lock_path, e)

        # Release the thread lock after releasing the file lock
        self._thread_lock.release()
