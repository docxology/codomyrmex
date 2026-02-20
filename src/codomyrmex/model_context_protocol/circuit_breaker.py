# DEPRECATED(v0.2.0): Shim module. Import from model_context_protocol.reliability.circuit_breaker instead. Will be removed in v0.3.0.
"""Backward-compatibility shim. Canonical location: model_context_protocol.reliability.circuit_breaker"""
from .reliability.circuit_breaker import *  # noqa: F401,F403
from .reliability.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitOpenError,
    CircuitState,
    get_circuit_breaker,
    get_all_circuit_metrics,
    reset_all_circuits,
)
