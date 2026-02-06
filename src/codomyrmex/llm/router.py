"""
LLM Model Router

Intelligent routing between LLM providers with fallback, cost optimization,
and load balancing.
"""

import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class RoutingStrategy(Enum):
    """Model routing strategies."""
    PRIORITY = "priority"  # Use first available in order
    ROUND_ROBIN = "round_robin"
    RANDOM = "random"
    COST_OPTIMIZED = "cost_optimized"
    LATENCY_OPTIMIZED = "latency_optimized"
    CAPABILITY_MATCH = "capability_match"


@dataclass
class ModelConfig:
    """Configuration for a model."""
    name: str
    provider: str
    model_id: str
    priority: int = 0
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0
    max_tokens: int = 4096
    capabilities: list[str] = field(default_factory=list)
    rate_limit: int = 100  # requests per minute
    enabled: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelStats:
    """Runtime statistics for a model."""
    success_count: int = 0
    failure_count: int = 0
    total_latency_ms: float = 0.0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    last_used: datetime | None = None
    last_error: str | None = None

    @property
    def avg_latency_ms(self) -> float:
        total = self.success_count + self.failure_count
        return self.total_latency_ms / total if total > 0 else 0.0

    @property
    def success_rate(self) -> float:
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 1.0

    @property
    def total_cost(self) -> float:
        # Simplified cost calculation
        return 0.0


class ModelProvider(ABC):
    """Abstract base class for model providers."""

    @abstractmethod
    def complete(self, prompt: str, **kwargs) -> str:
        """Generate completion."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available."""
        pass


class ModelRouter:
    """Route requests to appropriate LLM models."""

    def __init__(
        self,
        strategy: RoutingStrategy = RoutingStrategy.PRIORITY,
        fallback_enabled: bool = True,
        max_retries: int = 3,
    ):
        self.strategy = strategy
        self.fallback_enabled = fallback_enabled
        self.max_retries = max_retries
        self._models: dict[str, ModelConfig] = {}
        self._providers: dict[str, ModelProvider] = {}
        self._stats: dict[str, ModelStats] = {}
        self._round_robin_idx = 0

    def register_model(
        self,
        config: ModelConfig,
        provider: ModelProvider | None = None,
    ) -> None:
        """Register a model configuration."""
        self._models[config.name] = config
        if provider:
            self._providers[config.name] = provider
        self._stats[config.name] = ModelStats()

    def register_provider(self, name: str, provider: ModelProvider) -> None:
        """Register a provider for a model."""
        self._providers[name] = provider

    def select_model(
        self,
        required_capabilities: list[str] | None = None,
        prefer_low_cost: bool = False,
        prefer_low_latency: bool = False,
    ) -> ModelConfig | None:
        """Select best model based on strategy and requirements."""
        candidates = [
            m for m in self._models.values()
            if m.enabled and self._meets_requirements(m, required_capabilities)
        ]

        if not candidates:
            return None

        strategy = self.strategy
        if prefer_low_cost:
            strategy = RoutingStrategy.COST_OPTIMIZED
        elif prefer_low_latency:
            strategy = RoutingStrategy.LATENCY_OPTIMIZED

        if strategy == RoutingStrategy.PRIORITY:
            candidates.sort(key=lambda m: m.priority, reverse=True)
            return candidates[0]

        elif strategy == RoutingStrategy.ROUND_ROBIN:
            self._round_robin_idx = (self._round_robin_idx + 1) % len(candidates)
            return candidates[self._round_robin_idx]

        elif strategy == RoutingStrategy.RANDOM:
            return random.choice(candidates)

        elif strategy == RoutingStrategy.COST_OPTIMIZED:
            return min(candidates, key=lambda m: m.cost_per_1k_input + m.cost_per_1k_output)

        elif strategy == RoutingStrategy.LATENCY_OPTIMIZED:
            def latency(m):
                stats = self._stats.get(m.name)
                return stats.avg_latency_ms if stats else float('inf')
            return min(candidates, key=latency)

        elif strategy == RoutingStrategy.CAPABILITY_MATCH:
            if required_capabilities:
                def capability_score(m):
                    return len(set(required_capabilities) & set(m.capabilities))
                return max(candidates, key=capability_score)
            return candidates[0]

        return candidates[0]

    def _meets_requirements(
        self,
        model: ModelConfig,
        required_capabilities: list[str] | None,
    ) -> bool:
        """Check if model meets capability requirements."""
        if not required_capabilities:
            return True
        return all(cap in model.capabilities for cap in required_capabilities)

    def complete(
        self,
        prompt: str,
        model_name: str | None = None,
        required_capabilities: list[str] | None = None,
        **kwargs,
    ) -> str:
        """Generate completion with routing and fallback."""
        # Select model
        if model_name:
            model = self._models.get(model_name)
        else:
            model = self.select_model(required_capabilities)

        if not model:
            raise ValueError("No suitable model available")

        # Try selected model with fallback
        tried_models = set()
        last_error = None

        for attempt in range(self.max_retries):
            if model.name in tried_models:
                # Select different model for fallback
                model = self.select_model(required_capabilities)
                if not model or model.name in tried_models:
                    break

            tried_models.add(model.name)
            provider = self._providers.get(model.name)

            if not provider:
                continue

            start = time.time()
            try:
                result = provider.complete(prompt, **kwargs)
                latency = (time.time() - start) * 1000

                # Update stats
                stats = self._stats[model.name]
                stats.success_count += 1
                stats.total_latency_ms += latency
                stats.last_used = datetime.now()

                return result

            except Exception as e:
                last_error = e
                stats = self._stats[model.name]
                stats.failure_count += 1
                stats.last_error = str(e)

                if not self.fallback_enabled:
                    raise

        raise last_error or ValueError("All models failed")

    def get_stats(self, model_name: str) -> ModelStats | None:
        """Get statistics for a model."""
        return self._stats.get(model_name)

    def get_all_stats(self) -> dict[str, ModelStats]:
        """Get all model statistics."""
        return self._stats.copy()


