"""Unit tests for cost_management module."""

from datetime import datetime, timedelta

import pytest

from codomyrmex.cost_management import (
    Budget,
    BudgetAlert,
    BudgetManager,
    BudgetPeriod,
    CostCategory,
    CostEntry,
    CostTracker,
    InMemoryCostStore,
    JSONCostStore,
)


@pytest.mark.unit
class TestCostManagementImports:
    """Test suite for cost_management module imports."""

    def test_module_imports(self):
        """Verify module can be imported without errors."""
        from codomyrmex import cost_management

        assert cost_management is not None

    def test_public_api_exists(self):
        """Verify expected public API is available."""
        from codomyrmex.cost_management import __all__

        expected_exports = [
            "CostCategory",
            "BudgetPeriod",
            "CostEntry",
            "Budget",
            "CostSummary",
            "BudgetAlert",
            "CostStore",
            "InMemoryCostStore",
            "JSONCostStore",
            "CostTracker",
            "BudgetManager",
        ]
        for export in expected_exports:
            assert export in __all__, f"Missing export: {export}"


@pytest.mark.unit
class TestCostCategory:
    """Test suite for CostCategory enum."""

    def test_cost_category_values(self):
        """Verify all cost categories are available."""
        assert CostCategory.LLM_INFERENCE.value == "llm_inference"
        assert CostCategory.LLM_EMBEDDING.value == "llm_embedding"
        assert CostCategory.LLM_FINE_TUNING.value == "llm_fine_tuning"
        assert CostCategory.COMPUTE.value == "compute"
        assert CostCategory.STORAGE.value == "storage"
        assert CostCategory.NETWORK.value == "network"
        assert CostCategory.API_CALLS.value == "api_calls"
        assert CostCategory.DATABASE.value == "database"
        assert CostCategory.LICENSE.value == "license"
        assert CostCategory.OTHER.value == "other"


@pytest.mark.unit
class TestBudgetPeriod:
    """Test suite for BudgetPeriod enum."""

    def test_budget_period_values(self):
        """Verify all budget periods are available."""
        assert BudgetPeriod.HOURLY.value == "hourly"
        assert BudgetPeriod.DAILY.value == "daily"
        assert BudgetPeriod.WEEKLY.value == "weekly"
        assert BudgetPeriod.MONTHLY.value == "monthly"
        assert BudgetPeriod.YEARLY.value == "yearly"


@pytest.mark.unit
class TestCostEntry:
    """Test suite for CostEntry dataclass."""

    def test_cost_entry_creation(self):
        """Verify CostEntry can be created with required fields."""
        entry = CostEntry(
            id="cost_1",
            amount=0.05,
            category=CostCategory.LLM_INFERENCE,
        )

        assert entry.id == "cost_1"
        assert entry.amount == 0.05
        assert entry.category == CostCategory.LLM_INFERENCE
        assert entry.description == ""
        assert entry.resource_id == ""
        assert entry.tags == {}

    def test_cost_entry_to_dict(self):
        """Verify CostEntry serialization to dict."""
        entry = CostEntry(
            id="cost_2",
            amount=1.50,
            category=CostCategory.COMPUTE,
            description="Test compute cost",
            tags={"project": "alpha"},
            metadata={"source": "test"},
        )

        result = entry.to_dict()
        assert result["id"] == "cost_2"
        assert result["amount"] == 1.50
        assert result["category"] == "compute"
        assert result["description"] == "Test compute cost"
        assert result["tags"] == {"project": "alpha"}
        assert result["metadata"] == {"source": "test"}

    def test_cost_entry_from_dict(self):
        """Verify CostEntry can be created from dict."""
        data = {
            "id": "cost_3",
            "amount": 2.50,
            "category": "storage",
            "description": "Disk usage",
            "resource_id": "vol-123",
            "tags": {"env": "prod"},
            "timestamp": "2024-01-01T12:00:00",
            "metadata": {"info": "none"},
        }
        entry = CostEntry.from_dict(data)
        assert entry.id == "cost_3"
        assert entry.amount == 2.50
        assert entry.category == CostCategory.STORAGE
        assert entry.timestamp == datetime(2024, 1, 1, 12, 0, 0)


