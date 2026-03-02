# Reliability — Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Reliability primitives for MCP infrastructure: circuit breaker (cascading-failure prevention), token-bucket rate limiter (resource protection), and observability hooks (call tracking and metrics).

## Architecture

Three independent modules unified by `__init__.py`:

- **circuit_breaker**: State machine (CLOSED -> OPEN -> HALF_OPEN -> CLOSED) with configurable thresholds and async context manager support.
- **rate_limiter**: Token-bucket algorithm with global and per-tool buckets, lazy per-tool bucket creation.
- **observability**: Thread-safe Prometheus-style counters with singleton accessor.

## Key Classes

### `CircuitBreaker`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `record_success` | — | `None` | Record a successful call; in HALF_OPEN, close circuit after `success_threshold` |
| `record_failure` | — | `None` | Record a failure; open circuit after `failure_threshold` consecutive failures |
| `reset` | — | `None` | Manually reset to CLOSED |
| `execute` | `coro: Awaitable` | `Any` | Execute an awaitable within the circuit breaker |
| `__aenter__` / `__aexit__` | — | — | Async context manager that checks state on entry, records result on exit |

| Property | Type | Description |
|----------|------|-------------|
| `state` | `CircuitState` | Current state; auto-transitions OPEN to HALF_OPEN when `reset_timeout` elapses |
| `failure_count` | `int` | Consecutive failure counter |
| `metrics` | `dict` | Name, state, failure/success counts, last failure time |

### `CircuitBreakerConfig`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `failure_threshold` | `int` | 5 | Consecutive failures before opening |
| `reset_timeout` | `float` | 30.0 | Seconds in OPEN before probing |
| `half_open_max_calls` | `int` | 1 | Probe calls allowed in HALF_OPEN |
| `success_threshold` | `int` | 2 | Successes needed to close from HALF_OPEN |

### `RateLimiter`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `allow` | `tool_name: str` | `bool` | Check if request is permitted (consumes tokens) |
| `reset` | — | `None` | Reset all buckets to full |

| Property | Type | Description |
|----------|------|-------------|
| `metrics` | `dict` | Global and per-tool token counts, rates, burst sizes |

### `RateLimiterConfig`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `rate` | `float` | 50.0 | Tokens added per second |
| `burst` | `int` | 100 | Maximum bucket capacity |
| `per_tool_rate` | `dict[str, float]` | `{}` | Per-tool rate overrides |
| `per_tool_burst` | `dict[str, int]` | `{}` | Per-tool burst overrides |

### `MCPObservabilityHooks`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `on_tool_call_start` | `tool_name: str` | `float` | Returns start timestamp |
| `on_tool_call_end` | `tool_name, duration, error` | `None` | Records call count, duration, and optional error |
| `get_metrics` | — | `dict` | Global and per-tool counters (JSON-serializable) |
| `get_tool_metrics` | `tool_name: str` | `ToolMetrics | None` | Metrics for a specific tool |
| `get_metrics_json` | — | `str` | JSON string for MCP resource exposure |
| `reset` | — | `None` | Clear all counters |

## Dependencies

- **Internal**: `codomyrmex.logging_monitoring`
- **External**: Standard library only (`asyncio`, `time`, `threading`, `json`, `enum`, `dataclasses`)

## Constraints

- `CircuitBreaker` uses `asyncio.Lock` for async safety; not thread-safe across event loops.
- `MCPObservabilityHooks` uses `threading.Lock` for thread safety.
- Per-tool rate limiter buckets are created lazily on first `allow()` call.
- Zero-mock: real timing and counters only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `CircuitOpenError` raised when the circuit is OPEN and requests are rejected; includes `remaining` seconds.
- Rate limit exhaustion returns `False` from `allow()` rather than raising.
- All errors logged before propagation.
