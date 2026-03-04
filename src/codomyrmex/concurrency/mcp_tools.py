"""MCP tools for the concurrency module."""

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="concurrency")
def concurrency_pool_status() -> dict:
    """Report the status of the async worker pool.

    Creates a fresh AsyncWorkerPool instance and returns its current
    capacity and configuration statistics.

    Returns:
        Dictionary with pool size, capacity, and availability.

    """
    try:
        from codomyrmex.concurrency import AsyncWorkerPool

        pool = AsyncWorkerPool()
        stats = pool.stats
        return {
            "status": "success",
            "pool_stats": {
                "submitted": stats.submitted,
                "completed": stats.completed,
                "failed": stats.failed,
                "total_elapsed_ms": stats.total_elapsed_ms,
            },
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(category="concurrency")
def concurrency_list_locks() -> dict:
    """List all currently tracked distributed locks.

    Queries the LockManager for any locks that have been registered
    or are currently held.

    Returns:
        Dictionary with a list of lock names and their count.

    """
    try:
        from codomyrmex.concurrency import LockManager

        manager = LockManager()
        locks = manager.list_locks()
        return {
            "status": "success",
            "locks": locks,
            "count": len(locks),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
