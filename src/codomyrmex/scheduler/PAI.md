# Personal AI Infrastructure — Scheduler Module

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Scheduler Module This is an **Extended Layer** module.

## PAI Capabilities

```python
from codomyrmex.scheduler import Scheduler, Job, JobStatus, every, at, cron
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `Scheduler` | Class | Scheduler |
| `Job` | Class | Job |
| `JobStatus` | Class | Jobstatus |
| `Trigger` | Class | Trigger |
| `TriggerType` | Class | Triggertype |
| `OnceTrigger` | Class | Oncetrigger |
| `IntervalTrigger` | Class | Intervaltrigger |
| `CronTrigger` | Class | Crontrigger |
| `every` | Function/Constant | Every |
| `at` | Function/Constant | At |
| `cron` | Function/Constant | Cron |
| `DependencyScheduler` | Class | Dependencyscheduler |
| `PersistentScheduler` | Class | Persistentscheduler |
| `JobPipeline` | Class | Jobpipeline |
| `ScheduledRecurrence` | Class | Scheduledrecurrence |

*Plus 1 additional exports.*


## PAI Algorithm Phase Mapping

| Phase | Scheduler Contribution |
|-------|------------------------------|
| **OBSERVE** | Data gathering and state inspection |
| **PLAN** | Workflow planning and scheduling |

## Architecture Role

**Extended Layer** — Part of the codomyrmex layered architecture.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
