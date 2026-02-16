"""Backward-compatible re-export shim.

This module has been moved to concurrency.locks.lock_manager.
All public names are re-exported here to preserve the existing API.
"""

from .locks.lock_manager import LockManager, LockStats, ReadWriteLock  # noqa: F401
