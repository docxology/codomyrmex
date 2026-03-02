"""MCP tool definitions for the collaboration module.

Exposes swarm management and agent coordination as MCP tools
discoverable by Claude Code and other MCP-compatible agents.
"""

from __future__ import annotations

from typing import Any

try:
    from codomyrmex.model_context_protocol.decorators import mcp_tool
except ImportError:
    def mcp_tool(**kwargs: Any):  # type: ignore[misc]
        def decorator(func: Any) -> Any:
            func._mcp_tool_meta = kwargs
            return func
        return decorator


def _get_swarm_manager():
    """Lazy import SwarmManager to avoid circular imports."""
    from codomyrmex.collaboration.protocols.swarm import SwarmManager
    return SwarmManager()


def _get_task_decomposer():
    """Lazy import TaskDecomposer to avoid circular imports."""
    from codomyrmex.collaboration.protocols.swarm import TaskDecomposer
    return TaskDecomposer


@mcp_tool(
    category="collaboration",
    description="Submit a task to the agent swarm for distributed execution.",
)
def swarm_submit_task(
    mission: str,
    agents: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Submit a mission to the swarm and return results from each agent.

    Args:
        mission: Description of the task to execute.
        agents: Optional list of agent dicts with 'name' and 'role' keys.
                If not provided, uses a default single-agent swarm.

    Returns:
        Dictionary with agent names as keys and their results as values.
    """
    from codomyrmex.collaboration.protocols.swarm import AgentProxy

    swarm = _get_swarm_manager()

    if agents:
        for agent_spec in agents:
            proxy = AgentProxy(
                name=agent_spec.get("name", "agent"),
                role=agent_spec.get("role", "worker"),
            )
            swarm.add_agent(proxy)
    else:
        swarm.add_agent(AgentProxy(name="default_agent", role="worker"))

    results = swarm.execute(mission)

    # Also decompose the mission for reporting
    decomposer = _get_task_decomposer()
    subtasks = decomposer.decompose(mission)

    return {
        "mission": mission,
        "results": results,
        "subtasks": subtasks,
        "agent_count": len(swarm.agents),
    }


@mcp_tool(
    category="collaboration",
    description="Get the current status of the collaboration swarm pool.",
)
def pool_status() -> dict[str, Any]:
    """Return status information about the collaboration pool.

    Returns:
        Dictionary with pool capacity, protocol information, and available agents.
    """
    from codomyrmex.collaboration import (
        TaskPriority,
        TaskStatus,
    )

    return {
        "pool": {
            "status": "ready",
            "protocols": [
                "RoundRobinProtocol",
                "BroadcastProtocol",
                "CapabilityRoutingProtocol",
                "ConsensusProtocol",
            ],
        },
        "enums": {
            "task_priorities": [p.value for p in TaskPriority],
            "task_statuses": [s.value for s in TaskStatus],
        },
    }


@mcp_tool(
    category="collaboration",
    description="List available agent capabilities and coordination protocols.",
)
def list_agents() -> dict[str, Any]:
    """List the available agent classes and protocols.

    Returns:
        Dictionary with agent types, protocol classes, and capability info.
    """

    return {
        "agent_classes": ["BaseAgent", "AgentProxy"],
        "coordinator": "AgentCoordinator",
        "protocols": {
            "round_robin": {
                "class": "RoundRobinProtocol",
                "description": "Distributes tasks in round-robin order",
            },
            "broadcast": {
                "class": "BroadcastProtocol",
                "description": "Sends tasks to all agents simultaneously",
            },
            "capability": {
                "class": "CapabilityRoutingProtocol",
                "description": "Routes tasks based on agent capabilities",
            },
            "consensus": {
                "class": "ConsensusProtocol",
                "description": "Requires majority agreement among agents",
            },
        },
        "decomposer": "TaskDecomposer",
    }
