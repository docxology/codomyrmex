# Personal AI Infrastructure -- Exceptions Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Exceptions module is the **error handling foundation** for the entire Codomyrmex ecosystem. It defines a single root class (`CodomyrmexError`) and a hierarchical tree of 60+ specialized exception classes organized across 12 source files. Every module in the project raises exceptions from this package, ensuring consistent error reporting, structured context propagation, and serialization support.

## PAI Capabilities

### Structured Error Handling

All exceptions carry structured context for debugging and logging:

```python
from codomyrmex.exceptions import FileOperationError, create_error_context

try:
    process_file("data.txt")
except FileOperationError as e:
    print(e.context)       # {"file_path": "data.txt"}
    print(e.to_dict())     # Serializable dict for logging/API responses
    print(e.error_code)    # "FileOperationError"
```

### Exception Chain Formatting

Walk and format chained exceptions for diagnostics:

```python
from codomyrmex.exceptions import format_exception_chain

try:
    risky_operation()
except Exception as e:
    print(format_exception_chain(e))
```

### Context Factory

Create filtered context dictionaries for exception construction:

```python
from codomyrmex.exceptions import create_error_context

ctx = create_error_context(file_path="/tmp/data.json", line_number=42, column=None)
# {"file_path": "/tmp/data.json", "line_number": 42}  (None values filtered)
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `CodomyrmexError` | Class | Root exception with message, context dict, error_code, and `to_dict()` |
| `create_error_context()` | Function | Factory for structured error context dicts (filters None values) |
| `format_exception_chain()` | Function | Walk and format `__cause__`/`__context__` chains |
| `ConfigurationError` | Class | Configuration and settings errors |
| `FileOperationError` | Class | File I/O errors with `file_path` context |
| `AIProviderError` | Class | AI/LLM provider failures |
| `CodeExecutionError` | Class | Runtime execution errors with exit_code, stdout, stderr |
| `GitOperationError` | Class | Git command failures with command and repo path context |
| `NetworkError` | Class | Network errors with URL and status_code context |
| `ValidationError` | Class | Data validation errors with field_name and rule context |
| `CerebrumError` | Class | Root for CEREBRUM cognitive system error hierarchy |
| `CircuitOpenError` | Class | Circuit breaker open (non-CodomyrmexError) |
| `BulkheadFullError` | Class | Bulkhead exhausted (non-CodomyrmexError) |

## PAI Algorithm Phase Mapping

| Phase | Exceptions Module Contribution |
|-------|-------------------------------|
| **OBSERVE** | Structured `context` dicts on every exception provide observability into failure modes |
| **PLAN** | Exception hierarchy informs error handling strategy during planning |
| **EXECUTE** | All tool and module executions raise typed exceptions for precise catch handling |
| **VERIFY** | `to_dict()` serialization enables systematic error verification and reporting |
| **LEARN** | `format_exception_chain()` captures causal chains for post-mortem analysis |

## Architecture Role

**Foundation Layer** -- This module is imported by every other Codomyrmex module. It has no upward dependencies and must remain stable. The only external import is `pathlib.Path` from the standard library.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) -- Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) -- Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
