"""TokenCounter, CostTracker, BudgetGuard, and convenience functions."""

import json
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any

from .models import ModelProvider, UsageRecord, UsageSummary
from .pricing import MODEL_PRICING


class TokenCounter:
    """
    Estimate token counts for text.

    Uses heuristics since exact tokenization requires model-specific tokenizers.
    For precise counts, use tiktoken for OpenAI or model-specific tokenizers.
    """

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
        cls, text: str, provider: ModelProvider = ModelProvider.OPENAI
    ) -> int:
        """Estimate token count for text."""
        if not text:
            return 0

        chars_per_token = cls.CHARS_PER_TOKEN.get(provider, 4.0)
        char_count = len(text)
        word_count = len(text.split())

        char_estimate = char_count / chars_per_token
        word_estimate = word_count * 1.3

        return int((char_estimate + word_estimate) / 2)

    @classmethod
    def estimate_messages_tokens(
        cls,
        messages: list[dict[str, str]],
        provider: ModelProvider = ModelProvider.OPENAI,
    ) -> int:
        """Estimate tokens for a list of messages."""
        total = 0

        for msg in messages:
            total += 4

            content = msg.get("content", "")
            if content:
                total += cls.estimate_tokens(content, provider)

            if "name" in msg:
                total += cls.estimate_tokens(msg["name"], provider) + 1

        total += 2
        return total


class CostTracker:
    """
    Track LLM usage costs over time.

    Usage:
        tracker = CostTracker()
        tracker.record(model_id="gpt-4o", input_tokens=500, output_tokens=200)
        summary = tracker.get_summary(period_days=7)
        print(f"Total cost: ${summary.total_cost:.4f}")
    """

    def __init__(self, custom_pricing: dict | None = None):
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
        """Record a usage event."""
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
        """Estimate cost for a request before making it."""
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

    def _aggregate_by_model(
        self, records: list[UsageRecord]
    ) -> tuple[dict[str, dict[str, Any]], float]:
        """Aggregate records by model. Returns (by_model dict, total_latency)."""
        by_model: dict[str, dict[str, Any]] = defaultdict(
            lambda: {"requests": 0, "input_tokens": 0, "output_tokens": 0, "cost": 0.0}
        )
        total_latency = 0.0
        for record in records:
            by_model[record.model_id]["requests"] += 1
            by_model[record.model_id]["input_tokens"] += record.input_tokens
            by_model[record.model_id]["output_tokens"] += record.output_tokens
            by_model[record.model_id]["cost"] += record.cost
            total_latency += record.latency_ms
        return dict(by_model), total_latency

    def get_summary(
        self,
        period_days: int | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> UsageSummary:
        """Get usage summary for a period."""
        now = datetime.now()

        if end_date is None:
            end_date = now

        if start_date is None:
            if period_days is not None:
                start_date = now - timedelta(days=period_days)
            else:
                start_date = datetime.min

        filtered = [r for r in self._records if start_date <= r.timestamp <= end_date]

        if not filtered:
            return UsageSummary(period_start=start_date, period_end=end_date)

        by_model, total_latency = self._aggregate_by_model(filtered)

        return UsageSummary(
            period_start=start_date,
            period_end=end_date,
            total_requests=len(filtered),
            total_input_tokens=sum(r.input_tokens for r in filtered),
            total_output_tokens=sum(r.output_tokens for r in filtered),
            total_cost=sum(r.cost for r in filtered),
            avg_latency_ms=total_latency / len(filtered) if filtered else 0.0,
            by_model=by_model,
        )

    def get_records(
        self,
        model_id: str | None = None,
        limit: int = 100,
    ) -> list[UsageRecord]:
        """Get recent usage records."""
        records = self._records
        if model_id:
            records = [r for r in records if r.model_id == model_id]
        return sorted(records, key=lambda r: r.timestamp, reverse=True)[:limit]

    def export_to_json(self) -> str:
        """Export all records to JSON."""
        return json.dumps(
            [
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
            ],
            indent=2,
        )

    def clear(self) -> None:
        """Clear all records."""
        self._records = []


class BudgetGuard:
    """
    Guard against exceeding budget limits.

    Usage:
        guard = BudgetGuard(daily_limit=10.0)
        if guard.can_proceed(estimated_cost=0.05):
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
        self.daily_limit = daily_limit
        self.monthly_limit = monthly_limit
        self.total_limit = total_limit
        self._daily_spend: dict[str, float] = defaultdict(float)
        self._monthly_spend: dict[str, float] = defaultdict(float)
        self._total_spend = 0.0

    def _today_key(self) -> str:
        return datetime.now().strftime("%Y-%m-%d")

    def _month_key(self) -> str:
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

        if self.monthly_limit is not None and (
            self._monthly_spend[self._month_key()] + estimated_cost > self.monthly_limit
        ):
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
                if self.daily_limit
                else None
            ),
            "monthly": (
                self.monthly_limit - self._monthly_spend[self._month_key()]
                if self.monthly_limit
                else None
            ),
            "total": (
                self.total_limit - self._total_spend if self.total_limit else None
            ),
        }


# Convenience functions
def estimate_cost(model_id: str, input_text: str, output_tokens: int = 500) -> float:
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


def get_model_pricing(model_id: str):
    """Get pricing for a model."""
    return MODEL_PRICING.get(model_id)
