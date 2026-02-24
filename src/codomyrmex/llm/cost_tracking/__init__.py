"""
LLM Cost Tracking Module

Token counting, billing estimation, and usage analytics for LLM operations.
"""

__version__ = "0.1.0"

import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


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
    input_cost_per_1k: float  # Cost per 1000 input tokens
    output_cost_per_1k: float  # Cost per 1000 output tokens
    context_window: int = 0
    currency: str = "USD"

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate total cost for token counts."""
        input_cost = (input_tokens / 1000) * self.input_cost_per_1k
        output_cost = (output_tokens / 1000) * self.output_cost_per_1k
        return input_cost + output_cost


# Pricing data (as of late 2025 / early 2026 - prices change!)
MODEL_PRICING: dict[str, ModelPricing] = {
    # OpenAI
    "gpt-4o": ModelPricing("gpt-4o", ModelProvider.OPENAI, 0.0025, 0.01, 128000),
    "gpt-4o-mini": ModelPricing("gpt-4o-mini", ModelProvider.OPENAI, 0.00015, 0.0006, 128000),
    "gpt-4-turbo": ModelPricing("gpt-4-turbo", ModelProvider.OPENAI, 0.01, 0.03, 128000),
    "gpt-4": ModelPricing("gpt-4", ModelProvider.OPENAI, 0.03, 0.06, 8192),
    "gpt-3.5-turbo": ModelPricing("gpt-3.5-turbo", ModelProvider.OPENAI, 0.0005, 0.0015, 16385),
    "o1": ModelPricing("o1", ModelProvider.OPENAI, 0.015, 0.06, 200000),
    "o1-mini": ModelPricing("o1-mini", ModelProvider.OPENAI, 0.003, 0.012, 128000),

    # Anthropic
    "claude-3-5-sonnet": ModelPricing("claude-3-5-sonnet", ModelProvider.ANTHROPIC, 0.003, 0.015, 200000),
    "claude-3-opus": ModelPricing("claude-3-opus", ModelProvider.ANTHROPIC, 0.015, 0.075, 200000),
    "claude-3-haiku": ModelPricing("claude-3-haiku", ModelProvider.ANTHROPIC, 0.00025, 0.00125, 200000),

    # Google
    "gemini-1.5-pro": ModelPricing("gemini-1.5-pro", ModelProvider.GOOGLE, 0.00125, 0.005, 2000000),
    "gemini-1.5-flash": ModelPricing("gemini-1.5-flash", ModelProvider.GOOGLE, 0.000075, 0.0003, 1000000),
    "gemini-2.0-flash": ModelPricing("gemini-2.0-flash", ModelProvider.GOOGLE, 0.0001, 0.0004, 1000000),

    # Mistral
    "mistral-large": ModelPricing("mistral-large", ModelProvider.MISTRAL, 0.002, 0.006, 128000),
    "mistral-small": ModelPricing("mistral-small", ModelProvider.MISTRAL, 0.0002, 0.0006, 32000),
    "codestral": ModelPricing("codestral", ModelProvider.MISTRAL, 0.0002, 0.0006, 32000),
}


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
        """Execute Total Tokens operations natively."""
        return self.total_input_tokens + self.total_output_tokens


class TokenCounter:
    """
    Estimate token counts for text.

    Uses heuristics since exact tokenization requires model-specific tokenizers.
    For precise counts, use tiktoken for OpenAI or model-specific tokenizers.
    """

    # Average characters per token (rough estimate)
    CHARS_PER_TOKEN = {
        ModelProvider.OPENAI: 4.0,
        ModelProvider.ANTHROPIC: 3.5,
        ModelProvider.GOOGLE: 4.0,
        ModelProvider.MISTRAL: 4.0,
        ModelProvider.LOCAL: 4.0,
        ModelProvider.CUSTOM: 4.0,
    }

    @classmethod
    def estimate_tokens(
        cls,
        text: str,
        provider: ModelProvider = ModelProvider.OPENAI
    ) -> int:
        """
        Estimate token count for text.

        Args:
            text: Text to count tokens for
            provider: LLM provider (affects estimation)

        Returns:
            Estimated token count
        """
        if not text:
            return 0

        chars_per_token = cls.CHARS_PER_TOKEN.get(provider, 4.0)

        # Count characters
        char_count = len(text)

        # Adjust for whitespace and special characters
        word_count = len(text.split())

        # Use weighted average of character-based and word-based estimates
        char_estimate = char_count / chars_per_token
        word_estimate = word_count * 1.3  # Average ~1.3 tokens per word

        return int((char_estimate + word_estimate) / 2)

    @classmethod
    def estimate_messages_tokens(
        cls,
        messages: list[dict[str, str]],
        provider: ModelProvider = ModelProvider.OPENAI
    ) -> int:
        """
        Estimate tokens for a list of messages.

        Args:
            messages: List of message dicts with 'role' and 'content'
            provider: LLM provider

        Returns:
            Estimated token count
        """
        total = 0

        for msg in messages:
            # Add tokens for role and structural overhead
            total += 4  # ~4 tokens per message overhead

            content = msg.get("content", "")
            if content:
                total += cls.estimate_tokens(content, provider)

            # Add tokens for name if present
            if "name" in msg:
                total += cls.estimate_tokens(msg["name"], provider) + 1

        total += 2  # End of messages token

        return total


class CostTracker:
    """
    Track LLM usage costs over time.

    Usage:
        tracker = CostTracker()

        # Record usage
        tracker.record(
            model_id="gpt-4o",
            input_tokens=500,
            output_tokens=200,
            latency_ms=1500
        )

        # Get summary
        summary = tracker.get_summary(period_days=7)
        print(f"Total cost: ${summary.total_cost:.4f}")
    """

    def __init__(self, custom_pricing: dict[str, ModelPricing] | None = None):
        """
        Initialize cost tracker.

        Args:
            custom_pricing: Optional custom pricing overrides
        """
        self._records: list[UsageRecord] = []
        self._pricing = {**MODEL_PRICING}
        if custom_pricing:
            self._pricing.update(custom_pricing)

    def record(
        self,
        model_id: str,
        input_tokens: int,
        output_tokens: int,
        latency_ms: float = 0.0,
        metadata: dict[str, Any] | None = None,
    ) -> UsageRecord:
        """
        Record a usage event.

        Args:
            model_id: Model identifier
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            latency_ms: Request latency in milliseconds
            metadata: Optional additional metadata

        Returns:
            Created UsageRecord
        """
        # Calculate cost
        cost = 0.0
        if model_id in self._pricing:
            cost = self._pricing[model_id].calculate_cost(input_tokens, output_tokens)

        record = UsageRecord(
            model_id=model_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            latency_ms=latency_ms,
            metadata=metadata or {},
        )

        self._records.append(record)
        return record

    def estimate_cost(
        self,
        model_id: str,
        input_text: str,
        estimated_output_tokens: int = 500,
    ) -> tuple[int, int, float]:
        """
        Estimate cost for a request before making it.

        Args:
            model_id: Model to use
            input_text: Input prompt
            estimated_output_tokens: Estimated output length

        Returns:
            Tuple of (input_tokens, output_tokens, estimated_cost)
        """
        # Get provider from pricing
        provider = ModelProvider.OPENAI
        if model_id in self._pricing:
            provider = self._pricing[model_id].provider

        input_tokens = TokenCounter.estimate_tokens(input_text, provider)

        cost = 0.0
        if model_id in self._pricing:
            cost = self._pricing[model_id].calculate_cost(
                input_tokens, estimated_output_tokens
            )

        return input_tokens, estimated_output_tokens, cost

    def get_summary(
        self,
        period_days: int | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> UsageSummary:
        """
        Get usage summary for a period.

        Args:
            period_days: Number of days to look back (from now)
            start_date: Start of period (overrides period_days)
            end_date: End of period (defaults to now)

        Returns:
            UsageSummary with aggregated stats
        """
        now = datetime.now()

        if end_date is None:
            end_date = now

        if start_date is None:
            if period_days is not None:
                start_date = now - timedelta(days=period_days)
            else:
                start_date = datetime.min

        # Filter records
        filtered = [
            r for r in self._records
            if start_date <= r.timestamp <= end_date
        ]

        if not filtered:
            return UsageSummary(period_start=start_date, period_end=end_date)

        # Aggregate
        by_model: dict[str, dict[str, Any]] = defaultdict(lambda: {
            "requests": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "cost": 0.0,
        })

        total_latency = 0.0

        for record in filtered:
            by_model[record.model_id]["requests"] += 1
            by_model[record.model_id]["input_tokens"] += record.input_tokens
            by_model[record.model_id]["output_tokens"] += record.output_tokens
            by_model[record.model_id]["cost"] += record.cost
            total_latency += record.latency_ms

        return UsageSummary(
            period_start=start_date,
            period_end=end_date,
            total_requests=len(filtered),
            total_input_tokens=sum(r.input_tokens for r in filtered),
            total_output_tokens=sum(r.output_tokens for r in filtered),
            total_cost=sum(r.cost for r in filtered),
            avg_latency_ms=total_latency / len(filtered) if filtered else 0.0,
            by_model=dict(by_model),
        )

    def get_records(
        self,
        model_id: str | None = None,
        limit: int = 100,
    ) -> list[UsageRecord]:
        """
        Get recent usage records.

        Args:
            model_id: Filter by model (optional)
            limit: Maximum records to return

        Returns:
            List of UsageRecords, most recent first
        """
        records = self._records
        if model_id:
            records = [r for r in records if r.model_id == model_id]

        return sorted(records, key=lambda r: r.timestamp, reverse=True)[:limit]

    def export_to_json(self) -> str:
        """Export all records to JSON."""
        return json.dumps([
            {
                "model_id": r.model_id,
                "input_tokens": r.input_tokens,
                "output_tokens": r.output_tokens,
                "cost": r.cost,
                "latency_ms": r.latency_ms,
                "timestamp": r.timestamp.isoformat(),
                "metadata": r.metadata,
            }
            for r in self._records
        ], indent=2)

    def clear(self) -> None:
        """Clear all records."""
        self._records = []


class BudgetGuard:
    """
    Guard against exceeding budget limits.

    Usage:
        guard = BudgetGuard(daily_limit=10.0)

        if guard.can_proceed(estimated_cost=0.05):
            # Make request
            guard.record_spend(0.05)
        else:
            print("Budget exceeded!")
    """

    def __init__(
        self,
        daily_limit: float | None = None,
        monthly_limit: float | None = None,
        total_limit: float | None = None,
    ):
        """Execute   Init   operations natively."""
        self.daily_limit = daily_limit
        self.monthly_limit = monthly_limit
        self.total_limit = total_limit
        self._daily_spend: dict[str, float] = defaultdict(float)
        self._monthly_spend: dict[str, float] = defaultdict(float)
        self._total_spend = 0.0

    def _today_key(self) -> str:
        """Execute  Today Key operations natively."""
        return datetime.now().strftime("%Y-%m-%d")

    def _month_key(self) -> str:
        """Execute  Month Key operations natively."""
        return datetime.now().strftime("%Y-%m")

    def record_spend(self, amount: float) -> None:
        """Record spending."""
        self._daily_spend[self._today_key()] += amount
        self._monthly_spend[self._month_key()] += amount
        self._total_spend += amount

    def can_proceed(self, estimated_cost: float = 0.0) -> bool:
        """Check if a request with estimated cost can proceed."""
        if self.daily_limit is not None:
            if self._daily_spend[self._today_key()] + estimated_cost > self.daily_limit:
                return False

        if self.monthly_limit is not None:
            if self._monthly_spend[self._month_key()] + estimated_cost > self.monthly_limit:
                return False

        if self.total_limit is not None:
            if self._total_spend + estimated_cost > self.total_limit:
                return False

        return True

    def get_remaining(self) -> dict[str, float | None]:
        """Get remaining budget for each limit type."""
        return {
            "daily": (
                self.daily_limit - self._daily_spend[self._today_key()]
                if self.daily_limit else None
            ),
            "monthly": (
                self.monthly_limit - self._monthly_spend[self._month_key()]
                if self.monthly_limit else None
            ),
            "total": (
                self.total_limit - self._total_spend
                if self.total_limit else None
            ),
        }


# Convenience functions
def estimate_cost(
    model_id: str,
    input_text: str,
    output_tokens: int = 500
) -> float:
    """Quick cost estimation."""
    if model_id not in MODEL_PRICING:
        return 0.0

    provider = MODEL_PRICING[model_id].provider
    input_tokens = TokenCounter.estimate_tokens(input_text, provider)
    return MODEL_PRICING[model_id].calculate_cost(input_tokens, output_tokens)


def count_tokens(text: str, provider: str = "openai") -> int:
    """Quick token count."""
    provider_enum = ModelProvider[provider.upper()]
    return TokenCounter.estimate_tokens(text, provider_enum)


def get_model_pricing(model_id: str) -> ModelPricing | None:
    """Get pricing for a model."""
    return MODEL_PRICING.get(model_id)


__all__ = [
    # Enums
    "ModelProvider",
    # Data classes
    "ModelPricing",
    "UsageRecord",
    "UsageSummary",
    # Classes
    "TokenCounter",
    "CostTracker",
    "BudgetGuard",
    # Constants
    "MODEL_PRICING",
    # Functions
    "estimate_cost",
    "count_tokens",
    "get_model_pricing",
]
