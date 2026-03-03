"""
MCP tools for the Cost Management module.
"""

from typing import Any

from codomyrmex.logging_monitoring import get_logger
from codomyrmex.model_context_protocol.decorators import mcp_tool
from codomyrmex.validation.schemas import Result, ResultStatus

from .models import BudgetPeriod, CostCategory
from .tracker import BudgetManager, CostTracker

logger = get_logger(__name__)

# Global instances for the MCP tools to interact with
_tracker = CostTracker()
_budget_manager = BudgetManager(_tracker)


@mcp_tool(
    name="cost_management_record_cost",
    description="Record a cost entry into the cost tracker.",
)
def cost_management_record_cost(
    amount: float,
    category: str,
    description: str = "",
    resource_id: str = "",
    tags: dict[str, str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> Result:
    """Record a cost entry."""
    try:
        cost_category = CostCategory(category)
        entry = _tracker.record(
            amount=amount,
            category=cost_category,
            description=description,
            resource_id=resource_id,
            tags=tags,
            metadata=metadata,
        )
        return Result(
            status=ResultStatus.SUCCESS,
            data=entry.to_dict(),
            message="Cost recorded successfully.",
        )
    except ValueError as e:
        return Result(
            status=ResultStatus.FAILURE,
            message=f"Invalid category: {e}",
        )
    except Exception as e:
        logger.error(f"Error recording cost: {e}")
        return Result(
            status=ResultStatus.FAILURE,
            message=f"Failed to record cost: {e}",
        )


@mcp_tool(
    name="cost_management_get_summary",
    description="Get a summary of costs, optionally filtered by period and category.",
)
def cost_management_get_summary(
    period: str | None = None,
    category: str | None = None,
) -> Result:
    """Get a summary of costs."""
    try:
        budget_period = BudgetPeriod(period) if period else None
        cost_category = CostCategory(category) if category else None

        summary = _tracker.get_summary(
            period=budget_period,
            category=cost_category,
        )
        return Result(
            status=ResultStatus.SUCCESS,
            data=summary.to_dict(),
            message="Cost summary retrieved successfully.",
        )
    except ValueError as e:
        return Result(
            status=ResultStatus.FAILURE,
            message=f"Invalid period or category: {e}",
        )
    except Exception as e:
        logger.error(f"Error getting summary: {e}")
        return Result(
            status=ResultStatus.FAILURE,
            message=f"Failed to get summary: {e}",
        )


@mcp_tool(
    name="cost_management_create_budget",
    description="Create a new budget.",
)
def cost_management_create_budget(
    name: str,
    amount: float,
    period: str,
    category: str | None = None,
    tags_filter: dict[str, str] | None = None,
    alert_thresholds: list[float] | None = None,
) -> Result:
    """Create a new budget."""
    try:
        budget_period = BudgetPeriod(period)
        cost_category = CostCategory(category) if category else None

        budget = _budget_manager.create(
            name=name,
            amount=amount,
            period=budget_period,
            category=cost_category,
            tags_filter=tags_filter,
            alert_thresholds=alert_thresholds,
        )
        return Result(
            status=ResultStatus.SUCCESS,
            data={
                "id": budget.id,
                "name": budget.name,
                "amount": budget.amount,
                "period": budget.period.value,
                "category": budget.category.value if budget.category else None,
            },
            message="Budget created successfully.",
        )
    except ValueError as e:
        return Result(
            status=ResultStatus.FAILURE,
            message=f"Invalid input: {e}",
        )
    except Exception as e:
        logger.error(f"Error creating budget: {e}")
        return Result(
            status=ResultStatus.FAILURE,
            message=f"Failed to create budget: {e}",
        )


@mcp_tool(
    name="cost_management_check_budgets",
    description="Check all budgets and return any active alerts.",
)
def cost_management_check_budgets() -> Result:
    """Check budgets for alerts."""
    try:
        alerts = _budget_manager.check_budgets()
        alert_data = [
            {
                "budget_id": a.budget_id,
                "threshold": a.threshold,
                "current_spend": a.current_spend,
                "budget_amount": a.budget_amount,
                "message": a.message,
            }
            for a in alerts
        ]
        return Result(
            status=ResultStatus.SUCCESS,
            data=alert_data,
            message=f"Found {len(alerts)} alerts.",
        )
    except Exception as e:
        logger.error(f"Error checking budgets: {e}")
        return Result(
            status=ResultStatus.FAILURE,
            message=f"Failed to check budgets: {e}",
        )


@mcp_tool(
    name="cost_management_can_spend",
    description="Check if spending amount is within all applicable budgets.",
)
def cost_management_can_spend(
    amount: float,
    category: str,
    tags: dict[str, str] | None = None,
) -> Result:
    """Check if spending amount is within all applicable budgets."""
    try:
        cost_category = CostCategory(category)
        can_spend = _budget_manager.can_spend(
            amount=amount,
            category=cost_category,
            tags=tags,
        )
        return Result(
            status=ResultStatus.SUCCESS,
            data={"can_spend": can_spend},
            message="Spend check completed.",
        )
    except ValueError as e:
        return Result(
            status=ResultStatus.FAILURE,
            message=f"Invalid category: {e}",
        )
    except Exception as e:
        logger.error(f"Error checking spend: {e}")
        return Result(
            status=ResultStatus.FAILURE,
            message=f"Failed to check spend: {e}",
        )
