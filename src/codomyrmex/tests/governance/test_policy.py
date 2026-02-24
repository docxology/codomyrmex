import pytest
from codomyrmex.security.governance.policy import PolicyRule, PolicyEngine, PolicyError


def test_policy_enforcement():
    """Test functionality: policy enforcement."""
    engine = PolicyEngine()
    engine.create_policy("limits", "Spending limits")

    rule = PolicyRule("Limit", lambda ctx: ctx["amount"] < 100, "Amount too high")
    engine.add_rule("limits", rule)

    # Valid
    result = engine.evaluate("limits", {"amount": 50})
    assert result["passed"] is True

    # Invalid
    result = engine.evaluate("limits", {"amount": 150})
    assert result["passed"] is False
    assert result["violations"] == 1


def test_multiple_policies():
    """Test functionality: multiple policies."""
    engine = PolicyEngine()
    engine.create_policy("checks", "Multi-rule checks")

    r1 = PolicyRule("Positive", lambda ctx: ctx["val"] > 0, "Must be positive")
    r2 = PolicyRule("Even", lambda ctx: ctx["val"] % 2 == 0, "Must be even")
    engine.add_rule("checks", r1)
    engine.add_rule("checks", r2)

    # Valid
    result = engine.evaluate("checks", {"val": 2})
    assert result["passed"] is True

    # Fail both
    result = engine.evaluate("checks", {"val": -3})
    assert result["passed"] is False
    assert result["violations"] == 2
