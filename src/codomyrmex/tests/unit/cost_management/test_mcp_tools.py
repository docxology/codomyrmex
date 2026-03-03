"""Unit tests for cost management MCP tools."""

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
from codomyrmex.validation.schemas import ResultStatus


@pytest.fixture(autouse=True)
def reset_stores():
    """Reset the global tracker and budget manager before each test."""
    _tracker.store.clear()
    _budget_manager._budgets.clear()
    _budget_manager._triggered_alerts.clear()
    yield


@pytest.mark.unit
def test_cost_management_record_cost():
    result = cost_management_record_cost(
        amount=10.0,
        category="llm_inference",
        description="Test cost",
    )
    assert result.status == ResultStatus.SUCCESS
    assert result.data["amount"] == 10.0
    assert result.data["category"] == "llm_inference"
    assert result.data["description"] == "Test cost"


@pytest.mark.unit
def test_cost_management_record_cost_invalid_category():
    result = cost_management_record_cost(
        amount=10.0,
        category="invalid_category",
    )
    assert result.status == ResultStatus.FAILURE
    assert "Invalid category" in result.message


@pytest.mark.unit
def test_cost_management_get_summary():
    result = cost_management_get_summary(
        period="daily",
        category="llm_inference",
    )
    assert result.status == ResultStatus.SUCCESS
    assert "total" in result.data
    assert "entry_count" in result.data


@pytest.mark.unit
def test_cost_management_get_summary_invalid():
    result = cost_management_get_summary(
        period="invalid_period",
    )
    assert result.status == ResultStatus.FAILURE
    assert "Invalid period or category" in result.message


@pytest.mark.unit
def test_cost_management_create_budget():
    result = cost_management_create_budget(
        name="Test Budget",
        amount=100.0,
        period="monthly",
        category="llm_inference",
    )
    assert result.status == ResultStatus.SUCCESS
    assert result.data["name"] == "Test Budget"
    assert result.data["amount"] == 100.0
    assert result.data["period"] == "monthly"


@pytest.mark.unit
def test_cost_management_create_budget_invalid():
    result = cost_management_create_budget(
        name="Test Budget",
        amount=100.0,
        period="invalid_period",
    )
    assert result.status == ResultStatus.FAILURE
    assert "Invalid input" in result.message


@pytest.mark.unit
def test_cost_management_can_spend():
    # Create a budget first
    cost_management_create_budget(
        name="Test Budget Spend",
        amount=100.0,
        period="monthly",
        category="llm_inference",
    )

    # First record a cost
    cost_management_record_cost(
        amount=95.0,
        category="llm_inference",
    )

    # We should have $5 left in our budget of $100
    # A $10 spend should be blocked
    result = cost_management_can_spend(
        amount=10.0,
        category="llm_inference",
    )
    assert result.status == ResultStatus.SUCCESS
    # can_spend should return False since 95 + 10 > 100
    assert result.data["can_spend"] is False

    # We should be able to spend $1
    result2 = cost_management_can_spend(
        amount=1.0,
        category="llm_inference",
    )
    assert result2.status == ResultStatus.SUCCESS
    assert result2.data["can_spend"] is True


@pytest.mark.unit
def test_cost_management_can_spend_invalid():
    result = cost_management_can_spend(
        amount=10.0,
        category="invalid_category",
    )
    assert result.status == ResultStatus.FAILURE
    assert "Invalid category" in result.message


@pytest.mark.unit
def test_cost_management_check_budgets():
    # Create a budget first
    cost_management_create_budget(
        name="Test Budget Alerts",
        amount=100.0,
        period="monthly",
        category="llm_inference",
        alert_thresholds=[0.5, 0.8],
    )

    # Record a cost to trigger the 0.5 alert
    cost_management_record_cost(
        amount=60.0,
        category="llm_inference",
    )

    result = cost_management_check_budgets()
    assert result.status == ResultStatus.SUCCESS
    assert len(result.data) == 1
    assert result.data[0]["threshold"] == 0.5
    assert "at 60% utilization" in result.data[0]["message"]
