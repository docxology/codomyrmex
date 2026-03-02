# Codomyrmex Agents — src/codomyrmex/cloud/cost_management

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides cloud spend tracking, budgeting, and alerting. `CostTracker` records individual cost entries categorized by type (LLM inference, compute, storage, etc.), while `BudgetManager` creates budgets with configurable periods and threshold-based alerts.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `models.py` | `CostCategory` | Enum: `LLM_INFERENCE`, `LLM_EMBEDDING`, `COMPUTE`, `STORAGE`, `NETWORK`, `API_CALLS`, `OTHER` |
| `models.py` | `BudgetPeriod` | Enum: `HOURLY`, `DAILY`, `WEEKLY`, `MONTHLY` |
| `models.py` | `CostEntry` | Dataclass for a single cost record with amount, category, tags, and timestamp |
| `models.py` | `Budget` | Budget allocation with period, category filter, and alert thresholds; has `get_period_start()` |
| `models.py` | `CostSummary` | Aggregated view with `total`, `by_category`, `by_resource`, `by_tag` breakdowns |
| `models.py` | `BudgetAlert` | Alert dataclass with `utilization` and `message` properties |
| `stores.py` | `CostStore` | ABC defining `save_entry()` and `get_entries()` |
| `stores.py` | `InMemoryCostStore` | Thread-safe in-memory implementation of `CostStore` |
| `tracker.py` | `CostTracker` | Main service: `record()` costs and `get_summary()` / `get_total()` for periods |
| `tracker.py` | `BudgetManager` | Budget CRUD, utilization tracking, threshold alerting via `check_budgets()`, spend gating via `can_spend()` |

## Operating Contracts

- `CostTracker` defaults to `InMemoryCostStore` if no store is provided.
- `BudgetManager` requires a `CostTracker` instance at construction.
- Alert thresholds default to `[0.5, 0.8, 0.9, 1.0]`; each threshold fires only once per period.
- Call `reset_period_alerts()` at period boundaries to re-arm alerts.
- `can_spend(amount)` returns `False` if any budget would be exceeded.
- Thread safety is provided by `threading.Lock` in both `InMemoryCostStore` and `BudgetManager`.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.validation.schemas` (optional, for `Result`/`ResultStatus` interop)
- **Used by**: Any module tracking cloud or LLM expenditure

## Navigation

- **Parent**: [cloud](../README.md)
- **Root**: [Root](../../../../README.md)
