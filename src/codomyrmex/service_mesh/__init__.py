"""
Service Mesh Module

Service mesh patterns: circuit breaker, load balancer, retry, and proxy.
"""

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
try:
    from codomyrmex.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None


def cli_commands():
    """Return CLI commands for the service_mesh module."""
    return {
        "services": lambda: print(
            "Service Mesh Components\n"
            "  CircuitBreaker - Fault isolation with configurable thresholds\n"
            "  LoadBalancer   - Strategies: " + ", ".join(s.value for s in LoadBalancerStrategy) + "\n"
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
    "CircuitState",
    "CircuitBreakerConfig",
    "CircuitOpenError",
    "NoHealthyInstanceError",
    "LoadBalancerStrategy",
    "ServiceInstance",
    "CircuitBreaker",
    "LoadBalancer",
    "RetryPolicy",
    "ServiceProxy",
    "with_circuit_breaker",
    "with_retry",
    # CLI
    "cli_commands",
]
