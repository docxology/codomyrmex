"""MCP Tool definitions for the cost_management module."""

from typing import Any

from codomyrmex.cost_management.models import BudgetPeriod
from codomyrmex.cost_management.stores import JSONCostStore
from codomyrmex.cost_management.tracker import BudgetManager, CostTracker
from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="cost_management")
def get_cost_summary(period_str: str = "MONTHLY") -> dict[str, Any]:
    """Retrieve a summary of costs for the given period.

    Args:
        period_str: "DAILY", "WEEKLY", "MONTHLY", "YEARLY", or "ALL"
    """
    try:
        store = JSONCostStore()
        tracker = CostTracker(store=store)

        period = None
        if period_str.upper() != "ALL":
            try:
                period = BudgetPeriod[period_str.upper()]
            except KeyError:
                return {"error": f"Invalid period: {period_str}"}

        summary = tracker.get_summary(period=period)
        return {
            "total": summary.total,
            "by_category": {cat.name: amt for cat, amt in summary.by_category.items()},
            "by_resource": summary.by_resource,
            "period": period_str,
        }
    except Exception as e:
        return {"error": str(e)}

@mcp_tool(category="cost_management")
def check_budgets() -> dict[str, Any]:
    """Check all active budgets and return their utilization status and any alerts.
    """
    try:
        store = JSONCostStore()
        tracker = CostTracker(store=store)
        manager = BudgetManager(tracker=tracker)

        budgets = manager.list_budgets()
        utilizations = []
        for b in budgets:
            util = manager.get_utilization(b)
            utilizations.append({
                "budget_id": b.id,
                "name": b.name,
                "amount": b.amount,
                "period": b.period.name,
                "utilization_percentage": round(util * 100, 2)
            })

        alerts = manager.check_budgets()
        alert_list = [
            {"budget_id": a.budget_id, "threshold": a.threshold, "current_spend": a.current_spend}
            for a in alerts
        ]

        return {
            "budgets": utilizations,
            "alerts": alert_list
        }
    except Exception as e:
        return {"error": str(e)}

def register_mcp_tools(mcp_server: Any) -> None:
    """Register all MCP tools provided by the cost_management module."""
    @mcp_server.tool()
    def mcp_get_cost_summary(period_str: str = "MONTHLY") -> dict[str, Any]:
        """Retrieve a summary of costs for the given period."""
        return get_cost_summary(period_str)

    @mcp_server.tool()
    def mcp_check_budgets() -> dict[str, Any]:
        """Check all active budgets and return their utilization status and any alerts."""
        return check_budgets()
