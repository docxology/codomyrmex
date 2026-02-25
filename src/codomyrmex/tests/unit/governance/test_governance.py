"""Tests for the governance module.

Tests cover:
- Module import
- ContractStatus enum values and count
- ContractTerm creation, validation, fulfillment, is_overdue
- Contract construction, validation (min 2 parties, no duplicates)
- Contract add_term, sign, auto-activate, reject non-party, reject duplicate sign
- Contract expire, is_active, get_status, repr
- Contract check_compliance (no terms, all fulfilled, overdue, mixed)
- PolicyRule creation, evaluate (pass, fail, exception)
- PolicyEngine create_policy, add_rule, evaluate, get_violations, enforce
- PolicyEngine duplicate policy raises, nonexistent policy raises
- PolicyEngine list_policies
- Edge cases: signing non-DRAFT contract, adding term to non-DRAFT contract
"""

from datetime import datetime, timedelta

import pytest

from codomyrmex.security.governance.contracts import (
    Contract,
    ContractError,
    ContractStatus,
    ContractTerm,
)
from codomyrmex.security.governance.policy import PolicyEngine, PolicyError, PolicyRule

# ======================================================================
# Module & Enum tests
# ======================================================================

@pytest.mark.unit
def test_module_import():
    """governance module is importable."""
    from codomyrmex.security import governance
    assert governance is not None


@pytest.mark.unit
def test_contract_status_enum_values():
    """ContractStatus has expected members with string values."""
    assert ContractStatus.DRAFT.value == "draft"
    assert ContractStatus.ACTIVE.value == "active"
    assert ContractStatus.EXPIRED.value == "expired"
    assert ContractStatus.TERMINATED.value == "terminated"
    assert ContractStatus.DISPUTED.value == "disputed"


@pytest.mark.unit
def test_contract_status_enum_count():
    """ContractStatus has exactly five members."""
    members = list(ContractStatus)
    assert len(members) == 5


@pytest.mark.unit
def test_contract_status_distinct_values():
    """Each ContractStatus member has a distinct value."""
    values = [s.value for s in ContractStatus]
    assert len(values) == len(set(values))


# ======================================================================
# ContractTerm tests
# ======================================================================

@pytest.mark.unit
def test_contract_term_creation():
    """ContractTerm stores description, type, party, defaults."""
    term = ContractTerm(
        description="Must deliver goods",
        type="obligation",
        party="Alice",
    )
    assert term.description == "Must deliver goods"
    assert term.type == "obligation"
    assert term.party == "Alice"
    assert term.fulfilled is False
    assert term.deadline is None


@pytest.mark.unit
def test_contract_term_valid_types():
    """ContractTerm accepts obligation, prohibition, permission."""
    for t in ("obligation", "prohibition", "permission"):
        term = ContractTerm(description="test", type=t, party="X")
        assert term.type == t


@pytest.mark.unit
def test_contract_term_invalid_type_raises():
    """ContractTerm rejects invalid type."""
    with pytest.raises(ContractError, match="Invalid term type"):
        ContractTerm(description="test", type="invalid", party="X")


@pytest.mark.unit
def test_contract_term_fulfill():
    """ContractTerm.fulfill marks term as fulfilled."""
    term = ContractTerm(description="test", type="obligation", party="A")
    assert term.fulfilled is False
    term.fulfill()
    assert term.fulfilled is True


@pytest.mark.unit
def test_contract_term_is_overdue_no_deadline():
    """is_overdue returns False when no deadline is set."""
    term = ContractTerm(description="test", type="obligation", party="A")
    assert term.is_overdue() is False


@pytest.mark.unit
def test_contract_term_is_overdue_past_deadline():
    """is_overdue returns True when deadline is in the past and not fulfilled."""
    term = ContractTerm(
        description="test",
        type="obligation",
        party="A",
        deadline=datetime.now() - timedelta(days=1),
    )
    assert term.is_overdue() is True


@pytest.mark.unit
def test_contract_term_is_overdue_future_deadline():
    """is_overdue returns False when deadline is in the future."""
    term = ContractTerm(
        description="test",
        type="obligation",
        party="A",
        deadline=datetime.now() + timedelta(days=30),
    )
    assert term.is_overdue() is False


@pytest.mark.unit
def test_contract_term_is_overdue_fulfilled():
    """is_overdue returns False when term is fulfilled even with past deadline."""
    term = ContractTerm(
        description="test",
        type="obligation",
        party="A",
        deadline=datetime.now() - timedelta(days=1),
        fulfilled=True,
    )
    assert term.is_overdue() is False


# ======================================================================
# Contract construction tests
# ======================================================================

