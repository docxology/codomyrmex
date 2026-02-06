"""Concurrency and synchronization module for Codomyrmex.

This module provides distributed locks, semaphores, and other synchronization primitives.
"""

from .distributed_lock import (
    BaseLock,
    LocalLock,
)
from .lock_manager import (
    LockManager,
    ReadWriteLock,
)
try:
    from .redis_lock import (
        RedisLock,
    )
except ImportError:
    RedisLock = None
from .semaphore import (
    BaseSemaphore,
    LocalSemaphore,
)

__all__ = [
    "BaseLock",
    "LocalLock",
    "BaseSemaphore",
    "LocalSemaphore",
    "RedisLock",
    "LockManager",
    "ReadWriteLock",
]
