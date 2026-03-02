# Agent Guidelines - Exceptions

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

The `exceptions` package is the centralized source for all error types in Codomyrmex. Agents should strictly use these exceptions instead of generic Python exceptions (like `RuntimeError` or `ValueError`) whenever possible to ensure proper error tracking and context propagation.

## Key Rules

1. **Inheritance**: All new exceptions MUST inherit from `CodomyrmexError` (or a subclass).
2. **Context**: Always provide a `context` dictionary when raising errors with dynamic data (e.g., `file_path`, `status_code`, `user_id`).
3. **Re-exports**: If you add a new exception file, you MUST re-export its classes in `__init__.py`.
4. **Granularity**: Use specific exceptions (`FileOperationError`) over generic ones (`CodomyrmexError`).

## Usage Patterns

### Raising Exceptions

```python
from codomyrmex.exceptions import ConfigurationError, AIProviderError

# Domain-specific context via named parameters
if not config_file.exists():
    raise ConfigurationError(
        "Config file missing",
        config_file=path,
        config_key="api_key"
    )

# Another example with AI Provider
raise AIProviderError(
    "Rate limit exceeded",
    provider_name="OpenAI",
    model_name="gpt-4o"
)
```

### Catching Exceptions

```python
from codomyrmex.exceptions import CodomyrmexError

try:
    execute_workflow()
except CodomyrmexError as e:
    # All Codomyrmex errors have a consistent interface
    log_error(e.message, e.context, e.error_code)
```

## Special Cases

- **CEREBRUM**: Use `codomyrmex.exceptions.cerebrum` for all cognitive/inference errors.
- **Circuit Breakers**: Use `CircuitOpenError` (inherits from `Exception`, not `CodomyrmexError`, as it's a control flow signal).

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Re-exports all exception classes |
| `base.py` | `CodomyrmexError` root class with `message`, `context`, `error_code`, `to_dict()` |
| `ai.py` | `AIProviderError`, `CodeGenerationError`, `ModelContextError` |
| `config.py` | `ConfigurationError`, `EnvironmentError`, `DependencyError` |
| `execution.py` | `CodeExecutionError`, `SandboxError`, `BuildError` |
| `git.py` | `GitOperationError`, `RepositoryError` |
| `network.py` | `NetworkError`, `APIError`, `ValidationError` |
| `orchestration.py` | `OrchestrationError`, `WorkflowError` |
| `io.py` | `FileOperationError`, `DirectoryError` |
| `cerebrum.py` | `CerebrumError`, `InferenceError` |
| `specialized.py` | `DatabaseError`, `CacheError`, `PluginError` |

## Operating Contracts

**DO:**
- Always inherit new exceptions from `CodomyrmexError` (or a domain subclass)
- Provide domain-specific `context` dict with named kwargs: `raise AIProviderError("msg", provider_name="X")`
- Use `from cause` when re-raising to preserve exception chains
- Re-export new exception classes in `__init__.py`

**DO NOT:**
- Raise bare `RuntimeError`, `ValueError`, or `Exception` — always use typed codomyrmex exceptions
- Suppress exceptions silently (`except: pass`) — log and re-raise or raise a specific error
- Use `CircuitOpenError` for domain errors — it is a control-flow signal only

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Direct Python import, raise/catch any exception class | TRUSTED |
| **Architect** | Read + Design | Exception hierarchy design, context propagation review | OBSERVED |
| **QATester** | Validation | Exception context validation, error code coverage testing | OBSERVED |
| **Researcher** | Read-only | Inspect exception types and structures for analysis | SAFE |

### Engineer Agent
**Use Cases**: Use typed exception classes for explicit error handling, raise `CodomyrmexError` subclasses during BUILD/EXECUTE phases.

### Architect Agent
**Use Cases**: Design error hierarchy, review exception granularity, ensure context propagation patterns are consistent.

### QATester Agent
**Use Cases**: Unit and integration test execution, exception context validation, error code coverage verification during VERIFY.

### Researcher Agent
**Use Cases**: Inspect exception structures to understand error patterns and domain boundaries.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
