# Codomyrmex Agents — src/codomyrmex/agents/mistral_vibe

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Mistral Vibe CLI integration module providing a client interface for Mistral's Vibe coding assistant. This module enables interaction with Mistral Vibe for code generation and analysis within the Codomyrmex agent framework.

## Active Components

- `mistral_vibe_client.py` - Main Mistral Vibe CLI client implementation
- `mistral_vibe_integration.py` - Integration adapter for the agent framework
- `__init__.py` - Module exports
- `README.md` - Module documentation
- `SPEC.md` - Specification document

## Key Classes

### Client
- **`MistralVibeClient`** - Primary client for interacting with Mistral Vibe CLI
  - Handles CLI command execution and output parsing
  - Supports streaming output for interactive sessions
  - Manages code generation and analysis requests
  - Provides configuration for Mistral model parameters

### Integration
- **`MistralVibeIntegrationAdapter`** - Adapter implementing the core `AgentIntegrationAdapter` interface
  - Bridges Mistral Vibe client with the standardized agent framework
  - Translates between `AgentRequest`/`AgentResponse` and Mistral Vibe formats
  - Reports code generation capabilities for orchestration

## Operating Contracts

- Requires Mistral Vibe CLI to be installed and accessible in PATH.
- May require Mistral API credentials depending on CLI configuration.
- Follows the `AgentInterface` contract from `core` module.
- Supports both synchronous and streaming operation modes.
- Integrates with the generic CLI agent base patterns.

## Signposting

- **Direct CLI usage?** Use `MistralVibeClient` for low-level control.
- **Framework integration?** Use `MistralVibeIntegrationAdapter` for standardized access.
- **CLI patterns?** See `generic/cli_agent_base.py` for base patterns.
- **Configuration?** Configure via environment or `AgentConfig`.

## Navigation Links

- **Parent Directory**: [agents](../README.md) - Parent directory documentation
- **Core Module**: [core](../core/AGENTS.md) - Base classes and interfaces
- **Generic Base**: [generic](../generic/AGENTS.md) - Generic agent base classes
- **Project Root**: ../../../../README.md - Main project documentation
