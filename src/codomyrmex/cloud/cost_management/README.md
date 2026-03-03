# Cost Management

> **codomyrmex v1.0.8** | March 2026

## Overview

Spend tracking, budgeting, and cost optimization for cloud and LLM usage. Provides `CostTracker` for recording cost entries categorized by type (LLM inference, storage, compute, etc.) and `BudgetManager` for creating budgets with threshold-based alerting. Costs are stored via a pluggable `CostStore` backend, with an `InMemoryCostStore` provided by default.

## PAI Integration

| PAI Phase | Relevance | Usage |
|-----------|-----------|-------|
| OBSERVE | Primary | `CostTracker.get_summary()` reports spend by category, resource, and tag |
| VERIFY | Primary | `BudgetManager.check_budgets()` detects budget threshold breaches |
| EXECUTE | Supporting | `CostTracker.record()` logs costs during agent operations |
| PLAN | Supporting | `BudgetManager.can_spend()` gates planned operations against remaining budget |

## Key Exports

| Name | Type | Purpose |
|------|------|---------|
| `CostTracker` | class | Records cost entries and generates summaries |
| `BudgetManager` | class | Creates budgets, checks utilization, generates alerts |
| `CostStore` | ABC | Abstract storage backend for cost entries |
| `InMemoryCostStore` | class | Thread-safe in-memory cost storage |
| `CostEntry` | dataclass | Single cost record with amount, category, tags, metadata |
| `CostSummary` | dataclass | Aggregated costs by category, resource, and tag |
| `Budget` | dataclass | Budget definition with period, amount, thresholds |
| `BudgetAlert` | dataclass | Alert triggered when spend crosses a threshold |
| `CostCategory` | enum | Cost categories (LLM_INFERENCE, STORAGE, COMPUTE, etc.) |
| `BudgetPeriod` | enum | Budget periods (DAILY, WEEKLY, MONTHLY, etc.) |
| `cli_commands` | function | Returns CLI command dict for cost reporting and budget listing |

## Quick Start

```python
from codomyrmex.cloud.cost_management import (
    BudgetManager,
    BudgetPeriod,
    CostCategory,
    CostTracker,
)

tracker = CostTracker()

# Record LLM inference costs
tracker.record(
    amount=0.05,
    category=CostCategory.LLM_INFERENCE,
    description="GPT-4 completion",
    tags={"model": "gpt-4", "user": "alice"},
)

# Get daily spend summary
summary = tracker.get_summary(period=BudgetPeriod.DAILY)
print(f"Today's spend: ${summary.total:.2f}")
print(f"By category: {summary.by_category}")

# Set up budget with alerts
budgets = BudgetManager(tracker)
budgets.create(
    name="Daily LLM",
    amount=100.0,
    period=BudgetPeriod.DAILY,
    category=CostCategory.LLM_INFERENCE,
)

# Check for budget alerts
alerts = budgets.check_budgets()
for alert in alerts:
    print(f"Budget {alert.budget_id}: {alert.threshold*100}% threshold crossed")

# Pre-flight check before expensive operation
if budgets.can_spend(25.0, budget_id="daily_llm"):
    print("Budget allows this spend")
```

## Architecture

```
cloud/cost_management/
    __init__.py          # Package exports, cli_commands()
    models.py            # CostEntry, Budget, CostSummary, BudgetAlert, enums
    stores.py            # CostStore (ABC), InMemoryCostStore
    tracker.py           # CostTracker, BudgetManager
```

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/cloud/ -v -k cost
```

## Navigation

- Parent: [cloud](../README.md)
- Project root: [codomyrmex](../../../../README.md)
