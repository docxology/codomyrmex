# DEPRECATED(v0.2.0): Shim module. Import from concurrency.locks.redis_lock instead. Will be removed in v0.3.0.
"""Backward-compatible re-export shim.

This module has been moved to concurrency.locks.redis_lock.
All public names are re-exported here to preserve the existing API.
"""

from .locks.redis_lock import RedisLock  # noqa: F401