@pytest.mark.unit
def test_contract_construction():
    """Contract is created in DRAFT status with UUID id."""
    contract = Contract("NDA", ["Alice", "Bob"])
    assert contract.title == "NDA"
    assert contract.parties == ["Alice", "Bob"]
    assert contract.status == ContractStatus.DRAFT
    assert contract.id is not None
    assert contract.terms == []
    assert contract.signatures == {}


@pytest.mark.unit
def test_contract_requires_two_parties():
    """Contract with fewer than 2 parties raises ContractError."""
    with pytest.raises(ContractError, match="at least 2 parties"):
        Contract("Deal", ["Alice"])


@pytest.mark.unit
def test_contract_rejects_duplicate_parties():
    """Contract with duplicate party names raises ContractError."""
    with pytest.raises(ContractError, match="Duplicate"):
        Contract("Deal", ["Alice", "Alice"])


@pytest.mark.unit
def test_contract_created_at_is_datetime():
    """Contract created_at is a datetime instance."""
    contract = Contract("Test", ["Alice", "Bob"])
    assert isinstance(contract.created_at, datetime)


# ======================================================================
# Contract add_term tests
# ======================================================================

@pytest.mark.unit
def test_contract_add_term():
    """add_term adds a term to a DRAFT contract."""
    contract = Contract("NDA", ["Alice", "Bob"])
    term = ContractTerm(
        description="No disclosure",
        type="prohibition",
        party="Alice",
    )
    contract.add_term(term)
    assert len(contract.terms) == 1
    assert contract.terms[0].description == "No disclosure"


@pytest.mark.unit
def test_contract_add_term_nonparty_raises():
    """add_term rejects terms for non-parties."""
    contract = Contract("Deal", ["Alice", "Bob"])
    term = ContractTerm(description="test", type="obligation", party="Charlie")
    with pytest.raises(ContractError, match="not a party"):
        contract.add_term(term)


@pytest.mark.unit
def test_contract_add_term_non_draft_raises():
    """add_term rejects terms when contract is not in DRAFT status."""
    contract = Contract("Deal", ["Alice", "Bob"])
    contract.sign("Alice")
    contract.sign("Bob")
    assert contract.status == ContractStatus.ACTIVE
    term = ContractTerm(description="late term", type="obligation", party="Alice")
    with pytest.raises(ContractError, match="DRAFT"):
        contract.add_term(term)


# ======================================================================
# Contract signing tests
# ======================================================================

@pytest.mark.unit
def test_contract_sign_valid_party():
    """Valid party can sign a DRAFT contract."""
    contract = Contract("Deal", ["Alice", "Bob"])
    result = contract.sign("Alice")
    assert result is True
    assert "Alice" in contract.signatures
    assert contract.status == ContractStatus.DRAFT


@pytest.mark.unit
def test_contract_auto_activates_on_all_signatures():
    """Contract auto-activates when all parties have signed."""
    contract = Contract("Deal", ["Alice", "Bob"])
    contract.sign("Alice")
    contract.sign("Bob")
    assert contract.status == ContractStatus.ACTIVE


@pytest.mark.unit
def test_contract_sign_rejects_non_party():
    """Signing by a non-party raises ContractError."""
    contract = Contract("Deal", ["Alice", "Bob"])
    with pytest.raises(ContractError, match="not a party"):
        contract.sign("Charlie")


@pytest.mark.unit
def test_contract_sign_rejects_duplicate():
    """Same party cannot sign twice."""
    contract = Contract("Deal", ["Alice", "Bob"])
    contract.sign("Alice")
    with pytest.raises(ContractError, match="already signed"):
        contract.sign("Alice")


@pytest.mark.unit
def test_contract_sign_rejects_non_draft():
    """Signing a non-DRAFT contract raises ContractError."""
    contract = Contract("Deal", ["Alice", "Bob"])
    contract.sign("Alice")
    contract.sign("Bob")
    assert contract.status == ContractStatus.ACTIVE
    with pytest.raises(ContractError):
        contract.sign("Alice")


@pytest.mark.unit
def test_contract_sign_with_custom_signature():
    """sign() accepts a custom signature string."""
    contract = Contract("Deal", ["Alice", "Bob"])
    contract.sign("Alice", signature="custom-sig-abc")
    assert contract.signatures["Alice"]["signature"] == "custom-sig-abc"


@pytest.mark.unit
def test_contract_sign_three_parties():
    """Contract with three parties activates only when all three sign."""
    contract = Contract("Three-Way", ["Alice", "Bob", "Charlie"])
    contract.sign("Alice")
    assert contract.status == ContractStatus.DRAFT
    contract.sign("Bob")
    assert contract.status == ContractStatus.DRAFT
    contract.sign("Charlie")
    assert contract.status == ContractStatus.ACTIVE


