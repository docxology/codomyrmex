# DEPRECATED(v0.2.0): Shim module. Import from concurrency.semaphores.semaphore instead. Will be removed in v0.3.0.
"""Backward-compatible re-export shim.

This module has been moved to concurrency.semaphores.semaphore.
All public names are re-exported here to preserve the existing API.
"""

from .semaphores.semaphore import (  # noqa: F401
    AsyncLocalSemaphore,
    BaseSemaphore,
    LocalSemaphore,
)
