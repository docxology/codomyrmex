"""
Tests for LLM Cost Tracking Module
"""


import pytest

from codomyrmex.llm.cost_tracking import (
    MODEL_PRICING,
    BudgetGuard,
    CostTracker,
    ModelProvider,
    TokenCounter,
    count_tokens,
    estimate_cost,
    get_model_pricing,
)


class TestTokenCounter:
    """Tests for token counting."""

    def test_empty_string(self):
        """Empty string should return 0 tokens."""
        assert TokenCounter.estimate_tokens("") == 0

    def test_short_text(self):
        """Short text should return reasonable token count."""
        tokens = TokenCounter.estimate_tokens("Hello, world!")
        assert 1 <= tokens <= 10

    def test_longer_text(self):
        """Longer text should scale appropriately."""
        short = TokenCounter.estimate_tokens("Hello")
        long = TokenCounter.estimate_tokens("Hello " * 100)
        assert long > short * 50  # Should scale roughly linearly

    def test_different_providers(self):
        """Different providers may have different estimates."""
        text = "This is a test sentence with multiple words."
        openai = TokenCounter.estimate_tokens(text, ModelProvider.OPENAI)
        anthropic = TokenCounter.estimate_tokens(text, ModelProvider.ANTHROPIC)
        # Should be in same ballpark but may differ
        assert 5 <= openai <= 30
        assert 5 <= anthropic <= 30

    def test_messages_tokens(self):
        """Messages should include overhead."""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]
        tokens = TokenCounter.estimate_messages_tokens(messages)
        # Should include content + overhead
        assert tokens > 2  # More than just 2 words


class TestModelPricing:
    """Tests for pricing calculations."""

    def test_pricing_exists(self):
        """Common models should have pricing."""
        assert "gpt-4o" in MODEL_PRICING
        assert "claude-3-5-sonnet" in MODEL_PRICING
        assert "gemini-1.5-pro" in MODEL_PRICING

    def test_cost_calculation(self):
        """Cost calculation should work correctly."""
        pricing = MODEL_PRICING["gpt-4o"]
        cost = pricing.calculate_cost(1000, 1000)
        # 1000 input tokens at $0.0025/1k + 1000 output at $0.01/1k
        expected = 0.0025 + 0.01
        assert abs(cost - expected) < 0.0001

    def test_zero_tokens(self):
        """Zero tokens should cost zero."""
        pricing = MODEL_PRICING["gpt-4o"]
        assert pricing.calculate_cost(0, 0) == 0.0


class TestCostTracker:
    """Tests for cost tracking."""

    def test_record_usage(self):
        """Recording usage should work."""
        tracker = CostTracker()
        record = tracker.record("gpt-4o", 1000, 500)

        assert record.model_id == "gpt-4o"
        assert record.input_tokens == 1000
        assert record.output_tokens == 500
        assert record.cost > 0

    def test_estimate_cost(self):
        """Cost estimation should work."""
        tracker = CostTracker()
        input_tokens, output_tokens, cost = tracker.estimate_cost(
            "gpt-4o", "Hello, how are you?", 100
        )

        assert input_tokens > 0
        assert output_tokens == 100
        assert cost > 0

    def test_summary(self):
        """Summary should aggregate correctly."""
        tracker = CostTracker()
        tracker.record("gpt-4o", 1000, 500)
        tracker.record("gpt-4o", 2000, 1000)

        summary = tracker.get_summary()

        assert summary.total_requests == 2
        assert summary.total_input_tokens == 3000
        assert summary.total_output_tokens == 1500
        assert summary.total_cost > 0

    def test_summary_by_model(self):
        """Summary should break down by model."""
        tracker = CostTracker()
        tracker.record("gpt-4o", 1000, 500)
        tracker.record("claude-3-5-sonnet", 1000, 500)

        summary = tracker.get_summary()

        assert "gpt-4o" in summary.by_model
        assert "claude-3-5-sonnet" in summary.by_model
        assert summary.by_model["gpt-4o"]["requests"] == 1

    def test_period_filter(self):
        """Summary should filter by period."""
        tracker = CostTracker()
        tracker.record("gpt-4o", 1000, 500)

        # Summary for last 7 days should include it
        summary = tracker.get_summary(period_days=7)
        assert summary.total_requests == 1

    def test_get_records(self):
        """Getting records should work."""
        tracker = CostTracker()
        tracker.record("gpt-4o", 1000, 500)
        tracker.record("gpt-4o", 2000, 1000)

        records = tracker.get_records(limit=10)
        assert len(records) == 2

    def test_export_json(self):
        """JSON export should work."""
        tracker = CostTracker()
        tracker.record("gpt-4o", 1000, 500)

        json_output = tracker.export_to_json()
        assert "gpt-4o" in json_output
        assert "1000" in json_output

    def test_clear(self):
        """Clearing should remove all records."""
        tracker = CostTracker()
        tracker.record("gpt-4o", 1000, 500)
        tracker.clear()

        assert len(tracker.get_records()) == 0


class TestBudgetGuard:
    """Tests for budget guarding."""

    def test_within_budget(self):
        """Requests within budget should proceed."""
        guard = BudgetGuard(daily_limit=10.0)
        assert guard.can_proceed(0.05) is True

    def test_exceed_daily_budget(self):
        """Exceeding daily budget should block."""
        guard = BudgetGuard(daily_limit=1.0)
        guard.record_spend(0.9)
        assert guard.can_proceed(0.2) is False

    def test_exceed_total_budget(self):
        """Exceeding total budget should block."""
        guard = BudgetGuard(total_limit=5.0)
        guard.record_spend(4.5)
        assert guard.can_proceed(1.0) is False

    def test_remaining_budget(self):
        """Remaining budget should be calculated."""
        guard = BudgetGuard(daily_limit=10.0, total_limit=100.0)
        guard.record_spend(3.0)

        remaining = guard.get_remaining()
        assert remaining["daily"] == 7.0
        assert remaining["total"] == 97.0

    def test_no_limits(self):
        """Without limits, all requests should proceed."""
        guard = BudgetGuard()
        guard.record_spend(1000000.0)
        assert guard.can_proceed(1000000.0) is True


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_estimate_cost(self):
        """Quick cost estimation should work."""
        cost = estimate_cost("gpt-4o", "Hello world", 100)
        assert cost > 0

    def test_estimate_cost_unknown_model(self):
        """Unknown model should return 0."""
        cost = estimate_cost("unknown-model", "Hello", 100)
        assert cost == 0

    def test_count_tokens(self):
        """Quick token counting should work."""
        tokens = count_tokens("Hello, world!")
        assert tokens > 0

    def test_get_model_pricing(self):
        """Getting model pricing should work."""
        pricing = get_model_pricing("gpt-4o")
        assert pricing is not None
        assert pricing.model_id == "gpt-4o"

        pricing = get_model_pricing("unknown")
        assert pricing is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
