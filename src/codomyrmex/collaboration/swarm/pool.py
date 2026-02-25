"""Capability-based agent pool with load balancing.

Routes tasks to agents based on role, capabilities, and current load.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.collaboration.swarm.protocol import (
    AgentRole,
    SwarmAgent,
    TaskAssignment,
    TaskStatus,
)
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class AssignmentError(Exception):
    """Raised when no suitable agent is available."""


class AgentPool:
    """Capability-based agent pool with routing and load balancing.

    Usage::

        pool = AgentPool()
        pool.register(SwarmAgent("alice", AgentRole.CODER, {"python"}))
        pool.register(SwarmAgent("bob", AgentRole.REVIEWER, {"python", "security"}))
        agent = pool.assign(TaskAssignment(
            description="fix bug",
            required_role=AgentRole.CODER,
        ))
    """

    def __init__(self) -> None:
        """Execute   Init   operations natively."""
        self._agents: dict[str, SwarmAgent] = {}
        self._round_robin_index: int = 0

    def register(self, agent: SwarmAgent) -> None:
        """Register an agent in the pool."""
        self._agents[agent.agent_id] = agent
        logger.info("Agent registered", extra={"agent": agent.agent_id, "role": agent.role.value})

    def unregister(self, agent_id: str) -> bool:
        """Remove an agent from the pool."""
        if agent_id in self._agents:
            del self._agents[agent_id]
            return True
        return False

    @property
    def size(self) -> int:
        """Execute Size operations natively."""
        return len(self._agents)

    @property
    def available_agents(self) -> list[SwarmAgent]:
        """Execute Available Agents operations natively."""
        return [a for a in self._agents.values() if a.available]

    def get(self, agent_id: str) -> SwarmAgent | None:
        """Execute Get operations natively."""
        return self._agents.get(agent_id)

    def assign(self, task: TaskAssignment) -> SwarmAgent:
        """Assign a task to the best available agent.

        Selection: filter by role + capabilities → pick least-loaded.

        Args:
            task: The task to assign.

        Returns:
            The assigned ``SwarmAgent``.

        Raises:
            AssignmentError: If no suitable agent available.
        """
        candidates = list(self._agents.values())

        # Filter by availability
        candidates = [a for a in candidates if a.available]

        # Filter by role
        if task.required_role is not None:
            candidates = [a for a in candidates if a.role == task.required_role]

        # Filter by capabilities
        if task.required_capabilities:
            candidates = [
                a for a in candidates
                if task.required_capabilities.issubset(a.capabilities)
            ]

        if not candidates:
            raise AssignmentError(
                f"No agent available for role={task.required_role}, "
                f"caps={task.required_capabilities}"
            )

        # Select least-loaded agent
        best = min(candidates, key=lambda a: a.load)
        best.active_tasks += 1
        task.assignee = best.agent_id
        task.status = TaskStatus.ASSIGNED

        logger.info(
            "Task assigned",
            extra={"task": task.task_id, "agent": best.agent_id, "load": best.load},
        )

        return best

    def release(self, agent_id: str) -> None:
        """Release one task slot for an agent."""
        agent = self._agents.get(agent_id)
        if agent and agent.active_tasks > 0:
            agent.active_tasks -= 1

    def agents_by_role(self, role: AgentRole) -> list[SwarmAgent]:
        """Get all agents with a specific role."""
        return [a for a in self._agents.values() if a.role == role]

    def status(self) -> dict[str, Any]:
        """Get pool status summary."""
        return {
            "total": self.size,
            "available": len(self.available_agents),
            "by_role": {
                role.value: len(self.agents_by_role(role))
                for role in AgentRole
                if self.agents_by_role(role)
            },
        }


__all__ = [
    "AgentPool",
    "AssignmentError",
]
