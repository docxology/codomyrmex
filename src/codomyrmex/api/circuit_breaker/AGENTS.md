# AI Agent Guidelines — api/circuit_breaker

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Implements the circuit breaker resilience pattern with retry policies and bulkhead concurrency limiting for protecting API calls against cascading failures.

## Key Components

| Component | Role |
|-----------|------|
| `CircuitState` | Enum: `CLOSED`, `OPEN`, `HALF_OPEN` |
| `CircuitStats` | Dataclass tracking `total_requests`, `failures`, `successes`, `last_failure_time` |
| `CircuitBreakerConfig` | Dataclass with `failure_threshold`, `recovery_timeout`, `half_open_max_calls` |
| `CircuitBreaker` | Context-manager-based circuit breaker with state machine (closed/open/half-open transitions) |
| `RetryPolicy` | Configurable retry with exponential backoff, jitter, and retryable exception filtering |
| `Bulkhead` | Semaphore-based concurrency limiter with `max_concurrent` and `max_wait` settings |
| `circuit_breaker` | Decorator wrapping a function with circuit breaker protection |
| `retry` | Decorator wrapping a function with retry policy |

## Operating Contracts

- `CircuitBreaker` is used as a context manager (`with cb:`) or via the `circuit_breaker` decorator.
- State transitions: CLOSED (tracking failures) -> OPEN (rejecting calls) -> HALF_OPEN (probing) -> CLOSED.
- `RetryPolicy.execute(func)` runs `func` with configurable retries and backoff.
- `Bulkhead` limits concurrent access; raises `BulkheadFullError` when the semaphore is exhausted and `max_wait` expires.
- All three patterns are independent and can be composed.

## Integration Points

- **Parent**: `api` module composes these patterns around HTTP client calls.
- **Consumers**: Any module making external or unreliable calls (cloud providers, LLM APIs, webhooks).
- **Composition**: `circuit_breaker(retry(fn))` is a common stacking pattern.

## Navigation

- **Parent**: [api/README.md](../README.md)
- **Sibling**: [SPEC.md](SPEC.md) | [README.md](README.md)
- **Root**: [../../../../README.md](../../../../README.md)
