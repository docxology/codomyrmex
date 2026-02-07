# Collaboration Module — Agent Coordination

## Purpose

Collaboration module for Codomyrmex.

## Key Capabilities

- Collaboration operations and management

## Agent Usage Patterns

```python
from codomyrmex.collaboration import *

# Agent uses collaboration capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/collaboration/](../../../src/codomyrmex/collaboration/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)


## Key Components

- **`CollaborationError`** — Base exception for all collaboration module errors.
- **`AgentNotFoundError`** — Raised when an agent cannot be found in the registry.
- **`AgentBusyError`** — Raised when an agent is busy and cannot accept new tasks.
- **`TaskExecutionError`** — Raised when a task fails to execute.
- **`TaskNotFoundError`** — Raised when a task cannot be found.

### Submodules

- `agents` — Agents
- `communication` — Communication
- `coordination` — Coordination
- `protocols` — Protocols

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k collaboration -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
