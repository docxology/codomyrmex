"""
Unit tests for feature_flags.evaluation — Zero-Mock compliant.

Covers: TargetingRule (matches — all 8 operators, missing attribute, unknown
operator, type error), FlagDefinition (defaults), FlagEvaluator (global
disabled, targeting rules, percentage rollout determinism, full 100%,
mixed targeting+percentage, evaluate_targeting_rules, evaluate_percentage_rollout).
"""

import pytest

from codomyrmex.feature_flags.evaluation import (
    FlagDefinition,
    FlagEvaluator,
    TargetingRule,
)
from codomyrmex.feature_flags.strategies import EvaluationContext


# ── TargetingRule ──────────────────────────────────────────────────────────


@pytest.mark.unit
class TestTargetingRuleOperators:
    def _ctx(self, **attrs) -> EvaluationContext:
        return EvaluationContext(attributes=attrs)

    def test_eq_matches(self):
        rule = TargetingRule(attribute="role", operator="eq", value="admin")
        assert rule.matches(self._ctx(role="admin")) is True

    def test_eq_no_match(self):
        rule = TargetingRule(attribute="role", operator="eq", value="admin")
        assert rule.matches(self._ctx(role="user")) is False

    def test_neq_matches(self):
        rule = TargetingRule(attribute="role", operator="neq", value="guest")
        assert rule.matches(self._ctx(role="admin")) is True

    def test_in_matches(self):
        rule = TargetingRule(attribute="plan", operator="in", value=["free", "pro"])
        assert rule.matches(self._ctx(plan="pro")) is True

    def test_in_no_match(self):
        rule = TargetingRule(attribute="plan", operator="in", value=["free", "pro"])
        assert rule.matches(self._ctx(plan="enterprise")) is False

    def test_contains_matches(self):
        rule = TargetingRule(attribute="tags", operator="contains", value="beta")
        assert rule.matches(self._ctx(tags=["alpha", "beta", "gamma"])) is True

    def test_contains_no_match(self):
        rule = TargetingRule(attribute="tags", operator="contains", value="beta")
        assert rule.matches(self._ctx(tags=["alpha", "gamma"])) is False

    def test_gt_matches(self):
        rule = TargetingRule(attribute="age", operator="gt", value=18)
        assert rule.matches(self._ctx(age=25)) is True

    def test_gt_no_match(self):
        rule = TargetingRule(attribute="age", operator="gt", value=18)
        assert rule.matches(self._ctx(age=10)) is False

    def test_lt_matches(self):
        rule = TargetingRule(attribute="score", operator="lt", value=100)
        assert rule.matches(self._ctx(score=50)) is True

    def test_gte_boundary(self):
        rule = TargetingRule(attribute="count", operator="gte", value=5)
        assert rule.matches(self._ctx(count=5)) is True

    def test_lte_boundary(self):
        rule = TargetingRule(attribute="count", operator="lte", value=5)
        assert rule.matches(self._ctx(count=5)) is True

    def test_missing_attribute_returns_false(self):
        rule = TargetingRule(attribute="role", operator="eq", value="admin")
        assert rule.matches(self._ctx()) is False

    def test_unknown_operator_returns_false(self):
        rule = TargetingRule(attribute="x", operator="bogus", value="y")
        assert rule.matches(self._ctx(x="y")) is False

    def test_type_error_returns_false(self):
        """Comparison between incompatible types returns False (not raises)."""
        rule = TargetingRule(attribute="score", operator="gt", value="threshold")
        # int > str raises TypeError in Python 3
        assert rule.matches(self._ctx(score=10)) is False


# ── FlagDefinition ─────────────────────────────────────────────────────────


@pytest.mark.unit
class TestFlagDefinition:
    def test_name_stored(self):
        f = FlagDefinition(name="my-flag")
        assert f.name == "my-flag"

    def test_enabled_default_true(self):
        f = FlagDefinition(name="my-flag")
        assert f.enabled is True

    def test_percentage_default_100(self):
        f = FlagDefinition(name="my-flag")
        assert f.percentage == pytest.approx(100.0)

    def test_targeting_rules_default_empty(self):
        f = FlagDefinition(name="my-flag")
        assert f.targeting_rules == []


# ── FlagEvaluator ──────────────────────────────────────────────────────────


@pytest.mark.unit
class TestFlagEvaluatorGlobalDisabled:
    def test_globally_disabled_returns_disabled(self):
        ev = FlagEvaluator()
        flag = FlagDefinition(name="feat", enabled=False)
        result = ev.evaluate(flag, EvaluationContext())
        assert result.enabled is False

    def test_globally_disabled_reason(self):
        ev = FlagEvaluator()
        flag = FlagDefinition(name="feat", enabled=False)
        result = ev.evaluate(flag, EvaluationContext())
        assert result.reason == "flag_disabled"