@pytest.mark.unit
def test_contract_sign_order_independent():
    """Parties can sign in any order."""
    contract = Contract("Deal", ["Alice", "Bob"])
    contract.sign("Bob")
    contract.sign("Alice")
    assert contract.status == ContractStatus.ACTIVE
    assert set(contract.signatures.keys()) == {"Alice", "Bob"}


@pytest.mark.unit
def test_contract_signature_has_timestamp():
    """Signature record includes signed_at datetime."""
    contract = Contract("Deal", ["Alice", "Bob"])
    contract.sign("Alice")
    assert "signed_at" in contract.signatures["Alice"]
    assert isinstance(contract.signatures["Alice"]["signed_at"], datetime)


# ======================================================================
# Contract status and lifecycle tests
# ======================================================================

@pytest.mark.unit
def test_contract_is_active():
    """is_active returns True only when contract is ACTIVE."""
    contract = Contract("Deal", ["Alice", "Bob"])
    assert contract.is_active() is False
    contract.sign("Alice")
    contract.sign("Bob")
    assert contract.is_active() is True


@pytest.mark.unit
def test_contract_get_status():
    """get_status returns the current status string."""
    contract = Contract("Deal", ["Alice", "Bob"])
    assert contract.get_status() == "draft"
    contract.sign("Alice")
    contract.sign("Bob")
    assert contract.get_status() == "active"


@pytest.mark.unit
def test_contract_expire():
    """expire() transitions ACTIVE contract to EXPIRED."""
    contract = Contract("Deal", ["Alice", "Bob"])
    contract.sign("Alice")
    contract.sign("Bob")
    contract.expire()
    assert contract.status == ContractStatus.EXPIRED
    assert contract.expired_at is not None


@pytest.mark.unit
def test_contract_expire_non_active_raises():
    """expire() raises ContractError on non-ACTIVE contract."""
    contract = Contract("Deal", ["Alice", "Bob"])
    with pytest.raises(ContractError, match="Only active"):
        contract.expire()


@pytest.mark.unit
def test_contract_repr():
    """Contract repr includes title and status."""
    contract = Contract("Test Contract", ["Alice", "Bob"])
    r = repr(contract)
    assert "Test Contract" in r
    assert "draft" in r


@pytest.mark.unit
def test_contract_repr_after_activation():
    """Contract repr reflects active status after full signing."""
    contract = Contract("Activated", ["Alice", "Bob"])
    contract.sign("Alice")
    contract.sign("Bob")
    r = repr(contract)
    assert "active" in r


# ======================================================================
# Contract compliance tests
# ======================================================================

@pytest.mark.unit
def test_contract_check_compliance_no_terms():
    """Compliance with no terms returns 100% rate."""
    contract = Contract("Empty", ["Alice", "Bob"])
    result = contract.check_compliance()
    assert result["total_terms"] == 0
    assert result["compliance_rate"] == 1.0
    assert result["issues"] == []


@pytest.mark.unit
def test_contract_check_compliance_all_fulfilled():
    """Compliance with all fulfilled terms returns 100% rate."""
    contract = Contract("Deal", ["Alice", "Bob"])
    term = ContractTerm(description="deliver", type="obligation", party="Alice")
    contract.add_term(term)
    term.fulfill()
    result = contract.check_compliance()
    assert result["fulfilled"] == 1
    assert result["compliance_rate"] == 1.0


@pytest.mark.unit
def test_contract_check_compliance_overdue():
    """Compliance detects overdue unfulfilled terms."""
    contract = Contract("Deal", ["Alice", "Bob"])
    term = ContractTerm(
        description="deliver goods",
        type="obligation",
        party="Alice",
        deadline=datetime.now() - timedelta(days=1),
    )
    contract.add_term(term)
    result = contract.check_compliance()
    assert result["overdue"] == 1
    assert result["compliance_rate"] == 0.0
    assert len(result["issues"]) == 1
    assert result["issues"][0]["severity"] == "overdue"


@pytest.mark.unit
def test_contract_check_compliance_pending():
    """Compliance reports pending terms with future deadlines."""
    contract = Contract("Deal", ["Alice", "Bob"])
    term = ContractTerm(
        description="deliver",
        type="obligation",
        party="Alice",
        deadline=datetime.now() + timedelta(days=30),
    )
    contract.add_term(term)
    result = contract.check_compliance()
    assert result["pending"] == 1
    assert result["overdue"] == 0
    assert result["compliance_rate"] == 0.0


