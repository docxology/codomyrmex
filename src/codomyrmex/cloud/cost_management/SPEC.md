# Cost Management - Specification

> **codomyrmex v1.1.4** | March 2026

## Overview

Technical specification for the cost management subsystem. Provides cost entry recording, aggregation by multiple dimensions, budget creation with configurable thresholds, and budget guard checks for autonomous agent operations.

## Design Principles

- **Zero-Mock Policy**: Tests use real `InMemoryCostStore` instances. No mocking of storage backends.
- **Explicit Failure**: `BudgetManager.can_spend()` returns `False` (not a silent fallback) when budget is exceeded. No operations are silently degraded.
- **Thread Safety**: All mutable state in `CostTracker`, `BudgetManager`, and `InMemoryCostStore` is protected by `threading.Lock`.
- **Pluggable Storage**: `CostStore` is an abstract base class. Production deployments can implement persistent backends without changing the tracker or budget logic.

## Architecture

```
cloud/cost_management/
    __init__.py          # Public API, cli_commands()
    models.py            # CostEntry, Budget, CostSummary, BudgetAlert, CostCategory, BudgetPeriod
    stores.py            # CostStore (ABC), InMemoryCostStore
    tracker.py           # CostTracker, BudgetManager
```

## Functional Requirements

### CostTracker (tracker.py)

- **record(amount, category, description, resource_id, tags, metadata) -> CostEntry**: Create and persist a cost entry. Generates a sequential `cost_N` ID. Defaults to `CostCategory.LLM_INFERENCE`.
- **get_summary(period, start, end) -> CostSummary**: Aggregate costs within a date range. If `period` is provided, derives `start` from `Budget.get_period_start()`. Returns totals broken down by `by_category`, `by_resource`, and `by_tag`.
- **get_total(period, category) -> float**: Shorthand for total spend, optionally filtered by category.

### BudgetManager (tracker.py)

- **create(name, amount, period, category, tags_filter, alert_thresholds) -> Budget**: Register a budget. Default alert thresholds: `[0.5, 0.8, 0.9, 1.0]`. Budget ID is derived from lowercased name with spaces replaced by underscores.
- **get_budget(budget_id) -> Budget | None**: Retrieve by ID.
- **list_budgets() -> list[Budget]**: All registered budgets.
- **get_utilization(budget) -> float**: Current spend as fraction of budget amount.
- **check_budgets() -> list[BudgetAlert]**: Iterate all budgets, emit alerts for newly crossed thresholds. Each threshold fires once per period.
- **reset_period_alerts() -> None**: Clear triggered alert tracking for new period.
- **can_spend(amount, budget_id) -> bool**: Pre-flight check. Returns `True` if spending `amount` stays within budget. If `budget_id` is `None`, checks all budgets.

### CostStore (stores.py)

- **save_entry(entry: CostEntry) -> None**: Persist a cost entry (abstract).
- **get_entries(start, end, category) -> list[CostEntry]**: Retrieve entries in date range with optional category filter (abstract).

### InMemoryCostStore (stores.py)

- Implements `CostStore` with a thread-safe `list[CostEntry]`.
- **get_all() -> list[CostEntry]**: Return all stored entries.
- **clear() -> None**: Remove all entries.

## Interface Contracts

```python
# CostTracker.record signature
def record(
    self,
    amount: float,
    category: CostCategory = CostCategory.LLM_INFERENCE,
    description: str = "",
    resource_id: str = "",
    tags: dict[str, str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> CostEntry: ...

# BudgetManager.can_spend signature
def can_spend(self, amount: float, budget_id: str | None = None) -> bool: ...

# CostStore interface
class CostStore(ABC):
    @abstractmethod
    def save_entry(self, entry: CostEntry) -> None: ...

    @abstractmethod
    def get_entries(
        self, start: datetime, end: datetime, category: CostCategory | None = None
    ) -> list[CostEntry]: ...
```

## Dependencies

| Dependency | Purpose |
|-----------|---------|
| `threading` | Lock-based thread safety for stores, tracker, and budget manager |
| `datetime` | Timestamps for entries and period calculations |
| `codomyrmex.validation.schemas` | Optional `Result`/`ResultStatus` for cross-module interop (graceful import) |

## Constraints

- `models.py` must exist and export: `Budget`, `BudgetAlert`, `BudgetPeriod`, `CostCategory`, `CostEntry`, `CostSummary`.
- `Budget.get_period_start()` is expected to return a `datetime` for the current period boundary based on `BudgetPeriod`.
- `InMemoryCostStore` does not persist across process restarts. Implement a file or database `CostStore` for durability.
- Alert thresholds must be floats between 0 and 1 (fraction of budget, e.g., 0.8 = 80%).

## Navigation

- Parent: [cloud](../README.md)
- Agents: [AGENTS.md](AGENTS.md)
- Project root: [codomyrmex](../../../../README.md)
