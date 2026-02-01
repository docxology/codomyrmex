"""
Tests for Cost Management Module
"""

import pytest
from datetime import datetime, timedelta
from codomyrmex.cost_management import (
    CostCategory,
    BudgetPeriod,
    CostEntry,
    Budget,
    CostSummary,
    BudgetAlert,
    InMemoryCostStore,
    CostTracker,
    BudgetManager,
)


class TestCostEntry:
    """Tests for CostEntry."""
    
    def test_create(self):
        """Should create cost entry."""
        entry = CostEntry(
            id="c1",
            amount=0.05,
            category=CostCategory.LLM_INFERENCE,
        )
        assert entry.amount == 0.05
    
    def test_to_dict(self):
        """Should convert to dict."""
        entry = CostEntry(id="c1", amount=1.0, category=CostCategory.COMPUTE)
        d = entry.to_dict()
        
        assert d["amount"] == 1.0
        assert d["category"] == "compute"


class TestBudget:
    """Tests for Budget."""
    
    def test_get_period_start_daily(self):
        """Should get daily period start."""
        budget = Budget(id="b1", name="Daily", amount=100, period=BudgetPeriod.DAILY)
        
        ref = datetime(2024, 1, 15, 14, 30)
        start = budget.get_period_start(ref)
        
        assert start.hour == 0
        assert start.minute == 0
    
    def test_get_period_start_monthly(self):
        """Should get monthly period start."""
        budget = Budget(id="b1", name="Monthly", amount=1000, period=BudgetPeriod.MONTHLY)
        
        ref = datetime(2024, 1, 15, 14, 30)
        start = budget.get_period_start(ref)
        
        assert start.day == 1


class TestInMemoryCostStore:
    """Tests for InMemoryCostStore."""
    
    def test_save_and_get(self):
        """Should save and retrieve entries."""
        store = InMemoryCostStore()
        entry = CostEntry(id="c1", amount=1.0, category=CostCategory.LLM_INFERENCE)
        store.save_entry(entry)
        
        entries = store.get_entries(
            start=datetime.min,
            end=datetime.now() + timedelta(days=1),
        )
        assert len(entries) == 1
    
    def test_filter_by_date(self):
        """Should filter by date."""
        store = InMemoryCostStore()
        
        old = CostEntry(id="c1", amount=1.0, category=CostCategory.LLM_INFERENCE)
        old.timestamp = datetime(2020, 1, 1)
        store.save_entry(old)
        
        new = CostEntry(id="c2", amount=2.0, category=CostCategory.LLM_INFERENCE)
        store.save_entry(new)
        
        entries = store.get_entries(
            start=datetime(2024, 1, 1),
            end=datetime.now() + timedelta(days=1),
        )
        assert len(entries) == 1


class TestCostTracker:
    """Tests for CostTracker."""
    
    def test_record(self):
        """Should record costs."""
        tracker = CostTracker()
        entry = tracker.record(
            amount=0.05,
            category=CostCategory.LLM_INFERENCE,
            description="GPT-4 call",
        )
        
        assert entry.amount == 0.05
    
    def test_get_summary(self):
        """Should get cost summary."""
        tracker = CostTracker()
        tracker.record(1.0, category=CostCategory.LLM_INFERENCE)
        tracker.record(2.0, category=CostCategory.LLM_EMBEDDING)
        tracker.record(1.5, category=CostCategory.LLM_INFERENCE)
        
        summary = tracker.get_summary()
        
        assert summary.total == 4.5
        assert summary.by_category["llm_inference"] == 2.5
        assert summary.entry_count == 3
    
    def test_get_summary_with_tags(self):
        """Should track costs by tags."""
        tracker = CostTracker()
        tracker.record(1.0, tags={"model": "gpt-4"})
        tracker.record(0.5, tags={"model": "gpt-3.5"})
        tracker.record(2.0, tags={"model": "gpt-4"})
        
        summary = tracker.get_summary()
        
        assert summary.by_tag["model"]["gpt-4"] == 3.0
        assert summary.by_tag["model"]["gpt-3.5"] == 0.5
    
    def test_get_total(self):
        """Should get total cost."""
        tracker = CostTracker()
        tracker.record(5.0, category=CostCategory.LLM_INFERENCE)
        tracker.record(10.0, category=CostCategory.COMPUTE)
        
        assert tracker.get_total() == 15.0
        assert tracker.get_total(category=CostCategory.LLM_INFERENCE) == 5.0


class TestBudgetManager:
    """Tests for BudgetManager."""
    
    def test_create_budget(self):
        """Should create budget."""
        tracker = CostTracker()
        manager = BudgetManager(tracker)
        
        budget = manager.create(
            name="Daily LLM",
            amount=100.0,
            period=BudgetPeriod.DAILY,
        )
        
        assert budget.amount == 100.0
    
    def test_get_utilization(self):
        """Should calculate utilization."""
        tracker = CostTracker()
        manager = BudgetManager(tracker)
        
        manager.create("test", amount=100.0, period=BudgetPeriod.DAILY)
        tracker.record(50.0)
        
        budget = manager.get_budget("test")
        util = manager.get_utilization(budget)
        
        assert util == 0.5
    
    def test_check_budgets_alert(self):
        """Should generate alerts."""
        tracker = CostTracker()
        manager = BudgetManager(tracker)
        
        manager.create(
            name="test",
            amount=100.0,
            period=BudgetPeriod.DAILY,
            alert_thresholds=[0.5, 0.8],
        )
        
        tracker.record(60.0)  # 60% utilization
        
        alerts = manager.check_budgets()
        assert len(alerts) == 1
        assert alerts[0].threshold == 0.5
    
    def test_can_spend(self):
        """Should check if can spend."""
        tracker = CostTracker()
        manager = BudgetManager(tracker)
        
        manager.create("test", amount=100.0, period=BudgetPeriod.DAILY)
        tracker.record(90.0)
        
        assert manager.can_spend(5.0, "test") is True
        assert manager.can_spend(20.0, "test") is False


class TestBudgetAlert:
    """Tests for BudgetAlert."""
    
    def test_utilization(self):
        """Should calculate utilization."""
        alert = BudgetAlert(
            budget_id="test",
            threshold=0.8,
            current_spend=80.0,
            budget_amount=100.0,
        )
        
        assert alert.utilization == 0.8
    
    def test_message(self):
        """Should generate message."""
        alert = BudgetAlert(
            budget_id="test",
            threshold=0.8,
            current_spend=80.0,
            budget_amount=100.0,
        )
        
        assert "80%" in alert.message
        assert "test" in alert.message


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
