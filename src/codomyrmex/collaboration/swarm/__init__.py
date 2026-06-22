"""Swarm orchestration subpackage."""

import uuid


class AgentProxy:
    """Proxy for a Codomyrmex agent in a swarm."""

    def __init__(self, name: str, role: str) -> None:
        """Initialize AgentProxy."""
        from .protocol import AgentRole

        self.name = name
        try:
            self.role = AgentRole(role)
        except ValueError:
            self.role = AgentRole.CODER
        self.agent_id = str(uuid.uuid4())
        self.available = True

    def send_task(self, task: str) -> str:
        """Delegate to SwarmManager; raises NotImplementedError as legacy stub.

        Raises:
            NotImplementedError: Use ``SwarmManager`` for real agent delegation.
        """
        raise NotImplementedError(
            "AgentProxy.send_task is not implemented. "
            "Use codomyrmex.collaboration.swarm.SwarmManager for real agent delegation."
        )

    async def execute(self, task: str) -> str:
        return f"Executed by {self.name}: {task}"


from .consensus import ConsensusEngine, ConsensusResult, Decision, SwarmVote

Vote = SwarmVote  # backward-compat alias
from .decomposer import SubTask, TaskDecomposer
from .manager import SwarmManager
from .message_bus import MessageBus
from .pool import AgentPool
from .protocol import (
    AgentRole,
    SwarmAgent,
    SwarmMessage,
    SwarmMessageType,
    TaskAssignment,
    TaskStatus,
)

__all__ = [
    "AgentPool",
    "AgentProxy",
    "AgentRole",
    "ConsensusEngine",
    "ConsensusResult",
    "Decision",
    "MessageBus",
    "SubTask",
    "SwarmAgent",
    "SwarmManager",
    "SwarmMessage",
    "SwarmMessageType",
    "SwarmVote",
    "TaskAssignment",
    "TaskDecomposer",
    "TaskStatus",
]
