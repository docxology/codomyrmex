"""
Alert Manager

Alert rule management and notification for observability.
"""

import threading
from collections.abc import Callable

from .models import Alert, AlertSeverity


class AlertManager:
    """
    Manages alerts and notifications.

    Usage:
        alerts = AlertManager()

        # Define alert rule
        alerts.add_rule(
            name="high_cpu",
            condition=lambda m: m.get("cpu_usage", 0) > 0.9,
            message="CPU usage is high",
        )

        # Check metrics
        alerts.check({"cpu_usage": 0.95})
    """

    def __init__(self):
        """Execute   Init   operations natively."""
        self._alerts: dict[str, Alert] = {}
        self._rules: dict[str, dict[str, any]] = {}
        self._counter = 0
        self._lock = threading.Lock()

    def add_rule(
        self,
        name: str,
        condition: Callable[[dict[str, float]], bool],
        message: str,
        severity: AlertSeverity = AlertSeverity.WARNING,
    ) -> None:
        """Add an alert rule."""
        self._rules[name] = {
            "condition": condition,
            "message": message,
            "severity": severity,
        }

    def check(self, metrics: dict[str, float]) -> list[Alert]:
        """Check metrics against rules and fire alerts."""
        new_alerts = []

        for rule_name, rule in self._rules.items():
            try:
                if rule["condition"](metrics):
                    if rule_name not in self._alerts or not self._alerts[rule_name].is_active:
                        with self._lock:
                            self._counter += 1
                            alert = Alert(
                                id=f"alert_{self._counter}",
                                name=rule_name,
                                message=rule["message"],
                                severity=rule["severity"],
                            )
                            self._alerts[rule_name] = alert
                            new_alerts.append(alert)
                else:
                    if rule_name in self._alerts and self._alerts[rule_name].is_active:
                        self._alerts[rule_name].resolve()
            except Exception:
                pass

        return new_alerts

    def get_active_alerts(self) -> list[Alert]:
        """Get all active alerts."""
        return [a for a in self._alerts.values() if a.is_active]

    def get_alert_history(self, limit: int = 100) -> list[Alert]:
        """Get alert history."""
        alerts = list(self._alerts.values())
        alerts.sort(key=lambda a: a.fired_at, reverse=True)
        return alerts[:limit]

    def acknowledge(self, alert_id: str) -> bool:
        """Acknowledge an alert."""
        for alert in self._alerts.values():
            if alert.id == alert_id:
                alert.resolve()
                return True
        return False
