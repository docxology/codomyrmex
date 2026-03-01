# Exceptions Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The `exceptions` package provides a comprehensive, hierarchical error handling system for the Codomyrmex ecosystem. It defines a base `CodomyrmexError` class and specialized exceptions for all major domains (AI, I/O, Git, Validation, CEREBRUM, etc.), ensuring consistent error reporting and handling across the codebase.

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
from codomyrmex.exceptions import FileOperationError, create_error_context

try:
    process_file("data.txt")
except FileOperationError as e:
    # Access structured context
    filepath = e.context.get("file_path")
    logger.error(f"Failed to process {filepath}: {e}")
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

## Navigation

- **Extended Docs**: [docs/modules/exceptions/](../../../docs/modules/exceptions/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
- **Related**: [Validation](../validation/README.md)
