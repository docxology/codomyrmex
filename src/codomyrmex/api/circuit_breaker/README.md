# circuit_breaker

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Resilience patterns for API calls including circuit breaker, retry with backoff, and bulkhead isolation. The `CircuitBreaker` class implements the standard closed/open/half-open state machine with configurable failure thresholds, error-rate monitoring, and timed recovery. Works as a context manager, a standalone recorder, or a function decorator. Complemented by `RetryPolicy` for configurable exponential backoff with jitter and `Bulkhead` for limiting concurrent executions to prevent resource exhaustion.

## Key Exports

- **`CircuitState`** -- Enum of circuit breaker states (closed, open, half_open)
- **`CircuitStats`** -- Dataclass tracking success/failure counts, consecutive failures, latency totals, error rate, and average latency
- **`CircuitBreakerConfig`** -- Configuration dataclass with failure threshold, success threshold for half-open recovery, reset timeout, half-open max calls, and optional error-rate threshold
- **`CircuitBreaker`** -- Thread-safe circuit breaker with state transitions, request gating, context manager support (`with breaker:`), and manual record/reset methods
- **`RetryPolicy`** -- Configurable retry policy with exponential backoff, jitter, max delay cap, and exception-type filtering
- **`Bulkhead`** -- Concurrency limiter using semaphores with optional queue and timeout, usable as a context manager
- **`CircuitOpenError`** -- Exception raised when a request is rejected by an open circuit (imported from `codomyrmex.exceptions`)
- **`BulkheadFullError`** -- Exception raised when a bulkhead has no available slots (imported from `codomyrmex.exceptions`)
- **`circuit_breaker()`** -- Decorator that wraps a function with a `CircuitBreaker`; exposes the breaker instance via `func.circuit_breaker`
- **`retry()`** -- Decorator that wraps a function with `RetryPolicy` for automatic retry on failure

## Directory Contents

- `__init__.py` - All resilience logic: circuit breaker state machine, retry policy, bulkhead pattern, decorators
- `README.md` - This file
- `AGENTS.md` - Agent integration notes
- `PAI.md` - PAI-specific documentation
- `SPEC.md` - Module specification
- `py.typed` - PEP 561 type-checking marker

## Navigation

- **Parent Module**: [api](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
