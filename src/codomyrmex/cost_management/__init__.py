"""
Cost Management Module

Spend tracking, budgeting, and cost optimization.
"""

__version__ = "1.0.0"

from .models import (
    Budget,
    BudgetAlert,
    BudgetPeriod,
    CostCategory,
    CostEntry,
    CostSummary,
)
from .stores import CostStore, InMemoryCostStore, JSONCostStore
from .tracker import BudgetManager, CostTracker

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None


def cli_commands():
    """Return CLI commands for the cost_management module."""
    return {
        "report": lambda: print(
            "Cost Report\n"
            "  Categories: " + ", ".join(cc.value for cc in CostCategory) + "\n"
            "  Use CostTracker to record expenses and generate CostSummary reports."
        ),
        "budgets": lambda: print(
            "Budget Management\n"
            "  Budget periods: " + ", ".join(bp.value for bp in BudgetPeriod) + "\n"
            "  Use BudgetManager to create budgets and monitor BudgetAlerts."
        ),
    }


__all__ = [
    # Enums
    "CostCategory",
    "BudgetPeriod",
    # Data classes
    "CostEntry",
    "Budget",
    "CostSummary",
    "BudgetAlert",
    # Stores
    "CostStore",
    "InMemoryCostStore",
    "JSONCostStore",
    # Core
    "CostTracker",
    "BudgetManager",
    # CLI
    "cli_commands",
]

# Expose MCP tools if the module has them loaded
try:
    from .mcp_tools import (
        cost_management_can_spend,
        cost_management_check_budgets,
        cost_management_create_budget,
        cost_management_get_summary,
        cost_management_record_cost,
    )

    __all__.extend(
        [
            "cost_management_record_cost",
            "cost_management_get_summary",
            "cost_management_create_budget",
            "cost_management_check_budgets",
            "cost_management_can_spend",
        ]
    )
except ImportError:
    pass
