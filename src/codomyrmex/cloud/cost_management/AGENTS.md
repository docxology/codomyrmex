# Cost Management - Agent Coordination

> **codomyrmex v1.1.9** | March 2026

## Overview

Spend tracking and budget management for AI agent operations. Agents use `CostTracker` to record costs incurred during LLM calls, storage access, and compute usage. `BudgetManager` provides guardrails to prevent overspend via threshold alerting and pre-flight budget checks.

## Key Files

| File | Purpose | Key Classes |
|------|---------|-------------|
| `tracker.py` | Cost recording and budget management | `CostTracker`, `BudgetManager` |
| `stores.py` | Pluggable storage backend for cost entries | `CostStore` (ABC), `InMemoryCostStore` |
| `models.py` | Data models and enumerations | `CostEntry`, `Budget`, `CostSummary`, `BudgetAlert`, `CostCategory`, `BudgetPeriod` |
| `__init__.py` | Public API and CLI command registration | `cli_commands()` |

## MCP Tools Available

This submodule does not expose `@mcp_tool` decorated tools. Cost management is accessed programmatically via Python imports. The parent `cloud` module exposes its own MCP tools (`list_cloud_instances`, `list_s3_buckets`, `upload_file_to_s3`) separately.

## Agent Instructions

1. **Record costs immediately.** Call `tracker.record()` as soon as a billable operation completes. Include the `resource_id` and relevant `tags` for filtering and attribution.
2. **Check budget before expensive operations.** Use `budgets.can_spend(amount, budget_id)` before initiating operations that may exceed budget thresholds.
3. **Monitor alerts after recording.** Call `budgets.check_budgets()` after recording costs. Alerts are emitted only once per threshold crossing until `reset_period_alerts()` is called.
4. **Use appropriate CostCategory values.** Categories are defined in the `CostCategory` enum. Match the operation type accurately for correct reporting.
5. **Tag consistently.** Use standardized tag keys (`model`, `user`, `project`, `agent_id`) for cross-session aggregation.

## Operating Contracts

- **Thread safety**: Both `CostTracker` and `BudgetManager` use `threading.Lock` for safe concurrent access. `InMemoryCostStore` is also thread-safe.
- **ID generation**: `CostTracker` generates sequential IDs (`cost_1`, `cost_2`, ...) using a thread-safe counter.
- **Alert deduplication**: `BudgetManager` tracks triggered alert thresholds in a set. Each threshold fires once per period. Call `reset_period_alerts()` at period boundaries.
- **Budget utilization**: Calculated as `spend / budget.amount`. Returns 0 if `budget.amount` is 0 (no division error).
- **Storage abstraction**: `CostStore` is an ABC with `save_entry` and `get_entries` methods. Implement a custom store for persistent backends (database, file, cloud).

## Common Patterns

```python
# Pattern: Track LLM costs with metadata
entry = tracker.record(
    amount=0.03,
    category=CostCategory.LLM_INFERENCE,
    description="Claude Opus completion",
    resource_id="claude-opus-4",
    tags={"model": "claude-opus-4", "agent_id": "eng-01"},
    metadata={"tokens_in": 1500, "tokens_out": 800},
)

# Pattern: Budget guard for autonomous agents
if not budgets.can_spend(estimated_cost):
    raise RuntimeError("Budget exceeded - operation blocked")

# Pattern: Daily summary report
summary = tracker.get_summary(period=BudgetPeriod.DAILY)
for category, amount in summary.by_category.items():
    print(f"  {category}: ${amount:.2f}")
```

## PAI Agent Role Access Matrix

| Agent Role | Access Level | Typical Operations |
|------------|-------------|-------------------|
| Engineer | Read/Write | Record costs, check budgets, generate summaries |
| Architect | Read | Review spend summaries, budget utilization |
| QATester | Read | Verify cost recording accuracy, alert thresholds |

## Navigation

- Parent: [cloud](../README.md)
- Spec: [SPEC.md](SPEC.md)
- Project root: [codomyrmex](../../../../README.md)
