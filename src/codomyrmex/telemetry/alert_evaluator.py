"""Alert evaluation engine.

Rule-based alerting: metric threshold → alert with severity
and configurable routing (log, webhook, event bus).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from collections.abc import Callable

from codomyrmex.telemetry.metric_aggregator import MetricAggregator


class AlertSeverity(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertState(Enum):
    """Alert state."""

    OK = "ok"
    FIRING = "firing"
    RESOLVED = "resolved"


@dataclass
class AlertRule:
    """An alerting rule.

    Attributes:
        name: Rule identifier.
        metric_name: Metric to evaluate.
        threshold: Threshold value.
        operator: Comparison operator (gt, lt, gte, lte, eq).
        severity: Alert severity.
        message: Alert message template.
    """

    name: str
    metric_name: str
    threshold: float
    operator: str = "gt"
    severity: AlertSeverity = AlertSeverity.WARNING
    message: str = ""


@dataclass
class Alert:
    """A fired alert.

    Attributes:
        rule_name: Rule that triggered.
        metric_name: Metric that triggered.
        current_value: Current metric value.
        threshold: Threshold value.
        severity: Alert severity.
        state: Current alert state.
        message: Alert message.
        timestamp: When the alert fired.
    """

    rule_name: str
    metric_name: str
    current_value: float
    threshold: float
    severity: AlertSeverity = AlertSeverity.WARNING
    state: AlertState = AlertState.FIRING
    message: str = ""
    timestamp: float = field(default_factory=time.time)


class AlertEvaluator:
    """Evaluate alert rules against current metrics.

    Example::

        evaluator = AlertEvaluator(metrics=aggregator)
        evaluator.add_rule(AlertRule(
            name="high_latency", metric_name="latency_ms",
            threshold=100, operator="gt", severity=AlertSeverity.CRITICAL,
        ))
        alerts = evaluator.evaluate()
    """

    _OPERATORS: dict[str, Callable[[float, float], bool]] = {
        "gt": lambda v, t: v > t,
        "lt": lambda v, t: v < t,
        "gte": lambda v, t: v >= t,
        "lte": lambda v, t: v <= t,
        "eq": lambda v, t: v == t,
    }

    def __init__(self, metrics: MetricAggregator) -> None:
        """Execute   Init   operations natively."""
        self._metrics = metrics
        self._rules: dict[str, AlertRule] = {}
        self._alerts: list[Alert] = []
        self._active: dict[str, Alert] = {}

    @property
    def rule_count(self) -> int:
        """Execute Rule Count operations natively."""
        return len(self._rules)

    @property
    def active_alerts(self) -> list[Alert]:
        """Execute Active Alerts operations natively."""
        return list(self._active.values())

    def add_rule(self, rule: AlertRule) -> None:
        """Register an alert rule."""
        self._rules[rule.name] = rule

    def remove_rule(self, name: str) -> bool:
        """Remove an alert rule."""
        return self._rules.pop(name, None) is not None

    def evaluate(self) -> list[Alert]:
        """Evaluate all rules against current metrics.

        Returns:
            List of newly fired alerts.
        """
        new_alerts: list[Alert] = []
        snap = self._metrics.snapshot()

        for rule in self._rules.values():
            value = self._get_metric_value(rule, snap)
            if value is None:
                continue

            op = self._OPERATORS.get(rule.operator)
            if op is None:
                continue

            if op(value, rule.threshold):
                alert = Alert(
                    rule_name=rule.name,
                    metric_name=rule.metric_name,
                    current_value=value,
                    threshold=rule.threshold,
                    severity=rule.severity,
                    message=rule.message or f"{rule.name}: {value} {rule.operator} {rule.threshold}",
                )
                new_alerts.append(alert)
                self._active[rule.name] = alert
            else:
                # Resolve if previously active
                if rule.name in self._active:
                    self._active[rule.name].state = AlertState.RESOLVED
                    del self._active[rule.name]

        self._alerts.extend(new_alerts)
        return new_alerts

    def alert_history(self) -> list[Alert]:
        """Get full alert history."""
        return list(self._alerts)

    def _get_metric_value(self, rule: AlertRule, snap: Any) -> float | None:
        """Extract metric value from snapshot."""
        if rule.metric_name in snap.counters:
            return snap.counters[rule.metric_name]
        if rule.metric_name in snap.gauges:
            return snap.gauges[rule.metric_name]
        hist = snap.histograms.get(rule.metric_name, {})
        if hist:
            return hist.get("mean")
        return None


__all__ = ["Alert", "AlertEvaluator", "AlertRule", "AlertSeverity", "AlertState"]
