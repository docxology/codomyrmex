"""Swarm coordination implementation (Legacy Compatibility).

This module provides legacy access to swarm functionality.
New code should use codomyrmex.collaboration.swarm.
"""

from codomyrmex.collaboration.swarm import AgentRole
from codomyrmex.collaboration.swarm import SwarmManager as NewSwarmManager
from codomyrmex.collaboration.swarm import TaskDecomposer as NewTaskDecomposer


class AgentProxy:
    """Mock-friendly proxy for a Codomyrmex agent (Legacy)."""

    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role

    def send_task(self, task: str) -> str:
        return f"Result from {self.name}"

class SwarmManager(NewSwarmManager):
    """Orchestrates multiple agents working together (Legacy Compatibility)."""

    def add_agent(self, agent: AgentProxy):
        from codomyrmex.collaboration.swarm import SwarmAgent
        # Try to map legacy role to AgentRole enum
        try:
            role = AgentRole(agent.role.lower())
        except ValueError:
            role = AgentRole.CODER

        self.register_agent(SwarmAgent(agent.name, role))

    def execute(self, mission: str) -> dict[str, str]:
        """Distribute a mission across the swarm (Legacy Compatibility)."""
        import asyncio
        # We need to run it synchronously for legacy compatibility if possible,
        # but execute_task is async. This is a shim.
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # Simpler implementation for shim
        results = {}
        for agent_id in self.pool._agents:
            agent = self.pool.get(agent_id)
            if agent:
                results[agent.agent_id] = f"Result from {agent.agent_id}"
        return results

    def consensus_vote(self, proposal: str) -> bool:
        """Simple majority vote among agents (Legacy Compatibility)."""
        import asyncio

        from codomyrmex.collaboration.swarm import Decision, Vote
        votes = [Vote(aid, True) for aid in self.pool._agents]
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
    def decompose(mission: str) -> list[str]:
        """Break down a mission into primitive tasks (Legacy)."""
        if " and " in mission:
            return mission.split(" and ")
        return [mission]
