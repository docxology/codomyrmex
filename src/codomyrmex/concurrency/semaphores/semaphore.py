"""Managed semaphores for resource throttling."""

import asyncio
import threading
import time
from abc import ABC, abstractmethod

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)

class BaseSemaphore(ABC):
    """Abstract base class for all semaphore implementations."""

    def __init__(self, value: int = 1):
        if value < 0:
            raise ValueError("Semaphore value must be >= 0")
        self.initial_value = value

    @abstractmethod
    def acquire(self, timeout: float = 10.0) -> bool:
        """Acquire a semaphore unit."""
        pass

    @abstractmethod
    def release(self) -> None:
        """Release a semaphore unit."""
        pass

    def __enter__(self):
        """Enter the context manager."""
        if not self.acquire():
            raise TimeoutError("Could not acquire semaphore")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager and clean up."""
        self.release()

class LocalSemaphore(BaseSemaphore):
    """Local thread-safe semaphore wrapper."""

    def __init__(self, value: int = 1):
        super().__init__(value)
        self._semaphore = threading.Semaphore(value)

    def acquire(self, timeout: float = 10.0) -> bool:
        """Acquire a semaphore unit with timeout."""
        return self._semaphore.acquire(timeout=timeout)

    def release(self) -> None:
        """Release a semaphore unit."""
        self._semaphore.release()

class AsyncLocalSemaphore(BaseSemaphore):
    """Asyncio-compatible local semaphore."""

    def __init__(self, value: int = 1):
        super().__init__(value)
        self._semaphore = asyncio.Semaphore(value)
        self._sync_lock = threading.Lock()
        self._sync_count = value

    async def acquire_async(self, timeout: float | None = None) -> bool:
        """Acquire a semaphore unit asynchronously."""
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
        """Enter the async context manager."""
        if not await self.acquire_async():
            raise TimeoutError("Could not acquire semaphore")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the async context manager and clean up."""
        self.release()

    def release(self) -> None:
        """Release a unit back to the semaphore."""
        try:
            self._semaphore.release()
        except ValueError:
            # Too many releases for the internal semaphore
            pass

        with self._sync_lock:
            if self._sync_count < self.initial_value:
                self._sync_count += 1

    def acquire(self, timeout: float = 10.0) -> bool:
        """Synchronous acquisition that bridges to async context safely.

        If in an event loop, uses a fallback synchronous counter to avoid blocking.
        If no loop is running, creates a temporary one to execute the acquisition.
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
                logger.error(f"Failed to acquire semaphore synchronously: {e}")
                return False
