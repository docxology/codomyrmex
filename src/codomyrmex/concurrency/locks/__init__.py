"""Locks subpackage for distributed and local lock primitives."""

from .distributed_lock import BaseLock, LocalLock
from .lock_manager import LockManager, LockStats, ReadWriteLock

try:
    from .redis_lock import RedisLock
except ImportError:
    RedisLock = None

__all__ = [
    "BaseLock",
    "LocalLock",
    "LockManager",
    "LockStats",
    "ReadWriteLock",
    "RedisLock",
]
