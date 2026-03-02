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
from codomyrmex.exceptions import ConfigurationError

if not config_file.exists():
    raise ConfigurationError(
        "Config file missing",
        config_file=str(path),  # Automatically added to context
        expected_format="yaml"
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

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Direct Python import, class instantiation, full API access | TRUSTED |
| **Architect** | Read + Design | API review, interface design, dependency analysis | OBSERVED |
| **QATester** | Validation | Integration testing via pytest, output validation | OBSERVED |

### Engineer Agent
**Use Cases**: Use typed exception classes for explicit error handling, raise CodomyrmexError subclasses during BUILD/EXECUTE phases

### Architect Agent
**Use Cases**: Design error hierarchy, review exception granularity, ensure context propagation patterns

### QATester Agent
**Use Cases**: Unit and integration test execution, exception context validation, error code coverage verification

## Navigation

- [README](README.md) | [SPEC](SPEC.md)
