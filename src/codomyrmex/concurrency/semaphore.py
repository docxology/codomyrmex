"""Backward-compatible re-export shim.

This module has been moved to concurrency.semaphores.semaphore.
All public names are re-exported here to preserve the existing API.
"""

from .semaphores.semaphore import (  # noqa: F401
    AsyncLocalSemaphore,
    BaseSemaphore,
    LocalSemaphore,
)
