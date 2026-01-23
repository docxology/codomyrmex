# Codomyrmex Agents — src/codomyrmex/agents/jules

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Jules CLI integration module providing a client interface for the Jules coding assistant. This module enables interaction with Jules for automated code tasks and workflows within the Codomyrmex agent framework.

## Active Components

- `jules_client.py` - Main Jules CLI client implementation
- `jules_integration.py` - Integration adapter for the agent framework
- `__init__.py` - Module exports
- `README.md` - Module documentation
- `SPEC.md` - Specification document

## Key Classes

### Client
- **`JulesClient`** - Primary client for interacting with Jules CLI
  - Handles CLI command execution and output parsing
  - Supports streaming output for long-running tasks
  - Manages task execution and status monitoring
  - Provides help and command discovery

### Integration
- **`JulesIntegrationAdapter`** - Adapter implementing the core `AgentIntegrationAdapter` interface
  - Bridges Jules client with the standardized agent framework
  - Translates between `AgentRequest`/`AgentResponse` and Jules CLI formats
  - Reports task automation capabilities for orchestration

## Operating Contracts

- Requires Jules CLI to be installed and accessible in PATH.
- Follows the `AgentInterface` contract from `core` module.
- Errors are raised as `JulesError` exceptions (defined in `core.exceptions`).
- Supports both execute (blocking) and stream (non-blocking) operation modes.
- CLI handlers provide execute, stream, check, and help commands.

## Signposting

- **Direct CLI usage?** Use `JulesClient` for low-level control.
- **Framework integration?** Use `JulesIntegrationAdapter` for standardized access.
- **Streaming output?** Use the stream method for real-time output.
- **Error handling?** Catch `JulesError` for Jules-specific issues.

## Navigation Links

- **Parent Directory**: [agents](../README.md) - Parent directory documentation
- **Core Module**: [core](../core/AGENTS.md) - Base classes and interfaces
- **CLI Handlers**: [cli](../cli/AGENTS.md) - CLI command handlers
- **Project Root**: ../../../../README.md - Main project documentation
