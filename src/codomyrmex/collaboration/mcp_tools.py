"""MCP tool definitions for the collaboration module.

Exposes swarm management and agent coordination as MCP tools
discoverable by Claude Code and other MCP-compatible agents.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


def _get_swarm_manager() -> Any:
    """Lazy-import SwarmManager to avoid circular imports."""
    from codomyrmex.collaboration.swarm import SwarmManager

    return SwarmManager()


def _get_task_decomposer() -> Any:
    """Lazy-import TaskDecomposer to avoid circular imports."""
    from codomyrmex.collaboration.swarm import TaskDecomposer

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
    from codomyrmex.collaboration.swarm import AgentProxy

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
        "agent_count": swarm.pool.size,
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
def collaboration_list_agents() -> dict[str, Any]:
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


# Module-level authority instance for stateful attestation across MCP calls
_attestation_authority: Any = None


def _get_authority() -> Any:
    """Lazy-init a shared AttestationAuthority."""
    global _attestation_authority
    if _attestation_authority is None:
        from codomyrmex.collaboration.coordination.attestation import (
            AttestationAuthority,
        )

        _attestation_authority = AttestationAuthority()
    return _attestation_authority


@mcp_tool(
    category="collaboration",
    description="Create a cryptographic attestation proving an agent completed a task.",
)
def collaboration_attest_task(
    task_id: str,
    agent_id: str,
    result_data: str,
) -> dict[str, Any]:
    """Create an HMAC-SHA256 signed attestation for a completed task.

    Args:
        task_id: Identifier of the completed task.
        agent_id: Identifier of the attesting agent.
        result_data: Result data string to bind into the attestation.

    Returns:
        dict with keys: status, attestation (serialized TaskAttestation)
    """
    try:
        authority = _get_authority()
        attestation = authority.attest(task_id, agent_id, result_data.encode())
        return {
            "status": "success",
            "attestation": attestation.to_dict(),
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="collaboration",
    description="Verify a cryptographic task attestation against result data.",
)
def collaboration_verify_attestation(
    attestation_dict: dict[str, Any],
    result_data: str,
) -> dict[str, Any]:
    """Verify an HMAC-SHA256 attestation against result data.

    Args:
        attestation_dict: Serialized attestation (as returned by collaboration_attest_task).
        result_data: The original result data string.

    Returns:
        dict with keys: status, valid, task_id
    """
    try:
        from codomyrmex.collaboration.coordination.attestation import TaskAttestation

        authority = _get_authority()
        attestation = TaskAttestation(
            task_id=attestation_dict["task_id"],
            agent_id=attestation_dict["agent_id"],
            result_hash=attestation_dict["result_hash"],
            timestamp=attestation_dict["timestamp"],
            signature=attestation_dict["signature"],
        )
        valid = authority.verify(attestation, result_data.encode())
        return {
            "status": "success",
            "valid": valid,
            "task_id": attestation.task_id,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
