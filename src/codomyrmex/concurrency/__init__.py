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
        print("  Lock types available: LocalLock, ReadWriteLock" +
              (", RedisLock" if RedisLock is not None else ""))
        print("  Semaphore types: LocalSemaphore")
        active = mgr.list_locks() if hasattr(mgr, "list_locks") else []
        print(f"  Active locks: {len(active)}")

    def _stats(**kwargs):
        """Show concurrency statistics."""
        mgr = LockManager()
        print("=== Concurrency Stats ===")
        stats = mgr.get_stats() if hasattr(mgr, "get_stats") else {}
        if stats:
            for key, value in stats.items():
                print(f"  {key}: {value}")
        else:
            print("  No active concurrency operations")

    return {
        "pools": {"handler": _pools, "help": "List thread/process pools"},
        "stats": {"handler": _stats, "help": "Show concurrency statistics"},
    }


__all__ = [
    "BaseLock",
    "LocalLock",
    "BaseSemaphore",
    "LocalSemaphore",
    "RedisLock",
    "LockManager",
    "ReadWriteLock",
    "AsyncWorkerPool",
    "PoolStats",
    "TaskResult",
    "DeadLetterQueue",
    "cli_commands",
]

from . import tasks, workers  # noqa: E402, F401
