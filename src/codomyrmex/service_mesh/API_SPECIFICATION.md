# Service Mesh API Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## 1. Overview

The `service_mesh` module provides microservice communication patterns including circuit breakers, load balancing, retry policies, and service proxies. It enables resilient inter-service communication with automatic failure detection and recovery.

## 2. Core Components

### 2.1 Enums

- **`CircuitState`**: Circuit breaker states -- `CLOSED` (normal), `OPEN` (failing, reject requests), `HALF_OPEN` (testing recovery).
- **`LoadBalancerStrategy`**: Load balancing algorithms -- `ROUND_ROBIN`, `RANDOM`, `WEIGHTED`, `LEAST_CONNECTIONS`.

### 2.2 Configuration

- **`CircuitBreakerConfig`** (dataclass): Configures circuit breaker behavior.
  - `failure_threshold: int = 5` -- Failures before opening circuit.
  - `success_threshold: int = 2` -- Successes in half-open before closing.
  - `timeout_seconds: float = 30.0` -- Seconds before open circuit retries.
  - `half_open_max_calls: int = 3` -- Max concurrent calls in half-open state.

### 2.3 Circuit Breaker

```python
from codomyrmex.service_mesh import CircuitBreaker, CircuitBreakerConfig

config = CircuitBreakerConfig(failure_threshold=3, timeout_seconds=10.0)
cb = CircuitBreaker("payment-service", config)

# Check state
cb.can_execute()        # -> bool
cb.state                # -> CircuitState

# Execute with protection
result = cb.execute(my_function, arg1, arg2)

# Manual state recording
cb.record_success()
cb.record_failure()
```

### 2.4 Load Balancer

```python
from codomyrmex.service_mesh import LoadBalancer, LoadBalancerStrategy, ServiceInstance

lb = LoadBalancer(strategy=LoadBalancerStrategy.LEAST_CONNECTIONS)

instance = ServiceInstance(id="svc-1", host="10.0.0.1", port=8080, weight=3)
lb.register(instance)
lb.deregister("svc-1")

selected = lb.get_instance()        # -> ServiceInstance | None
lb.mark_healthy("svc-1", False)     # Mark unhealthy
```

**`ServiceInstance`** (dataclass): `id`, `host`, `port`, `weight=1`, `healthy=True`, `connections=0`, `metadata={}`. Property: `address -> str` returns `"host:port"`.

### 2.5 Retry Policy

```python
from codomyrmex.service_mesh import RetryPolicy

policy = RetryPolicy(
    max_retries=3,
    initial_delay=0.1,
    max_delay=10.0,
    exponential_base=2.0,
    jitter=True,
)

result = policy.execute(my_function, arg1, kwarg=val)
delay = policy.get_delay(attempt=2)  # -> float (seconds)
```

### 2.6 Service Proxy

```python
from codomyrmex.service_mesh import ServiceProxy

proxy = ServiceProxy(
    service_name="orders",
    load_balancer=lb,
    circuit_breaker=cb,
    retry_policy=policy,
)

# Full resilience stack: load balance -> circuit break -> retry
result = proxy.call(handler_fn, request_data)
```

### 2.7 Decorator Functions

```python
from codomyrmex.service_mesh import with_circuit_breaker, with_retry

@with_circuit_breaker("auth-service", config=CircuitBreakerConfig(failure_threshold=3))
def call_auth(token):
    ...

@with_retry(max_retries=5, initial_delay=0.2)
def fetch_data(url):
    ...
```

## 3. Error Handling

| Exception | Raised When |
|:----------|:------------|
| `CircuitOpenError` | Circuit is open and rejecting calls |
| `NoHealthyInstanceError` | Load balancer has no healthy instances |

Both inherit from `Exception`. Catch these to implement fallback logic.

## 4. Thread Safety

All public methods on `CircuitBreaker`, `LoadBalancer`, and `ServiceProxy` are thread-safe via internal `threading.Lock`.

## 5. Integration Points

- **chaos_engineering**: Combine with fault injection to test circuit breaker thresholds.
- **metrics**: Track circuit state transitions, retry counts, and load balancer distribution.
- **logging_monitoring**: Log circuit open/close events and retry attempts.

## 6. Navigation

- **Human Documentation**: [README.md](README.md)
- **MCP Tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
- **Parent Directory**: [codomyrmex](../README.md)
