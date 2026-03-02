"""AI Gateway with load balancing, health checks, and circuit breaking."""

import time
import random
from dataclasses import dataclass, field
from typing import Callable, Optional
from enum import Enum


class CircuitState(Enum):
    CLOSED = "closed"       # Normal operation
    OPEN = "open"           # Failing, reject requests
    HALF_OPEN = "half_open" # Testing recovery


@dataclass
class Provider:
    """An LLM provider endpoint."""
    name: str
    endpoint: str
    model_fn: Optional[Callable[[str], str]] = None
    weight: float = 1.0
    max_retries: int = 3
    timeout_s: float = 30.0
    is_healthy: bool = True


@dataclass
class GatewayConfig:
    """Configuration for the AI Gateway."""
    strategy: str = "round_robin"  # "round_robin", "weighted", "least_loaded"
    circuit_failure_threshold: int = 5
    circuit_recovery_timeout_s: float = 60.0
    retry_on_failure: bool = True


class CircuitBreaker:
    """Per-provider circuit breaker with closed/open/half-open states."""

    def __init__(self, failure_threshold: int = 5, recovery_timeout_s: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout_s = recovery_timeout_s
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time: Optional[float] = None

    def call(self, fn: Callable, *args, **kwargs):
        """Execute fn through circuit breaker."""
        if self.state == CircuitState.OPEN:
            elapsed = time.time() - (self.last_failure_time or 0)
            if elapsed > self.recovery_timeout_s:
                self.state = CircuitState.HALF_OPEN
            else:
                raise RuntimeError("Circuit OPEN: provider unavailable")

        try:
            result = fn(*args, **kwargs)
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
            return result
        except Exception:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
            raise

    @property
    def is_available(self) -> bool:
        """Check if the circuit breaker allows requests."""
        if self.state == CircuitState.CLOSED or self.state == CircuitState.HALF_OPEN:
            return True
        elapsed = time.time() - (self.last_failure_time or 0)
        return elapsed > self.recovery_timeout_s


class AIGateway:
    """
    AI Gateway with load balancing, health checks, and circuit breaking.

    Routes requests across multiple LLM providers with:
    - Round-robin / weighted load balancing
    - Automatic failover on provider failure
    - Circuit breaker to prevent cascade failures
    - Request/response logging and metrics
    """

    def __init__(self, providers: list[Provider], config: GatewayConfig = None):
        self.providers = providers
        self.config = config or GatewayConfig()
        self.circuit_breakers = {
            p.name: CircuitBreaker(
                self.config.circuit_failure_threshold,
                self.config.circuit_recovery_timeout_s,
            )
            for p in providers
        }
        self._round_robin_idx = 0
        self.metrics = {
            p.name: {"requests": 0, "failures": 0, "total_ms": 0.0}
            for p in providers
        }

    def _select_provider(self) -> Provider:
        """Select next provider based on strategy."""
        available = [
            p for p in self.providers
            if p.is_healthy and self.circuit_breakers[p.name].is_available
        ]

        if not available:
            raise RuntimeError("All providers unavailable")

        if self.config.strategy == "weighted":
            total_weight = sum(p.weight for p in available)
            r = random.random() * total_weight
            cumulative = 0
            for p in available:
                cumulative += p.weight
                if r <= cumulative:
                    return p
            return available[-1]

        elif self.config.strategy == "round_robin":
            idx = self._round_robin_idx % len(available)
            self._round_robin_idx += 1
            return available[idx]

        return available[0]

    def complete(self, prompt: str) -> dict:
        """
        Route a completion request to the best available provider.

        Returns:
            dict with: provider, response, latency_ms, success
        """
        last_error = None
        provider = None

        for attempt in range(max(p.max_retries for p in self.providers)):
            try:
                provider = self._select_provider()
                t0 = time.perf_counter()

                def _call(p=provider):
                    if p.model_fn:
                        return p.model_fn(prompt)
                    return f"[{p.name}] response to: {prompt[:50]}"

                response = self.circuit_breakers[provider.name].call(_call)
                latency_ms = (time.perf_counter() - t0) * 1000

                self.metrics[provider.name]["requests"] += 1
                self.metrics[provider.name]["total_ms"] += latency_ms

                return {
                    "provider": provider.name,
                    "response": response,
                    "latency_ms": latency_ms,
                    "attempt": attempt + 1,
                    "success": True,
                }
            except Exception as e:
                last_error = str(e)
                if provider:
                    self.metrics[provider.name]["failures"] += 1
                if not self.config.retry_on_failure:
                    break

        return {"provider": None, "response": None, "success": False, "error": last_error}

    def health_check(self) -> dict:
        """Check health of all providers."""
        return {
            p.name: {
                "healthy": p.is_healthy,
                "circuit": self.circuit_breakers[p.name].state.value,
                "requests": self.metrics[p.name]["requests"],
                "failures": self.metrics[p.name]["failures"],
            }
            for p in self.providers
        }
