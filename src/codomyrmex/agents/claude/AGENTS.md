# Codomyrmex Agents — src/codomyrmex/agents/claude

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Claude API integration module providing a client interface for Anthropic's Claude models. This module enables direct interaction with Claude for code generation, analysis, and conversational AI tasks within the Codomyrmex agent framework.

## Active Components

- `claude_client.py` - Main Claude API client implementation
- `claude_integration.py` - Integration adapter for the agent framework
- `__init__.py` - Module exports
- `README.md` - Module documentation
- `SPEC.md` - Specification document

## Key Classes

### Client
- **`ClaudeClient`** - Primary client for interacting with Claude API
  - Handles authentication and API communication
  - Supports streaming and non-streaming responses
  - Manages conversation context and message history
  - Provides code generation and analysis capabilities

### Integration
- **`ClaudeIntegrationAdapter`** - Adapter implementing the core `AgentIntegrationAdapter` interface
  - Bridges Claude client with the standardized agent framework
  - Translates between `AgentRequest`/`AgentResponse` and Claude-specific formats
  - Manages capability reporting for orchestration

## Operating Contracts

- Requires valid `ANTHROPIC_API_KEY` environment variable or explicit configuration.
- Respects rate limits and implements appropriate retry logic.
- Follows the `AgentInterface` contract from `core` module.
- Errors are raised as `ClaudeError` exceptions (defined in `core.exceptions`).
- Supports both synchronous and asynchronous operation modes.

## Signposting

- **Direct API usage?** Use `ClaudeClient` for low-level control.
- **Framework integration?** Use `ClaudeIntegrationAdapter` for standardized access.
- **Configuration?** Set API key via environment or `AgentConfig`.
- **Error handling?** Catch `ClaudeError` for Claude-specific issues.

## Navigation Links

- **Parent Directory**: [agents](../README.md) - Parent directory documentation
- **Core Module**: [core](../core/AGENTS.md) - Base classes and interfaces
- **Project Root**: ../../../../README.md - Main project documentation
