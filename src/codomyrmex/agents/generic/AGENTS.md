# Codomyrmex Agents — src/codomyrmex/agents/generic

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Generic agent utilities and base classes providing reusable patterns for agent implementations. This module includes base classes for API and CLI agents, orchestration utilities, message bus, and task planning.

## Active Components

- `api_agent_base.py` - Base class for API-based agents
- `cli_agent_base.py` - Base class for CLI-based agents
- `agent_orchestrator.py` - Multi-agent orchestration
- `message_bus.py` - Inter-agent messaging
- `task_planner.py` - Task planning and scheduling
- `__init__.py` - Module exports
- `README.md` - Module documentation
- `SPEC.md` - Specification document

## Key Classes

### Base Classes
- **`APIAgentBase`** - Abstract base for agents using HTTP/REST APIs
  - Handles authentication and request formatting
  - Manages rate limiting and retries
  - Provides common API interaction patterns

- **`CLIAgentBase`** - Abstract base for agents using CLI tools
  - Handles command execution and output parsing
  - Manages process lifecycle and timeouts
  - Provides streaming output capabilities

### Orchestration
- **`AgentOrchestrator`** - Coordinates multiple agents for complex tasks
  - Routes tasks to appropriate agents
  - Manages agent lifecycle and state
  - Aggregates results from multiple agents
  - Handles fallback and error recovery

### Messaging
- **`MessageBus`** - Pub/sub messaging between agents
  - Asynchronous message delivery
  - Topic-based subscription
  - Message persistence and replay

- **`Message`** - Message dataclass for inter-agent communication
  - Sender and recipient identification
  - Payload and metadata
  - Timestamp and correlation IDs

### Task Planning
- **`TaskPlanner`** - Plans and schedules agent tasks
  - Task decomposition and sequencing
  - Dependency resolution
  - Priority-based scheduling

- **`Task`** - Dataclass representing a planned task
  - Task definition and parameters
  - Dependencies and constraints
  - Execution context

- **`TaskStatus`** - Enum for task execution states
  - PENDING, RUNNING, COMPLETED, FAILED, CANCELLED

## Operating Contracts

- Base classes define abstract methods that must be implemented.
- Orchestrator requires agents to implement the `AgentInterface`.
- Message bus operations are non-blocking by default.
- Task planner respects dependency ordering.
- All components integrate with the core logging and configuration.

## Signposting

- **Building an API agent?** Extend `APIAgentBase`.
- **Building a CLI agent?** Extend `CLIAgentBase`.
- **Multi-agent workflows?** Use `AgentOrchestrator`.
- **Agent communication?** Use `MessageBus` for async messaging.
- **Task scheduling?** Use `TaskPlanner` for complex workflows.

## Navigation Links

- **Parent Directory**: [agents](../README.md) - Parent directory documentation
- **Core Module**: [core](../core/AGENTS.md) - Base classes and interfaces
- **Every Code**: [every_code](../every_code/AGENTS.md) - Multi-agent client
- **Project Root**: ../../../../README.md - Main project documentation
