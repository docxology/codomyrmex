# Ide -- Technical Specification

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Functional Requirements

### FR-1: Core Functionality
- The module shall provide ide capabilities as described in the module docstring.
- The module shall export 14 public symbols via `__all__`.

### FR-2: MCP Integration
- The module shall expose 2 MCP tools for agent consumption.

## Interface Contracts

### MCP Tool Signatures

- `ide_get_active_file()`
- `ide_list_tools()`

## Non-Functional Requirements

### NFR-1: Zero-Mock Testing
- All tests follow the Zero-Mock policy -- no unittest.mock, MagicMock, or monkeypatch.

### NFR-2: Explicit Failure
- All failures shall raise exceptions; no silent fallbacks or placeholder returns.

## Navigation

- **Source**: [src/codomyrmex/ide/](../../../../src/codomyrmex/ide/)
- **Extended README**: [README.md](readme.md)
- **AGENTS**: [AGENTS.md](AGENTS.md)
- **Parent**: [All Modules](../README.md)
