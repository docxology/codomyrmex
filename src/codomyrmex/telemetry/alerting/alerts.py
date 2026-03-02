"""Rule-based alert engine for telemetry data.

Evaluates alert rules against metric values and fires notifications.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


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
    """A rule for generating alerts.

    Attributes:
        name: Rule name.
        metric: Metric name to evaluate.
        condition: ``gt``, ``lt``, ``eq``, ``gte``, ``lte``.
        threshold: Threshold value.
        severity: Alert severity.
        message_template: Alert message template.
    """

    name: str
    metric: str
    condition: str = "gt"
    threshold: float = 0.0
    severity: AlertSeverity = AlertSeverity.WARNING
    message_template: str = "{metric} is {value} (threshold: {threshold})"

    def evaluate(self, value: float) -> bool:
        """Evaluate."""
        ops = {
            "gt": value > self.threshold,
            "lt": value < self.threshold,
            "eq": value == self.threshold,
            "gte": value >= self.threshold,
            "lte": value <= self.threshold,
        }
        return ops.get(self.condition, False)


@dataclass
class Alert:
    """A fired alert.

    Attributes:
        rule_name: Name of the rule that fired.
        severity: Alert severity.
        message: Human-readable message.
        value: Metric value that triggered.
        state: Current alert state.
        fired_at: Timestamp.
    """

    rule_name: str
    severity: AlertSeverity = AlertSeverity.WARNING
    message: str = ""
    value: float = 0.0
    state: AlertState = AlertState.FIRING
    fired_at: float = 0.0

    def __post_init__(self) -> None:
        if not self.fired_at:
            self.fired_at = time.time()

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "rule": self.rule_name,
            "severity": self.severity.value,
            "message": self.message,
            "value": self.value,
            "state": self.state.value,
        }


AlertHandler = Callable[[Alert], None]


class AlertEngine:
    """Evaluate metrics against rules and fire alerts.

    Usage::

        engine = AlertEngine()
        engine.add_rule(AlertRule("high_error_rate", "error_rate", "gt", 0.05))
        alerts = engine.evaluate({"error_rate": 0.08})
    """

    def __init__(self) -> None:
        self._rules: list[AlertRule] = []
        self._handlers: list[AlertHandler] = []
        self._alert_history: list[Alert] = []

    def add_rule(self, rule: AlertRule) -> None:
        self._rules.append(rule)

    def on_alert(self, handler: AlertHandler) -> None:
        self._handlers.append(handler)

    def evaluate(self, metrics: dict[str, float]) -> list[Alert]:
        """Evaluate all rules against provided metrics.

        Returns:
            List of fired alerts.
        """
        fired: list[Alert] = []
        for rule in self._rules:
            value = metrics.get(rule.metric)
            if value is not None and rule.evaluate(value):
                msg = rule.message_template.format(
                    metric=rule.metric,
                    value=value,
                    threshold=rule.threshold,
                )
                alert = Alert(
                    rule_name=rule.name,
                    severity=rule.severity,
                    message=msg,
                    value=value,
                )
                fired.append(alert)
                self._alert_history.append(alert)

                for handler in self._handlers:
                    try:
                        handler(alert)
                    except Exception as e:
                        logger.warning("Alert handler failed for rule %s: %s", rule.name, e)
                        pass

        return fired

    @property
    def rule_count(self) -> int:
        return len(self._rules)

    @property
    def history(self) -> list[Alert]:
        """History."""
        return list(self._alert_history)


__all__ = ["Alert", "AlertEngine", "AlertRule", "AlertSeverity", "AlertState"]
