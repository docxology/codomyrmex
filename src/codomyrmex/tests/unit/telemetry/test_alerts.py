"""
Unit tests for telemetry.alerting.alerts — Zero-Mock compliant.

Covers: AlertSeverity, AlertState (enum values), AlertRule.evaluate
(gt/lt/eq/gte/lte/unknown), Alert (dataclass, __post_init__, to_dict),
AlertEngine (add_rule, on_alert, evaluate, rule_count, history).
"""

import pytest

from codomyrmex.telemetry.alerting.alerts import (
    Alert,
    AlertEngine,
    AlertRule,
    AlertSeverity,
    AlertState,
)

# ── AlertSeverity ──────────────────────────────────────────────────────


@pytest.mark.unit
class TestAlertSeverity:
    def test_info_value(self):
        assert AlertSeverity.INFO.value == "info"

    def test_warning_value(self):
        assert AlertSeverity.WARNING.value == "warning"

    def test_critical_value(self):
        assert AlertSeverity.CRITICAL.value == "critical"


# ── AlertState ─────────────────────────────────────────────────────────


@pytest.mark.unit
class TestAlertState:
    def test_ok_value(self):
        assert AlertState.OK.value == "ok"

    def test_firing_value(self):
        assert AlertState.FIRING.value == "firing"

    def test_resolved_value(self):
        assert AlertState.RESOLVED.value == "resolved"


# ── AlertRule ──────────────────────────────────────────────────────────


@pytest.mark.unit
class TestAlertRule:
    def test_defaults(self):
        r = AlertRule(name="test", metric="cpu")
        assert r.condition == "gt"
        assert r.threshold == 0.0
        assert r.severity == AlertSeverity.WARNING

    def test_evaluate_gt_true(self):
        r = AlertRule("r", "m", condition="gt", threshold=5.0)
        assert r.evaluate(6.0) is True

    def test_evaluate_gt_false(self):
        r = AlertRule("r", "m", condition="gt", threshold=5.0)
        assert r.evaluate(5.0) is False
        assert r.evaluate(4.0) is False

    def test_evaluate_lt_true(self):
        r = AlertRule("r", "m", condition="lt", threshold=5.0)
        assert r.evaluate(4.0) is True

    def test_evaluate_lt_false(self):
        r = AlertRule("r", "m", condition="lt", threshold=5.0)
        assert r.evaluate(5.0) is False
        assert r.evaluate(6.0) is False

    def test_evaluate_eq_true(self):
        r = AlertRule("r", "m", condition="eq", threshold=5.0)
        assert r.evaluate(5.0) is True

    def test_evaluate_eq_false(self):
        r = AlertRule("r", "m", condition="eq", threshold=5.0)
        assert r.evaluate(4.9) is False

    def test_evaluate_gte_at_threshold(self):
        r = AlertRule("r", "m", condition="gte", threshold=5.0)
        assert r.evaluate(5.0) is True

    def test_evaluate_gte_above(self):
        r = AlertRule("r", "m", condition="gte", threshold=5.0)
        assert r.evaluate(6.0) is True

    def test_evaluate_gte_below(self):
        r = AlertRule("r", "m", condition="gte", threshold=5.0)
        assert r.evaluate(4.9) is False

    def test_evaluate_lte_at_threshold(self):
        r = AlertRule("r", "m", condition="lte", threshold=5.0)
        assert r.evaluate(5.0) is True

    def test_evaluate_lte_below(self):
        r = AlertRule("r", "m", condition="lte", threshold=5.0)
        assert r.evaluate(4.0) is True

    def test_evaluate_lte_above(self):
        r = AlertRule("r", "m", condition="lte", threshold=5.0)
        assert r.evaluate(5.1) is False

    def test_evaluate_unknown_condition_returns_false(self):
        r = AlertRule("r", "m", condition="neq", threshold=5.0)
        assert r.evaluate(5.0) is False
        assert r.evaluate(99.0) is False

    def test_custom_severity(self):
        r = AlertRule("r", "m", severity=AlertSeverity.CRITICAL)
        assert r.severity == AlertSeverity.CRITICAL

    def test_custom_message_template(self):
        r = AlertRule("r", "m", message_template="Alert: {metric}")
        assert "{metric}" in r.message_template


# ── Alert ──────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestAlert:
    def test_defaults(self):
        a = Alert(rule_name="my_rule")
        assert a.severity == AlertSeverity.WARNING
        assert a.message == ""
        assert a.value == 0.0
        assert a.state == AlertState.FIRING

    def test_fired_at_set_automatically(self):
        a = Alert(rule_name="r")
        assert a.fired_at > 0.0

    def test_fired_at_explicit_value_preserved(self):
        a = Alert(rule_name="r", fired_at=12345.0)
        assert a.fired_at == pytest.approx(12345.0)

    def test_to_dict_has_required_keys(self):
        a = Alert(rule_name="cpu_high", severity=AlertSeverity.CRITICAL, message="CPU over limit", value=95.0)
        d = a.to_dict()
        assert d["rule"] == "cpu_high"
        assert d["severity"] == "critical"
        assert d["message"] == "CPU over limit"
        assert d["value"] == pytest.approx(95.0)
        assert d["state"] == "firing"

    def test_to_dict_state_value(self):
        a = Alert(rule_name="r", state=AlertState.RESOLVED)
        d = a.to_dict()
        assert d["state"] == "resolved"


