# DEPRECATED(v0.2.0): Shim module. Import from orchestrator.resilience.agent_circuit_breaker instead. Will be removed in v0.3.0.
"""Backward-compatibility shim. Canonical location: orchestrator.resilience.agent_circuit_breaker"""
from .resilience.agent_circuit_breaker import *  # noqa: F401,F403
from .resilience.agent_circuit_breaker import (
    AgentHealth,
    CircuitBreaker,
    CircuitState,
)
