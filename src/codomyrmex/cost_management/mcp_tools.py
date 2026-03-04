"""MCP Tools for Cost Management.

Exposes cost tracking and budgeting functionality via the Model Context Protocol.
"""

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool

from .models import BudgetPeriod, CostCategory
from .tracker import BudgetManager, CostTracker

# We can initialize a global tracker and manager for tools to use
# Or we can accept they need to be initialized. For now we will create a global instance.
_tracker = CostTracker()
_budget_manager = BudgetManager(_tracker)


@mcp_tool()
def cost_management_record_cost(
    amount: float,
    category: str,
    description: str = "",
    resource_id: str = "",
    tags: dict[str, str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Record a cost entry.

    Args:
        amount: Cost amount in dollars.
        category: Cost category (e.g., 'llm_inference', 'compute').
        description: Description of the cost.
        resource_id: ID of the resource that incurred the cost.
        tags: Key-value tags for filtering.
        metadata: Additional metadata.

    Returns:
        A dictionary containing the recorded cost entry details.

    """
    try:
        cat = CostCategory(category)
    except ValueError:
        return {
            "error": f"Invalid category. Must be one of {[c.value for c in CostCategory]}"
        }

    entry = _tracker.record(
        amount=amount,
        category=cat,
        description=description,
        resource_id=resource_id,
        tags=tags,
        metadata=metadata,
    )
    return entry.to_dict()


@mcp_tool()
def cost_management_get_summary(
    period: str | None = None,
    category: str | None = None,
    tags_filter: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Get a summary of costs for a specific period and optional filters.

    Args:
        period: Budget period (e.g., 'hourly', 'daily', 'weekly', 'monthly', 'yearly'). Optional.
        category: Filter by cost category. Optional.
        tags_filter: Filter by tags. Optional.

    Returns:
        A dictionary containing the cost summary.

    """
    p = None
    if period:
        try:
            p = BudgetPeriod(period)
        except ValueError:
            return {
                "error": f"Invalid period. Must be one of {[p.value for p in BudgetPeriod]}"
            }

    c = None
    if category:
        try:
            c = CostCategory(category)
        except ValueError:
            return {
                "error": f"Invalid category. Must be one of {[c.value for c in CostCategory]}"
            }

    summary = _tracker.get_summary(period=p, category=c, tags_filter=tags_filter)
    return summary.to_dict()


@mcp_tool()
def cost_management_create_budget(
    name: str,
    amount: float,
    period: str,
    category: str | None = None,
    tags_filter: dict[str, str] | None = None,
    alert_thresholds: list[float] | None = None,
) -> dict[str, Any]:
    """Create a new budget.

    Args:
        name: Name of the budget.
        amount: Budget amount in dollars.
        period: Budget period (e.g., 'hourly', 'daily', 'weekly', 'monthly', 'yearly').
        category: Optional category filter.
        tags_filter: Optional tags filter.
        alert_thresholds: Optional list of utilization thresholds (e.g., [0.5, 0.8, 1.0]).

    Returns:
        A dictionary containing the created budget details.

    """
    try:
        p = BudgetPeriod(period)
    except ValueError:
        return {
            "error": f"Invalid period. Must be one of {[p.value for p in BudgetPeriod]}"
        }

    c = None
    if category:
        try:
            c = CostCategory(category)
        except ValueError:
            return {
                "error": f"Invalid category. Must be one of {[c.value for c in CostCategory]}"
            }

    budget = _budget_manager.create(
        name=name,
        amount=amount,
        period=p,
        category=c,
        tags_filter=tags_filter,
        alert_thresholds=alert_thresholds,
    )

    return {
        "id": budget.id,
        "name": budget.name,
        "amount": budget.amount,
        "period": budget.period.value,
        "category": budget.category.value if budget.category else None,
        "tags_filter": budget.tags_filter,
        "alert_thresholds": budget.alert_thresholds,
    }


@mcp_tool()
def cost_management_check_budgets() -> list[dict[str, Any]]:
    """Check all budgets for new alerts based on configured thresholds.

    Returns:
        A list of alert dictionaries, each containing 'budget_id', 'threshold',
        'current_spend', 'budget_amount', 'utilization', and 'message'.

    """
    alerts = _budget_manager.check_budgets()
    return [
        {
            "budget_id": alert.budget_id,
            "threshold": alert.threshold,
            "current_spend": alert.current_spend,
            "budget_amount": alert.budget_amount,
            "utilization": alert.utilization,
            "message": alert.message,
            "timestamp": alert.timestamp.isoformat(),
        }
        for alert in alerts
    ]


@mcp_tool()
def cost_management_can_spend(
    amount: float,
    category: str,
    tags: dict[str, str] | None = None,
) -> bool:
    """Check if a spending amount is within all applicable budgets.

    Args:
        amount: Amount to spend.
        category: Cost category of the spend.
        tags: Optional tags associated with the spend.

    Returns:
        True if the spend is allowed, False if it exceeds any applicable budget.

    """
    try:
        cat = CostCategory(category)
    except ValueError:
        return False  # If invalid category, assume we can't spend

    return _budget_manager.can_spend(amount=amount, category=cat, tags=tags)
