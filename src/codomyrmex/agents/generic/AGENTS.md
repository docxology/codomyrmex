# Codomyrmex Agents -- src/codomyrmex/agents/generic

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Shared base classes and utilities for building agent implementations: an API-based agent base class, a CLI subprocess agent base class, a multi-agent orchestrator, a publish/subscribe message bus, and a task planner with dependency-aware execution ordering.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `api_agent_base.py` | `APIAgentBase` | Base class for API-backed agents; handles API-key extraction, config fallback chain, client initialization, token extraction, error normalization, and standardized `AgentResponse` construction |
| `cli_agent_base.py` | `CLIAgentBase` | Base class for CLI subprocess agents; provides command availability checking, `_execute_command` with timeout/cwd/env, `_stream_command` for line-by-line output, health checks, and a `retry_on_failure` decorator |
| `agent_orchestrator.py` | `AgentOrchestrator`, `OrchestrationStrategy` | Multi-agent orchestration with parallel (ThreadPoolExecutor), sequential, and fallback execution strategies; capability-based agent selection |
| `message_bus.py` | `MessageBus`, `Message` | Pub/sub inter-agent communication with typed subscriptions, wildcard listeners, directed `send`, `broadcast`, and message history retrieval |
| `task_planner.py` | `TaskPlanner`, `Task`, `TaskStatus` | Task decomposition, dependency tracking, topological execution ordering, and status lifecycle management (PENDING, IN_PROGRESS, COMPLETED, FAILED, CANCELLED) |
| `__init__.py` | -- | Exports all public classes: `APIAgentBase`, `CLIAgentBase`, `AgentOrchestrator`, `MessageBus`, `Message`, `TaskPlanner`, `Task`, `TaskStatus` |

## Operating Contracts

- `APIAgentBase` requires a non-None `client_class` and a valid API key; raises `AgentConfigurationError` if the key is missing.
- `CLIAgentBase._check_command_available` caches its result after the first probe; callers should not assume re-evaluation.
- `AgentOrchestrator` raises `AgentError` if invoked with an empty agent list.
- `MessageBus` handler exceptions are caught, logged, and do not interrupt delivery to other subscribers.
- `TaskPlanner.get_task_execution_order` performs topological sort and logs a warning on circular dependencies rather than raising.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.agents.core` (BaseAgent, AgentRequest, AgentResponse, AgentInterface, AgentCapabilities, AgentError, AgentTimeoutError, AgentConfigurationError), `codomyrmex.agents.core.config` (AgentConfig, get_config), `codomyrmex.logging_monitoring`
- **Used by**: `codomyrmex.agents.claude.ClaudeClient` (extends `APIAgentBase`), `codomyrmex.agents.gemini.GeminiCLIWrapper` (extends `BaseAgent` but follows CLI patterns), any custom agent implementation

## Navigation

- **Parent**: [agents](../README.md)
- **Root**: [Root](../../../../README.md)
