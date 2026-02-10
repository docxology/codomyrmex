# Cost Management Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The `cost_management` module provides spend tracking, budgeting, and cost optimization for cloud and API usage. It supports recording cost entries by category, computing summaries over configurable time periods, setting budgets with threshold-based alerting, and checking spend authorization before incurring costs. The module is designed to track LLM inference, embedding, compute, storage, network, and API call expenses.


## Installation

```bash
uv pip install codomyrmex
```

## Key Features

- **Multi-category cost tracking**: Track costs across LLM inference, LLM embedding, compute, storage, network, API calls, and other categories via `CostCategory` enum
- **Configurable budget periods**: Hourly, daily, weekly, and monthly budget cycles with automatic period boundary calculation
- **Threshold-based alerting**: Configurable alert thresholds (default: 50%, 80%, 90%, 100%) that trigger `BudgetAlert` notifications when utilization exceeds each level
- **Multi-dimensional summaries**: `CostSummary` aggregates spend by category, resource, and arbitrary tag key-value pairs
- **Tag-based filtering**: Attach key-value tags to cost entries for granular spend analysis (e.g., by model, user, team)
- **Pre-spend authorization**: `can_spend()` checks whether a proposed cost fits within remaining budget before incurring it
- **Pluggable storage backends**: Abstract `CostStore` base class with `InMemoryCostStore` implementation
- **Thread-safe operations**: All storage and budget operations use threading locks for concurrent safety
- **Period-aware budget tracking**: Budgets automatically compute the current period start for accurate utilization calculation


## Key Components

| Component | Description |
|-----------|-------------|
| `CostCategory` | Enum defining cost categories: LLM_INFERENCE, LLM_EMBEDDING, COMPUTE, STORAGE, NETWORK, API_CALLS, OTHER |
| `BudgetPeriod` | Enum for budget cycles: HOURLY, DAILY, WEEKLY, MONTHLY |
| `CostEntry` | Dataclass representing a single cost record with amount, category, description, resource ID, tags, and timestamp |
| `Budget` | Dataclass defining a budget allocation with name, amount, period, optional category filter, and alert thresholds |
| `CostSummary` | Dataclass aggregating costs by total, category, resource, and tags over a specified time range |
| `BudgetAlert` | Dataclass representing a triggered budget alert with utilization percentage and formatted message |
| `CostStore` | Abstract base class for cost storage with `save_entry()` and `get_entries()` interface |
| `InMemoryCostStore` | Thread-safe in-memory list-based storage backend with date range and category filtering |
| `CostTracker` | Main cost tracking service for recording entries and computing summaries over time periods |
| `BudgetManager` | Budget management and alerting service; creates budgets, checks utilization, triggers alerts, and validates pre-spend authorization |

## Quick Start

```python
from codomyrmex.cost_management import (
    CostTracker,
    BudgetManager,
    CostCategory,
    BudgetPeriod,
)

# Create a cost tracker
tracker = CostTracker()

# Record costs
tracker.record(
    amount=0.05,
    category=CostCategory.LLM_INFERENCE,
    description="GPT-4 completion",
    tags={"model": "gpt-4", "user": "alice"},
)

tracker.record(
    amount=0.002,
    category=CostCategory.LLM_EMBEDDING,
    description="Text embedding",
    tags={"model": "text-embedding-3-small"},
)

# Get daily summary
summary = tracker.get_summary(period=BudgetPeriod.DAILY)
print(f"Today's spend: ${summary.total:.2f}")
print(f"By category: {summary.by_category}")

# Set up budget management
budgets = BudgetManager(tracker)

budgets.create(
    name="Daily LLM",
    amount=100.0,
    period=BudgetPeriod.DAILY,
    category=CostCategory.LLM_INFERENCE,
)

# Check budget alerts
alerts = budgets.check_budgets()
for alert in alerts:
    print(alert.message)

# Pre-spend authorization
if budgets.can_spend(25.0, budget_id="daily_llm"):
    print("Spend authorized")
else:
    print("Budget exceeded")
```


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k cost_management -v
```

## Related Modules

- [llm](../llm/) - LLM providers whose inference costs are tracked by this module
- [logging_monitoring](../logging_monitoring/) - Centralized logging for cost tracking events and alerts
- [metrics](../metrics/) - Metrics collection that can surface cost data in dashboards

## Navigation

- **Source**: [src/codomyrmex/cost_management/](../../../src/codomyrmex/cost_management/)
- **Parent**: [docs/modules/](../README.md)
