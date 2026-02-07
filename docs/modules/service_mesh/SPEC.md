# Service Mesh — Functional Specification

**Module**: `codomyrmex.service_mesh`  
**Version**: v0.1.0  
**Status**: Active

## 1. Overview

Microservice communication patterns, circuit breakers, and load balancing.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `CircuitState` | Class | Circuit breaker states. |
| `CircuitBreakerConfig` | Class | Circuit breaker configuration. |
| `CircuitBreaker` | Class | Circuit breaker pattern implementation. |
| `CircuitOpenError` | Class | Raised when circuit is open. |
| `LoadBalancerStrategy` | Class | Load balancing strategies. |
| `ServiceInstance` | Class | A service instance endpoint. |
| `LoadBalancer` | Class | Load balancer for service instances. |
| `RetryPolicy` | Class | Retry policy for failed requests. |
| `ServiceProxy` | Class | Proxy for service calls with resilience patterns. |
| `NoHealthyInstanceError` | Class | Raised when no healthy instances are available. |
| `with_circuit_breaker()` | Function | Decorator for circuit breaker protection. |
| `with_retry()` | Function | Decorator for retry logic. |
| `can_execute()` | Function | Check if execution is allowed. |
| `record_success()` | Function | Record a successful call. |
| `record_failure()` | Function | Record a failed call. |

## 3. Dependencies

See `src/codomyrmex/service_mesh/__init__.py` for import dependencies.

## 4. Public API

```python
from codomyrmex.service_mesh import CircuitState, CircuitBreakerConfig, CircuitBreaker, CircuitOpenError, LoadBalancerStrategy
```

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k service_mesh -v
```

## References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Source Code](../../../src/codomyrmex/service_mesh/)
