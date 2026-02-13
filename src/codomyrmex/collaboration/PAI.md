# Personal AI Infrastructure — Collaboration Module

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Collaboration module for Codomyrmex. This is an **Extended Layer** module.

## PAI Capabilities

```python
from codomyrmex.collaboration import TaskPriority, TaskStatus, Task, agents, communication, coordination
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `TaskPriority` | Class | Taskpriority |
| `TaskStatus` | Class | Taskstatus |
| `Task` | Class | Task |
| `TaskResult` | Class | Taskresult |
| `SwarmStatus` | Class | Swarmstatus |
| `AgentStatus` | Class | Agentstatus |
| `CollaborationError` | Class | Collaborationerror |
| `AgentNotFoundError` | Class | Agentnotfounderror |
| `AgentBusyError` | Class | Agentbusyerror |
| `TaskExecutionError` | Class | Taskexecutionerror |
| `TaskNotFoundError` | Class | Tasknotfounderror |
| `TaskDependencyError` | Class | Taskdependencyerror |
| `ConsensusError` | Class | Consensuserror |
| `ChannelError` | Class | Channelerror |
| `MessageDeliveryError` | Class | Messagedeliveryerror |

*Plus 22 additional exports.*


## PAI Algorithm Phase Mapping

| Phase | Collaboration Contribution |
|-------|------------------------------|
| **OBSERVE** | Data gathering and state inspection |
| **THINK** | Analysis and reasoning |
| **EXECUTE** | Execution and deployment |

## Architecture Role

**Extended Layer** — Part of the codomyrmex layered architecture.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
