"""Swarm orchestration subpackage."""


class AgentProxy:
    """Proxy for a Codomyrmex agent in a swarm."""

    def __init__(self, name: str, role: str) -> None:
        """Initialize AgentProxy."""
        self.name = name
        self.role = role

    def send_task(self, task: str) -> str:
        """Delegate to SwarmManager; raises NotImplementedError as legacy stub.

        Raises:
            NotImplementedError: Use ``SwarmManager`` for real agent delegation.
        """
        raise NotImplementedError(
            "AgentProxy.send_task is not implemented. "
            "Use codomyrmex.collaboration.swarm.SwarmManager for real agent delegation."
        )


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
