"""Cost tracking data models: ModelProvider, ModelPricing, UsageRecord, UsageSummary."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ModelProvider(Enum):
    """Supported LLM providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    MISTRAL = "mistral"
    COHERE = "cohere"
    LOCAL = "local"
    CUSTOM = "custom"


@dataclass
class ModelPricing:
    """Pricing information for a model."""

    model_id: str
    provider: ModelProvider
    input_cost_per_1k: float
    output_cost_per_1k: float
    context_window: int = 0
    currency: str = "USD"

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate total cost for token counts."""
        input_cost = (input_tokens / 1000) * self.input_cost_per_1k
        output_cost = (output_tokens / 1000) * self.output_cost_per_1k
        return input_cost + output_cost


@dataclass
class UsageRecord:
    """Record of a single LLM usage event."""

    model_id: str
    input_tokens: int
    output_tokens: int
    timestamp: datetime = field(default_factory=datetime.now)
    cost: float = 0.0
    latency_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def total_tokens(self) -> int:
        """Total tokens used."""
        return self.input_tokens + self.output_tokens


@dataclass
class UsageSummary:
    """Aggregated usage summary."""

    period_start: datetime
    period_end: datetime
    total_requests: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cost: float = 0.0
    avg_latency_ms: float = 0.0
    by_model: dict[str, dict[str, Any]] = field(default_factory=dict)

    @property
    def total_tokens(self) -> int:
        return self.total_input_tokens + self.total_output_tokens