class FallbackChain:
    """Chain of models with automatic fallback."""

    def __init__(self, models: list[str]):
        self.models = models
        self._router: ModelRouter | None = None

    def with_router(self, router: ModelRouter) -> "FallbackChain":
        """Associate with a router."""
        self._router = router
        return self

    def complete(self, prompt: str, **kwargs) -> str:
        """Complete with fallback through chain."""
        if not self._router:
            raise ValueError("Router not set")

        last_error = None
        for model_name in self.models:
            try:
                return self._router.complete(prompt, model_name=model_name, **kwargs)
            except Exception as e:
                last_error = e
                continue

        raise last_error or ValueError("All models in chain failed")


class CostTracker:
    """Track LLM API costs."""

    def __init__(self):
        self._usage: dict[str, dict[str, float]] = {}

    def record(
        self,
        model_name: str,
        input_tokens: int,
        output_tokens: int,
        cost: float,
    ) -> None:
        """Record usage."""
        if model_name not in self._usage:
            self._usage[model_name] = {
                "input_tokens": 0,
                "output_tokens": 0,
                "total_cost": 0.0,
                "request_count": 0,
            }

        self._usage[model_name]["input_tokens"] += input_tokens
        self._usage[model_name]["output_tokens"] += output_tokens
        self._usage[model_name]["total_cost"] += cost
        self._usage[model_name]["request_count"] += 1

    def get_total_cost(self) -> float:
        """Get total cost across all models."""
        return sum(u["total_cost"] for u in self._usage.values())

    def get_usage_report(self) -> dict[str, Any]:
        """Get detailed usage report."""
        return {
            "by_model": self._usage.copy(),
            "total_cost": self.get_total_cost(),
            "total_requests": sum(u["request_count"] for u in self._usage.values()),
        }


__all__ = [
    "ModelRouter",
    "ModelConfig",
    "ModelStats",
    "ModelProvider",
    "RoutingStrategy",
    "FallbackChain",
    "CostTracker",
]
