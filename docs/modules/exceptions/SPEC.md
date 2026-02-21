# Exceptions -- Functional Specification

**Module**: `codomyrmex.exceptions`
**Version**: v1.0.0
**Status**: Active

## 1. Overview

The exceptions package provides a unified, hierarchical, and context-aware error handling system for the entire Codomyrmex application. All application errors descend from a single root (`CodomyrmexError`) and carry structured metadata for debugging, logging, and API serialization.

## 2. Architecture

### Class Hierarchy

```text
CodomyrmexError
  +-- ConfigurationError
  +-- EnvironmentError
  +-- DependencyError
  +-- FileOperationError
  +-- DirectoryError
  +-- AIProviderError
  +-- CodeGenerationError
  +-- CodeEditingError
  +-- ModelContextError
  +-- StaticAnalysisError
  +-- PatternMatchingError
  +-- SecurityAuditError
  +-- CodeExecutionError
  +-- SandboxError
  +-- ContainerError
  +-- BuildError
  +-- SynthesisError
  +-- GitOperationError
  +-- RepositoryError
  +-- NetworkError
  |     +-- APIError
  |     +-- TimeoutError
  +-- ValidationError
  +-- SchemaError
  +-- OrchestrationError
  +-- WorkflowError
  +-- ProjectManagementError
  +-- TaskExecutionError
  +-- VisualizationError
  +-- PlottingError
  +-- DocumentationError
  +-- APIDocumentationError
  +-- CerebrumError
  |     +-- CaseError
  |     +-- InferenceError
  |     +-- ModelError
  +-- [Specialized domain errors...]
```

### Source Files

- `base.py` -- Root exception and utility functions
- `config.py` -- Configuration, environment, dependency errors
- `io.py` -- File and directory operation errors
- `ai.py` -- AI provider and code generation errors
- `analysis.py` -- Static analysis and security audit errors
- `execution.py` -- Runtime, sandbox, container, build errors
- `git.py` -- Git and repository errors
- `network.py` -- Network, API, validation errors
- `orchestration.py` -- Workflow and project management errors
- `viz.py` -- Visualization and documentation errors
- `cerebrum.py` -- Cognitive system and inference errors
- `specialized.py` -- Miscellaneous domain-specific errors

## 3. Dependencies

The exceptions package has no external dependencies beyond the Python standard library. See `src/codomyrmex/exceptions/__init__.py` for the full list of re-exported classes.

## 4. Public API

### `CodomyrmexError`

| Attribute | Type | Description |
| :--- | :--- | :--- |
| `message` | `str` | Human-readable error message |
| `context` | `dict` | Key-value pairs of debugging info |
| `error_code` | `str` | Unique code (default: class name) |
| `to_dict()` | `dict` | Returns serialized error representation |

### Utilities

- `format_exception_chain(e)` -- Returns formatted string dump of exception chain.
- `create_error_context(**kwargs)` -- Helper to build context dicts, filtering `None` values.

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k exceptions -v
```

## References

- [README.md](README.md) -- Human-readable documentation
- [AGENTS.md](AGENTS.md) -- Agent coordination guide
- [Source Code](../../../src/codomyrmex/exceptions/)