@pytest.mark.unit
class TestFlagEvaluatorTargetingRules:
    def test_no_rules_returns_enabled(self):
        ev = FlagEvaluator()
        flag = FlagDefinition(name="feat")
        result = ev.evaluate(flag, EvaluationContext())
        assert result.enabled is True

    def test_matching_rule_allows_flag(self):
        ev = FlagEvaluator()
        rule = TargetingRule(attribute="plan", operator="eq", value="premium")
        flag = FlagDefinition(name="feat", targeting_rules=[rule])
        ctx = EvaluationContext(attributes={"plan": "premium"})
        result = ev.evaluate(flag, ctx)
        assert result.enabled is True

    def test_non_matching_rule_blocks_flag(self):
        ev = FlagEvaluator()
        rule = TargetingRule(attribute="plan", operator="eq", value="premium")
        flag = FlagDefinition(name="feat", targeting_rules=[rule])
        ctx = EvaluationContext(attributes={"plan": "free"})
        result = ev.evaluate(flag, ctx)
        assert result.enabled is False

    def test_non_matching_rule_reason(self):
        ev = FlagEvaluator()
        rule = TargetingRule(attribute="plan", operator="eq", value="premium")
        flag = FlagDefinition(name="feat", targeting_rules=[rule])
        ctx = EvaluationContext(attributes={"plan": "free"})
        result = ev.evaluate(flag, ctx)
        assert result.reason == "targeting_rules_no_match"

    def test_multiple_rules_or_logic_first_matches(self):
        """Any one rule matching enables the flag."""
        ev = FlagEvaluator()
        rule1 = TargetingRule(attribute="plan", operator="eq", value="premium")
        rule2 = TargetingRule(attribute="role", operator="eq", value="admin")
        flag = FlagDefinition(name="feat", targeting_rules=[rule1, rule2])
        ctx = EvaluationContext(attributes={"plan": "free", "role": "admin"})
        result = ev.evaluate(flag, ctx)
        assert result.enabled is True

    def test_multiple_rules_none_match_blocks_flag(self):
        ev = FlagEvaluator()
        rule1 = TargetingRule(attribute="plan", operator="eq", value="premium")
        rule2 = TargetingRule(attribute="role", operator="eq", value="admin")
        flag = FlagDefinition(name="feat", targeting_rules=[rule1, rule2])
        ctx = EvaluationContext(attributes={"plan": "free", "role": "user"})
        result = ev.evaluate(flag, ctx)
        assert result.enabled is False


@pytest.mark.unit
class TestFlagEvaluatorPercentageRollout:
    def test_100_percent_always_enabled(self):
        ev = FlagEvaluator()
        flag = FlagDefinition(name="feat", percentage=100.0)
        # Multiple users should all be enabled
        for uid in ("alice", "bob", "charlie", "dave"):
            result = ev.evaluate(flag, EvaluationContext(user_id=uid))
            assert result.enabled is True, f"Expected enabled for user {uid}"

    def test_0_percent_always_disabled(self):
        ev = FlagEvaluator()
        flag = FlagDefinition(name="feat", percentage=0.0)
        for uid in ("alice", "bob", "charlie"):
            result = ev.evaluate(flag, EvaluationContext(user_id=uid))
            assert result.enabled is False, f"Expected disabled for user {uid}"

    def test_percentage_reason_contains_value(self):
        ev = FlagEvaluator()
        flag = FlagDefinition(name="feat", percentage=50.0)
        result = ev.evaluate(flag, EvaluationContext(user_id="alice"))
        assert "50.0" in result.reason

    def test_percentage_rollout_deterministic(self):
        """Same user/flag combo always returns the same result."""
        ev = FlagEvaluator()
        flag = FlagDefinition(name="my-flag", percentage=50.0)
        ctx = EvaluationContext(user_id="stable-user-123")
        result1 = ev.evaluate(flag, ctx)
        result2 = ev.evaluate(flag, ctx)
        assert result1.enabled == result2.enabled

    def test_evaluate_percentage_rollout_direct(self):
        """evaluate_percentage_rollout is deterministic for same flag+user."""
        ev = FlagEvaluator()
        flag = FlagDefinition(name="feature-x", percentage=60.0)
        user_id = "test-user-abc"
        r1 = ev.evaluate_percentage_rollout(flag, user_id)
        r2 = ev.evaluate_percentage_rollout(flag, user_id)
        assert r1 == r2

    def test_evaluate_targeting_rules_any_match(self):
        rule_a = TargetingRule(attribute="x", operator="eq", value=1)
        rule_b = TargetingRule(attribute="y", operator="eq", value=2)
        ctx = EvaluationContext(attributes={"x": 1, "y": 99})
        ev = FlagEvaluator()
        assert ev.evaluate_targeting_rules([rule_a, rule_b], ctx) is True

    def test_evaluate_targeting_rules_none_match(self):
        rule_a = TargetingRule(attribute="x", operator="eq", value=1)
        ctx = EvaluationContext(attributes={"x": 99})
        ev = FlagEvaluator()
        assert ev.evaluate_targeting_rules([rule_a], ctx) is False

    def test_full_flow_enabled_reason(self):
        """Flag with no rules at 100% → reason='enabled'."""
        ev = FlagEvaluator()
        flag = FlagDefinition(name="feat")
        result = ev.evaluate(flag, EvaluationContext())
        assert result.reason == "enabled"

    def test_percentage_metadata_contains_percentage(self):
        ev = FlagEvaluator()
        flag = FlagDefinition(name="feat", percentage=30.0)
        result = ev.evaluate(flag, EvaluationContext(user_id="user-xyz"))
        assert result.metadata.get("percentage") == pytest.approx(30.0)
