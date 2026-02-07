# Coding Module — Agent Coordination

## Purpose

Coding Module.

## Key Capabilities

- Coding operations and management

## Agent Usage Patterns

```python
from codomyrmex.coding import *

# Agent uses coding capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/coding/](../../../src/codomyrmex/coding/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)


## Key Components

- **`ExecutionTimeoutError`** — Raised when code execution exceeds time limit.
- **`MemoryLimitError`** — Raised when code execution exceeds memory limit.
- **`SandboxSecurityError`** — Raised when code violates sandbox security policies.
- **`SandboxResourceError`** — Raised when sandbox resource allocation fails.
- **`DebuggerError`** — Raised when debugging operations fail.

### Submodules

- `analysis` — Analysis
- `debugging` — Debugging
- `execution` — Execution
- `generation` — Generation
- `monitoring` — Monitoring
- `refactoring` — Refactoring
- `review` — Review
- `sandbox` — Sandbox

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k coding -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
