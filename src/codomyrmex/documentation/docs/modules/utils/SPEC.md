# Utils -- Technical Specification

**Version**: v1.2.8 | **Status**: Active | **Last Updated**: April 2026

## Functional Requirements

### FR-1: Core Functionality
- The module shall provide utils capabilities as described in the module docstring.
- The module shall export 44 public symbols via `__all__` (includes `retry`, `RetryConfig`, `async_retry`; sync/async retry implementation lives in `retry_sync.py`).

### FR-2: Retry documentation
- Published API docs ([api_specification.md](api_specification.md)) shall describe both package `retry` and `retry_sync` surfaces without implying a `utils/retry.py` submodule.

## Non-Functional Requirements

### NFR-1: Zero-Mock Testing
- All tests follow the Zero-Mock policy -- no unittest.mock, MagicMock, or monkeypatch.

### NFR-2: Explicit Failure
- All failures shall raise exceptions; no silent fallbacks or placeholder returns.

## Navigation

- **Source**: [src/codomyrmex/utils/](../../../../utils/)
- **Extended README**: [README.md](readme.md)
- **AGENTS**: [AGENTS.md](AGENTS.md)
- **Parent**: [All Modules](../README.md)
