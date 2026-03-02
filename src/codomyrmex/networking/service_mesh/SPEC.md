# Service Mesh - Technical Specification

## Overview

Implements four service mesh patterns: circuit breaking, load balancing, retry policies, and service proxying. Models and resilience logic are split across `models.py` and a resilience module.

## Key Classes

### `CircuitBreakerConfig` (models.py)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `failure_threshold` | `int` | 5 | Failures before opening circuit |
| `success_threshold` | `int` | 2 | Successes in HALF_OPEN before closing |
| `timeout_seconds` | `float` | 30.0 | Time before OPEN transitions to HALF_OPEN |
| `half_open_max_calls` | `int` | 3 | Max test calls in HALF_OPEN state |

### `ServiceInstance` (models.py)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | required | Instance identifier |
| `host` | `str` | required | Hostname or IP |
| `port` | `int` | required | Port number |
| `weight` | `int` | 1 | Load balancing weight |
| `healthy` | `bool` | True | Health status |
| `connections` | `int` | 0 | Active connection count |
| `metadata` | `dict[str, Any]` | `{}` | Custom metadata |

Property: `address -> str` returns `"{host}:{port}"`.

### `LoadBalancerStrategy` (models.py)

Enum values: `ROUND_ROBIN`, `RANDOM`, `WEIGHTED`, `LEAST_CONNECTIONS`.

### Exceptions (models.py)

| Exception | When Raised |
|-----------|-------------|
| `CircuitOpenError` | Call attempted on open circuit |
| `NoHealthyInstanceError` | No healthy service instances available |

## Module Exports (__init__.py)

Re-exports from models and resilience: `CircuitBreaker`, `LoadBalancer`, `RetryPolicy`, `ServiceProxy`, `with_circuit_breaker`, `with_retry`, plus all model classes.

## Dependencies

- **Internal**: None (standalone data classes)
- **External**: `dataclasses`, `enum` (stdlib only)

## Constraints

- Models module contains only data classes, enums, and exceptions -- no runtime logic.
- Circuit breaker state transitions and load balancer algorithms are in the resilience module.
