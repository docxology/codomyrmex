"""Locks subpackage for distributed and local lock primitives."""

import contextlib

from .distributed_lock import BaseLock, LocalLock
from .lock_manager import LockManager, LockStats, ReadWriteLock

with contextlib.suppress(ImportError):
    from .redis_lock import RedisLock

__all__ = [
    "BaseLock",
    "LocalLock",
    "LockManager",
    "LockStats",
    "ReadWriteLock",
    "RedisLock",
]
