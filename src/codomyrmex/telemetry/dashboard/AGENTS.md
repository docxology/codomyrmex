# Telemetry Dashboard - Agentic Context

**Module**: `codomyrmex.telemetry.dashboard`
**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Key Components

| Component | Purpose | Key Methods |
|-----------|---------|-------------|
| `DashboardManager` | Create, list, delete dashboards and query panel data | `create()`, `get()`, `list()`, `delete()`, `get_panel_data()` |
| `MetricCollector` | Thread-safe time-series metric storage with retention-based cleanup | `record()`, `get_metrics()`, `get_latest()`, `list_metric_names()`, `cleanup_old()` |
| `AlertManager` | Lambda-condition alert rules with active/resolved state tracking | `add_rule()`, `check()`, `get_active_alerts()`, `acknowledge()` |
| `SLOTracker` | Service Level Objective tracking with error budget computation | `create_slo()`, `record_event()`, `get_status()`, `get_violations()` |
| `ErrorBudgetPolicy` | Policy engine returning deployment posture based on error budget consumption | `add_policy()`, `evaluate()` returns `"normal"` / `"increase_reviews"` / `"reduce_risk"` / `"freeze_deployments"` |
| `SLI` | Service Level Indicator: good/total event counters with percentage `value` property | `record_good()`, `record_bad()` |
| `SLO` | Objective wrapping an SLI with target percentage and error budget calculation | `is_met`, `error_budget_remaining`, `error_budget_consumed` |

## Operating Contracts

- `DashboardManager` and `MetricCollector` use `threading.Lock` for thread safety.
- `MetricCollector.cleanup_old()` removes metrics older than `retention_minutes` (default 60).
- `AlertManager.check()` auto-resolves alerts when conditions no longer match; handler exceptions are caught and logged.
- `SLOTracker.record_event()` automatically creates `SLOViolation` records when SLO drops below target.
- `ErrorBudgetPolicy.evaluate()` uses fixed thresholds: >=100% consumed = `freeze_deployments`, >=75% = `reduce_risk`, >=50% = `increase_reviews`.

## Integration Points

- **telemetry/alerting**: `AlertManager` provides dashboard-level alerting alongside module-level `AlertEvaluator` and `AlertEngine`.
- **dashboard.models**: `Dashboard`, `Panel`, `MetricValue`, `MetricType`, `Alert`, `AlertSeverity` dataclasses.
- All state is in-memory; no persistence layer.

## Constraints

- `DashboardManager.get_panel_data()` queries `MetricCollector` with time-range filtering; performance depends on metric volume.
- `SLI.value` returns 100.0 when `total_events == 0` (vacuous truth).
