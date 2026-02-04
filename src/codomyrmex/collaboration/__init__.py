"""Collaboration module for Codomyrmex.

Provides multi-agent collaboration capabilities including:
- Agent management (workers, supervisors, registry)
- Communication (channels, broadcasting, direct messaging)
- Coordination (task management, consensus, leader election)
- Protocols (message passing, swarm behavior)
"""

# Core data models
from .models import (
    TaskPriority,
    TaskStatus,
    Task,
    TaskResult,
    SwarmStatus,
    AgentStatus,
)

# Exceptions
from .exceptions import (
    CollaborationError,
    AgentNotFoundError,
    AgentBusyError,
    TaskExecutionError,
    TaskNotFoundError,
    TaskDependencyError,
    ConsensusError,
    ChannelError,
    MessageDeliveryError,
    CoordinationError,
    LeaderElectionError,
    CapabilityMismatchError,
)

# Protocol classes (existing)
from .protocols import (
    AgentState,
    MessageType,
    AgentMessage,
    AgentCapability,
    AgentProtocol,
    BaseAgent,
    AgentCoordinator,
    RoundRobinProtocol,
    BroadcastProtocol,
    CapabilityRoutingProtocol,
    ConsensusProtocol,
)

from .protocols.swarm import SwarmManager, AgentProxy, TaskDecomposer

# Submodule exports
from . import agents
from . import communication
from . import coordination
from . import protocols

__all__ = [
    # Data models
    "TaskPriority",
    "TaskStatus",
    "Task",
    "TaskResult",
    "SwarmStatus",
    "AgentStatus",
    # Exceptions
    "CollaborationError",
    "AgentNotFoundError",
    "AgentBusyError",
    "TaskExecutionError",
    "TaskNotFoundError",
    "TaskDependencyError",
    "ConsensusError",
    "ChannelError",
    "MessageDeliveryError",
    "CoordinationError",
    "LeaderElectionError",
    "CapabilityMismatchError",
    # Protocol classes
    "AgentState",
    "MessageType",
    "AgentMessage",
    "AgentCapability",
    "AgentProtocol",
    "BaseAgent",
    "AgentCoordinator",
    "RoundRobinProtocol",
    "BroadcastProtocol",
    "CapabilityRoutingProtocol",
    "ConsensusProtocol",
    # Legacy swarm
    "SwarmManager",
    "AgentProxy",
    "TaskDecomposer",
    # Submodules
    "agents",
    "communication",
    "coordination",
    "protocols",
]

__version__ = "0.2.0"
