# Graph Rag -- Technical Specification

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Functional Requirements

### FR-1: Core Functionality
- The module shall provide graph rag capabilities as described in the module docstring.
- The module shall export 8 public symbols via `__all__`.

## Non-Functional Requirements

### NFR-1: Zero-Mock Testing
- All tests follow the Zero-Mock policy -- no unittest.mock, MagicMock, or monkeypatch.

### NFR-2: Explicit Failure
- All failures shall raise exceptions; no silent fallbacks or placeholder returns.

## Navigation

- **Source**: [src/codomyrmex/graph_rag/](../../../../graph_rag/)
- **Extended README**: [README.md](readme.md)
- **AGENTS**: [AGENTS.md](AGENTS.md)
- **Parent**: [All Modules](../README.md)