@pytest.mark.unit
def test_contract_check_compliance_mixed():
    """Compliance correctly reports mixed fulfilled/overdue/pending."""
    contract = Contract("Deal", ["Alice", "Bob"])
    # Fulfilled term
    t1 = ContractTerm(description="a", type="obligation", party="Alice")
    t1.fulfill()
    # Overdue term
    t2 = ContractTerm(
        description="b", type="obligation", party="Bob",
        deadline=datetime.now() - timedelta(days=1),
    )
    # Pending term (no deadline)
    t3 = ContractTerm(description="c", type="permission", party="Alice")
    contract.add_term(t1)
    contract.add_term(t2)
    contract.add_term(t3)
    result = contract.check_compliance()
    assert result["total_terms"] == 3
    assert result["fulfilled"] == 1
    assert result["overdue"] == 1
    assert result["pending"] == 1


# ======================================================================
# PolicyRule tests
# ======================================================================

@pytest.mark.unit
def test_policy_rule_creation():
    """PolicyRule stores name, condition, action, priority."""
    rule = PolicyRule(
        name="max_spend",
        condition=lambda ctx: ctx.get("amount", 0) <= 1000,
        action="Reject over $1000",
        priority=10,
    )
    assert rule.name == "max_spend"
    assert rule.action == "Reject over $1000"
    assert rule.priority == 10


@pytest.mark.unit
def test_policy_rule_default_priority():
    """PolicyRule defaults to priority 0."""
    rule = PolicyRule(name="test", condition=lambda ctx: True, action="nothing")
    assert rule.priority == 0


@pytest.mark.unit
def test_policy_rule_evaluate_passes():
    """PolicyRule.evaluate returns True when condition passes."""
    rule = PolicyRule(
        name="positive",
        condition=lambda ctx: ctx.get("value", 0) > 0,
        action="Must be positive",
    )
    assert rule.evaluate({"value": 5}) is True


@pytest.mark.unit
def test_policy_rule_evaluate_fails():
    """PolicyRule.evaluate returns False when condition fails."""
    rule = PolicyRule(
        name="positive",
        condition=lambda ctx: ctx.get("value", 0) > 0,
        action="Must be positive",
    )
    assert rule.evaluate({"value": -1}) is False


@pytest.mark.unit
def test_policy_rule_evaluate_exception_returns_false():
    """PolicyRule.evaluate returns False when condition raises."""
    def bad_condition(ctx):
        raise RuntimeError("broken")

    rule = PolicyRule(name="bad", condition=bad_condition, action="fix")
    assert rule.evaluate({}) is False


@pytest.mark.unit
def test_policy_rule_repr():
    """PolicyRule repr includes name and priority."""
    rule = PolicyRule(name="test_rule", condition=lambda c: True, action="a", priority=5)
    r = repr(rule)
    assert "test_rule" in r
    assert "5" in r


# ======================================================================
# PolicyEngine tests
# ======================================================================

@pytest.mark.unit
def test_policy_engine_create_policy():
    """PolicyEngine.create_policy creates and returns a policy."""
    engine = PolicyEngine()
    result = engine.create_policy("budget", "Spending controls")
    assert result["name"] == "budget"
    assert "id" in result


@pytest.mark.unit
def test_policy_engine_duplicate_policy_raises():
    """Creating a duplicate policy raises PolicyError."""
    engine = PolicyEngine()
    engine.create_policy("budget")
    with pytest.raises(PolicyError, match="already exists"):
        engine.create_policy("budget")


@pytest.mark.unit
def test_policy_engine_add_rule():
    """add_rule adds a rule to an existing policy."""
    engine = PolicyEngine()
    engine.create_policy("budget")
    rule = PolicyRule(
        name="max_spend",
        condition=lambda ctx: ctx.get("amount", 0) <= 1000,
        action="Reject",
    )
    engine.add_rule("budget", rule)
    # Evaluate to verify rule was added
    result = engine.evaluate("budget", {"amount": 500})
    assert result["total_rules"] == 1


@pytest.mark.unit
def test_policy_engine_add_rule_nonexistent_raises():
    """add_rule to nonexistent policy raises PolicyError."""
    engine = PolicyEngine()
    rule = PolicyRule(name="r", condition=lambda c: True, action="a")
    with pytest.raises(PolicyError, match="does not exist"):
        engine.add_rule("nonexistent", rule)


