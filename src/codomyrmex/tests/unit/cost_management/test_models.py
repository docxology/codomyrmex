"""Tests for cost_management.models."""

from datetime import datetime

from codomyrmex.cost_management.models import (
    Budget,
    BudgetAlert,
    BudgetPeriod,
    CostCategory,
    CostEntry,
    CostSummary,
)


class TestCostCategory:
    def test_all_values(self):
        values = {c.value for c in CostCategory}
        assert "llm_inference" in values
        assert "compute" in values
        assert "storage" in values
        assert "network" in values
        assert "other" in values

    def test_construction(self):
        assert CostCategory("llm_inference") == CostCategory.LLM_INFERENCE


class TestBudgetPeriod:
    def test_all_values(self):
        values = {p.value for p in BudgetPeriod}
        assert "hourly" in values
        assert "daily" in values
        assert "weekly" in values
        assert "monthly" in values
        assert "yearly" in values


class TestCostEntry:
    def test_construction(self):
        entry = CostEntry(id="e1", amount=1.50, category=CostCategory.LLM_INFERENCE)
        assert entry.id == "e1"
        assert entry.amount == 1.50
        assert entry.category == CostCategory.LLM_INFERENCE
        assert entry.description == ""

    def test_to_dict(self):
        entry = CostEntry(
            id="e1", amount=2.00, category=CostCategory.COMPUTE,
            description="EC2 instance", resource_id="i-abc123"
        )
        d = entry.to_dict()
        assert d["id"] == "e1"
        assert d["amount"] == 2.00
        assert d["category"] == "compute"
        assert d["description"] == "EC2 instance"
        assert d["resource_id"] == "i-abc123"
        assert "timestamp" in d

    def test_from_dict_roundtrip(self):
        entry = CostEntry(
            id="e1", amount=3.00, category=CostCategory.STORAGE,
            tags={"env": "prod"}, resource_id="vol-123"
        )
        d = entry.to_dict()
        restored = CostEntry.from_dict(d)
        assert restored.id == "e1"
        assert restored.amount == 3.00
        assert restored.category == CostCategory.STORAGE
        assert restored.tags == {"env": "prod"}

    def test_independent_default_tags(self):
        e1 = CostEntry(id="a", amount=1.0, category=CostCategory.OTHER)
        e2 = CostEntry(id="b", amount=2.0, category=CostCategory.OTHER)
        e1.tags["key"] = "val"
        assert e2.tags == {}


class TestBudget:
    def _make_entry(self, category=CostCategory.COMPUTE, tags=None) -> CostEntry:
        return CostEntry(
            id="e1", amount=1.0, category=category, tags=tags or {}
        )

    def test_construction(self):
        b = Budget(id="b1", name="Monthly Compute", amount=1000.0, period=BudgetPeriod.MONTHLY)
        assert b.id == "b1"
        assert b.amount == 1000.0
        assert b.alert_thresholds == [0.5, 0.8, 0.9, 1.0]

    def test_is_match_no_filters(self):
        b = Budget(id="b1", name="All", amount=100.0, period=BudgetPeriod.DAILY)
        entry = self._make_entry()
        assert b.is_match(entry) is True

    def test_is_match_category_filter_match(self):
        b = Budget(id="b1", name="Compute", amount=100.0, period=BudgetPeriod.DAILY, category=CostCategory.COMPUTE)
        entry = self._make_entry(category=CostCategory.COMPUTE)
        assert b.is_match(entry) is True

    def test_is_match_category_filter_no_match(self):
        b = Budget(id="b1", name="LLM", amount=100.0, period=BudgetPeriod.DAILY, category=CostCategory.LLM_INFERENCE)
        entry = self._make_entry(category=CostCategory.COMPUTE)
        assert b.is_match(entry) is False

    def test_is_match_tags_filter(self):
        b = Budget(id="b1", name="Prod", amount=100.0, period=BudgetPeriod.DAILY, tags_filter={"env": "prod"})
        entry_match = self._make_entry(tags={"env": "prod", "team": "ml"})
        entry_no_match = self._make_entry(tags={"env": "dev"})
        assert b.is_match(entry_match) is True
        assert b.is_match(entry_no_match) is False

    def test_get_period_start_hourly(self):
        b = Budget(id="b1", name="h", amount=10.0, period=BudgetPeriod.HOURLY)
        ref = datetime(2024, 6, 15, 14, 32, 45)
        start = b.get_period_start(ref)
        assert start.hour == 14
        assert start.minute == 0
        assert start.second == 0

    def test_get_period_start_daily(self):
        b = Budget(id="b1", name="d", amount=10.0, period=BudgetPeriod.DAILY)
        ref = datetime(2024, 6, 15, 14, 32, 45)
        start = b.get_period_start(ref)
        assert start.hour == 0
        assert start.minute == 0

    def test_get_period_start_monthly(self):
        b = Budget(id="b1", name="m", amount=10.0, period=BudgetPeriod.MONTHLY)
        ref = datetime(2024, 6, 15, 14, 0, 0)
        start = b.get_period_start(ref)
        assert start.day == 1
        assert start.month == 6

    def test_get_period_start_yearly(self):
        b = Budget(id="b1", name="y", amount=10.0, period=BudgetPeriod.YEARLY)
        ref = datetime(2024, 6, 15)
        start = b.get_period_start(ref)
        assert start.month == 1
        assert start.day == 1
        assert start.year == 2024


class TestCostSummary:
    def test_defaults(self):
        s = CostSummary()
        assert s.total == 0.0
        assert s.entry_count == 0
        assert s.by_category == {}
        assert s.period_start is None

    def test_to_dict_with_periods(self):
        s = CostSummary(
            total=100.0,
            entry_count=5,
            period_start=datetime(2024, 1, 1),
            period_end=datetime(2024, 1, 31),
        )
        d = s.to_dict()
        assert d["total"] == 100.0
        assert d["entry_count"] == 5
        assert "2024-01-01" in d["period_start"]

    def test_to_dict_none_periods(self):
        s = CostSummary()
        d = s.to_dict()
        assert d["period_start"] is None
        assert d["period_end"] is None

    def test_independent_defaults(self):
        s1 = CostSummary()
        s2 = CostSummary()
        s1.by_category["compute"] = 50.0
        assert "compute" not in s2.by_category


class TestBudgetAlert:
    def test_utilization(self):
        alert = BudgetAlert(
            budget_id="b1", threshold=0.8, current_spend=80.0, budget_amount=100.0
        )
        assert alert.utilization == 0.8

    def test_utilization_zero_budget(self):
        alert = BudgetAlert(
            budget_id="b1", threshold=0.8, current_spend=50.0, budget_amount=0.0
        )
        assert alert.utilization == 0.0

    def test_message_contains_id(self):
        alert = BudgetAlert(
            budget_id="monthly-compute", threshold=0.9,
            current_spend=900.0, budget_amount=1000.0
        )
        assert "monthly-compute" in alert.message
        assert "90%" in alert.message

    def test_message_contains_amounts(self):
        alert = BudgetAlert(
            budget_id="b1", threshold=0.5,
            current_spend=50.0, budget_amount=100.0
        )
        assert "$50.00" in alert.message
        assert "$100.00" in alert.message
