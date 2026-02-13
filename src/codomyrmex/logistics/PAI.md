# Personal AI Infrastructure — Logistics Module

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Logistics Module for Codomyrmex This is a **Service Layer** module.

## PAI Capabilities

```python
from codomyrmex.logistics import WorkflowManager, TaskOrchestrator, ProjectManager, routing, optimization, resources
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `WorkflowManager` | Class | Workflowmanager |
| `TaskOrchestrator` | Class | Taskorchestrator |
| `ProjectManager` | Class | Projectmanager |
| `ResourceManager` | Class | Resourcemanager |
| `OrchestrationEngine` | Class | Orchestrationengine |
| `OrchestrationSession` | Class | Orchestrationsession |
| `Queue` | Class | Queue |
| `Job` | Class | Job |
| `JobScheduler` | Class | Jobscheduler |
| `ScheduleManager` | Class | Schedulemanager |
| `CronScheduler` | Class | Cronscheduler |
| `CronExpression` | Class | Cronexpression |
| `RecurringScheduler` | Class | Recurringscheduler |
| `RecurringSchedule` | Class | Recurringschedule |
| `TimezoneManager` | Class | Timezonemanager |

*Plus 5 additional exports.*


## PAI Algorithm Phase Mapping

| Phase | Logistics Contribution |
|-------|------------------------------|
| **PLAN** | Workflow planning and scheduling |

## Architecture Role

**Service Layer** — Part of the codomyrmex layered architecture.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
