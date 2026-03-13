"""Unit tests for asynchronous edge computing mesh execution topologies."""

import asyncio

import pytest

from codomyrmex.edge_computing.orchestrator import AsyncEdgeOrchestrator


async def async_multiplier(x: int, y: int) -> int:
    """A synthetic async workload payload."""
    await asyncio.sleep(0.01)
    return x * y


def sync_adder(x: int, y: int) -> int:
    """A synthetic sync workload payload."""
    return x + y


@pytest.mark.asyncio
async def test_async_edge_orchestrator_dispatch():
    """Verify that the AsyncEdgeOrchestrator can dispatch and retrieve properly."""
    orchestrator = AsyncEdgeOrchestrator()

    # Register purely synthetic nodes
    orchestrator.register_peer("peer-001")
    orchestrator.register_peer("peer-002")

    # Dispatch workloads
    node_a, task_a = await orchestrator.dispatch(async_multiplier, 5, 20)
    node_b, task_b = await orchestrator.dispatch(sync_adder, 15, 15)

    # Tasks are distributed to least-loaded node
    # The first one increments active tasks by 1 on the best node, making the second go to the other node
    assert node_a != node_b

    # Retrieve explicitly through the targeted nodes
    res_a = await orchestrator.nodes[node_a].retrieve_result(task_a)
    assert res_a == 100

    res_b = await orchestrator.nodes[node_b].retrieve_result(task_b)
    assert res_b == 30


@pytest.mark.asyncio
async def test_async_edge_orchestrator_bulk_gather():
    """Verify that multiple concurrent payloads gather successfully via the mesh."""
    orchestrator = AsyncEdgeOrchestrator()
    for i in range(5):
        orchestrator.register_peer(f"mesh-{i}")

    # Build 100 small computational payloads
    payloads = []
    for i in range(100):
        # Odd indexes use async, even use sync
        if i % 2 == 0:
            payloads.append((sync_adder, (i, 1), {}))
        else:
            payloads.append((async_multiplier, (i, 2), {}))

    # Scatter and gather the entire batch natively
    results = await orchestrator.gather(payloads)

    assert len(results) == 100
    assert results[0] == 1  # 0 + 1 = 1
    assert results[1] == 2  # 1 * 2 = 2
    assert results[98] == 99  # 98 + 1 = 99
    assert results[99] == 198 # 99 * 2 = 198
