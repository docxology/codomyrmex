# Telemetry Dashboard - Technical Specification

**Module**: `codomyrmex.telemetry.dashboard`
**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Architecture

Four subsystems: `DashboardManager` for panel-based dashboard CRUD, `MetricCollector` for time-series storage, `AlertManager` for lambda-condition alerting, and `SLOTracker` with `ErrorBudgetPolicy` for SLO/SLI management.

## Key Classes

### DashboardManager

| Method | Signature | Description |
|--------|-----------|-------------|
| `create` | `(name, description?, tags?) -> Dashboard` | Create dashboard with ID derived from lowercased name |
| `get` | `(dashboard_id) -> Dashboard \| None` | Retrieve by ID |
| `list` | `() -> list[Dashboard]` | All dashboards |
| `delete` | `(dashboard_id) -> bool` | Remove a dashboard |
| `get_panel_data` | `(dashboard_id, panel_id, duration_minutes=60) -> list[MetricValue]` | Query collector for panel metrics within time range |

### MetricCollector

| Method | Signature | Description |
|--------|-----------|-------------|
| `record` | `(name, value, labels?, metric_type?) -> None` | Store a metric value with timestamp |
| `get_metrics` | `(name, start?, end?) -> list[MetricValue]` | Time-range filtered query |
| `get_latest` | `(name) -> MetricValue \| None` | Most recent value |
| `cleanup_old` | `() -> int` | Remove metrics older than `retention_minutes` (default 60) |

### SLOTracker

| Method | Signature | Description |
|--------|-----------|-------------|
| `create_slo` | `(slo_id, name, sli_type, target, window_days=30) -> SLO` | Create SLO with associated SLI |
| `record_event` | `(slo_id, is_good, count=1)` | Record good/bad events; auto-detects violations |
| `get_status` | `(slo_id) -> dict \| None` | Current SLI value, budget remaining, event counts |
| `get_violations` | `(slo_id?, since?) -> list[SLOViolation]` | Filtered violation history |

### ErrorBudgetPolicy

| Method | Signature | Description |
|--------|-----------|-------------|
| `evaluate` | `(slo_id) -> str \| None` | Returns posture: `"normal"`, `"increase_reviews"`, `"reduce_risk"`, `"freeze_deployments"` |

### Key Dataclasses

- `SLI`: `good_events`, `total_events`, `sli_type`. Property `value` = percentage (100.0 when no events).
- `SLO`: `target` (e.g. 99.9), `window_days`. Properties: `is_met`, `error_budget_remaining`, `error_budget_consumed`.
- `SLOViolation`: `slo_id`, `target`, `actual`, `occurred_at`, `duration_minutes`.
- `SLIType` enum: AVAILABILITY, LATENCY, THROUGHPUT, ERROR_RATE, SATURATION.

## Dependencies

- `threading`: Locks for `DashboardManager`, `MetricCollector`, `SLOTracker`.
- `dashboard.models`: `Dashboard`, `Panel`, `MetricValue`, `MetricType`, `Alert`, `AlertSeverity`.
- No external dependencies.

## Constraints

- All state is in-memory; no persistence across process restarts.
- `ErrorBudgetPolicy` thresholds are hardcoded: 50% -> `increase_reviews`, 75% -> `reduce_risk`, 100% -> `freeze_deployments`.
- `AlertManager.check()` catches and logs handler exceptions without halting evaluation.
- `SLI.value` returns 100.0 when `total_events == 0` (vacuous truth -- no events means no failures).

## Error Handling

- `AlertManager` handler exceptions: caught, logged at WARNING, evaluation continues.
- `DashboardManager.get_panel_data()`: returns empty list if dashboard or panel not found.
