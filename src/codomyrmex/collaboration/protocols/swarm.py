"""Swarm coordination implementation (Legacy Compatibility).

.. deprecated::
    This module is deprecated and will be removed in a future release.
    Use :mod:`codomyrmex.collaboration.swarm` for all new code.
"""

import warnings

warnings.warn(
    "codomyrmex.collaboration.protocols.swarm is deprecated. "
    "Use codomyrmex.collaboration.swarm instead.",
    DeprecationWarning,
    stacklevel=2,
)

from codomyrmex.collaboration.swarm import AgentRole
from codomyrmex.collaboration.swarm import SwarmManager as NewSwarmManager
from codomyrmex.collaboration.swarm import TaskDecomposer as NewTaskDecomposer


class AgentProxy:
    """Mock-friendly proxy for a Codomyrmex agent (Legacy)."""

    def __init__(self, name: str, role: str):
        """Initialize legacy AgentProxy."""
        self.name = name
        self.role = role

    def send_task(self, task: str) -> str:
        """Send a task to this agent.

        Raises:
            NotImplementedError: Legacy AgentProxy does not implement task execution.
                Use codomyrmex.collaboration.swarm.SwarmManager for real delegation.

        """
        raise NotImplementedError(
            "AgentProxy.send_task is not implemented. "
            "Use codomyrmex.collaboration.swarm.SwarmManager for real agent delegation."
        )


class SwarmManager(NewSwarmManager):
    """Orchestrates multiple agents working together (Legacy Compatibility)."""

    def add_agent(self, agent: AgentProxy):
        """Add legacy AgentProxy."""
        from codomyrmex.collaboration.swarm import SwarmAgent

        # Try to map legacy role to AgentRole enum
        try:
            role = AgentRole(agent.role.lower())
        except ValueError:
            role = AgentRole.CODER

        self.register_agent(SwarmAgent(agent.name, role))

    def execute(self, mission: str) -> dict[str, str]:
        """Distribute a mission across the swarm (Legacy Compatibility).

        Decomposes the mission into role-based subtasks and returns the
        distribution plan keyed by task_id.  For full async execution with
        real result values, call ``execute_mission()`` directly.

        Returns:
            Mapping of task_id to task description for each decomposed subtask.

        """
        subtasks = self.decomposer.decompose(mission)
        return {st.task_id: st.description for st in subtasks}

    def consensus_vote(self, proposal: str) -> bool:
        """Perform simple majority vote among agents (Legacy Compatibility)."""
        import asyncio

        from codomyrmex.collaboration.swarm import Decision, SwarmVote

        votes = [SwarmVote(aid, True) for aid in self.pool._agents]
        if not votes:
            return False
        try:
            result = asyncio.run(self.request_consensus(proposal, votes))
        except RuntimeError:
            loop = asyncio.new_event_loop()
            result = loop.run_until_complete(self.request_consensus(proposal, votes))
            loop.close()
        return result.decision == Decision.APPROVED


class TaskDecomposer(NewTaskDecomposer):
    """Utilities for breaking down complex missions (Legacy Compatibility)."""

    @staticmethod
    def decompose(mission: str) -> list[str]:  # type: ignore
        """Break down a mission into primitive tasks (Legacy)."""
        if " and " in mission:
            return mission.split(" and ")
        return [mission]
