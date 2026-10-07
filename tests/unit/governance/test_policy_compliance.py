"""Tests for PolicyEngine outcome tracking and the compliance pie chart.

Real PolicyEngine evaluations and real matplotlib figures; no mocks.
"""

from __future__ import annotations

import pytest

from codomyrmex.security.governance.policy import PolicyEngine, PolicyError, PolicyRule
from codomyrmex.security.governance.visualization import plot_policy_compliance


def _engine() -> PolicyEngine:
    engine = PolicyEngine()
    engine.create_policy("limits")
    engine.add_rule(
        "limits", PolicyRule("cap", lambda ctx: ctx["amount"] < 100, "reject")
    )
    engine.create_policy("auth")
    engine.add_rule("auth", PolicyRule("signed", lambda ctx: ctx["signed"], "deny"))
    return engine


def _wedge_sweeps(fig) -> list[float]:
    ax = fig.axes[0]
    return [w.theta2 - w.theta1 for w in ax.patches if hasattr(w, "theta1")]


@pytest.mark.unit
class TestComplianceStats:
    def test_new_engine_has_no_evaluations(self):
        assert _engine().compliance_stats() == {
            "evaluations": 0,
            "passed": 0,
            "failed": 0,
        }

    def test_evaluate_records_each_outcome(self):
        engine = _engine()
        for amount in (10, 20, 500):
            engine.evaluate("limits", {"amount": amount})
        engine.evaluate("auth", {"signed": False})
        assert engine.compliance_stats("limits") == {
            "evaluations": 3,
            "passed": 2,
            "failed": 1,
        }
        assert engine.compliance_stats("auth") == {
            "evaluations": 1,
            "passed": 0,
            "failed": 1,
        }
        assert engine.compliance_stats() == {
            "evaluations": 4,
            "passed": 2,
            "failed": 2,
        }

    def test_get_violations_and_enforce_each_record_one_evaluation(self):
        engine = _engine()
        engine.get_violations("limits", {"amount": 1})
        engine.enforce("limits", {"amount": 1000})
        assert engine.compliance_stats("limits") == {
            "evaluations": 2,
            "passed": 1,
            "failed": 1,
        }

    def test_failed_lookup_records_nothing(self):
        engine = _engine()
        with pytest.raises(PolicyError):
            engine.evaluate("missing", {})
        assert engine.compliance_stats()["evaluations"] == 0

    def test_unknown_policy_raises(self):
        with pytest.raises(PolicyError, match="does not exist"):
            _engine().compliance_stats("missing")

    def test_existing_policy_without_evaluations(self):
        assert _engine().compliance_stats("auth")["evaluations"] == 0


@pytest.mark.unit
class TestPlotPolicyCompliance:
    def test_chart_reflects_recorded_outcomes(self):
        engine = _engine()
        for amount in (1, 2, 3, 500):
            engine.evaluate("limits", {"amount": amount})
        fig = plot_policy_compliance(engine)
        assert fig.axes[0].get_title() == "Policy Compliance Rate (n=4)"
        assert _wedge_sweeps(fig) == pytest.approx([270.0, 90.0])
        labels = [t.get_text() for t in fig.axes[0].texts]
        assert "Pass" in labels
        assert "Fail" in labels
        assert "75.0%" in labels
        assert "25.0%" in labels

    def test_single_policy_and_zero_category_omitted(self):
        engine = _engine()
        engine.evaluate("limits", {"amount": 500})
        engine.evaluate("auth", {"signed": True})
        engine.evaluate("auth", {"signed": True})
        fig = plot_policy_compliance(engine, policy_name="auth")
        assert fig.axes[0].get_title() == "Policy Compliance Rate: auth (n=2)"
        assert _wedge_sweeps(fig) == pytest.approx([360.0])
        labels = [t.get_text() for t in fig.axes[0].texts]
        assert "Pass" in labels
        assert "Fail" not in labels

    def test_saves_to_output_path(self, tmp_path):
        engine = _engine()
        engine.evaluate("limits", {"amount": 5})
        out = tmp_path / "compliance.png"
        plot_policy_compliance(engine, output_path=str(out))
        assert out.read_bytes().startswith(b"\x89PNG")

    def test_no_evaluations_raises(self):
        with pytest.raises(ValueError, match="No evaluations recorded"):
            plot_policy_compliance(_engine())

    def test_unknown_policy_raises(self):
        engine = _engine()
        engine.evaluate("limits", {"amount": 5})
        with pytest.raises(PolicyError):
            plot_policy_compliance(engine, policy_name="missing")
