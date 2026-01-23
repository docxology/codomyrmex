# Codomyrmex Agents — src/codomyrmex/agents/gemini

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Google Gemini CLI integration module providing a client interface for Google's Gemini models. This module enables interaction with Gemini for code generation, analysis, and multi-modal tasks within the Codomyrmex agent framework.

## Active Components

- `gemini_client.py` - Main Gemini client implementation
- `gemini_integration.py` - Integration adapter for the agent framework
- `__init__.py` - Module exports
- `README.md` - Module documentation
- `SPEC.md` - Specification document

## Key Classes

### Client
- **`GeminiClient`** - Primary client for interacting with Google Gemini
  - Handles authentication and API/CLI communication
  - Supports chat sessions with save/resume functionality
  - Manages conversation context and history
  - Provides multi-modal capabilities

### Integration
- **`GeminiIntegrationAdapter`** - Adapter implementing the core `AgentIntegrationAdapter` interface
  - Bridges Gemini client with the standardized agent framework
  - Translates between `AgentRequest`/`AgentResponse` and Gemini-specific formats
  - Reports multi-modal capabilities for orchestration

## Operating Contracts

- Requires valid Google Cloud credentials or Gemini API key.
- Follows the `AgentInterface` contract from `core` module.
- Errors are raised as `GeminiError` exceptions (defined in `core.exceptions`).
- Supports chat session persistence for multi-turn conversations.
- CLI handlers support save, resume, and list operations for chat sessions.

## Signposting

- **Direct usage?** Use `GeminiClient` for low-level control.
- **Framework integration?** Use `GeminiIntegrationAdapter` for standardized access.
- **Chat persistence?** Use chat save/resume methods for session management.
- **Error handling?** Catch `GeminiError` for Gemini-specific issues.

## Navigation Links

- **Parent Directory**: [agents](../README.md) - Parent directory documentation
- **Core Module**: [core](../core/AGENTS.md) - Base classes and interfaces
- **CLI Handlers**: [cli](../cli/AGENTS.md) - CLI command handlers
- **Project Root**: ../../../../README.md - Main project documentation
