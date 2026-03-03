# Tests -- Technical Specification

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Functional Requirements

### FR-1: Core Functionality
- The module shall provide tests capabilities as described in the module docstring.

## Non-Functional Requirements

### NFR-1: Zero-Mock Testing
- All tests follow the Zero-Mock policy -- no unittest.mock, MagicMock, or monkeypatch.

### NFR-2: Explicit Failure
- All failures shall raise exceptions; no silent fallbacks or placeholder returns.

## Navigation

- **Source**: [src/codomyrmex/tests/](../../../../src/codomyrmex/tests/)
- **Extended README**: [README.md](readme.md)
- **AGENTS**: [AGENTS.md](AGENTS.md)
- **Parent**: [All Modules](../README.md)
