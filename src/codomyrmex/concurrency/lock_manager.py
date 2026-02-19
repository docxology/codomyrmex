# DEPRECATED(v0.2.0): Shim module. Import from concurrency.locks.lock_manager instead. Will be removed in v0.3.0.
"""Backward-compatible re-export shim.

This module has been moved to concurrency.locks.lock_manager.
All public names are re-exported here to preserve the existing API.
"""

from .locks.lock_manager import LockManager, LockStats, ReadWriteLock  # noqa: F401
