"""Managed semaphores for resource throttling."""

import asyncio
import threading
import time
from abc import ABC, abstractmethod

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class BaseSemaphore(ABC):
    """Abstract base class for all semaphore implementations."""

    def __init__(self, value: int = 1):
        """Initialize base semaphore.

        Args:
            value: Initial number of available units.

        Raises:
            ValueError: If value is negative.

        Example:
            >>> sem = LocalSemaphore(value=5)
        """
        if value < 0:
            raise ValueError("Semaphore value must be >= 0")
        self.initial_value = value

    @abstractmethod
    def acquire(self, timeout: float = 10.0) -> bool:
        """Acquire a semaphore unit.

        Args:
            timeout: Maximum time to wait in seconds.

        Returns:
            True if acquired, False otherwise.

        Example:
            >>> sem.acquire(timeout=2.0)
            True
        """

    @abstractmethod
    def release(self) -> None:
        """Release a semaphore unit.

        Example:
            >>> sem.release()
        """

    def __enter__(self):
        """Enter the context manager.

        Returns:
            The semaphore instance.

        Raises:
            TimeoutError: If the semaphore could not be acquired.

        Example:
            >>> with LocalSemaphore(2) as sem:
            ...     pass
        """
        if not self.acquire():
            raise TimeoutError("Could not acquire semaphore")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager and clean up.

        Example:
            >>> sem.__exit__(None, None, None)
        """
        self.release()


class LocalSemaphore(BaseSemaphore):
    """Local thread-safe semaphore wrapper."""

    def __init__(self, value: int = 1):
        """Initialize a local thread-safe semaphore.

        Args:
            value: Initial number of available units.

        Example:
            >>> sem = LocalSemaphore(value=3)
        """
        super().__init__(value)
        self._semaphore = threading.Semaphore(value)

    def acquire(self, timeout: float = 10.0) -> bool:
        """Acquire a semaphore unit with timeout.

        Args:
            timeout: Maximum time to wait in seconds.

        Returns:
            True if acquired, False otherwise.

        Example:
            >>> sem.acquire(timeout=5.0)
            True
        """
        return self._semaphore.acquire(timeout=timeout)

    def release(self) -> None:
        """Release a semaphore unit.

        Example:
            >>> sem.release()
        """
        self._semaphore.release()


class AsyncLocalSemaphore(BaseSemaphore):
    """Asyncio-compatible local semaphore."""

    def __init__(self, value: int = 1):
        """Initialize a local asyncio-compatible semaphore.

        Args:
            value: Initial number of available units.

        Example:
            >>> sem = AsyncLocalSemaphore(value=10)
        """
        super().__init__(value)
        self._semaphore = asyncio.Semaphore(value)
        self._sync_lock = threading.Lock()
        self._sync_count = value

    async def acquire_async(self, timeout: float | None = None) -> bool:
        """Acquire a semaphore unit asynchronously.

        Args:
            timeout: Maximum time to wait in seconds.

        Returns:
            True if acquired, False otherwise.

        Example:
            >>> await sem.acquire_async(timeout=1.0)
            True
        """
        try:
            if timeout is not None:
                await asyncio.wait_for(self._semaphore.acquire(), timeout=timeout)
            else:
                await self._semaphore.acquire()

            with self._sync_lock:
                self._sync_count -= 1
            return True
        except TimeoutError:
            return False

    async def __aenter__(self):
        """Enter the async context manager.

        Returns:
            The semaphore instance.

        Raises:
            TimeoutError: If acquisition fails.

        Example:
            >>> async with AsyncLocalSemaphore(1) as sem:
            ...     pass
        """
        if not await self.acquire_async():
            raise TimeoutError("Could not acquire semaphore")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the async context manager and clean up.

        Example:
            >>> await sem.__aexit__(None, None, None)
        """
        self.release()

    def release(self) -> None:
        """Release a unit back to the semaphore.

        Example:
            >>> sem.release()
        """
        try:
            self._semaphore.release()
        except ValueError:
            # Too many releases for the internal semaphore
            pass

        with self._sync_lock:
            if self._sync_count < self.initial_value:
                self._sync_count += 1

    def acquire(self, timeout: float = 10.0) -> bool:
        """Acquire synchronously, bridging safely to an async context.

        If in an event loop, uses a fallback synchronous counter to avoid blocking.
        If no loop is running, creates a temporary one to execute the acquisition.

        Args:
            timeout: Maximum time to wait in seconds.

        Returns:
            True if acquired, False otherwise.

        Example:
            >>> sem.acquire(timeout=5.0)
            True
        """
        try:
            # Check if there's a running event loop
            asyncio.get_running_loop()
            # We're inside an async context - use the sync counter fallback to avoid blocking the loop
            logger.warning(
                "Synchronous acquire() called from async context. "
                "Using fallback sync counter - prefer acquire_async() instead."
            )
            start_time = time.time()
            while time.time() - start_time < timeout:
                with self._sync_lock:
                    if self._sync_count > 0:
                        self._sync_count -= 1
                        # Note: This does NOT acquire the underlying asyncio.Semaphore
                        # which is okay as long as this is only for sync-from-async bridging
                        return True
                time.sleep(0.01)
            return False

        except RuntimeError:
            # No running event loop - we can create one temporarily
            async def _acquire_with_timeout():
                try:
                    return await self.acquire_async(timeout=timeout)
                except Exception as e:
                    logger.warning("Semaphore acquisition failed: %s", e)
                    return False

            try:
                return asyncio.run(_acquire_with_timeout())
            except Exception as e:
                logger.error("Failed to acquire semaphore synchronously: %s", e)
                return False
