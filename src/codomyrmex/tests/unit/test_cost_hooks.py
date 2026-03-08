"""Tests for cloud.cost_management.hooks — AutoCostTracker and ModelPricingTable.

Zero-Mock: All tests use real CostTracker with InMemoryCostStore.
"""

from __future__ import annotations

import time

import pytest

from codomyrmex.cloud.cost_management.hooks import (
    AutoCostTracker,
    ModelPricingTable,
    cost_tracked,
)
from codomyrmex.cloud.cost_management.models import CostCategory
from codomyrmex.cloud.cost_management.tracker import CostTracker

# ── ModelPricingTable ─────────────────────────────────────────────────


class TestModelPricingTable:
    """Verify pricing lookup and cost calculation."""

    def test_seeded_defaults(self) -> None:
        table = ModelPricingTable()
        models = table.list_models()
        assert "gpt-4o" in models
        assert "hermes3" in models

    def test_get_price_known_model(self) -> None:
        table = ModelPricingTable()
        price = table.get_price("gpt-4o")
        assert price is not None
        assert price.input_cost_per_1k_tokens > 0

    def test_get_price_unknown_returns_none(self) -> None:
        table = ModelPricingTable()
        assert table.get_price("nonexistent-model-xyz") is None

    def test_set_custom_price(self) -> None:
        table = ModelPricingTable()
        table.set_price("my-model", input_per_1k=0.01, output_per_1k=0.02)
        price = table.get_price("my-model")
        assert price is not None
        assert price.input_cost_per_1k_tokens == 0.01
        assert price.output_cost_per_1k_tokens == 0.02

    def test_calculate_cost_token_based(self) -> None:
        table = ModelPricingTable()
        table.set_price("test", input_per_1k=1.0, output_per_1k=2.0)
        cost = table.calculate_cost("test", input_tokens=1000, output_tokens=500)
        # 1000/1000 * 1.0 + 500/1000 * 2.0 = 1.0 + 1.0 = 2.0
        assert cost == pytest.approx(2.0)

    def test_calculate_cost_per_call(self) -> None:
        table = ModelPricingTable()
        table.set_price("flat", per_call=0.5)
        cost = table.calculate_cost("flat", calls=3)
        assert cost == pytest.approx(1.5)

    def test_calculate_cost_per_second(self) -> None:
        table = ModelPricingTable()
        table.set_price("gpu", per_second=0.001)
        cost = table.calculate_cost("gpu", duration_seconds=10.0)
        assert cost == pytest.approx(0.01)

    def test_calculate_cost_unknown_model_returns_zero(self) -> None:
        table = ModelPricingTable()
        assert table.calculate_cost("unknown-999", input_tokens=1000) == 0.0

    def test_local_models_are_free(self) -> None:
        table = ModelPricingTable()
        assert table.calculate_cost("hermes3", input_tokens=10000) == 0.0
        assert table.calculate_cost("llava", input_tokens=10000) == 0.0


# ── AutoCostTracker ──────────────────────────────────────────────────


class TestAutoCostTracker:
    """Verify automatic cost recording via context manager."""

    def test_track_records_cost_entry(self) -> None:
        tracker = CostTracker()
        auto = AutoCostTracker(tracker)

        with auto.track("openai", "chat.completion", model="gpt-4o") as ctx:
            ctx.set_tokens(input=100, output=50)

        summary = tracker.get_summary()
        assert summary.total > 0
        assert summary.entry_count == 1

    def test_track_with_zero_tokens(self) -> None:
        tracker = CostTracker()
        auto = AutoCostTracker(tracker)

        with auto.track("openai", "embedding"):
            pass  # No tokens set

        summary = tracker.get_summary()
        assert summary.entry_count == 1

    def test_track_tags_include_provider_and_operation(self) -> None:
        tracker = CostTracker()
        auto = AutoCostTracker(tracker)

        with auto.track("gcp", "vision.annotate", model="llava", tags={"env": "test"}):
            pass

        summary = tracker.get_summary()
        entry = summary.entries[0]
        assert entry.tags["provider"] == "gcp"
        assert entry.tags["operation"] == "vision.annotate"
        assert entry.tags["model"] == "llava"
        assert entry.tags["env"] == "test"

    def test_track_records_duration(self) -> None:
        tracker = CostTracker()
        auto = AutoCostTracker(tracker)

        with auto.track("test", "slow_op"):
            time.sleep(0.05)

        summary = tracker.get_summary()
        meta = summary.entries[0].metadata
        assert meta["duration_ms"] >= 40  # ~50ms ± tolerance

    def test_track_records_token_metadata(self) -> None:
        tracker = CostTracker()
        auto = AutoCostTracker(tracker)

        with auto.track("openai", "chat", model="gpt-4o") as ctx:
            ctx.set_tokens(input=200, output=100)

        meta = tracker.get_summary().entries[0].metadata
        assert meta["input_tokens"] == 200
        assert meta["output_tokens"] == 100

    def test_multiple_tracks_accumulate(self) -> None:
        tracker = CostTracker()
        auto = AutoCostTracker(tracker)

        for _ in range(5):
            with auto.track("openai", "chat", model="gpt-4o") as ctx:
                ctx.set_tokens(input=100, output=50)

        summary = tracker.get_summary()
        assert summary.entry_count == 5
        assert summary.total > 0


# ── cost_tracked decorator ───────────────────────────────────────────


class TestCostTrackedDecorator:
    """Verify the decorator records cost entries."""

    def test_decorator_records_on_call(self) -> None:
        tracker = CostTracker()
        auto = AutoCostTracker(tracker)

        @cost_tracked(auto, provider="openai", model="gpt-4o-mini")
        def my_function(x: int) -> int:
            return x * 2

        result = my_function(21)
        assert result == 42
        summary = tracker.get_summary()
        assert summary.entry_count == 1

    def test_decorator_uses_function_name_as_operation(self) -> None:
        tracker = CostTracker()
        auto = AutoCostTracker(tracker)

        @cost_tracked(auto, provider="test")
        def analyze_data() -> str:
            return "done"

        analyze_data()
        entry = tracker.get_summary().entries[0]
        assert "analyze_data" in entry.description
