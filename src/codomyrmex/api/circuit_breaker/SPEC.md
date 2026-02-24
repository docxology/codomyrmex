# Technical Specification - Circuit Breaker

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Module**: `codomyrmex.api.circuit_breaker`  
**Last Updated**: 2026-01-29

## 1. Purpose

Resilience patterns including retry, circuit breaker, and bulkhead

## 2. Architecture

### 2.1 Components

```
circuit_breaker/
├── __init__.py          # Module exports
├── README.md            # Documentation
├── AGENTS.md            # Agent guidelines
├── SPEC.md              # This file
├── PAI.md               # Personal AI context
└── core.py              # Core implementation
```

### 2.2 Dependencies

- Python 3.10+
- Parent module: `api`

## 3. Interfaces

### 3.1 Public API

```python
# Primary exports from codomyrmex.api.circuit_breaker
from codomyrmex.api.circuit_breaker import (
    # Enums
    CircuitState,            # Enum: CLOSED (normal), OPEN (fail-fast), HALF_OPEN (testing recovery)
    # Data classes
    CircuitStats,            # Stats: success_count, failure_count, consecutive_failures, error_rate, avg_latency_ms
    CircuitBreakerConfig,    # Config: failure_threshold, success_threshold, reset_timeout_s, half_open_max_calls
    # Classes
    CircuitBreaker,          # Core circuit breaker with context manager and state machine
    RetryPolicy,             # Configurable retry with exponential backoff and jitter
    Bulkhead,                # Concurrency limiter using semaphores (context manager)
    # Exceptions (from codomyrmex.exceptions)
    CircuitOpenError,        # Raised when circuit is open and request is rejected
    BulkheadFullError,       # Raised when bulkhead has no available slots
    # Decorators
    circuit_breaker,         # Decorator: @circuit_breaker(name="api", failure_threshold=3)
    retry,                   # Decorator: @retry(max_retries=3, backoff_base=0.1)
)

# Key class signatures:
class CircuitBreaker:
    def __init__(self, name: str = "default", config: CircuitBreakerConfig | None = None): ...
    def allow_request(self) -> bool: ...
    def record_success(self, latency_ms: float = 0.0) -> None: ...
    def record_failure(self, latency_ms: float = 0.0) -> None: ...
    def reset(self) -> None: ...
    def __enter__(self) -> CircuitBreaker: ...   # Raises CircuitOpenError if open
    def __exit__(self, exc_type, exc_val, exc_tb) -> None: ...

class RetryPolicy:
    def __init__(self, max_retries: int = 3, backoff_base: float = 0.1, backoff_multiplier: float = 2.0, backoff_max: float = 30.0, jitter: bool = True, retryable_exceptions: tuple | None = None): ...
    def get_delay(self, attempt: int) -> float: ...
    def should_retry(self, exception: Exception) -> bool: ...
    def attempts(self) -> Generator[int, None, None]: ...

class Bulkhead:
    def __init__(self, name: str = "default", max_concurrent: int = 10, max_queue: int = 0, timeout_s: float = 0.0): ...
    def acquire(self) -> bool: ...
    def release(self) -> None: ...
    def __enter__(self) -> Bulkhead: ...          # Raises BulkheadFullError if full
```

### 3.2 Configuration

Environment variables:
- `CODOMYRMEX_*`: Configuration options

## 4. Implementation Notes

### 4.1 Design Decisions

1. **Three resilience patterns in one module**: Circuit breaker, retry, and bulkhead are co-located because they are typically composed together for API call protection.
2. **Thread-safe state machine**: `CircuitBreaker` uses `threading.Lock` for all state transitions (CLOSED -> OPEN -> HALF_OPEN -> CLOSED), making it safe for multi-threaded use.
3. **Decorator and context manager APIs**: Both `CircuitBreaker` and `Bulkhead` support `with` statements; `circuit_breaker()` and `retry()` decorators provide function-level wrappers.

### 4.2 Limitations

- All timing uses synchronous `time.sleep`; not suitable for async frameworks without wrapping
- `RetryPolicy.attempts()` blocks the calling thread during backoff delays
- `Bulkhead` semaphore-based; no distributed bulkhead support across processes

## 5. Testing

```bash
# Run tests for this module
uv run pytest src/codomyrmex/tests/unit/api/circuit_breaker/
```

## 6. Future Considerations

- Async-compatible circuit breaker and retry (asyncio-native, no `time.sleep`)
- Sliding-window error rate tracking instead of cumulative counters
- Event hooks/callbacks for state transitions (e.g., on_open, on_close, on_half_open)
