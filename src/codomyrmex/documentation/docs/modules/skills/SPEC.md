# Skills -- Technical Specification

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Functional Requirements

### FR-1: Core Functionality
- The module shall provide skills capabilities as described in the module docstring.
- The module shall export 14 public symbols via `__all__`.

### FR-2: MCP Integration
- The module shall expose 7 MCP tools for agent consumption.

## Interface Contracts

### MCP Tool Signatures

- `skills_list()`
- `skills_get()`
- `skills_search()`
- `skills_sync()`
- `skills_add_custom()`
- `skills_get_categories()`
- `skills_get_upstream_status()`

## Non-Functional Requirements

### NFR-1: Zero-Mock Testing
- All tests follow the Zero-Mock policy -- no unittest.mock, MagicMock, or monkeypatch.

### NFR-2: Explicit Failure
- All failures shall raise exceptions; no silent fallbacks or placeholder returns.

## Navigation

- **Source**: [src/codomyrmex/skills/](../../../../src/codomyrmex/skills/)
- **Extended README**: [README.md](readme.md)
- **AGENTS**: [AGENTS.md](AGENTS.md)
- **Parent**: [All Modules](../README.md)
