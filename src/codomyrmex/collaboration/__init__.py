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
    TaskAssignment,
    TaskDecomposer,
    Vote,
)

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:  # pragma: no cover
    Result = None  # type: ignore
    ResultStatus = None  # type: ignore


def cli_commands():  # pragma: no cover
    """Return CLI commands for the collaboration module.

    Returns:
        Dictionary of CLI commands and handlers.

    """
    return {
        "sessions": {
            "help": "List active collaboration sessions",
            "handler": lambda: print(
                "Active Collaboration Sessions:\n"
                "  (no active sessions)"
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
    # Swarm components
    "SwarmManager",
    "AgentPool",
    "MessageBus",
    "TaskDecomposer",
    "SwarmAgent",
    "SwarmMessage",
    "TaskAssignment",
    "AgentRole",
    "SwarmMessageType",
    "Vote",
    "ConsensusResult",
    "Decision",
    "AgentProxy", # Legacy
    # Submodules
    "agents",
    "communication",
    "coordination",
    "protocols",
    "swarm",
    # CLI integration
    "cli_commands",
]

__version__ = "0.2.1"
