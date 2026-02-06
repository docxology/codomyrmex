# Personal AI Infrastructure — Collaboration Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Collaboration module provides PAI integration for multi-agent coordination.

## PAI Capabilities

### Agent Communication

Enable agents to collaborate:

```python
from codomyrmex.collaboration import MessageBus, Channel

bus = MessageBus()
channel = bus.create_channel("code_review")

# Send message
channel.publish({"action": "review", "file": "main.py"})

# Receive messages
messages = channel.receive()
```

### Shared State

Share context between agents:

```python
from codomyrmex.collaboration import SharedContext

context = SharedContext()
context.set("current_task", "refactoring")

# Other agents can read
task = context.get("current_task")
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `MessageBus` | Inter-agent messaging |
| `SharedContext` | State sharing |
| `TaskQueue` | Work distribution |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
