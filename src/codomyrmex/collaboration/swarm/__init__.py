"""Swarm orchestration subpackage."""

from .consensus import ConsensusEngine, ConsensusResult, Decision, Vote
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
    "Vote",
    "ConsensusResult",
    "Decision",
    "AgentRole",
    "SwarmMessageType",
    "SwarmAgent",
    "SwarmMessage",
    "TaskAssignment",
    "TaskStatus",
]
