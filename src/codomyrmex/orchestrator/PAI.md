# Personal AI Infrastructure — Orchestrator Module

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Script Orchestrator Module This is a **Service Layer** module.

## PAI Capabilities

```python
from codomyrmex.orchestrator import Workflow, Task, TaskStatus, scheduler, templates, state
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `scheduler` | Function/Constant | Scheduler |
| `templates` | Function/Constant | Templates |
| `state` | Function/Constant | State |
| `triggers` | Function/Constant | Triggers |
| `pipelines` | Function/Constant | Pipelines |
| `run_orchestrator` | Function/Constant | Run orchestrator |
| `load_config` | Function/Constant | Load config |
| `get_script_config` | Function/Constant | Get script config |
| `discover_scripts` | Function/Constant | Discover scripts |
| `Workflow` | Class | Workflow |
| `Task` | Class | Task |
| `TaskStatus` | Class | Taskstatus |
| `TaskResult` | Class | Taskresult |
| `RetryPolicy` | Class | Retrypolicy |

*Plus 55 additional exports.*


## PAI Algorithm Phase Mapping

| Phase | Orchestrator Contribution |
|-------|------------------------------|
| **OBSERVE** | Data gathering and state inspection |
| **PLAN** | Workflow planning and scheduling |
| **BUILD** | Artifact creation and code generation |
| **EXECUTE** | Execution and deployment |
| **LEARN** | Learning and knowledge capture |

## Architecture Role

**Service Layer** — Part of the codomyrmex layered architecture.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
