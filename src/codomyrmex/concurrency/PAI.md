# Personal AI Infrastructure — Concurrency Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Concurrency module provides distributed locks, semaphores, async worker pools, and dead letter queues for safe parallel execution of AI agent tasks. It ensures that concurrent agent operations don't conflict and that failed tasks are captured for retry.

## PAI Capabilities

### Distributed Locking

```python
from codomyrmex.concurrency import DistributedLock, LockManager

manager = LockManager()
async with manager.acquire("file_edit:main.py"):
    # Exclusive access to resource
    pass
```

### Async Worker Pool

```python
from codomyrmex.concurrency import AsyncWorkerPool, PoolStats, TaskResult

pool = AsyncWorkerPool(max_workers=4)
results: list[TaskResult] = await pool.map(analyze_files, file_list)
stats: PoolStats = pool.stats()
```

### Semaphores and Dead Letter Queues

```python
from codomyrmex.concurrency import Semaphore, DeadLetterQueue

sem = Semaphore(max_concurrent=3)
dlq = DeadLetterQueue()
# Failed tasks automatically routed to DLQ for retry/investigation
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `DistributedLock` | Class | Cross-process resource locking |
| `LockManager` | Class | Lock lifecycle management |
| `Semaphore` | Class | Concurrency-limited resource access |
| `AsyncWorkerPool` | Class | Parallel async task execution |
| `PoolStats` | Class | Worker pool statistics |
| `TaskResult` | Class | Individual task outcome |
| `DeadLetterQueue` | Class | Failed task capture and retry |

## PAI Algorithm Phase Mapping

| Phase | Concurrency Contribution |
|-------|--------------------------|
| **PLAN** | Configure parallelism level for workflow steps |
| **EXECUTE** | Run multiple agent tasks in parallel with resource locking |
| **VERIFY** | Check DLQ for failed tasks; inspect pool stats |

## Architecture Role

**Foundation Layer** — Cross-cutting concurrency primitives consumed by `orchestrator/`, `agents/` (AgentPool), and `ci_cd_automation/`.

## MCP Tools

This module does not expose MCP tools directly. Access its capabilities via:
- Direct Python import: `from codomyrmex.concurrency import ...`
- CLI: `codomyrmex concurrency <command>`

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
