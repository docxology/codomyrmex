# Cost Management - API Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## 1. Overview
The `cost_management` module provides spend tracking, budgeting, and cost optimization. Supports multiple cost categories, budget alerts, and persistent storage backends (in-memory, JSON file).

## 2. Core Components

### 2.1 Classes

| Class | Description |
|-------|-------------|
| `CostTracker` | Records cost entries and generates summary reports |
| `BudgetManager` | Creates and monitors budgets with alert thresholds |
| `CostStore` | Abstract base for cost data persistence |
| `InMemoryCostStore` | Ephemeral in-memory store for testing and development |
| `JSONCostStore` | Persistent JSON-backed cost storage |

### 2.2 Data Models

| Class | Description |
|-------|-------------|
| `CostEntry` | Single cost record (amount, category, timestamp, description) |
| `CostSummary` | Aggregated cost report over a period |
| `Budget` | Budget definition (name, limit, period, alert thresholds) |
| `BudgetAlert` | Alert triggered when spending exceeds a threshold |

### 2.3 Enums

| Enum | Values |
|------|--------|
| `CostCategory` | Compute, storage, network, API, etc. |
| `BudgetPeriod` | Daily, weekly, monthly, quarterly, annual |

## 3. Usage Example

```python
from codomyrmex.cost_management import CostTracker, InMemoryCostStore, CostCategory

tracker = CostTracker(store=InMemoryCostStore())
tracker.record(amount=12.50, category=CostCategory.COMPUTE, description="GPU hours")

summary = tracker.summary()
print(f"Total: ${summary.total:.2f}")
```

## 4. Navigation

- [README](README.md) | [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
