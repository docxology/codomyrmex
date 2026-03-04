# Llm -- Technical Specification

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Functional Requirements

### FR-1: Core Functionality
- The module shall provide llm capabilities as described in the module docstring.
- The module shall export 2 public symbols via `__all__`.

### FR-2: MCP Integration
- The module shall expose 4 MCP tools for agent consumption.

## Interface Contracts

### MCP Tool Signatures

- `generate_text()`
- `list_local_models()`
- `query_fabric_metadata()`
- `reason()`

## Non-Functional Requirements

### NFR-1: Zero-Mock Testing
- All tests follow the Zero-Mock policy -- no unittest.mock, MagicMock, or monkeypatch.

### NFR-2: Explicit Failure
- All failures shall raise exceptions; no silent fallbacks or placeholder returns.

## Navigation

- **Source**: [src/codomyrmex/llm/](../../../../src/codomyrmex/llm/)
- **Extended README**: [README.md](readme.md)
- **AGENTS**: [AGENTS.md](AGENTS.md)
- **Parent**: [All Modules](../README.md)
