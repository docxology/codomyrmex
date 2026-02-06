# Service Mesh Module

Microservice communication patterns with circuit breakers, load balancing, and retries.

## Quick Start

```python
from codomyrmex.service_mesh import (
    CircuitBreaker, LoadBalancer, RetryPolicy,
    ServiceInstance, with_circuit_breaker,
)

# Circuit breaker
@with_circuit_breaker("api-service")
def call_api():
    return requests.get("http://api/data")

# Load balancer
lb = LoadBalancer()
lb.register(ServiceInstance("1", "host1", 8080))
lb.register(ServiceInstance("2", "host2", 8080))
instance = lb.get_instance()
```

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
