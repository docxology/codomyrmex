"""Tests for llm.cost_tracking.models."""

from datetime import datetime

from codomyrmex.llm.cost_tracking.models import (
    ModelPricing,
    ModelProvider,
    UsageRecord,
    UsageSummary,
)


class TestModelProvider:
    def test_all_values(self):
        values = {p.value for p in ModelProvider}
        assert "openai" in values
        assert "anthropic" in values
        assert "google" in values
        assert "local" in values

    def test_custom_provider(self):
        assert ModelProvider.CUSTOM.value == "custom"


class TestModelPricing:
    def test_construction(self):
        p = ModelPricing(
            model_id="gpt-4",
            provider=ModelProvider.OPENAI,
            input_cost_per_1k=0.03,
            output_cost_per_1k=0.06,
        )
        assert p.model_id == "gpt-4"
        assert p.provider == ModelProvider.OPENAI
        assert p.currency == "USD"

    def test_calculate_cost_exact(self):
        p = ModelPricing(
            model_id="test",
            provider=ModelProvider.ANTHROPIC,
            input_cost_per_1k=0.01,
            output_cost_per_1k=0.02,
        )
        # 1000 input tokens → $0.01; 1000 output tokens → $0.02 = $0.03
        cost = p.calculate_cost(1000, 1000)
        assert abs(cost - 0.03) < 1e-9

    def test_calculate_cost_zero_tokens(self):
        p = ModelPricing(
            model_id="test",
            provider=ModelProvider.LOCAL,
            input_cost_per_1k=0.01,
            output_cost_per_1k=0.01,
        )
        assert p.calculate_cost(0, 0) == 0.0

    def test_calculate_cost_partial(self):
        p = ModelPricing(
            model_id="test",
            provider=ModelProvider.MISTRAL,
            input_cost_per_1k=0.002,
            output_cost_per_1k=0.002,
        )
        # 500 input tokens = 0.5k × 0.002 = $0.001
        cost = p.calculate_cost(500, 0)
        assert abs(cost - 0.001) < 1e-9

    def test_calculate_cost_large(self):
        p = ModelPricing(
            model_id="claude",
            provider=ModelProvider.ANTHROPIC,
            input_cost_per_1k=0.015,
            output_cost_per_1k=0.075,
            context_window=100000,
        )
        cost = p.calculate_cost(10000, 5000)
        # 10k × 0.015 + 5k × 0.075 = 0.15 + 0.375 = 0.525
        assert abs(cost - 0.525) < 1e-9

    def test_context_window_default(self):
        p = ModelPricing(
            model_id="x",
            provider=ModelProvider.COHERE,
            input_cost_per_1k=0.0,
            output_cost_per_1k=0.0,
        )
        assert p.context_window == 0


class TestUsageRecord:
    def test_construction(self):
        r = UsageRecord(model_id="gpt-4", input_tokens=100, output_tokens=50)
        assert r.model_id == "gpt-4"
        assert r.input_tokens == 100
        assert r.output_tokens == 50

    def test_total_tokens(self):
        r = UsageRecord(model_id="test", input_tokens=800, output_tokens=200)
        assert r.total_tokens == 1000

    def test_timestamp_auto_set(self):
        r = UsageRecord(model_id="m", input_tokens=0, output_tokens=0)
        assert isinstance(r.timestamp, datetime)

    def test_defaults(self):
        r = UsageRecord(model_id="m", input_tokens=0, output_tokens=0)
        assert r.cost == 0.0
        assert r.latency_ms == 0.0
        assert r.metadata == {}

    def test_with_cost(self):
        r = UsageRecord(model_id="m", input_tokens=1000, output_tokens=500, cost=0.045)
        assert r.cost == 0.045

    def test_independent_default_metadata(self):
        r1 = UsageRecord(model_id="a", input_tokens=1, output_tokens=1)
        r2 = UsageRecord(model_id="b", input_tokens=1, output_tokens=1)
        r1.metadata["key"] = "val"
        assert r2.metadata == {}


class TestUsageSummary:
    def _make_summary(self, **kwargs) -> UsageSummary:
        defaults = {
            "period_start": datetime(2024, 1, 1),
            "period_end": datetime(2024, 1, 31),
        }
        defaults.update(kwargs)
        return UsageSummary(**defaults)

    def test_construction(self):
        s = self._make_summary()
        assert s.total_requests == 0
        assert s.total_cost == 0.0
        assert s.by_model == {}

    def test_total_tokens_property(self):
        s = self._make_summary(
            total_input_tokens=5000,
            total_output_tokens=2000,
        )
        assert s.total_tokens == 7000

    def test_with_data(self):
        s = self._make_summary(
            total_requests=100,
            total_input_tokens=50000,
            total_output_tokens=20000,
            total_cost=12.50,
            avg_latency_ms=250.0,
        )
        assert s.total_requests == 100
        assert s.total_cost == 12.50
        assert s.avg_latency_ms == 250.0

    def test_by_model_default_independent(self):
        s1 = self._make_summary()
        s2 = self._make_summary()
        s1.by_model["gpt-4"] = {"requests": 5}
        assert s2.by_model == {}
