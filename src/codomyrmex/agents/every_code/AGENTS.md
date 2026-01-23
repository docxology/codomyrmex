# Codomyrmex Agents — src/codomyrmex/agents/every_code

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Every Code CLI integration module providing multi-agent orchestration capabilities. This module enables coordination and routing of tasks across multiple coding agents (Claude, Codex, Gemini, Jules, etc.) within the Codomyrmex agent framework.

## Active Components

- `every_code_client.py` - Main Every Code client implementation
- `every_code_integration.py` - Integration adapter for the agent framework
- `__init__.py` - Module exports
- `README.md` - Module documentation
- `SPEC.md` - Specification document

## Key Classes

### Client
- **`EveryCodeClient`** - Primary client for multi-agent orchestration
  - Coordinates tasks across multiple agent backends
  - Routes requests to appropriate agents based on capabilities
  - Aggregates and synthesizes responses from multiple agents
  - Manages agent selection and fallback strategies

### Integration
- **`EveryCodeIntegrationAdapter`** - Adapter implementing the core `AgentIntegrationAdapter` interface
  - Bridges Every Code client with the standardized agent framework
  - Provides unified access to multiple agent backends
  - Reports aggregated capabilities from all registered agents

## Operating Contracts

- Requires at least one backend agent to be properly configured.
- Follows the `AgentInterface` contract from `core` module.
- Routes tasks based on agent capabilities and availability.
- Supports fallback to alternative agents on failure.
- Integrates with the generic `AgentOrchestrator` pattern.

## Signposting

- **Multi-agent tasks?** Use `EveryCodeClient` for automatic agent selection.
- **Framework integration?** Use `EveryCodeIntegrationAdapter` for standardized access.
- **Custom orchestration?** See `generic/agent_orchestrator.py` for base patterns.
- **Agent capabilities?** Query the adapter for available agent capabilities.

## Navigation Links

- **Parent Directory**: [agents](../README.md) - Parent directory documentation
- **Core Module**: [core](../core/AGENTS.md) - Base classes and interfaces
- **Generic Module**: [generic](../generic/AGENTS.md) - Orchestration utilities
- **Project Root**: ../../../../README.md - Main project documentation
