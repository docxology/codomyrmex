# Concurrency

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Concurrency and synchronization module for Codomyrmex.

## Architecture Overview

```
concurrency/
    __init__.py              # Public API exports
    mcp_tools.py             # MCP tool definitions
```

## Key Exports

- **`BaseLock`**
- **`LocalLock`**
- **`BaseSemaphore`**
- **`LocalSemaphore`**
- **`AsyncLocalSemaphore`**
- **`RedisLock`**
- **`LockManager`**
- **`ReadWriteLock`**
- **`AsyncWorkerPool`**
- **`PoolStats`**
- **`TaskResult`**
- **`DeadLetterQueue`**
- **`cli_commands`**

## MCP Tools Reference

| Tool | Trust Level |
|------|-------------|
| `concurrency_pool_status` | Safe |
| `concurrency_list_locks` | Safe |

## Related Modules

See [All Modules](../README.md) for the complete module listing.

## Navigation

- **Source**: [src/codomyrmex/concurrency/](../../../../src/codomyrmex/concurrency/)
- **Parent**: [All Modules](../README.md)
