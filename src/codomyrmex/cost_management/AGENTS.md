# Codomyrmex Agents — src/codomyrmex/cost_management

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides comprehensive spend tracking, budgeting, and alerting. `CostTracker` records individual cost entries categorized by type (LLM inference, compute, storage, etc.), while `BudgetManager` creates budgets with configurable periods and threshold-based alerts.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `models.py` | `CostCategory` | Enum: `LLM_INFERENCE`, `LLM_EMBEDDING`, `LLM_FINE_TUNING`, `COMPUTE`, `STORAGE`, `NETWORK`, `API_CALLS`, `DATABASE`, `LICENSE`, `OTHER` |
| `models.py` | `BudgetPeriod` | Enum: `HOURLY`, `DAILY`, `WEEKLY`, `MONTHLY`, `YEARLY` |
| `models.py` | `CostEntry` | Dataclass for a single cost record with amount, category, tags, and timestamp |
| `models.py` | `Budget` | Budget allocation with period, category filter, and alert thresholds; has `get_period_start()` |
| `models.py` | `CostSummary` | Aggregated view with `total`, `by_category`, `by_resource`, `by_tag` breakdowns |
| `models.py` | `BudgetAlert` | Alert dataclass with `utilization` and `message` properties |
| `stores.py` | `CostStore` | ABC defining `save_entry()` and `get_entries()` |
| `stores.py` | `InMemoryCostStore` | Thread-safe in-memory implementation of `CostStore` |
| `stores.py` | `JSONCostStore` | File-based JSON storage implementation of `CostStore` |
| `tracker.py` | `CostTracker` | Main service: `record()` costs and `get_summary()` / `get_total()` for periods |
| `tracker.py` | `BudgetManager` | Budget CRUD, utilization tracking, threshold alerting via `check_budgets()`, spend gating via `can_spend()` |
| `mcp_tools.py` | MCP Tools | Exposes `@mcp_tool` decorated functions: `cost_management_record_cost`, `cost_management_get_summary`, `cost_management_create_budget`, `cost_management_check_budgets`, `cost_management_can_spend` |

## Operating Contracts

- `CostTracker` defaults to `InMemoryCostStore` if no store is provided.
- `BudgetManager` requires a `CostTracker` instance at construction.
- Alert thresholds default to `[0.5, 0.8, 0.9, 1.0]`; each threshold fires only once per period.
- Call `reset_period_alerts()` at period boundaries to re-arm alerts.
- `can_spend(amount, category, tags)` returns `False` if any applicable budget would be exceeded.
- Thread safety is provided by `threading.Lock` in `InMemoryCostStore`, `JSONCostStore`, `CostTracker`, and `BudgetManager`.
- Errors must be logged via `codomyrmex.logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.logging_monitoring` (for logging), `codomyrmex.validation.schemas` (optional, for `Result`/`ResultStatus` interop)
- **Used by**: Any module tracking expenditure or requiring budget gating.

## Navigation

- **Root**: [Root](../../../README.md)
