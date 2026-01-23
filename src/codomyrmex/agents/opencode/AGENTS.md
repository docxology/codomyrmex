# Codomyrmex Agents — src/codomyrmex/agents/opencode

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

OpenCode CLI integration module providing a client interface for the OpenCode coding assistant. This module enables interaction with OpenCode for code editing, generation, and project management within the Codomyrmex agent framework.

## Active Components

- `opencode_client.py` - Main OpenCode CLI client implementation
- `opencode_integration.py` - Integration adapter for the agent framework
- `__init__.py` - Module exports
- `README.md` - Module documentation
- `SPEC.md` - Specification document

## Key Classes

### Client
- **`OpenCodeClient`** - Primary client for interacting with OpenCode CLI
  - Handles CLI command execution and output parsing
  - Supports streaming output for interactive sessions
  - Manages project initialization and configuration
  - Provides version checking and status monitoring

### Integration
- **`OpenCodeIntegrationAdapter`** - Adapter implementing the core `AgentIntegrationAdapter` interface
  - Bridges OpenCode client with the standardized agent framework
  - Translates between `AgentRequest`/`AgentResponse` and OpenCode CLI formats
  - Reports code editing capabilities for orchestration

## Operating Contracts

- Requires OpenCode CLI to be installed and accessible in PATH.
- Follows the `AgentInterface` contract from `core` module.
- Errors are raised as `OpenCodeError` exceptions (defined in `core.exceptions`).
- Supports execute, stream, check, init, and version CLI operations.
- CLI handlers provide initialization and version management.

## Signposting

- **Direct CLI usage?** Use `OpenCodeClient` for low-level control.
- **Framework integration?** Use `OpenCodeIntegrationAdapter` for standardized access.
- **Project setup?** Use the init handler to initialize OpenCode in a project.
- **Error handling?** Catch `OpenCodeError` for OpenCode-specific issues.

## Navigation Links

- **Parent Directory**: [agents](../README.md) - Parent directory documentation
- **Core Module**: [core](../core/AGENTS.md) - Base classes and interfaces
- **CLI Handlers**: [cli](../cli/AGENTS.md) - CLI command handlers
- **Project Root**: ../../../../README.md - Main project documentation
