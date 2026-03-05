"""Concurrency and synchronization module for Codomyrmex.

This module provides distributed locks, semaphores, and other synchronization primitives.
"""

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None

from .locks.distributed_lock import (
    BaseLock,
    LocalLock,
)
from .locks.lock_manager import (
    LockManager,
    ReadWriteLock,
)

try:
    from .locks.redis_lock import (
        RedisLock,
    )
except ImportError:
    RedisLock = None
from .dead_letter import DeadLetterQueue
from .semaphores.semaphore import (
    AsyncLocalSemaphore,
    BaseSemaphore,
    LocalSemaphore,
)
from .workers.pool import AsyncWorkerPool, PoolStats, TaskResult


def cli_commands():
    """Return CLI commands for the concurrency module."""

    def _pools(**kwargs):
        """List thread/process pools."""
        mgr = LockManager()
        print("=== Concurrency Pools ===")
        print(
            "  Lock types available: LocalLock, ReadWriteLock"
            + (", RedisLock" if RedisLock is not None else "")
        )
        print("  Semaphore types: LocalSemaphore, AsyncLocalSemaphore")
        active = mgr.list_locks() if hasattr(mgr, "list_locks") else []
        print(f"  Active locks: {len(active)}")

    def _stats(**kwargs):
        """Show concurrency statistics."""
        mgr = LockManager()
        print("=== Concurrency Stats ===")
        stats = mgr.stats
        if stats.total_locks > 0 or stats.total_acquisitions > 0:
            print(f"  Total Locks: {stats.total_locks}")
            print(f"  Total Acquisitions: {stats.total_acquisitions}")
            print(f"  Total Releases: {stats.total_releases}")
            print(f"  Active Locks: {stats.active_locks}")
        else:
            print("  No active concurrency operations")

    return {
        "pools": {"handler": _pools, "help": "List thread/process pools"},
        "stats": {"handler": _stats, "help": "Show concurrency statistics"},
    }


__all__ = [
    "AsyncLocalSemaphore",
    "AsyncWorkerPool",
    "BaseLock",
    "BaseSemaphore",
    "DeadLetterQueue",
    "LocalLock",
    "LocalSemaphore",
    "LockManager",
    "PoolStats",
    "ReadWriteLock",
    "RedisLock",
    "TaskResult",
    "cli_commands",
]

from . import tasks, workers  # noqa: E402
