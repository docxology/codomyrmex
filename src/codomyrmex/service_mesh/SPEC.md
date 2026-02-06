# Technical Specification - Service Mesh

**Module**: `codomyrmex.service_mesh` | **Version**: v0.1.0

## Public API

- `CircuitBreaker`, `CircuitBreakerConfig` - Fault tolerance
- `LoadBalancer`, `LoadBalancerStrategy` - Traffic distribution
- `RetryPolicy` - Automatic retries with backoff
- `ServiceProxy` - Combined resilience stack
