"""Collaboration module for Codomyrmex.

Provides multi-agent collaboration capabilities including:
- Agent management (workers, supervisors, registry)
- Communication (channels, broadcasting, direct messaging)
- Coordination (task management, consensus, leader election)
- Protocols (message passing, swarm behavior)
"""

# Core data models
# Submodule exports
from . import agents, communication, coordination, protocols

# Exceptions
from .exceptions import (
    AgentBusyError,
    AgentNotFoundError,
    CapabilityMismatchError,
    ChannelError,
    CollaborationError,
    ConsensusError,
    CoordinationError,
    LeaderElectionError,
    MessageDeliveryError,
    TaskDependencyError,
    TaskExecutionError,
    TaskNotFoundError,
)
from .models import (
    AgentStatus,
    SwarmStatus,
    Task,
    TaskPriority,
    TaskResult,
    TaskStatus,
)

# Protocol classes (existing)
from .protocols import (
    AgentCapability,
    AgentCoordinator,
    AgentMessage,
    AgentProtocol,
    AgentState,
    BaseAgent,
    BroadcastProtocol,
    CapabilityRoutingProtocol,
    ConsensusProtocol,
    MessageType,
    RoundRobinProtocol,
)
from .protocols.swarm import AgentProxy, SwarmManager, TaskDecomposer

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
