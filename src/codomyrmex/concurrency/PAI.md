# Personal AI Infrastructure — Concurrency Module

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Concurrency module provides distributed locks, semaphores, async worker pools, and dead letter queues for safe parallel execution of AI agent tasks. It ensures that concurrent agent operations don't conflict and that failed tasks are captured for retry.

## PAI Capabilities

### Distributed Locking

```python
from codomyrmex.concurrency import LocalLock, LockManager

manager = LockManager()
manager.register_lock("file_edit:main.py", LocalLock("file_edit_main_py"))
with manager.get_lock("file_edit:main.py"):
    # Exclusive access to resource
    pass
```

### Async Worker Pool

```python
from codomyrmex.concurrency import AsyncWorkerPool, PoolStats, TaskResult

pool = AsyncWorkerPool(max_workers=4)
results: list[TaskResult] = await pool.map(analyze_files, file_list)
stats: PoolStats = pool.stats
```

### Semaphores and Dead Letter Queues

```python
from codomyrmex.concurrency import DeadLetterQueue, LocalSemaphore

sem = LocalSemaphore(value=3)
dlq = DeadLetterQueue()
with sem:
    try:
        run_agent_task()
    except Exception as exc:
        # Record failed tasks in the DLQ for retry/investigation
        dlq.add(operation="run_agent_task", error=str(exc))
```

## Key Exports

| Export | Type | Purpose |
| --- | --- | --- |
| `LocalLock` / `RedisLock` | Class | Cross-process (file) / distributed (Redis) resource locking |
| `LockManager` | Class | Lock lifecycle management |
| `LocalSemaphore` / `AsyncLocalSemaphore` | Class | Concurrency-limited resource access |
| `AsyncWorkerPool` | Class | Parallel async task execution |
| `PoolStats` | Class | Worker pool statistics |
| `TaskResult` | Class | Individual task outcome |
| `DeadLetterQueue` | Class | Failed task capture and retry |

## PAI Algorithm Phase Mapping

| Phase | Concurrency Contribution |
| --- | --- |
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
