"""Tests for llm.router module."""

import pytest

try:
    from codomyrmex.llm.router import (
        CostTracker,
        FallbackChain,
        ModelConfig,
        ModelRouter,
        ModelStats,
        RoutingStrategy,
    )
    HAS_MODULE = True
except ImportError:
    HAS_MODULE = False

if not HAS_MODULE:
    pytest.skip("llm.router module not available", allow_module_level=True)


@pytest.mark.unit
class TestRoutingStrategy:
    def test_priority(self):
        assert RoutingStrategy.PRIORITY is not None

    def test_round_robin(self):
        assert RoutingStrategy.ROUND_ROBIN is not None

    def test_random(self):
        assert RoutingStrategy.RANDOM is not None

    def test_cost_optimized(self):
        assert RoutingStrategy.COST_OPTIMIZED is not None

    def test_latency_optimized(self):
        assert RoutingStrategy.LATENCY_OPTIMIZED is not None


@pytest.mark.unit
class TestModelConfig:
    def test_create_config(self):
        config = ModelConfig(name="gpt-4", provider="openai", model_id="gpt-4")
        assert config.name == "gpt-4"
        assert config.provider == "openai"

    def test_config_defaults(self):
        config = ModelConfig(name="test", provider="test", model_id="test")
        assert config.priority == 0
        assert config.cost_per_1k_input == 0.0
        assert config.max_tokens == 4096
        assert config.rate_limit == 100
        assert config.enabled is True

    def test_config_with_capabilities(self):
        config = ModelConfig(
            name="claude",
            provider="anthropic",
            model_id="claude-3",
            capabilities=["vision", "tools"],
        )
        assert "vision" in config.capabilities


@pytest.mark.unit
class TestModelStats:
    def test_create_stats(self):
        stats = ModelStats()
        assert stats.success_count == 0
        assert stats.failure_count == 0
        assert stats.total_latency_ms == 0.0

    def test_avg_latency(self):
        stats = ModelStats(success_count=10, total_latency_ms=5000.0)
        assert stats.avg_latency_ms == 500.0

    def test_success_rate(self):
        stats = ModelStats(success_count=8, failure_count=2)
        assert stats.success_rate == 0.8


@pytest.mark.unit
class TestModelRouter:
    def test_create_router(self):
        router = ModelRouter()
        assert router is not None

    def test_create_with_strategy(self):
        router = ModelRouter(strategy=RoutingStrategy.COST_OPTIMIZED)
        assert router is not None

    def test_register_model(self):
        router = ModelRouter()
        config = ModelConfig(name="test", provider="test", model_id="test")
        router.register_model(config)
        stats = router.get_stats("test")
        assert stats is not None

    def test_select_model(self):
        router = ModelRouter()
        config = ModelConfig(name="test", provider="test", model_id="test")
        router.register_model(config)
        selected = router.select_model()
        assert selected is not None


@pytest.mark.unit
class TestFallbackChain:
    def test_create_chain(self):
        chain = FallbackChain(models=["gpt-4", "gpt-3.5"])
        assert chain is not None


@pytest.mark.unit
class TestCostTracker:
    def test_create_tracker(self):
        tracker = CostTracker()
        assert tracker is not None

    def test_record_and_total(self):
        tracker = CostTracker()
        tracker.record("gpt-4", input_tokens=100, output_tokens=50, cost=0.01)
        total = tracker.get_total_cost()
        assert total >= 0.01

    def test_usage_report(self):
        tracker = CostTracker()
        report = tracker.get_usage_report()
        assert isinstance(report, dict)
