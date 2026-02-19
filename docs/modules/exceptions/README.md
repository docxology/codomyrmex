# Exceptions Module Documentation

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

The `exceptions` package provides a comprehensive, hierarchical error handling system for the Codomyrmex ecosystem. All project exceptions inherit from a single root class (`CodomyrmexError`), ensuring consistent error reporting, structured context propagation, and JSON-serializable error representations across the entire codebase.

## Key Features

- **Unified hierarchy** rooted at `CodomyrmexError` for consistent catch-all handling
- **Structured context** dictionaries attached to every error for debugging and logging
- **JSON serialization** via `to_dict()` for API responses and structured log output
- **Domain-specific categories** covering AI, I/O, Git, networking, orchestration, and more

## Installation

```bash
uv pip install codomyrmex
```

## Quick Start

```python
from codomyrmex.exceptions import FileOperationError, create_error_context

try:
    process_file("data.txt")
except FileOperationError as e:
    # Access structured context
    filepath = e.context.get("file_path")
    logger.error(f"Failed to process {filepath}: {e}")
```

## Exception Categories

| Module | Key Exceptions | Domain |
|--------|---------------|--------|
| `base.py` | `CodomyrmexError` | Root exception, utilities |
| `config.py` | `ConfigurationError`, `EnvironmentError`, `DependencyError` | Configuration and setup |
| `io.py` | `FileOperationError`, `DirectoryError` | File and directory operations |
| `ai.py` | `AIProviderError`, `CodeGenerationError`, `ModelContextError` | AI/LLM integration |
| `analysis.py` | `StaticAnalysisError`, `SecurityAuditError` | Code analysis |
| `execution.py` | `CodeExecutionError`, `SandboxError`, `BuildError` | Runtime and build |
| `git.py` | `GitOperationError`, `RepositoryError` | Version control |
| `network.py` | `NetworkError`, `APIError`, `ValidationError` | Networking and validation |
| `orchestration.py` | `OrchestrationError`, `WorkflowError` | Workflow management |
| `viz.py` | `VisualizationError`, `DocumentationError` | Visualization and docs |
| `cerebrum.py` | `CerebrumError`, `InferenceError`, `CaseError` | Cognitive system |
| `specialized.py` | `DatabaseError`, `CacheError`, `PluginError` | Miscellaneous domains |

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |

## Related Modules

- [Validation](../validation/README.md)
- [Logging & Monitoring](../logging_monitoring/README.md)
- [Events](../events/README.md)

## Navigation

- **Source**: [src/codomyrmex/exceptions/](../../../src/codomyrmex/exceptions/)
- **Parent**: [Modules](../README.md)

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k exceptions -v
```
