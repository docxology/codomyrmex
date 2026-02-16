"""Backward-compatible re-export shim.

This module has been moved to concurrency.locks.distributed_lock.
All public names are re-exported here to preserve the existing API.
"""

from .locks.distributed_lock import BaseLock, LocalLock  # noqa: F401
