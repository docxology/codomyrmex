# Service Mesh Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Microservice communication patterns, circuit breakers, and load balancing.

## Key Features

- **CircuitState** — Circuit breaker states.
- **CircuitBreakerConfig** — Circuit breaker configuration.
- **CircuitBreaker** — Circuit breaker pattern implementation.
- **CircuitOpenError** — Raised when circuit is open.
- **LoadBalancerStrategy** — Load balancing strategies.
- **ServiceInstance** — A service instance endpoint.
- `with_circuit_breaker()` — Decorator for circuit breaker protection.
- `with_retry()` — Decorator for retry logic.
- `can_execute()` — Check if execution is allowed.
- `record_success()` — Record a successful call.

## Quick Start

```python
from codomyrmex.service_mesh import CircuitState, CircuitBreakerConfig, CircuitBreaker

# Initialize
instance = CircuitState()
```


## Installation

```bash
uv pip install codomyrmex
```

## API Reference

### Classes

| Class | Description |
|-------|-------------|
| `CircuitState` | Circuit breaker states. |
| `CircuitBreakerConfig` | Circuit breaker configuration. |
| `CircuitBreaker` | Circuit breaker pattern implementation. |
| `CircuitOpenError` | Raised when circuit is open. |
| `LoadBalancerStrategy` | Load balancing strategies. |
| `ServiceInstance` | A service instance endpoint. |
| `LoadBalancer` | Load balancer for service instances. |
| `RetryPolicy` | Retry policy for failed requests. |
| `ServiceProxy` | Proxy for service calls with resilience patterns. |
| `NoHealthyInstanceError` | Raised when no healthy instances are available. |

### Functions

| Function | Description |
|----------|-------------|
| `with_circuit_breaker()` | Decorator for circuit breaker protection. |
| `with_retry()` | Decorator for retry logic. |
| `can_execute()` | Check if execution is allowed. |
| `record_success()` | Record a successful call. |
| `record_failure()` | Record a failed call. |
| `execute()` | Execute function with circuit breaker protection. |
| `address()` | address |
| `register()` | Register a service instance. |
| `deregister()` | Deregister a service instance. |
| `get_instance()` | Get next instance based on strategy. |
| `mark_healthy()` | Update instance health status. |
| `get_delay()` | Get delay for retry attempt. |
| `call()` | Make a service call with full resilience stack. |
| `decorator()` | decorator |
| `wrapped()` | wrapped |
| `wrapper()` | wrapper |

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k service_mesh -v
```

## Navigation

- **Source**: [src/codomyrmex/service_mesh/](../../../src/codomyrmex/service_mesh/)
- **Parent**: [Modules](../README.md)
