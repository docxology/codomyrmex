"""Swarm orchestration subpackage."""

from .manager import SwarmManager
from .pool import AgentPool
from .message_bus import MessageBus
from .decomposer import TaskDecomposer, SubTask
from .consensus import ConsensusEngine, Vote, ConsensusResult, Decision
from .protocol import (
    AgentRole,
    SwarmMessageType,
    SwarmAgent,
    SwarmMessage,
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
