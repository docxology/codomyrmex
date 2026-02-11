import pytest
from codomyrmex.governance.policy import Policy, PolicyEngine, PolicyError

def test_policy_enforcement():
    # Rule: Amount must be less than 100
    p1 = Policy("Limit", lambda ctx: ctx["amount"] < 100, "Amount too high")
    
    engine = PolicyEngine()
    engine.add_policy(p1)
    
    # Valid
    engine.enforce({"amount": 50})
    
    # Invalid
    with pytest.raises(PolicyError, match="Amount too high"):
        engine.enforce({"amount": 150})

def test_multiple_policies():
    p1 = Policy("Positive", lambda ctx: ctx["val"] > 0, "Must be positive")
    p2 = Policy("Even", lambda ctx: ctx["val"] % 2 == 0, "Must be even")
    
    engine = PolicyEngine()
    engine.add_policy(p1)
    engine.add_policy(p2)
    
    # Valid
    engine.enforce({"val": 2})
    
    # Fail both
    with pytest.raises(PolicyError) as excinfo:
        engine.enforce({"val": -3})
    
    assert "Must be positive" in str(excinfo.value)
    assert "Must be even" in str(excinfo.value)
