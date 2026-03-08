"""
Cost Management Module

Spend tracking, budgeting, and cost optimization.
"""

__version__ = "0.1.0"

from .hooks import (
    AutoCostTracker,
    CostHook,
    ModelPrice,
    ModelPricingTable,
    cost_tracked,
)
from .models import (
    Budget,
    BudgetAlert,
    BudgetPeriod,
    CostCategory,
    CostEntry,
    CostSummary,
)
from .stores import CostStore, InMemoryCostStore
from .tracker import BudgetManager, CostTracker

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    pass


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
    "AutoCostTracker",
    "Budget",
    "BudgetAlert",
    "BudgetManager",
    "BudgetPeriod",
    # Enums
    "CostCategory",
    # Data classes
    "CostEntry",
    "CostHook",
    # Stores
    "CostStore",
    "CostSummary",
    # Core
    "CostTracker",
    "InMemoryCostStore",
    "ModelPrice",
    "ModelPricingTable",
    # CLI
    "cli_commands",
    "cost_tracked",
]
