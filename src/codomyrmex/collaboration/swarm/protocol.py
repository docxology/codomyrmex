"""Swarm protocol definitions — roles, messages, and task types.

Defines the vocabulary for multi-agent swarm communication including
agent roles, message types, and task assignment structures.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class AgentRole(Enum):
    """Roles an agent can assume in a swarm."""
    CODER = "coder"
    REVIEWER = "reviewer"
    ARCHITECT = "architect"
    TESTER = "tester"
    DOCUMENTER = "documenter"
    DEVOPS = "devops"


class MessageType(Enum):
    """Types of swarm messages."""
    TASK_ASSIGNMENT = "task_assignment"
    REVIEW_REQUEST = "review_request"
    APPROVAL_VOTE = "approval_vote"
    STATUS_UPDATE = "status_update"
    RESULT = "result"
    ERROR = "error"


class TaskStatus(Enum):
    """Status of a swarm task."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class SwarmMessage:
    """A message exchanged between swarm agents.

    Attributes:
        message_type: Type of message.
        sender: Sender agent ID.
        recipient: Recipient agent ID (empty = broadcast).
        payload: Message payload.
        message_id: Unique message identifier.
        timestamp: Creation timestamp.
    """

    message_type: MessageType
    sender: str
    recipient: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    message_id: str = ""
    timestamp: float = 0.0

    def __post_init__(self) -> None:
        """Execute   Post Init   operations natively."""
        if not self.message_id:
            self.message_id = str(uuid.uuid4())[:8]
        if not self.timestamp:
            self.timestamp = time.time()

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "message_type": self.message_type.value,
            "sender": self.sender,
            "recipient": self.recipient,
            "payload": self.payload,
            "message_id": self.message_id,
            "timestamp": self.timestamp,
        }


@dataclass
class SwarmAgent:
    """An agent participating in a swarm.

    Attributes:
        agent_id: Unique agent identifier.
        role: Agent's role.
        capabilities: Set of capability tags (e.g. ``python``, ``security``).
        active_tasks: Number of currently assigned tasks.
        max_concurrent: Maximum concurrent tasks.
    """

    agent_id: str
    role: AgentRole
    capabilities: set[str] = field(default_factory=set)
    active_tasks: int = 0
    max_concurrent: int = 3

    @property
    def available(self) -> bool:
        """Execute Available operations natively."""
        return self.active_tasks < self.max_concurrent

    @property
    def load(self) -> float:
        """Execute Load operations natively."""
        return self.active_tasks / self.max_concurrent if self.max_concurrent > 0 else 1.0

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "agent_id": self.agent_id,
            "role": self.role.value,
            "capabilities": sorted(self.capabilities),
            "active_tasks": self.active_tasks,
            "available": self.available,
            "load": round(self.load, 2),
        }


@dataclass
class TaskAssignment:
    """Assignment of a task to an agent.

    Attributes:
        task_id: Unique task identifier.
        description: Task description.
        assignee: Agent ID of assignee.
        required_role: Required role for this task.
        required_capabilities: Required capabilities.
        status: Current task status.
        priority: Task priority (lower = higher priority).
        result: Task result payload.
    """

    task_id: str = ""
    description: str = ""
    assignee: str = ""
    required_role: AgentRole | None = None
    required_capabilities: set[str] = field(default_factory=set)
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 5
    result: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Execute   Post Init   operations natively."""
        if not self.task_id:
            self.task_id = str(uuid.uuid4())[:8]

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "task_id": self.task_id,
            "description": self.description,
            "assignee": self.assignee,
            "required_role": self.required_role.value if self.required_role else None,
            "status": self.status.value,
            "priority": self.priority,
        }


__all__ = [
    "AgentRole",
    "MessageType",
    "SwarmAgent",
    "SwarmMessage",
    "TaskAssignment",
    "TaskStatus",
]
