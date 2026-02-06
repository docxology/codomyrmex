# Agent Guidelines - Service Mesh

## Module Overview

Service mesh patterns: circuit breakers, load balancing, and retries.

## Key Classes

- **CircuitBreaker** — Prevent cascade failures
- **LoadBalancer** — Distribute requests
- **RetryPolicy** — Retry configuration
- **ServiceProxy** — Service proxy wrapper

## Agent Instructions

1. **Wrap external calls** — Use circuit breakers
2. **Configure thresholds** — Balance resilience vs latency
3. **Monitor open circuits** — Alert on failures
4. **Health-based routing** — Route to healthy instances
5. **Retry idempotent** — Only retry safe operations

## Common Patterns

```python
from codomyrmex.service_mesh import (
    CircuitBreaker, LoadBalancer, RetryPolicy, with_retry
)

# Circuit breaker
breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=30
)

@breaker
async def call_external_api():
    return await make_request()

# Load balancing
balancer = LoadBalancer(
    instances=["host1:8080", "host2:8080"],
    strategy="round_robin"
)
host = balancer.get_next()

# Retry with policy
policy = RetryPolicy(max_attempts=3, backoff="exponential")

@with_retry(policy)
async def flaky_operation():
    return await external_call()
```

## Testing Patterns

```python
# Verify circuit breaker
breaker = CircuitBreaker(failure_threshold=2)
# Trigger failures
for _ in range(2):
    try:
        breaker.call(failing_func)
    except:
        pass
assert breaker.is_open

# Verify load balancer
lb = LoadBalancer(["a", "b"])
assert lb.get_next() in ["a", "b"]
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
