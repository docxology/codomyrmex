# Concurrency Configuration

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Distributed locks, semaphores, and synchronization primitives. Provides local locks, Redis-backed distributed locks, read-write locks, and dead letter queues.

## Configuration Options

The concurrency module operates with sensible defaults and does not require environment variable configuration. Redis-backed locks require `redis` package (`uv sync --extra concurrency`). Local locks use threading primitives. Lock timeout and retry parameters are set per-lock.

## MCP Tools

This module exposes 2 MCP tool(s):

- `concurrency_lock_status`
- `concurrency_list_locks`

## PAI Integration

PAI agents invoke concurrency tools through the MCP bridge. Redis-backed locks require `redis` package (`uv sync --extra concurrency`). Local locks use threading primitives. Lock timeout and retry parameters are set per-lock.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep concurrency

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/concurrency/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
