# Exceptions Module -- Agent Coordination

## Purpose

The `exceptions` package is the centralized source for all error types in Codomyrmex. Agents must use these exceptions instead of generic Python exceptions (`RuntimeError`, `ValueError`, etc.) to ensure proper error tracking and context propagation across the system.

## Key Capabilities

- Hierarchical exception handling with a single root class
- Structured context propagation on every error
- JSON-serializable error representations for API and logging
- Domain-specific exception categories for precise error handling

## Key Rules for Agents

1. **Inheritance**: All new exceptions MUST inherit from `CodomyrmexError` (or a subclass).
2. **Context**: Always provide a `context` dictionary when raising errors with dynamic data (e.g., `file_path`, `status_code`).
3. **Re-exports**: If adding a new exception file, you MUST re-export its classes in `__init__.py`.
4. **Granularity**: Use specific exceptions (`FileOperationError`) over generic ones (`CodomyrmexError`).

## Agent Usage Patterns

### Raising Exceptions

```python
from codomyrmex.exceptions import ConfigurationError

if not config_file.exists():
    raise ConfigurationError(
        "Config file missing",
        config_file=str(path),
        expected_format="yaml"
    )
```

### Catching Exceptions

```python
from codomyrmex.exceptions import CodomyrmexError

try:
    execute_workflow()
except CodomyrmexError as e:
    log_error(e.message, e.context, e.error_code)
```

## Special Cases

- **CEREBRUM**: Use `codomyrmex.exceptions.cerebrum` for all cognitive/inference errors.
- **Circuit Breakers**: `CircuitOpenError` inherits from `Exception` (not `CodomyrmexError`) as it is a control flow signal.

## Integration Points

- **Source**: [src/codomyrmex/exceptions/](../../../src/codomyrmex/exceptions/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)

## Related Modules

- [Validation](../validation/AGENTS.md)
- [Events](../events/AGENTS.md)

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k exceptions -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
