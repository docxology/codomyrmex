"""Managed semaphores for resource throttling."""

import asyncio
import threading
from abc import ABC, abstractmethod

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)

class BaseSemaphore(ABC):
    """Abstract base class for all semaphore implementations."""

    def __init__(self, value: int = 1):
        self.initial_value = value

    @abstractmethod
    def acquire(self, timeout: float = 10.0) -> bool:
        """Acquire a semaphore unit."""
        pass

    @abstractmethod
    def release(self) -> None:
        """Release a semaphore unit."""
        pass

class LocalSemaphore(BaseSemaphore):
    """Local thread-safe semaphore wrapper."""

    def __init__(self, value: int = 1):
        super().__init__(value)
        self._semaphore = threading.Semaphore(value)

    def acquire(self, timeout: float = 10.0) -> bool:
        """acquire ."""
        return self._semaphore.acquire(timeout=timeout)

    def release(self) -> None:
        """release ."""
        self._semaphore.release()

class AsyncLocalSemaphore(BaseSemaphore):
    """Asyncio-compatible local semaphore."""

    def __init__(self, value: int = 1):
        super().__init__(value)
        self._semaphore = asyncio.Semaphore(value)
        self._sync_lock = threading.Lock()
        self._sync_count = value

    async def acquire_async(self) -> None:
        await self._semaphore.acquire()

    def release(self) -> None:
        """release ."""
        self._semaphore.release()
        # Also update sync count if it was acquired synchronously
        with self._sync_lock:
            if self._sync_count < self.initial_value:
                self._sync_count += 1

    def acquire(self, timeout: float = 10.0) -> bool:
        """Synchronous acquisition that bridges to async context safely.

        This method attempts to acquire the semaphore synchronously by:
        1. Checking if we're in an event loop - if so, use the sync fallback counter
        2. If no loop is running, create one temporarily to run the acquire

        Args:
            timeout: Maximum time to wait for acquisition in seconds

        Returns:
            True if acquired, False if timeout occurred
        """
        try:
            # Check if there's a running event loop
            loop = asyncio.get_running_loop()
            # We're inside an async context - use the sync counter fallback
            logger.warning(
                "Synchronous acquire() called from async context. "
                "Using fallback sync counter - prefer acquire_async() instead."
            )
            with self._sync_lock:
                if self._sync_count > 0:
                    self._sync_count -= 1
                    return True
                return False
        except RuntimeError:
            # No running event loop - we can create one temporarily
            async def _acquire_with_timeout():
                try:
                    await asyncio.wait_for(
                        self._semaphore.acquire(),
                        timeout=timeout
                    )
                    return True
                except TimeoutError as e:
                    logger.warning("Semaphore acquisition timed out after %.1fs: %s", timeout, e)
                    return False

            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(_acquire_with_timeout())
                finally:
                    loop.close()
                    asyncio.set_event_loop(None)
            except Exception as e:
                logger.error(f"Failed to acquire semaphore synchronously: {e}")
                return False
