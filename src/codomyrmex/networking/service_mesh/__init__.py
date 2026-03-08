"""
Service Mesh Module

Service mesh patterns: circuit breaker, load balancer, retry, and proxy.
"""

import contextlib

from .models import (
    CircuitBreakerConfig,
    CircuitOpenError,
    CircuitState,
    LoadBalancerStrategy,
    NoHealthyInstanceError,
    ServiceInstance,
)
from .resilience import (
    CircuitBreaker,
    LoadBalancer,
    RetryPolicy,
    ServiceProxy,
    with_circuit_breaker,
    with_retry,
)

# Shared schemas for cross-module interop
with contextlib.suppress(ImportError):
    from codomyrmex.validation.schemas import Result, ResultStatus


def cli_commands():
    """Return CLI commands for the service_mesh module."""
    return {
        "services": lambda: print(
            "Service Mesh Components\n"
            "  CircuitBreaker - Fault isolation with configurable thresholds\n"
            "  LoadBalancer   - Strategies: "
            + ", ".join(s.value for s in LoadBalancerStrategy)
            + "\n"
            "  RetryPolicy    - Configurable retry with backoff\n"
            "  ServiceProxy   - Unified proxy with resilience patterns"
        ),
        "topology": lambda: print(
            "Mesh Topology\n"
            "  Circuit states: " + ", ".join(cs.value for cs in CircuitState) + "\n"
            "  Use ServiceProxy to wire services with circuit breakers and load balancing.\n"
            "  Use with_circuit_breaker / with_retry decorators for inline resilience."
        ),
    }


__all__ = [
    "CircuitBreaker",
    "CircuitBreakerConfig",
    "CircuitOpenError",
    "CircuitState",
    "LoadBalancer",
    "LoadBalancerStrategy",
    "NoHealthyInstanceError",
    "RetryPolicy",
    "ServiceInstance",
    "ServiceProxy",
    # CLI
    "cli_commands",
    "with_circuit_breaker",
    "with_retry",
]
