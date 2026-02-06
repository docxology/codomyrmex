# Service Mesh Module

**Version**: v0.1.0 | **Status**: Active

Microservice communication patterns: circuit breakers, load balancing, and retry policies.

## Quick Start

```python
from codomyrmex.service_mesh import (
    CircuitBreaker, LoadBalancer, RetryPolicy, ServiceInstance,
    LoadBalancerStrategy, with_circuit_breaker, with_retry
)

# Circuit breaker pattern
cb = CircuitBreaker("payment-service")

def call_payment_api():
    # External API call
    return {"status": "ok"}

result = cb.execute(call_payment_api)  # Protected call

# Load balancer
lb = LoadBalancer(strategy=LoadBalancerStrategy.ROUND_ROBIN)
lb.register(ServiceInstance(id="1", host="api-1", port=8080))
lb.register(ServiceInstance(id="2", host="api-2", port=8080))

instance = lb.get_instance()  # Returns next healthy instance
print(f"Routing to: {instance.address}")

# Retry with exponential backoff
policy = RetryPolicy(max_retries=3, initial_delay=0.1)
result = policy.execute(call_payment_api)
```

## Decorators

```python
@with_circuit_breaker("api-service")
def fetch_data():
    return requests.get("https://api.example.com")

@with_retry(max_retries=3)
def upload_file(path):
    # Automatically retries on failure
    pass
```

## Exports

| Class | Description |
|-------|-------------|
| `CircuitBreaker` | Circuit breaker with closed/open/half-open states |
| `CircuitBreakerConfig` | Failure threshold, timeout, recovery settings |
| `CircuitState` | Enum: closed, open, half_open |
| `LoadBalancer` | Route requests across service instances |
| `LoadBalancerStrategy` | Enum: round_robin, random, weighted, least_connections |
| `ServiceInstance` | Service endpoint with host, port, weight, health |
| `ServiceProxy` | Full resilience stack (LB + CB + retry) |
| `RetryPolicy` | Exponential backoff with jitter |
| `with_circuit_breaker` | Decorator for circuit protection |
| `with_retry` | Decorator for retry logic |

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
