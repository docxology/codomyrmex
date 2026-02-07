# collaboration

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The collaboration module provides multi-agent collaboration capabilities including agent management, communication channels, task coordination, and message-passing protocols. It supports round-robin, broadcast, capability-routing, and consensus protocols, along with swarm-based task decomposition and parallel execution for orchestrating complex multi-agent workflows.


## Installation

```bash
pip install codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Data Models

- **`TaskPriority`** -- Enum for task priority levels used in coordination
- **`TaskStatus`** -- Enum tracking task lifecycle states
- **`Task`** -- Core task representation with priority, status, dependencies, and metadata
- **`TaskResult`** -- Result container for completed task executions
- **`SwarmStatus`** -- Status tracking for swarm-based multi-agent operations
- **`AgentStatus`** -- Individual agent availability and health status

### Protocol Classes

- **`AgentState`** -- Enum representing agent operational states
- **`MessageType`** -- Enum classifying inter-agent message types
- **`AgentMessage`** -- Structured message for agent-to-agent communication
- **`AgentCapability`** -- Declares what an agent can do, used for capability-based routing
- **`AgentProtocol`** -- Abstract base protocol for agent communication patterns
- **`BaseAgent`** -- Base class for all collaborative agents with message handling
- **`AgentCoordinator`** -- Central coordinator managing agent registration and task dispatch
- **`RoundRobinProtocol`** -- Distributes tasks evenly across available agents in rotation
- **`BroadcastProtocol`** -- Sends messages to all registered agents simultaneously
- **`CapabilityRoutingProtocol`** -- Routes tasks to agents based on declared capabilities
- **`ConsensusProtocol`** -- Achieves agreement among agents through voting mechanisms

### Swarm Components

- **`SwarmManager`** -- Orchestrates swarm-based parallel task execution across agent proxies
- **`AgentProxy`** -- Lightweight proxy representing a remote agent in the swarm
- **`TaskDecomposer`** -- Breaks complex tasks into subtasks for parallel swarm execution

### Exceptions

- **`CollaborationError`** -- Base exception for all collaboration failures
- **`AgentNotFoundError`** -- Raised when referencing a non-existent agent
- **`AgentBusyError`** -- Raised when an agent cannot accept new tasks
- **`TaskExecutionError`** -- Raised when task execution fails
- **`TaskNotFoundError`** -- Raised when referencing a non-existent task
- **`TaskDependencyError`** -- Raised when task dependencies cannot be satisfied
- **`ConsensusError`** -- Raised when consensus cannot be reached
- **`ChannelError`** -- Raised on communication channel failures
- **`MessageDeliveryError`** -- Raised when message delivery fails
- **`CoordinationError`** -- Raised on general coordination failures
- **`LeaderElectionError`** -- Raised when leader election fails
- **`CapabilityMismatchError`** -- Raised when no agent matches required capabilities

### Submodules

- **`agents`** -- Agent definitions, workers, supervisors, and registry
- **`communication`** -- Communication channels, broadcasting, and direct messaging
- **`coordination`** -- Task management, consensus, and leader election
- **`protocols`** -- Message passing protocols and swarm behavior

## Directory Contents

- `__init__.py` - Module entry point; exports all models, protocols, exceptions, and submodules
- `models.py` - Core data models (`Task`, `TaskResult`, `TaskPriority`, `TaskStatus`, `SwarmStatus`, `AgentStatus`)
- `exceptions.py` - Full exception hierarchy for collaboration error handling
- `agents/` - Agent implementations (workers, supervisors, registry)
- `communication/` - Channel-based messaging (broadcast, direct, pub/sub)
- `coordination/` - Task coordination, consensus algorithms, leader election
- `protocols/` - Communication protocols (round-robin, broadcast, capability routing, consensus, swarm)
- `AGENTS.md` - Agent integration specification
- `API_SPECIFICATION.md` - Programmatic interface documentation
- `SECURITY.md` - Security considerations
- `SPEC.md` - Module specification
- `PAI.md` - PAI integration notes

## Quick Start

```python
from codomyrmex.collaboration import CollaborationError, AgentNotFoundError, AgentBusyError

# Initialize CollaborationError
instance = CollaborationError()
```


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k collaboration -v
```

## Navigation

- **Full Documentation**: [docs/modules/collaboration/](../../../docs/modules/collaboration/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
