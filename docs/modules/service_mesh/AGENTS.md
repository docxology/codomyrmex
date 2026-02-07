# Service Mesh Module — Agent Coordination

## Purpose

Microservice communication patterns, circuit breakers, and load balancing.

## Key Capabilities

- **CircuitState**: Circuit breaker states.
- **CircuitBreakerConfig**: Circuit breaker configuration.
- **CircuitBreaker**: Circuit breaker pattern implementation.
- **CircuitOpenError**: Raised when circuit is open.
- **LoadBalancerStrategy**: Load balancing strategies.
- `with_circuit_breaker()`: Decorator for circuit breaker protection.
- `with_retry()`: Decorator for retry logic.
- `can_execute()`: Check if execution is allowed.

## Agent Usage Patterns

```python
from codomyrmex.service_mesh import CircuitState

# Agent initializes service mesh
instance = CircuitState()
```

## Integration Points

- **Source**: [src/codomyrmex/service_mesh/](../../../src/codomyrmex/service_mesh/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)
