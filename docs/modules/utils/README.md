# utils

**Version**: v1.2.8 | **Status**: Active | **Last Updated**: April 2026

## Overview

Canonical **documentation** for the `codomyrmex.utils` module (implementation lives under `src/codomyrmex/utils/`). Covers shared helpers: JSON, hashing, subprocess utilities, script bases, and retry decorators.

## Retry: package vs `retry_sync`

| Surface | Import | Use when |
|--------|--------|----------|
| **Package `retry`** | `from codomyrmex.utils import retry` | Simple sync retries: `max_attempts`, `delay`, `backoff`, `exceptions`. |
| **`retry_sync` module** | `from codomyrmex.utils.retry_sync import retry, async_retry` | Jitter, delay caps, `RetryConfig`, and async retries. |

See [API_SPECIFICATION.md](API_SPECIFICATION.md) for signatures and examples.

## Key files here

- [API_SPECIFICATION.md](API_SPECIFICATION.md)
- [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
- [SPEC.md](SPEC.md), [PAI.md](PAI.md)

## Navigation

- **Parent**: [modules](../README.md)
- **Project root**: [../../../README.md](../../../README.md)
- **Source tree**: [src/codomyrmex/utils/README.md](../../../src/codomyrmex/utils/README.md)
