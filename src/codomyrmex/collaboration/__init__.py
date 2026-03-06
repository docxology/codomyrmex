"""Collaboration module for Codomyrmex.

Provides multi-agent collaboration capabilities including:
- Agent management (workers, supervisors, registry)
- Communication (channels, broadcasting, direct messaging)
- Coordination (task management, consensus, leader election)
- Protocols (message passing, swarm behavior)
"""

# Core data models
# Submodule exports
from . import agents, communication, coordination, protocols, swarm

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

# Legacy swarm components (for backward compatibility)
from .protocols.swarm import AgentProxy

# Swarm components (modern interface)
from .swarm import (
    AgentPool,
    AgentRole,
    ConsensusResult,
    Decision,
    MessageBus,
    SwarmAgent,
    SwarmManager,
    SwarmMessage,
    SwarmMessageType,
    SwarmVote,
    TaskAssignment,
    TaskDecomposer,
)

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:  # pragma: no cover
    Result = None
    ResultStatus = None


def cli_commands():  # pragma: no cover
    """Return CLI commands for the collaboration module.

    Returns:
        Dictionary of CLI commands and handlers.

    """
    return {
        "sessions": {
            "help": "List active collaboration sessions",
            "handler": lambda: print(
                "Active Collaboration Sessions:\n  (no active sessions)"
            ),
        },
        "status": {
            "help": "Show collaboration system status",
            "handler": lambda: print(
                "Collaboration Status:\n"
                f"  Version:      {__version__}\n"
                "  Agents:       module loaded\n"
                "  Communication: module loaded\n"
                "  Coordination:  module loaded\n"
                "  Protocols:     module loaded\n"
                "  Swarm:         module loaded"
            ),
        },
    }


__all__ = [
    "AgentBusyError",
    "AgentCapability",
    "AgentCoordinator",
    "AgentMessage",
    "AgentNotFoundError",
    "AgentPool",
    "AgentProtocol",
    "AgentProxy",  # Legacy
    "AgentRole",
    # Protocol classes
    "AgentState",
    "AgentStatus",
    "BaseAgent",
    "BroadcastProtocol",
    "CapabilityMismatchError",
    "CapabilityRoutingProtocol",
    "ChannelError",
    # Exceptions
    "CollaborationError",
    "ConsensusError",
    "ConsensusProtocol",
    "ConsensusResult",
    "CoordinationError",
    "Decision",
    "LeaderElectionError",
    "MessageBus",
    "MessageDeliveryError",
    "MessageType",
    "RoundRobinProtocol",
    "SwarmAgent",
    # Swarm components
    "SwarmManager",
    "SwarmMessage",
    "SwarmMessageType",
    "SwarmStatus",
    "Task",
    "TaskAssignment",
    "TaskDecomposer",
    "TaskDependencyError",
    "TaskExecutionError",
    "TaskNotFoundError",
    # Data models
    "TaskPriority",
    "TaskResult",
    "TaskStatus",
    "Vote",
    # Submodules
    "agents",
    # CLI integration
    "cli_commands",
    "communication",
    "coordination",
    "protocols",
    "swarm",
]

__version__ = "0.2.1"