# ── AlertEngine ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestAlertEngine:
    def test_initial_rule_count_zero(self):
        engine = AlertEngine()
        assert engine.rule_count == 0

    def test_add_rule_increments_count(self):
        engine = AlertEngine()
        engine.add_rule(AlertRule("r1", "metric1"))
        assert engine.rule_count == 1

    def test_add_multiple_rules(self):
        engine = AlertEngine()
        engine.add_rule(AlertRule("r1", "m1"))
        engine.add_rule(AlertRule("r2", "m2"))
        assert engine.rule_count == 2

    def test_history_empty_initially(self):
        engine = AlertEngine()
        assert engine.history == []

    def test_evaluate_fires_alert_when_condition_met(self):
        engine = AlertEngine()
        engine.add_rule(AlertRule("high_cpu", "cpu_pct", condition="gt", threshold=80.0))
        fired = engine.evaluate({"cpu_pct": 90.0})
        assert len(fired) == 1
        assert fired[0].rule_name == "high_cpu"

    def test_evaluate_no_alert_when_condition_not_met(self):
        engine = AlertEngine()
        engine.add_rule(AlertRule("high_cpu", "cpu_pct", condition="gt", threshold=80.0))
        fired = engine.evaluate({"cpu_pct": 70.0})
        assert fired == []

    def test_evaluate_skips_missing_metric(self):
        engine = AlertEngine()
        engine.add_rule(AlertRule("r", "missing_metric", condition="gt", threshold=5.0))
        fired = engine.evaluate({"other_metric": 100.0})
        assert fired == []

    def test_evaluate_multiple_rules(self):
        engine = AlertEngine()
        engine.add_rule(AlertRule("r1", "cpu", condition="gt", threshold=80.0))
        engine.add_rule(AlertRule("r2", "mem", condition="gt", threshold=90.0))
        fired = engine.evaluate({"cpu": 85.0, "mem": 95.0})
        assert len(fired) == 2

    def test_evaluate_partial_triggers(self):
        engine = AlertEngine()
        engine.add_rule(AlertRule("r1", "cpu", condition="gt", threshold=80.0))
        engine.add_rule(AlertRule("r2", "mem", condition="gt", threshold=90.0))
        fired = engine.evaluate({"cpu": 85.0, "mem": 85.0})
        assert len(fired) == 1
        assert fired[0].rule_name == "r1"

    def test_evaluate_updates_history(self):
        engine = AlertEngine()
        engine.add_rule(AlertRule("r1", "cpu", condition="gt", threshold=80.0))
        engine.evaluate({"cpu": 90.0})
        assert len(engine.history) == 1

    def test_evaluate_accumulates_history(self):
        engine = AlertEngine()
        engine.add_rule(AlertRule("r1", "cpu", condition="gt", threshold=80.0))
        engine.evaluate({"cpu": 90.0})
        engine.evaluate({"cpu": 95.0})
        assert len(engine.history) == 2

    def test_history_is_copy(self):
        engine = AlertEngine()
        engine.add_rule(AlertRule("r", "cpu", condition="gt", threshold=80.0))
        engine.evaluate({"cpu": 90.0})
        history = engine.history
        history.clear()
        # Original should still have the alert
        assert len(engine.history) == 1

    def test_alert_has_correct_value(self):
        engine = AlertEngine()
        engine.add_rule(AlertRule("r", "latency_ms", condition="gt", threshold=100.0))
        fired = engine.evaluate({"latency_ms": 150.0})
        assert fired[0].value == pytest.approx(150.0)

    def test_alert_message_formatted(self):
        engine = AlertEngine()
        rule = AlertRule("r", "cpu_pct", condition="gt", threshold=80.0)
        engine.add_rule(rule)
        fired = engine.evaluate({"cpu_pct": 90.0})
        msg = fired[0].message
        assert "cpu_pct" in msg
        assert "90.0" in msg or "90" in msg

    def test_on_alert_handler_called(self):
        received = []
        engine = AlertEngine()
        engine.on_alert(lambda a: received.append(a))
        engine.add_rule(AlertRule("r", "metric", condition="gt", threshold=0.0))
        engine.evaluate({"metric": 1.0})
        assert len(received) == 1

    def test_on_alert_handler_exception_does_not_propagate(self):
        def bad_handler(alert):
            raise RuntimeError("handler failure")

        engine = AlertEngine()
        engine.on_alert(bad_handler)
        engine.add_rule(AlertRule("r", "metric", condition="gt", threshold=0.0))
        # Should NOT raise even though handler fails
        fired = engine.evaluate({"metric": 1.0})
        assert len(fired) == 1

    def test_multiple_handlers(self):
        received_a = []
        received_b = []
        engine = AlertEngine()
        engine.on_alert(lambda a: received_a.append(a))
        engine.on_alert(lambda a: received_b.append(a))
        engine.add_rule(AlertRule("r", "m", condition="gt", threshold=0.0))
        engine.evaluate({"m": 1.0})
        assert len(received_a) == 1
        assert len(received_b) == 1

    def test_evaluate_returns_list(self):
        engine = AlertEngine()
        result = engine.evaluate({})
        assert isinstance(result, list)
