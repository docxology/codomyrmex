# Codomyrmex Agents — src/codomyrmex/model_context_protocol/reliability

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides reliability primitives for MCP tool execution and transport: circuit breaking to prevent cascading failures, token-bucket rate limiting with per-tool overrides, and Prometheus-style observability hooks for tracking call counts, durations, and error rates.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `circuit_breaker.py` | `CircuitBreaker` | Async-safe circuit breaker with CLOSED/OPEN/HALF_OPEN states; usable as async context manager or via `execute()` |
| `circuit_breaker.py` | `CircuitBreakerConfig` | Dataclass: `failure_threshold`, `reset_timeout`, `half_open_max_calls`, `success_threshold` |
| `circuit_breaker.py` | `CircuitState` | Enum: CLOSED, OPEN, HALF_OPEN |
| `circuit_breaker.py` | `CircuitOpenError` | Raised when circuit is OPEN; includes `remaining` seconds until retry |
| `circuit_breaker.py` | `get_circuit_breaker()` | Async factory returning named circuit breaker from global registry |
| `circuit_breaker.py` | `get_all_circuit_metrics()` | Returns metrics for all registered circuit breakers |
| `circuit_breaker.py` | `reset_all_circuits()` | Resets all circuits to CLOSED |
| `rate_limiter.py` | `RateLimiter` | Token-bucket rate limiter with global and per-tool buckets |
| `rate_limiter.py` | `RateLimiterConfig` | Dataclass: `rate` (tokens/s), `burst`, `per_tool_rate`, `per_tool_burst` |
| `observability.py` | `MCPObservabilityHooks` | Thread-safe Prometheus-style counters for tool call total, duration, and errors |
| `observability.py` | `ToolMetrics` | Per-tool metrics: calls, errors, total_duration, last_call_time |
| `observability.py` | `get_mcp_observability_hooks()` | Returns global singleton instance |

## Operating Contracts

- `CircuitBreaker` auto-transitions from OPEN to HALF_OPEN when `reset_timeout` elapses (checked on property access).
- In HALF_OPEN, only `half_open_max_calls` probe requests are allowed; `success_threshold` successes close the circuit.
- `RateLimiter.allow()` checks the per-tool bucket first (if configured), then the global bucket; returns `False` if either is exhausted.
- `MCPObservabilityHooks` is thread-safe via `threading.Lock`; metrics are JSON-serializable.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.logging_monitoring` (structured logging)
- **Used by**: `model_context_protocol.transport.server` (uses `RateLimiter` for per-request rate limiting in `_call_tool`)

## Navigation

- **Parent**: [model_context_protocol](../README.md)
- **Root**: [Root](../../../../README.md)
