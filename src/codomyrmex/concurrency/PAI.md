# Personal AI Infrastructure — Concurrency Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Concurrency module provides PAI integration for async operations and parallel execution.

## PAI Capabilities

### Parallel Execution

Run tasks in parallel:

```python
from codomyrmex.concurrency import gather, Semaphore

results = await gather([
    process_file(f) for f in files
])
```

### Rate Limiting

Control concurrency:

```python
from codomyrmex.concurrency import Semaphore

sem = Semaphore(10)  # Max 10 concurrent
async with sem:
    await make_api_call()
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `gather` | Parallel execution |
| `Semaphore` | Limit concurrency |
| `Lock` | Resource locking |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
