# Plugin System -- Technical Specification

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Functional Requirements

### FR-1: Core Functionality
- The module shall provide plugin system capabilities as described in the module docstring.

### FR-2: MCP Integration
- The module shall expose 2 MCP tools for agent consumption.

## Interface Contracts

### MCP Tool Signatures

- `plugin_scan_entry_points()`
- `plugin_resolve_dependencies()`

## Non-Functional Requirements

### NFR-1: Zero-Mock Testing
- All tests follow the Zero-Mock policy -- no unittest.mock, MagicMock, or monkeypatch.

### NFR-2: Explicit Failure
- All failures shall raise exceptions; no silent fallbacks or placeholder returns.

## Navigation

- **Source**: [src/codomyrmex/plugin_system/](../../../../plugin_system/)
- **Extended README**: [README.md](readme.md)
- **AGENTS**: [AGENTS.md](AGENTS.md)
- **Parent**: [All Modules](../README.md)
