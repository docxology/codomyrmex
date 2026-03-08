# Cost Management

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview
The `cost_management` module provides a comprehensive framework for tracking, aggregating, and managing costs within the Codomyrmex ecosystem. It supports multiple storage backends, flexible budgeting with period-based resets, and real-time alerting.

## Key Features
- **Flexible Tracking**: Record costs by category (LLM, Compute, Storage, etc.) with custom tags and metadata.
- **Budgeting & Alerting**: Define budgets for specific periods (Hourly, Daily, Weekly, Monthly, Yearly) and receive alerts at configurable thresholds.
- **Multi-backend Storage**: Choose between `InMemoryCostStore` for volatile tracking or `JSONCostStore` for persistent tracking.
- **Cost Aggregation**: Generate summaries and reports broken down by category, resource, and tags.
- **Spend Gating**: Use `BudgetManager.can_spend()` to proactively prevent overspending.

## Installation
The module is part of the core `codomyrmex` package. No additional dependencies are required beyond the standard library.

## Usage Example
```python
from codomyrmex.cost_management import CostTracker, BudgetManager, CostCategory, BudgetPeriod

# Initialize tracker and manager
tracker = CostTracker()
budgets = BudgetManager(tracker)

# Create a daily budget for LLM inference
budgets.create(
    name="LLM Daily",
    amount=50.0,
    period=BudgetPeriod.DAILY,
    category=CostCategory.LLM_INFERENCE
)

# Record a cost
tracker.record(
    amount=0.05,
    category=CostCategory.LLM_INFERENCE,
    description="GPT-4 completion"
)

# Check if spend is within budget
if budgets.can_spend(1.0, category=CostCategory.LLM_INFERENCE):
    # Proceed with API call
    pass

# Check for alerts
for alert in budgets.check_budgets():
    print(alert.message)
```

## Principles
- **Functional Integrity**: All methods and classes are fully operational and production-ready.
- **Zero-Mock Policy**: Code adheres to the strict Zero-Mock testing policy, ensuring all tests run against real logic.
- **Thread Safety**: Core components are designed to be thread-safe for use in concurrent environments.
