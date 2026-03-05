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
    "AgentPool",
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
