# Exceptions Module

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The `exceptions` package provides a comprehensive, hierarchical error handling system for the Codomyrmex ecosystem. It defines a base `CodomyrmexError` class and specialized exceptions for all major domains (AI, I/O, Git, Validation, CEREBRUM, etc.), ensuring consistent error reporting and handling across the codebase.

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **ALL PHASES** | Raise and catch structured errors throughout the pipeline | Direct Python import |
| **VERIFY** | Validate error handling behavior and exception chains | Direct Python import |

PAI agents access this module via direct Python import through the MCP bridge. All agents import CodomyrmexError subclasses for structured error handling; the QATester validates exception chains during VERIFY phase.

## Key Components

### Base Exceptions (`base.py`)

- **`CodomyrmexError`** — The root exception class. All project exceptions inherit from this.
  - Attributes: `message`, `context` (dict), `error_code`.
  - Methods: `to_dict()` for serialization.
- **`format_exception_chain()`** — continued utility for formatting exception chains.
- **`create_error_context()`** — Utility for creating structured error contexts.

### Categories

The exceptions are organized into logical modules:

- **`config.py`** — `ConfigurationError`, `EnvironmentError`, `DependencyError`
- **`io.py`** — `FileOperationError`, `DirectoryError`
- **`ai.py`** — `AIProviderError`, `CodeGenerationError`, `ModelContextError`
- **`analysis.py`** — `StaticAnalysisError`, `SecurityAuditError`
- **`execution.py`** — `CodeExecutionError`, `SandboxError`, `BuildError`
- **`git.py`** — `GitOperationError`, `RepositoryError`
- **`network.py`** — `NetworkError`, `APIError`, `ValidationError`
- **`orchestration.py`** — `OrchestrationError`, `WorkflowError`
- **`viz.py`** — `VisualizationError`, `DocumentationError`
- **`cerebrum.py`** — Cognitive system errors (`CerebrumError`, `InferenceError`)
- **`specialized.py`** — Domain-specific errors (`DatabaseError`, `CacheError`, `PluginError`)

## Usage

```python
from codomyrmex.exceptions import FileOperationError, AIProviderError

# Raising with domain-specific context
try:
    raise AIProviderError("Connection failed", provider_name="Anthropic")
except AIProviderError as e:
    print(f"Provider: {e.context.get('provider_name')}")

# Chaining exceptions
try:
    try:
        raise FileOperationError("Missing file", file_path="config.json")
    except FileOperationError as cause:
        raise ConfigurationError("Load failed") from cause
except CodomyrmexError as e:
    from codomyrmex.exceptions import format_exception_chain
    print(format_exception_chain(e))
```

## Directory Structure

```text
exceptions/
├── __init__.py      # Re-exports all exceptions
├── base.py          # Root CodomyrmexError
├── config.py        # Config/Env errors
├── io.py            # File/Dir errors
├── ai.py            # AI/LLM errors
├── analysis.py      # Static analysis errors
├── execution.py     # Runtime/Sandbox errors
├── git.py           # VSC errors
├── network.py       # API/Net errors
├── orchestration.py # Workflow errors
├── viz.py           # Visualization errors
├── cerebrum.py      # Cognitive errors
└── specialized.py   # Misc domain errors
```

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/exceptions/ -v
```

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
- **Extended Docs**: [docs/modules/exceptions/](../../../docs/modules/exceptions/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Related**: [Validation](../validation/README.md)