@pytest.mark.unit
class TestBudget:
    """Test suite for Budget dataclass."""

    def test_budget_creation(self):
        """Verify Budget can be created."""
        budget = Budget(
            id="daily_llm",
            name="Daily LLM Budget",
            amount=100.0,
            period=BudgetPeriod.DAILY,
            category=CostCategory.LLM_INFERENCE,
        )

        assert budget.id == "daily_llm"
        assert budget.amount == 100.0
        assert budget.period == BudgetPeriod.DAILY
        assert 0.5 in budget.alert_thresholds

    def test_budget_get_period_start_daily(self):
        """Verify daily period start calculation."""
        budget = Budget(id="test", name="Test", amount=100.0, period=BudgetPeriod.DAILY)
        reference = datetime(2024, 1, 15, 14, 30, 45)

        period_start = budget.get_period_start(reference)
        assert period_start.hour == 0
        assert period_start.minute == 0
        assert period_start.second == 0

    def test_budget_get_period_start_hourly(self):
        """Verify hourly period start calculation."""
        budget = Budget(id="test", name="Test", amount=50.0, period=BudgetPeriod.HOURLY)
        reference = datetime(2024, 1, 15, 14, 30, 45)

        period_start = budget.get_period_start(reference)
        assert period_start.hour == 14
        assert period_start.minute == 0
        assert period_start.second == 0

    def test_budget_get_period_start_yearly(self):
        """Verify yearly period start calculation."""
        budget = Budget(id="test", name="Test", amount=5000.0, period=BudgetPeriod.YEARLY)
        reference = datetime(2024, 6, 15, 14, 30, 45)

        period_start = budget.get_period_start(reference)
        assert period_start.year == 2024
        assert period_start.month == 1
        assert period_start.day == 1

    def test_budget_is_match(self):
        """Verify budget filter matching."""
        budget = Budget(
            id="test",
            name="Test",
            amount=100.0,
            period=BudgetPeriod.DAILY,
            category=CostCategory.COMPUTE,
            tags_filter={"env": "prod"},
        )

        match_entry = CostEntry(
            id="1", amount=1.0, category=CostCategory.COMPUTE, tags={"env": "prod"}
        )
        non_match_entry_cat = CostEntry(
            id="2", amount=1.0, category=CostCategory.STORAGE, tags={"env": "prod"}
        )
        non_match_entry_tags = CostEntry(
            id="3", amount=1.0, category=CostCategory.COMPUTE, tags={"env": "dev"}
        )

        assert budget.is_match(match_entry) is True
        assert budget.is_match(non_match_entry_cat) is False
        assert budget.is_match(non_match_entry_tags) is False


@pytest.mark.unit
class TestBudgetAlert:
    """Test suite for BudgetAlert dataclass."""

    def test_budget_alert_utilization(self):
        """Verify utilization calculation."""
        alert = BudgetAlert(
            budget_id="test_budget",
            threshold=0.8,
            current_spend=80.0,
            budget_amount=100.0,
        )

        assert alert.utilization == 0.8

    def test_budget_alert_message(self):
        """Verify alert message generation."""
        alert = BudgetAlert(
            budget_id="test_budget",
            threshold=0.9,
            current_spend=90.0,
            budget_amount=100.0,
        )

        message = alert.message
        assert "test_budget" in message
        assert "90%" in message


@pytest.mark.unit
class TestInMemoryCostStore:
    """Test suite for InMemoryCostStore."""

    def test_store_save_and_retrieve(self):
        """Verify entries can be saved and retrieved."""
        store = InMemoryCostStore()
        entry = CostEntry(
            id="test_1",
            amount=10.0,
            category=CostCategory.COMPUTE,
        )

        store.save_entry(entry)
        all_entries = store.get_all()

        assert len(all_entries) == 1
        assert all_entries[0].id == "test_1"

    def test_store_get_entries_with_filters(self):
        """Verify filtering by date range, category, and tags."""
        store = InMemoryCostStore()

        now = datetime.now()
        yesterday = now - timedelta(days=1)

        store.save_entry(
            CostEntry(
                id="e1",
                amount=10.0,
                category=CostCategory.COMPUTE,
                timestamp=now,
                tags={"env": "prod"},
            )
        )
        store.save_entry(
            CostEntry(
                id="e2",
                amount=5.0,
                category=CostCategory.STORAGE,
                timestamp=now,
                tags={"env": "prod"},
            )
        )
        store.save_entry(
            CostEntry(
                id="e3",
                amount=3.0,
                category=CostCategory.COMPUTE,
                timestamp=yesterday,
                tags={"env": "dev"},
            )
        )

        # Date range only
        entries = store.get_entries(now - timedelta(hours=1), now + timedelta(hours=1))
        assert len(entries) == 2

        # Date range + category
        entries = store.get_entries(
            now - timedelta(hours=1), now + timedelta(hours=1), category=CostCategory.COMPUTE
        )
        assert len(entries) == 1
        assert entries[0].id == "e1"

        # Date range + tags
        entries = store.get_entries(
            datetime.min, datetime.max, tags_filter={"env": "dev"}
        )
        assert len(entries) == 1
        assert entries[0].id == "e3"

    def test_store_clear(self):
        """Verify store can be cleared."""
        store = InMemoryCostStore()
        store.save_entry(CostEntry(id="1", amount=5.0, category=CostCategory.OTHER))
        store.save_entry(CostEntry(id="2", amount=10.0, category=CostCategory.OTHER))

        store.clear()
        assert len(store.get_all()) == 0


