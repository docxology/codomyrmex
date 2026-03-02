"""Abstract base class and local implementation of distributed locks."""

import fcntl
import os
import time
from abc import ABC, abstractmethod

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)

class BaseLock(ABC):
    """Abstract base class for all lock implementations."""

    def __init__(self, name: str):
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
        """
        pass

    @abstractmethod
    def release(self) -> None:
        """Release the lock."""
        pass

    def __enter__(self):
        """enter ."""
        if not self.acquire():
            raise TimeoutError(f"Could not acquire lock: {self.name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """exit ."""
        self.release()

class LocalLock(BaseLock):
    """File-based lock for local multi-process synchronization."""

    def __init__(self, name: str, lock_dir: str = "/tmp/codomyrmex/locks"):
        super().__init__(name)
        self.lock_path = os.path.join(lock_dir, f"{name}.lock")
        os.makedirs(lock_dir, exist_ok=True)
        self._lock_file = None

    def acquire(self, timeout: float = 10.0, retry_interval: float = 0.1) -> bool:
        """acquire ."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                self._lock_file = open(self.lock_path, "w")
                fcntl.flock(self._lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
                self.is_held = True
                return True
            except OSError:
                if self._lock_file:
                    self._lock_file.close()
                    self._lock_file = None
                time.sleep(retry_interval)
        return False

    def release(self) -> None:
        """release ."""
        if self.is_held and self._lock_file:
            fcntl.flock(self._lock_file, fcntl.LOCK_UN)
            self._lock_file.close()
            self._lock_file = None
            self.is_held = False
            try:
                os.remove(self.lock_path)
            except OSError as e:
                logger.debug("Failed to remove lock file %s: %s", self.lock_path, e)
                pass
