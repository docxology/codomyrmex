# Email -- Technical Specification

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Functional Requirements

### FR-1: Core Functionality
- The module shall provide email capabilities as described in the module docstring.
- The module shall export 15 public symbols via `__all__`.

### FR-2: MCP Integration
- The module shall expose 8 MCP tools for agent consumption.

## Interface Contracts

### MCP Tool Signatures

- `agentmail_send_message()`
- `agentmail_list_messages()`
- `agentmail_get_message()`
- `agentmail_reply_to_message()`
- `agentmail_list_inboxes()`
- `agentmail_create_inbox()`
- `agentmail_list_threads()`
- `agentmail_create_webhook()`

## Non-Functional Requirements

### NFR-1: Zero-Mock Testing
- All tests follow the Zero-Mock policy -- no unittest.mock, MagicMock, or monkeypatch.

### NFR-2: Explicit Failure
- All failures shall raise exceptions; no silent fallbacks or placeholder returns.

## Navigation

- **Source**: [src/codomyrmex/email/](../../../../email/)
- **Extended README**: [README.md](readme.md)
- **AGENTS**: [AGENTS.md](AGENTS.md)
- **Parent**: [All Modules](../README.md)
