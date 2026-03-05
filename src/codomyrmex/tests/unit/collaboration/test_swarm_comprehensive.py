"""Comprehensive zero-mock tests for the collaboration swarm module."""

import asyncio

import pytest

from codomyrmex.collaboration.swarm import (
    AgentPool,
    AgentRole,
    Decision,
    MessageBus,
    SwarmAgent,
    SwarmManager,
    SwarmMessage,
    SwarmMessageType,
    TaskAssignment,
    TaskDecomposer,
    Vote,
)


@pytest.mark.asyncio
async def test_swarm_manager_mission_execution():
    """Test full mission execution flow with real objects and simulated responses."""
    manager = SwarmManager()

    # Register agents
    manager.register_agent(SwarmAgent("arch", AgentRole.ARCHITECT))
    manager.register_agent(SwarmAgent("coder", AgentRole.CODER))

    # Helper to simulate agent response
    async def simulate_agent(message: SwarmMessage):
        if message.message_type == SwarmMessageType.TASK_ASSIGNMENT:
            await manager.bus.publish(
                f"results.agent.{message.recipient}",
                SwarmMessage(
                    SwarmMessageType.RESULT,
                    message.recipient,
                    payload={
                        "task_id": message.payload["task_id"],
                        "result": {"status": "success"},
                    },
                ),
            )

    manager.bus.subscribe("sim", "tasks.role.#", simulate_agent)

    mission = "Design and implement feature X"
    results = await manager.execute_mission(mission)

    assert len(results) >= 2
    for r in results:
        assert r["result"]["status"] == "success"


@pytest.mark.asyncio
async def test_agent_pool_assignment():
    """Test agent pool routing and load balancing."""
    pool = AgentPool()
    a1 = SwarmAgent("a1", AgentRole.CODER)
    a2 = SwarmAgent("a2", AgentRole.CODER)
    pool.register(a1)
    pool.register(a2)

    task = TaskAssignment(description="task1", required_role=AgentRole.CODER)

    # First assignment
    agent = pool.assign(task)
    assert agent.agent_id in ["a1", "a2"]
    assert agent.active_tasks == 1

    # Second assignment should pick the other one (least loaded)
    task2 = TaskAssignment(description="task2", required_role=AgentRole.CODER)
    agent2 = pool.assign(task2)
    assert agent2.agent_id != agent.agent_id
    assert agent2.active_tasks == 1


@pytest.mark.asyncio
async def test_message_bus_routing():
    """Test message bus pub/sub with wildcards."""
    bus = MessageBus()
    received = []

    bus.subscribe("sub1", "tasks.role.*", lambda m: received.append(m))
    bus.subscribe("sub2", "broadcast.#", lambda m: received.append(m))

    msg1 = SwarmMessage(SwarmMessageType.TASK_ASSIGNMENT, "sender", payload={"id": 1})
    await bus.publish("tasks.role.coder", msg1)

    msg2 = SwarmMessage(
        SwarmMessageType.STATUS_UPDATE, "sender", payload={"status": "ok"}
    )
    await bus.publish("broadcast.system.status", msg2)

    # Wait for tasks if any
    await asyncio.sleep(0.1)

    assert len(received) == 2
    assert received[0].payload["id"] == 1
    assert received[1].payload["status"] == "ok"


@pytest.mark.asyncio
async def test_consensus_engine_strategies():
    """Test different consensus resolution strategies."""
    manager = SwarmManager()

    votes = [Vote("a1", True), Vote("a2", True), Vote("a3", False)]

    # Majority
    res_maj = await manager.request_consensus("test", votes, strategy="majority")
    assert res_maj.decision == Decision.APPROVED

    # Veto
    res_veto = await manager.request_consensus("test", votes, strategy="veto")
    assert res_veto.decision == Decision.VETOED

    # Weighted
    votes_weighted = [Vote("a1", False, weight=2.0), Vote("a2", True, weight=1.0)]
    res_weight = await manager.request_consensus(
        "test", votes_weighted, strategy="weighted"
    )
    assert res_weight.decision == Decision.REJECTED


def test_task_decomposer_logic():
    """Test DAG-based task decomposition."""
    decomposer = TaskDecomposer()
    mission = "Add user auth and tests"

    subtasks = decomposer.decompose(mission)
    assert len(subtasks) >= 2

    order = decomposer.execution_order(subtasks)
    assert len(order) == len(subtasks)

    # Check dependency: tests should depend on implementation if both present
    auth_task = next(t for t in subtasks if t.role == AgentRole.CODER)
    test_task = next(t for t in subtasks if t.role == AgentRole.TESTER)

    assert auth_task.task_id in test_task.depends_on or any(
        dep == auth_task.task_id for dep in test_task.depends_on
    )
