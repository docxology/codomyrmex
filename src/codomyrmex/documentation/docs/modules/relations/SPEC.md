# Relations -- Technical Specification

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Functional Requirements

### FR-1: Core Functionality
- The module shall provide relations capabilities as described in the module docstring.
- The module shall export 13 public symbols via `__all__`.

### FR-2: MCP Integration
- The module shall expose 1 MCP tools for agent consumption.

## Interface Contracts

### MCP Tool Signatures

- `relations_score_strength()`

## Non-Functional Requirements

### NFR-1: Zero-Mock Testing
- All tests follow the Zero-Mock policy -- no unittest.mock, MagicMock, or monkeypatch.

### NFR-2: Explicit Failure
- All failures shall raise exceptions; no silent fallbacks or placeholder returns.

## Navigation

- **Source**: [src/codomyrmex/relations/](../../../../src/codomyrmex/relations/)
- **Extended README**: [README.md](readme.md)
- **AGENTS**: [AGENTS.md](AGENTS.md)
- **Parent**: [All Modules](../README.md)
