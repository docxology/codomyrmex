"""Managed semaphores for resource throttling."""

from abc import ABC, abstractmethod
import asyncio
import threading
import logging
from typing import Optional

logger = logging.getLogger(__name__)

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
        return self._semaphore.acquire(timeout=timeout)

    def release(self) -> None:
        self._semaphore.release()

class AsyncLocalSemaphore(BaseSemaphore):
    """Asyncio-compatible local semaphore."""
    
    def __init__(self, value: int = 1):
        super().__init__(value)
        self._semaphore = asyncio.Semaphore(value)

    async def acquire_async(self) -> None:
        await self._semaphore.acquire()

    def release(self) -> None:
        self._semaphore.release()
        
    def acquire(self, timeout: float = 10.0) -> bool:
        """Synchronous acquisition of an async semaphore (not recommended)."""
        raise NotImplementedError("Use acquire_async() for AsyncLocalSemaphore")
