# Codomyrmex Agents — src/codomyrmex/agents/codex

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

OpenAI Codex integration module providing a client interface for OpenAI's code-focused models. This module enables code completion, generation, and transformation tasks using OpenAI's API within the Codomyrmex agent framework.

## Active Components

- `codex_client.py` - Main Codex API client implementation
- `codex_integration.py` - Integration adapter for the agent framework
- `__init__.py` - Module exports
- `README.md` - Module documentation
- `SPEC.md` - Specification document

## Key Classes

### Client
- **`CodexClient`** - Primary client for interacting with OpenAI Codex/GPT models
  - Handles authentication and API communication
  - Supports code completion and generation
  - Manages model selection and parameters
  - Provides streaming capabilities

### Integration
- **`CodexIntegrationAdapter`** - Adapter implementing the core `AgentIntegrationAdapter` interface
  - Bridges Codex client with the standardized agent framework
  - Translates between `AgentRequest`/`AgentResponse` and OpenAI-specific formats
  - Reports code-focused capabilities for orchestration

## Operating Contracts

- Requires valid `OPENAI_API_KEY` environment variable or explicit configuration.
- Respects OpenAI rate limits and implements retry logic.
- Follows the `AgentInterface` contract from `core` module.
- Errors are raised as `CodexError` exceptions (defined in `core.exceptions`).
- Supports temperature and other generation parameters.

## Signposting

- **Direct API usage?** Use `CodexClient` for low-level control.
- **Framework integration?** Use `CodexIntegrationAdapter` for standardized access.
- **Configuration?** Set API key via environment or `AgentConfig`.
- **Error handling?** Catch `CodexError` for Codex-specific issues.

## Navigation Links

- **Parent Directory**: [agents](../README.md) - Parent directory documentation
- **Core Module**: [core](../core/AGENTS.md) - Base classes and interfaces
- **Project Root**: ../../../../README.md - Main project documentation