@pytest.mark.unit
def test_policy_engine_evaluate_all_pass():
    """Evaluate returns passed=True when all rules pass."""
    engine = PolicyEngine()
    engine.create_policy("checks")
    engine.add_rule("checks", PolicyRule(
        name="positive",
        condition=lambda ctx: ctx.get("value", 0) > 0,
        action="Must be positive",
    ))
    engine.add_rule("checks", PolicyRule(
        name="small",
        condition=lambda ctx: ctx.get("value", 0) < 100,
        action="Must be under 100",
    ))
    result = engine.evaluate("checks", {"value": 50})
    assert result["passed"] is True
    assert result["violations"] == 0
    assert result["total_rules"] == 2


@pytest.mark.unit
def test_policy_engine_evaluate_single_violation():
    """Evaluate detects a single violation."""
    engine = PolicyEngine()
    engine.create_policy("budget")
    engine.add_rule("budget", PolicyRule(
        name="max",
        condition=lambda ctx: ctx.get("amount", 0) <= 1000,
        action="Reject over 1000",
    ))
    result = engine.evaluate("budget", {"amount": 5000})
    assert result["passed"] is False
    assert result["violations"] == 1


@pytest.mark.unit
def test_policy_engine_evaluate_multiple_violations():
    """Evaluate detects multiple violations."""
    engine = PolicyEngine()
    engine.create_policy("checks")
    engine.add_rule("checks", PolicyRule(
        name="check_a",
        condition=lambda ctx: ctx.get("a", False),
        action="A must be true",
    ))
    engine.add_rule("checks", PolicyRule(
        name="check_b",
        condition=lambda ctx: ctx.get("b", False),
        action="B must be true",
    ))
    result = engine.evaluate("checks", {"a": False, "b": False})
    assert result["violations"] == 2


@pytest.mark.unit
def test_policy_engine_get_violations():
    """get_violations returns only failed rules."""
    engine = PolicyEngine()
    engine.create_policy("mixed")
    engine.add_rule("mixed", PolicyRule(
        name="passes",
        condition=lambda ctx: True,
        action="Should pass",
    ))
    engine.add_rule("mixed", PolicyRule(
        name="fails",
        condition=lambda ctx: False,
        action="Should fail",
    ))
    violations = engine.get_violations("mixed", {})
    assert len(violations) == 1
    assert violations[0]["rule"] == "fails"
    assert violations[0]["action"] == "Should fail"


@pytest.mark.unit
def test_policy_engine_enforce():
    """enforce returns result with actions and enforced flag."""
    engine = PolicyEngine()
    engine.create_policy("budget")
    engine.add_rule("budget", PolicyRule(
        name="max",
        condition=lambda ctx: ctx.get("amount", 0) <= 1000,
        action="Reject transaction",
        priority=10,
    ))
    result = engine.enforce("budget", {"amount": 5000})
    assert result["enforced"] is True
    assert "Reject transaction" in result["actions"]


@pytest.mark.unit
def test_policy_engine_enforce_no_violations():
    """enforce with no violations has enforced=False."""
    engine = PolicyEngine()
    engine.create_policy("budget")
    engine.add_rule("budget", PolicyRule(
        name="max",
        condition=lambda ctx: ctx.get("amount", 0) <= 1000,
        action="Reject",
    ))
    result = engine.enforce("budget", {"amount": 500})
    assert result["enforced"] is False
    assert result["actions"] == []


@pytest.mark.unit
def test_policy_engine_list_policies():
    """list_policies returns names of all registered policies."""
    engine = PolicyEngine()
    engine.create_policy("alpha")
    engine.create_policy("beta")
    names = engine.list_policies()
    assert set(names) == {"alpha", "beta"}


@pytest.mark.unit
def test_policy_engine_list_policies_empty():
    """list_policies returns empty list when no policies exist."""
    engine = PolicyEngine()
    assert engine.list_policies() == []


@pytest.mark.unit
def test_policy_engine_evaluate_nonexistent_raises():
    """Evaluating a nonexistent policy raises PolicyError."""
    engine = PolicyEngine()
    with pytest.raises(PolicyError, match="does not exist"):
        engine.evaluate("nonexistent", {})


@pytest.mark.unit
def test_policy_engine_rules_sorted_by_priority():
    """Rules are evaluated in descending priority order."""
    engine = PolicyEngine()
    engine.create_policy("ordered")
    engine.add_rule("ordered", PolicyRule(
        name="low",
        condition=lambda ctx: True,
        action="low priority",
        priority=1,
    ))
    engine.add_rule("ordered", PolicyRule(
        name="high",
        condition=lambda ctx: True,
        action="high priority",
        priority=10,
    ))
    result = engine.evaluate("ordered", {})
    # High priority should be first in details
    assert result["details"][0]["rule"] == "high"
    assert result["details"][1]["rule"] == "low"
