import pytest

from codomyrmex.cost_management.mcp_tools import (
    _budget_manager,
    _tracker,
    cost_management_can_spend,
    cost_management_check_budgets,
    cost_management_create_budget,
    cost_management_get_summary,
    cost_management_record_cost,
)


@pytest.fixture(autouse=True)
def reset_cost_management_state():
    """Reset the global tracker and budget manager before each test."""
    _tracker.store.clear()
    _budget_manager._budgets.clear()
    _budget_manager._triggered_alerts.clear()
    _tracker._counter = 0


@pytest.mark.unit
def test_cost_management_record_cost():
    """Test recording a cost via MCP tool."""
    result = cost_management_record_cost(
        amount=10.5,
        category="compute",
        description="Test compute cost",
        resource_id="vm-1",
        tags={"env": "prod"},
    )

    assert result["amount"] == 10.5
    assert result["category"] == "compute"
    assert result["description"] == "Test compute cost"
    assert result["resource_id"] == "vm-1"
    assert result["tags"] == {"env": "prod"}
    assert "id" in result

    # Test invalid category
    error_result = cost_management_record_cost(
        amount=10.5,
        category="invalid_category",
    )
    assert "error" in error_result


@pytest.mark.unit
def test_cost_management_get_summary():
    """Test getting cost summary via MCP tool."""
    # Add some data
    cost_management_record_cost(amount=10.0, category="compute", tags={"env": "test"})
    cost_management_record_cost(amount=20.0, category="storage", tags={"env": "test"})
    cost_management_record_cost(amount=30.0, category="compute", tags={"env": "prod"})

    # Get overall summary
    summary = cost_management_get_summary()
    assert summary["total"] == 60.0
    assert summary["entry_count"] == 3
    assert summary["by_category"]["compute"] == 40.0
    assert summary["by_category"]["storage"] == 20.0

    # Filter by category
    compute_summary = cost_management_get_summary(category="compute")
    assert compute_summary["total"] == 40.0
    assert compute_summary["entry_count"] == 2

    # Filter by tags
    test_env_summary = cost_management_get_summary(tags_filter={"env": "test"})
    assert test_env_summary["total"] == 30.0
    assert test_env_summary["entry_count"] == 2

    # Test invalid category
    error_cat_summary = cost_management_get_summary(category="invalid")
    assert "error" in error_cat_summary

    # Test invalid period
    error_per_summary = cost_management_get_summary(period="invalid")
    assert "error" in error_per_summary


@pytest.mark.unit
def test_cost_management_create_budget():
    """Test creating a budget via MCP tool."""
    budget = cost_management_create_budget(
        name="Test Budget",
        amount=100.0,
        period="daily",
        category="compute",
        tags_filter={"env": "prod"},
    )

    assert budget["name"] == "Test Budget"
    assert budget["amount"] == 100.0
    assert budget["period"] == "daily"
    assert budget["category"] == "compute"
    assert budget["tags_filter"] == {"env": "prod"}
    assert budget["id"] == "test_budget"

    # Check that budget is actually added to manager
    assert "test_budget" in _budget_manager._budgets

    # Test invalid period
    error_budget_per = cost_management_create_budget(
        name="Bad Period", amount=100.0, period="invalid"
    )
    assert "error" in error_budget_per

    # Test invalid category
    error_budget_cat = cost_management_create_budget(
        name="Bad Cat", amount=100.0, period="daily", category="invalid"
    )
    assert "error" in error_budget_cat


@pytest.mark.unit
def test_cost_management_check_budgets():
    """Test checking budgets via MCP tool."""
    cost_management_create_budget(
        name="Daily Compute",
        amount=100.0,
        period="daily",
        category="compute",
        alert_thresholds=[0.5, 0.9],
    )

    # Spend 60 (60% utilization, crosses 0.5 threshold)
    cost_management_record_cost(amount=60.0, category="compute")

    alerts = cost_management_check_budgets()
    assert len(alerts) == 1
    assert alerts[0]["budget_id"] == "daily_compute"
    assert alerts[0]["threshold"] == 0.5
    assert alerts[0]["current_spend"] == 60.0

    # Spend 35 more (95% utilization, crosses 0.9 threshold)
    cost_management_record_cost(amount=35.0, category="compute")

    alerts = cost_management_check_budgets()
    assert len(alerts) == 1  # Only the new 0.9 alert, 0.5 already triggered
    assert alerts[0]["threshold"] == 0.9
    assert alerts[0]["current_spend"] == 95.0


@pytest.mark.unit
def test_cost_management_can_spend():
    """Test spend gating via MCP tool."""
    cost_management_create_budget(
        name="Daily Compute",
        amount=100.0,
        period="daily",
        category="compute",
    )

    # Should be able to spend 90
    assert cost_management_can_spend(amount=90.0, category="compute") is True

    # Record spend of 90
    cost_management_record_cost(amount=90.0, category="compute")

    # Should not be able to spend 20 more (exceeds 100 budget)
    assert cost_management_can_spend(amount=20.0, category="compute") is False

    # Should still be able to spend 20 on a different category
    assert cost_management_can_spend(amount=20.0, category="storage") is True

    # Test invalid category gracefully returns False (or depends on implementation)
    assert cost_management_can_spend(amount=10.0, category="invalid") is False
