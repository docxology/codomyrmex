"""Backward-compatible re-export shim.

This module has been moved to concurrency.locks.redis_lock.
All public names are re-exported here to preserve the existing API.
"""

from .locks.redis_lock import RedisLock  # noqa: F401
