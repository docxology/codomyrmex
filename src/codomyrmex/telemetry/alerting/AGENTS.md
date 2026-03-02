# Telemetry Alerting - Agentic Context

**Module**: `codomyrmex.telemetry.alerting`
**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Key Components

| Component | Purpose | Key Methods |
|-----------|---------|-------------|
| `AlertEvaluator` | Evaluates `AlertRule` objects against `MetricAggregator` snapshots (counters, gauges, histograms) | `add_rule()`, `remove_rule()`, `evaluate()`, `alert_history()` |
| `AlertEngine` | Standalone rule engine evaluating dict-based metrics with handler callbacks | `add_rule()`, `on_alert()`, `evaluate()` |
| `AlertRule` (alert_evaluator) | Rule dataclass: metric name, threshold, operator (gt/lt/gte/lte/eq), severity | Dataclass |
| `AlertRule` (alerts) | Rule dataclass with `evaluate(value)` method and `message_template` formatting | `evaluate()` returns bool |
| `Alert` | Fired alert record: rule name, severity, value, state (FIRING/RESOLVED), timestamp | Dataclass with `to_dict()` |
| `AlertSeverity` | Enum: INFO, WARNING, CRITICAL | Enum |
| `AlertState` | Enum: OK, FIRING, RESOLVED | Enum |

## Operating Contracts

- Two parallel implementations exist: `alert_evaluator.py` evaluates against `MetricAggregator` snapshots; `alerts.py` evaluates against flat `dict[str, float]` metrics.
- `AlertEvaluator` tracks active alerts and auto-resolves when a previously firing rule stops triggering.
- `AlertEngine` dispatches to registered `AlertHandler` callbacks; handler exceptions are caught, logged at WARNING, and do not prevent other handlers from running.
- Operator comparison uses a dict of lambdas mapping string operators (`"gt"`, `"lt"`, etc.) to comparison functions.

## Integration Points

- **telemetry.metric_aggregator**: `AlertEvaluator` reads counters/gauges/histograms from `MetricAggregator.snapshot()`.
- **logging_monitoring**: `AlertEngine` uses `get_logger` for handler failure warnings.
- **telemetry.dashboard.alerting**: `AlertManager` provides a higher-level API layered on similar concepts.

## Constraints

- No persistence of alert history; state is in-memory only and lost on process restart.
- `AlertEvaluator` extracts histogram `mean` for threshold comparison; percentile-based alerting is not supported.
