# Personal AI Infrastructure — Events Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Events module provides a publish/subscribe (pub/sub) event system for inter-module and inter-agent communication. It enables decoupled, event-driven workflows where modules emit events that other modules react to without direct coupling.

## PAI Capabilities

### Event Bus

```python
from codomyrmex.events import EventBus

bus = EventBus()

# Subscribe to events
@bus.on("code_committed")
async def on_commit(event):
    print(f"New commit: {event.data['hash']}")

# Emit events
bus.emit("code_committed", data={"hash": "abc123", "author": "pai"})
```

### Event-Driven Agent Workflows

- Trigger agent actions on codebase changes
- Chain agent responses through event cascades
- Decouple module interactions for flexible orchestration

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `EventBus` | Class | Pub/sub event system |
| Event types | Various | Typed event definitions |

## PAI Algorithm Phase Mapping

| Phase | Events Contribution |
|-------|----------------------|
| **PLAN** | Define event-driven workflow triggers |
| **EXECUTE** | Emit and consume events during workflow execution |
| **LEARN** | Event history provides audit trail of system activity |

## Architecture Role

**Foundation Layer** — Cross-cutting event infrastructure consumed by `orchestrator/`, `agents/`, `git_operations/`, and the PAI dashboard.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
