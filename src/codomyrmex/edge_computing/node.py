"""Asynchronous Edge Node for peer-to-peer execution topologies.

Wraps the core EdgeNode model with async runtime evaluation capabilities.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

from .core.models import EdgeNode, EdgeNodeStatus

logger = logging.getLogger(__name__)


class AsyncEdgeNode:
    """An asynchronous peer node capable of executing functions locally."""

    def __init__(self, node_model: EdgeNode) -> None:
        self.model = node_model
        # Map of task ID to active asyncio.Task objects executing locally
        self._active_tasks: dict[str, asyncio.Task[Any]] = {}
        # Stores final results by task ID
        self._completed_results: dict[str, Any] = {}
        self._lock = asyncio.Lock()

    @property
    def is_available(self) -> bool:
        """True if the node is ONLINE and not overloaded."""
        if self.model.status != EdgeNodeStatus.ONLINE:
            return False
        # Prevent taking new payloads if active count exceeds threshold
        if len(self._active_tasks) >= self.model.max_functions:
            return False
        return not self.model.resources.is_overloaded

    async def accept_payload(
        self, handler: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> str:
        """Accept an executable payload asynchronously.

        Returns:
            A unique task_id for tracking this execution.
        """
        async with self._lock:
            if not self.is_available:
                raise RuntimeError(
                    f"EdgeNode {self.model.id} is unavailable or overloaded."
                )

            task_id = str(uuid.uuid4())
            # Start background execution
            task = asyncio.create_task(
                self._execute_payload(task_id, handler, *args, **kwargs)
            )
            self._active_tasks[task_id] = task

            # Update mock internal resources for the local run
            self.model.resources.active_functions += 1
            return task_id

    async def _execute_payload(
        self, task_id: str, handler: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> None:
        """Internal execution lifecycle tracking."""
        try:
            # If the handler is a coroutine, await it, else execute it in executor
            # (simplistic execution strategy for zero-mock testing)
            if asyncio.iscoroutinefunction(handler):
                result = await handler(*args, **kwargs)
            else:
                result = handler(*args, **kwargs)

            async with self._lock:
                self._completed_results[task_id] = result
        except Exception as exc:
            logger.error(f"Node {self.model.id} failed task {task_id}: {exc}")
            async with self._lock:
                self._completed_results[task_id] = exc
        finally:
            async with self._lock:
                if task_id in self._active_tasks:
                    del self._active_tasks[task_id]
                self.model.resources.active_functions = max(
                    0, self.model.resources.active_functions - 1
                )

    async def retrieve_result(self, task_id: str) -> Any:
        """Pull the result for a given task ID if it has completed."""
        async with self._lock:
            # Check if done
            if task_id in self._completed_results:
                res = self._completed_results[task_id]
                if isinstance(res, Exception):
                    raise res
                return res

        # If it's still running, await it natively
        task = self._active_tasks.get(task_id)
        if task:
            await task
            async with self._lock:
                res = self._completed_results.get(task_id)
                if isinstance(res, Exception):
                    raise res
                return res

        raise KeyError(f"Task ID {task_id} not found on node {self.model.id}")
