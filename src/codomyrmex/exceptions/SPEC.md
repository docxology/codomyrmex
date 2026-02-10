# Exceptions - Functional Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

To provide a unified, hierarchical, and context-aware error handling system for the entire Codomyrmex application.

## Functional Requirements

1. **Unified Hierarchy**: All application errors descend from a single root (`CodomyrmexError`).
2. **Context Propagation**: Errors must carry structured data (`context` dict) for debugging and logging.
3. **Serialization**: Errors must be serializable to JSON (`to_dict()`) for API responses and logs.
4. **Categorization**: Errors must be grouped by domain (IO, AI, Config, etc.) for clean organization.
5. **Backward Compatibility**: The package must be a drop-in replacement for the old `exceptions.py`.

## Class Hierarchy (Simplified)

```text
CodomyrmexError
├── ConfigurationError
├── EnvironmentError
├── DependencyError
├── FileOperationError
├── AIProviderError
├── CodeExecutionError
├── GitOperationError
├── NetworkError
│   ├── APIError
│   └── TimeoutError
├── CerebrumError
│   ├── InferenceError
│   └── CaseError
└── [Domain Specific Errors...]
```

## API Surface

### `CodomyrmexError`

| Attribute | Type | Description |
| :--- | :--- | :--- |
| `message` | `str` | Human-readable error message |
| `context` | `dict` | Key-value pairs of debugging info |
| `error_code` | `str` | Unique code (default: ClassName) |
| `to_dict()` | `dict` | Returns serialized error representation |

### Utilities

- `format_exception_chain(e)`: Returns string dump of exception chain.
- `create_error_context(**kwargs)`: Helper to build context dicts filtering None values.

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md)
