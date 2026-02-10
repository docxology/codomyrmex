"""
Cost Management Module

Spend tracking, budgeting, and cost optimization.
"""

__version__ = "0.1.0"

from .models import Budget, BudgetAlert, BudgetPeriod, CostCategory, CostEntry, CostSummary
from .stores import CostStore, InMemoryCostStore
from .tracker import BudgetManager, CostTracker

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
    # Core
    "CostTracker",
    "BudgetManager",
]