@pytest.mark.unit
class TestJSONCostStore:
    """Test suite for JSONCostStore."""

    def test_json_store_save_and_load(self, tmp_path):
        """Verify JSON storage persistence."""
        file_path = tmp_path / "costs.json"
        store = JSONCostStore(file_path)

        entry = CostEntry(
            id="json_1",
            amount=15.0,
            category=CostCategory.NETWORK,
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
        )

        store.save_entry(entry)

        # Create a new store instance pointing to same file
        new_store = JSONCostStore(file_path)
        entries = new_store.get_entries(datetime.min, datetime.max)

        assert len(entries) == 1
        assert entries[0].id == "json_1"
        assert entries[0].amount == 15.0
        assert entries[0].category == CostCategory.NETWORK


@pytest.mark.unit
class TestCostTracker:
    """Test suite for CostTracker."""

    def test_tracker_record_cost(self):
        """Verify costs can be recorded."""
        tracker = CostTracker()
        entry = tracker.record(
            amount=0.05,
            category=CostCategory.LLM_INFERENCE,
            description="GPT-4 call",
        )

        assert entry.amount == 0.05
        assert entry.category == CostCategory.LLM_INFERENCE
        assert entry.id.startswith("cost_")

    def test_tracker_get_summary(self):
        """Verify cost summary generation."""
        tracker = CostTracker()
        tracker.record(amount=10.0, category=CostCategory.COMPUTE)
        tracker.record(amount=5.0, category=CostCategory.COMPUTE)
        tracker.record(amount=3.0, category=CostCategory.STORAGE)

        summary = tracker.get_summary()

        assert summary.total == 18.0
        assert summary.entry_count == 3
        assert summary.by_category["compute"] == 15.0
        assert summary.by_category["storage"] == 3.0

    def test_tracker_get_total_by_category(self):
        """Verify total cost retrieval by category."""
        tracker = CostTracker()
        tracker.record(amount=20.0, category=CostCategory.LLM_INFERENCE)
        tracker.record(amount=10.0, category=CostCategory.NETWORK)

        total = tracker.get_total(category=CostCategory.LLM_INFERENCE)
        assert total == 20.0


@pytest.mark.unit
class TestBudgetManager:
    """Test suite for BudgetManager."""

    def test_manager_create_budget(self):
        """Verify budget creation."""
        tracker = CostTracker()
        manager = BudgetManager(tracker)

        budget = manager.create(
            name="Daily API",
            amount=50.0,
            period=BudgetPeriod.DAILY,
            category=CostCategory.API_CALLS,
        )

        assert budget.name == "Daily API"
        assert budget.amount == 50.0
        assert budget.id == "daily_api"

    def test_manager_list_budgets(self):
        """Verify listing all budgets."""
        tracker = CostTracker()
        manager = BudgetManager(tracker)

        manager.create(name="Budget A", amount=100.0, period=BudgetPeriod.DAILY)
        manager.create(name="Budget B", amount=200.0, period=BudgetPeriod.WEEKLY)

        budgets = manager.list_budgets()
        assert len(budgets) == 2

    def test_manager_can_spend(self):
        """Verify spend allowance check."""
        tracker = CostTracker()
        manager = BudgetManager(tracker)

        manager.create(
            name="Compute Budget",
            amount=100.0,
            period=BudgetPeriod.DAILY,
            category=CostCategory.COMPUTE,
        )

        # Should allow spend within budget
        assert manager.can_spend(50.0, category=CostCategory.COMPUTE) is True

        # Should block spend exceeding budget
        assert manager.can_spend(150.0, category=CostCategory.COMPUTE) is False

        # Should ignore spend for different categories
        assert manager.can_spend(200.0, category=CostCategory.STORAGE) is True

    def test_manager_check_budgets_generates_alerts(self):
        """Verify budget check generates alerts when threshold exceeded."""
        tracker = CostTracker()
        manager = BudgetManager(tracker)

        manager.create(
            name="Small Budget",
            amount=10.0,
            period=BudgetPeriod.DAILY,
            alert_thresholds=[0.5],
        )

        # Record cost that exceeds 50%
        tracker.record(amount=6.0, category=CostCategory.OTHER)

        alerts = manager.check_budgets()
        assert len(alerts) >= 1
        assert alerts[0].threshold == 0.5

        # Check again - alert should not be duplicated
        new_alerts = manager.check_budgets()
        assert len(new_alerts) == 0

    def test_manager_reset_alerts(self):
        """Verify alert reset."""
        tracker = CostTracker()
        manager = BudgetManager(tracker)

        manager.create(
            name="Small Budget",
            amount=10.0,
            period=BudgetPeriod.DAILY,
            alert_thresholds=[0.5],
        )

        tracker.record(amount=6.0, category=CostCategory.OTHER)
        manager.check_budgets()

        manager.reset_period_alerts()

        # Should fire alert again after reset
        alerts = manager.check_budgets()
        assert len(alerts) == 1
