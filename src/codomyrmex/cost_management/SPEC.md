# Cost Management -- Technical Specification

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Comprehensive cost tracking, budgeting, and alerting service for the Codomyrmex ecosystem. Records individual cost entries with category, tag, and metadata, aggregates them into summaries by period, and fires threshold-based budget alerts. Supports multiple storage backends, including file-based JSON persistence.

## Architecture

Three-layer design: **Models** (pure data), **Stores** (persistence abstraction), **Tracker/Manager** (business logic).

```
CostTracker ──> CostStore (ABC)
     │               │
     │          InMemoryCostStore
     │          JSONCostStore
     │
BudgetManager ──> CostTracker
```

## Key Classes

### `CostTracker`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `record` | `amount: float, category: CostCategory, description: str, resource_id: str, tags: dict, metadata: dict, timestamp: datetime` | `CostEntry` | Record a cost entry and persist to store |
| `get_summary` | `period: BudgetPeriod \| None, start: datetime \| None, end: datetime \| None, category: CostCategory \| None, tags_filter: dict \| None` | `CostSummary` | Aggregate costs by category, resource, and tag |
| `get_total` | `period: BudgetPeriod \| None, category: CostCategory \| None, tags_filter: dict \| None` | `float` | Get total spend, with period, category, and tag filters |

### `BudgetManager`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `create` | `name: str, amount: float, period: BudgetPeriod, category: CostCategory \| None, tags_filter: dict, alert_thresholds: list[float]` | `Budget` | Create a new budget |
| `get_budget` | `budget_id: str` | `Budget \| None` | Retrieve budget by ID |
| `list_budgets` | -- | `list[Budget]` | List all budgets |
| `get_utilization` | `budget: Budget` | `float` | Current utilization ratio (0.0 - 1.0+) |
| `check_budgets` | -- | `list[BudgetAlert]` | Check all budgets, return new alerts |
| `can_spend` | `amount: float, category: CostCategory, tags: dict \| None` | `bool` | Check if spending is within all applicable budgets |
| `reset_period_alerts` | -- | `None` | Clear triggered alert state |

### `CostStore` (ABC)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `save_entry` | `entry: CostEntry` | `None` | Persist a cost entry |
| `get_entries` | `start: datetime, end: datetime, category: CostCategory \| None, tags_filter: dict \| None` | `list[CostEntry]` | Query entries by date range, category, and tag |

### `InMemoryCostStore`

Extends `CostStore` with thread-safe in-memory list. Additional methods: `get_all() -> list[CostEntry]`, `clear() -> None`.

### `JSONCostStore`

Extends `CostStore` with thread-safe JSON file-based persistence. Ideal for local environments and simple tracking needs.

## Dependencies

- **Internal**: `codomyrmex.logging_monitoring` (for logging), `codomyrmex.validation.schemas` (optional, for `Result`/`ResultStatus`)
- **External**: None (stdlib only: `threading`, `dataclasses`, `datetime`, `enum`, `json`, `pathlib`)

## Constraints

- Alert thresholds are checked per-budget with deduplication (each threshold fires once per period).
- Budget IDs are derived from name via `name.lower().replace(" ", "_")`.
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `CostTracker.record()` delegates to `CostStore.save_entry()` -- store implementations are responsible for error propagation.
- `BudgetManager.can_spend()` returns `True` if no budgets are matched by the provided category and tags (permissive default).
- All errors logged via `codomyrmex.logging_monitoring` before propagation.
