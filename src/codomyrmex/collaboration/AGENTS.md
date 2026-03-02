# Agent Guidelines - Collaboration

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Multi-agent collaboration, shared state, and coordination patterns.

## Key Classes

- **CollaborationSession** — Shared workspace for agents
- **MessageBus** — Inter-agent messaging
- **SharedState** — Synchronized state
- **TaskPool** — Distributed task allocation

## MCP Tools Available

All tools are auto-discovered via `@mcp_tool` decorators and exposed through the MCP bridge.

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `swarm_submit_task` | Submit a task to the agent swarm for distributed execution | Safe |
| `pool_status` | Get the current status of the collaboration swarm pool and protocols | Safe |
| `list_agents` | List available agent capabilities and coordination protocols | Safe |

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

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | `swarm_submit_task`, `pool_status`, `list_agents`; full multi-agent coordination | TRUSTED |
| **Architect** | Read + Design | `pool_status`, `list_agents`; agent pool design, swarm architecture review | OBSERVED |
| **QATester** | Validation | `pool_status`, `list_agents`; agent availability verification, swarm health checks | OBSERVED |

### Engineer Agent
**Use Cases**: Submitting tasks to agent swarm during EXECUTE, monitoring pool status, coordinating multi-agent workflows.

### Architect Agent
**Use Cases**: Designing agent pool configurations, reviewing swarm task distribution, planning collaborative workflows.

### QATester Agent
**Use Cases**: Verifying agent pool health during VERIFY, confirming task submission and completion.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
