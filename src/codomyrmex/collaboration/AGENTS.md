# Agent Guidelines - Collaboration

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Module Overview

Multi-agent collaboration, shared state, and coordination patterns.

## Key Classes

- **CollaborationSession** — Shared workspace for agents
- **MessageBus** — Inter-agent messaging
- **SharedState** — Synchronized state
- **TaskPool** — Distributed task allocation

## Agent Instructions

1. **Use sessions** — Create sessions for related work
2. **Message async** — Prefer async messaging
3. **Lock shared state** — Use locks for concurrent access
4. **Acknowledge tasks** — Confirm task completion
5. **Handle failures** — Implement task retry logic

## Common Patterns

```python
from codomyrmex.collaboration import (
    CollaborationSession, MessageBus, SharedState
)

# Create collaboration session
session = CollaborationSession("project_analysis")
session.add_agent("analyzer")
session.add_agent("validator")

# Shared state
state = SharedState()
state.set("progress", 0.5)
progress = state.get("progress")

# Inter-agent messaging
bus = MessageBus()
bus.subscribe("results", handle_result)
bus.publish("tasks", {"type": "analyze", "file": "main.py"})
```

## Testing Patterns

```python
# Verify session
session = CollaborationSession("test")
session.add_agent("a1")
assert "a1" in session.agents

# Verify shared state
state = SharedState()
state.set("key", "value")
assert state.get("key") == "value"
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
