# Security -- Technical Specification

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Functional Requirements

### FR-1: Core Functionality
- The module shall provide security capabilities as described in the module docstring.
- The module shall export 1 public symbols via `__all__`.

### FR-2: MCP Integration
- The module shall expose 3 MCP tools for agent consumption.

## Interface Contracts

### MCP Tool Signatures

- `scan_vulnerabilities()`
- `scan_secrets()`
- `audit_code_security()`

## Non-Functional Requirements

### NFR-1: Zero-Mock Testing
- All tests follow the Zero-Mock policy -- no unittest.mock, MagicMock, or monkeypatch.

### NFR-2: Explicit Failure
- All failures shall raise exceptions; no silent fallbacks or placeholder returns.

## Navigation

- **Source**: [src/codomyrmex/security/](../../../../security/)
- **Extended README**: [README.md](readme.md)
- **AGENTS**: [AGENTS.md](AGENTS.md)
- **Parent**: [All Modules](../README.md)
