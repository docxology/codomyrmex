"""Swarm orchestration subpackage."""

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
    "SwarmManager",
    "AgentPool",
    "MessageBus",
    "TaskDecomposer",
    "SubTask",
    "ConsensusEngine",
    "SwarmVote",
    "ConsensusResult",
    "Decision",
    "AgentRole",
    "SwarmMessageType",
    "SwarmAgent",
    "SwarmMessage",
    "TaskAssignment",
    "TaskStatus",
]
