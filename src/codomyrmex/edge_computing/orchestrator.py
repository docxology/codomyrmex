"""Asynchronous Edge Orchestrator.

Manages distributed async deployments across a graph of AsyncEdgeNodes.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

from .core.models import EdgeNode, EdgeNodeStatus
from .node import AsyncEdgeNode


class AsyncEdgeOrchestrator:
    """Dispatches workloads across peer nodes asynchronously."""

    def __init__(self) -> None:
        self.nodes: dict[str, AsyncEdgeNode] = {}
        self._lock = asyncio.Lock()

    def register_peer(
        self, node_id: str, capabilities: list[str] | None = None
    ) -> AsyncEdgeNode:
        """Register a new peer into the mesh."""
        model = EdgeNode(
            id=node_id,
            name=f"peer-{node_id}",
            status=EdgeNodeStatus.ONLINE,
            capabilities=capabilities or [],
            max_functions=100,
        )
        async_node = AsyncEdgeNode(model)
        self.nodes[node_id] = async_node
        return async_node

    async def _find_best_node(self) -> AsyncEdgeNode:
        """Find the least loaded accessible node."""
        async with self._lock:
            available_nodes = [n for n in self.nodes.values() if n.is_available]
            if not available_nodes:
                raise RuntimeError(
                    "No edge nodes are currently available for workload."
                )

            # Least active functions
            best_node = min(
                available_nodes, key=lambda n: n.model.resources.active_functions
            )
            return best_node

    async def dispatch(
        self, handler: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> tuple[str, str]:
        """Dispatch a single payload, returning the targeting node_id and task_id."""
        target_node = await self._find_best_node()
        task_id = await target_node.accept_payload(handler, *args, **kwargs)
        return target_node.model.id, task_id

    async def gather(
        self, payloads: list[tuple[Callable[..., Any], tuple[Any, ...], dict[str, Any]]]
    ) -> list[Any]:
        """Dispatch a bulk list of payloads concurrently and wait for all results."""
        tasks = []
        # Dispatch phase
        for handler, args, kwargs in payloads:
            target_node = await self._find_best_node()
            task_id = await target_node.accept_payload(handler, *args, **kwargs)
            tasks.append((target_node, task_id))

        # Gathering phase
        results = []
        for target_node, task_id in tasks:
            res = await target_node.retrieve_result(task_id)
            results.append(res)

        return results
