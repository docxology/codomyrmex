# Service Mesh - Agent Coordination

## Purpose

Service mesh primitives providing circuit breaker, load balancer, retry policy, and service proxy patterns for resilient inter-service communication.

## Key Components

| Component | Role |
|-----------|------|
| `CircuitBreaker` | Fault tolerance with CLOSED/OPEN/HALF_OPEN state machine |
| `CircuitBreakerConfig` | Config: failure_threshold (5), success_threshold (2), timeout_seconds (30), half_open_max_calls (3) |
| `CircuitState` | Enum: CLOSED, OPEN, HALF_OPEN |
| `LoadBalancer` | Request distribution across service instances |
| `LoadBalancerStrategy` | Enum: ROUND_ROBIN, RANDOM, WEIGHTED, LEAST_CONNECTIONS |
| `ServiceInstance` | Dataclass: id, host, port, weight, healthy, connections, metadata |
| `RetryPolicy` | Configurable retry logic with backoff |
| `ServiceProxy` | Composite proxy combining circuit breaker, load balancer, and retry |
| `with_circuit_breaker` | Decorator for circuit breaker wrapping |
| `with_retry` | Decorator for retry policy wrapping |

## Operating Contracts

- `CircuitOpenError` is raised when calling through an open circuit breaker.
- `NoHealthyInstanceError` is raised when no healthy `ServiceInstance` entries are available for load balancing.
- `ServiceInstance.address` property returns `"{host}:{port}"`.
- `cli_commands()` function provides CLI integration for service mesh operations.

## Integration Points

- **Parent module**: `networking/` provides shared exceptions and network utilities.
- **Decorators**: `with_circuit_breaker` and `with_retry` can wrap any callable.

## Navigation

- **Parent**: [networking/](../README.md)
- **Sibling**: [SPEC.md](SPEC.md)
- **Root**: [/README.md](../../../../README.md)
