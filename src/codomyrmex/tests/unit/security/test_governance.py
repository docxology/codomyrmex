"""Tests for security/governance/policy.py, contracts.py, dispute_resolution.py."""

from datetime import datetime, timedelta

import pytest

from codomyrmex.security.governance.contracts import (
    Contract,
    ContractError,
    ContractStatus,
    ContractTerm,
)
from codomyrmex.security.governance.dispute_resolution import (
    Dispute,
    DisputeError,
    DisputeResolver,
    DisputeStatus,
)
from codomyrmex.security.governance.policy import PolicyEngine, PolicyError, PolicyRule

# ===== PolicyRule Tests =====


class TestPolicyRule:
    """Tests for the PolicyRule class."""

    def test_create_policy_rule(self):
        """PolicyRule stores name, action, priority."""
        rule = PolicyRule(
            name="max-cost",
            condition=lambda ctx: ctx.get("cost", 0) < 100,
            action="deny-excessive-cost",
            priority=10,
        )
        assert rule.name == "max-cost"
        assert rule.action == "deny-excessive-cost"
        assert rule.priority == 10

    def test_evaluate_passes_when_condition_true(self):
        """evaluate() returns True when condition is satisfied."""
        rule = PolicyRule(
            name="age-check",
            condition=lambda ctx: ctx.get("age", 0) >= 18,
            action="deny-minor",
        )
        assert rule.evaluate({"age": 25}) is True

    def test_evaluate_fails_when_condition_false(self):
        """evaluate() returns False when condition is not satisfied."""
        rule = PolicyRule(
            name="age-check",
            condition=lambda ctx: ctx.get("age", 0) >= 18,
            action="deny-minor",
        )
        assert rule.evaluate({"age": 15}) is False

    def test_evaluate_returns_false_on_exception(self):
        """evaluate() returns False (not raise) when condition throws."""
        rule = PolicyRule(
            name="bad-rule",
            condition=lambda ctx: 1 / 0,  # ZeroDivisionError
            action="error-action",
        )
        assert rule.evaluate({}) is False

    def test_repr(self):
        """repr contains rule name and priority."""
        rule = PolicyRule("my-rule", lambda ctx: True, "action", priority=5)
        r = repr(rule)
        assert "my-rule" in r
        assert "5" in r

    def test_default_priority_zero(self):
        """Default priority is 0."""
        rule = PolicyRule("r", lambda ctx: True, "act")
        assert rule.priority == 0


class TestPolicyEngine:
    """Tests for the PolicyEngine class."""

    def test_create_policy(self):
        """create_policy() returns dict with name, id, description."""
        engine = PolicyEngine()
        result = engine.create_policy("cost-control", "Limit agent costs")
        assert result["name"] == "cost-control"
        assert "id" in result
        assert result["description"] == "Limit agent costs"

    def test_create_policy_duplicate_raises(self):
        """Creating policy with duplicate name raises PolicyError."""
        engine = PolicyEngine()
        engine.create_policy("p1")
        with pytest.raises(PolicyError, match="already exists"):
            engine.create_policy("p1")

    def test_add_rule_to_policy(self):
        """add_rule() attaches rule to named policy."""
        engine = PolicyEngine()
        engine.create_policy("security")
        rule = PolicyRule("tls-required", lambda ctx: ctx.get("tls", False), "block-no-tls")
        engine.add_rule("security", rule)
        # Verify by evaluating
        result = engine.evaluate("security", {"tls": True})
        assert result["total_rules"] == 1

    def test_add_rule_nonexistent_policy_raises(self):
        """add_rule() to nonexistent policy raises PolicyError."""
        engine = PolicyEngine()
        rule = PolicyRule("r", lambda ctx: True, "a")
        with pytest.raises(PolicyError, match="does not exist"):
            engine.add_rule("ghost", rule)

    def test_evaluate_all_pass(self):
        """evaluate() returns passed=True when all rules pass."""
        engine = PolicyEngine()
        engine.create_policy("p")
        engine.add_rule("p", PolicyRule("r1", lambda ctx: True, "a"))
        engine.add_rule("p", PolicyRule("r2", lambda ctx: True, "b"))
        result = engine.evaluate("p", {})
        assert result["passed"] is True
        assert result["violations"] == 0

    def test_evaluate_one_violation(self):
        """evaluate() reports violation when one rule fails."""
        engine = PolicyEngine()
        engine.create_policy("p")
        engine.add_rule("p", PolicyRule("r1", lambda ctx: True, "a"))
        engine.add_rule("p", PolicyRule("r2", lambda ctx: False, "deny"))
        result = engine.evaluate("p", {})
        assert result["passed"] is False
        assert result["violations"] == 1

    def test_evaluate_details_list(self):
        """evaluate() returns details for each rule."""
        engine = PolicyEngine()
        engine.create_policy("p")
        engine.add_rule("p", PolicyRule("pass-rule", lambda ctx: True, "ok"))
        engine.add_rule("p", PolicyRule("fail-rule", lambda ctx: False, "deny"))
        result = engine.evaluate("p", {})
        names = {d["rule"] for d in result["details"]}
        assert "pass-rule" in names
        assert "fail-rule" in names

    def test_evaluate_nonexistent_policy_raises(self):
        """evaluate() on missing policy raises PolicyError."""
        engine = PolicyEngine()
        with pytest.raises(PolicyError):
            engine.evaluate("ghost", {})

    def test_evaluate_priority_order(self):
        """Rules sorted by descending priority."""
        engine = PolicyEngine()
        engine.create_policy("p")
        order = []
        engine.add_rule("p", PolicyRule("low", lambda ctx: (order.append("low") or True), "a", priority=1))
        engine.add_rule("p", PolicyRule("high", lambda ctx: (order.append("high") or True), "b", priority=10))
        engine.evaluate("p", {})
        assert order[0] == "high"  # High priority evaluated first

    def test_get_violations_returns_failed_rules(self):
        """get_violations() returns only rules that failed."""
        engine = PolicyEngine()
        engine.create_policy("p")
        engine.add_rule("p", PolicyRule("r1", lambda ctx: True, "ok"))
        engine.add_rule("p", PolicyRule("r2", lambda ctx: False, "deny-x"))
        violations = engine.get_violations("p", {})
        assert len(violations) == 1
        assert violations[0]["rule"] == "r2"
        assert violations[0]["action"] == "deny-x"

    def test_get_violations_none(self):
        """get_violations() returns empty list when all rules pass."""
        engine = PolicyEngine()
        engine.create_policy("p")
        engine.add_rule("p", PolicyRule("r1", lambda ctx: True, "ok"))
        violations = engine.get_violations("p", {})
        assert violations == []

    def test_enforce_returns_actions(self):
        """enforce() returns list of actions for violated rules."""
        engine = PolicyEngine()
        engine.create_policy("p")
        engine.add_rule("p", PolicyRule("fail", lambda ctx: False, "block-traffic"))
        result = engine.enforce("p", {})
        assert result["enforced"] is True
        assert "block-traffic" in result["actions"]
        assert result["violations"] == 1

    def test_enforce_no_violations(self):
        """enforce() returns enforced=False when no violations."""
        engine = PolicyEngine()
        engine.create_policy("p")
        engine.add_rule("p", PolicyRule("pass", lambda ctx: True, "allow"))
        result = engine.enforce("p", {})
        assert result["enforced"] is False
        assert result["violations"] == 0

    def test_list_policies(self):
        """list_policies() returns names of all policies."""
        engine = PolicyEngine()
        engine.create_policy("alpha")
        engine.create_policy("beta")
        names = engine.list_policies()
        assert "alpha" in names
        assert "beta" in names

    def test_empty_policy_evaluates_passed(self):
        """Policy with no rules evaluates as passed."""
        engine = PolicyEngine()
        engine.create_policy("empty")
        result = engine.evaluate("empty", {})
        assert result["passed"] is True
        assert result["total_rules"] == 0

    def test_add_policy_uses_default_bucket(self):
        """add_policy() adds rule to _default policy."""
        engine = PolicyEngine()
        rule = PolicyRule("r", lambda ctx: True, "a")
        engine.add_policy(rule)
        assert "_default" in engine.list_policies()


# ===== Contract Tests =====


class TestContractTerm:
    """Tests for the ContractTerm dataclass."""

    def test_create_obligation(self):
        """ContractTerm with type='obligation' is valid."""
        term = ContractTerm(description="Deliver on time", type="obligation", party="alice")
        assert term.type == "obligation"
        assert term.fulfilled is False

    def test_create_prohibition(self):
        """ContractTerm with type='prohibition' is valid."""
        term = ContractTerm(description="Do not share data", type="prohibition", party="bob")
        assert term.type == "prohibition"

    def test_create_permission(self):
        """ContractTerm with type='permission' is valid."""
        term = ContractTerm(description="May audit logs", type="permission", party="auditor")
        assert term.type == "permission"

    def test_invalid_type_raises(self):
        """Invalid term type raises ContractError."""
        with pytest.raises(ContractError, match="Invalid term type"):
            ContractTerm(description="bad", type="invalid", party="x")

    def test_fulfill_marks_fulfilled(self):
        """fulfill() sets fulfilled=True."""
        term = ContractTerm(description="Do X", type="obligation", party="alice")
        term.fulfill()
        assert term.fulfilled is True

    def test_is_overdue_future_deadline(self):
        """is_overdue() returns False for future deadline."""
        future = datetime.now() + timedelta(days=30)
        term = ContractTerm(description="Do Y", type="obligation", party="bob", deadline=future)
        assert term.is_overdue() is False

    def test_is_overdue_past_deadline(self):
        """is_overdue() returns True for past deadline when unfulfilled."""
        past = datetime.now() - timedelta(days=1)
        term = ContractTerm(description="Do Z", type="obligation", party="carol", deadline=past)
        assert term.is_overdue() is True

    def test_is_overdue_fulfilled_despite_past_deadline(self):
        """is_overdue() returns False when fulfilled even past deadline."""
        past = datetime.now() - timedelta(days=1)
        term = ContractTerm(description="Done", type="obligation", party="alice", deadline=past)
        term.fulfill()
        assert term.is_overdue() is False

    def test_is_overdue_no_deadline(self):
        """is_overdue() returns False when no deadline."""
        term = ContractTerm(description="No deadline", type="obligation", party="x")
        assert term.is_overdue() is False


class TestContract:
    """Tests for the Contract class."""

    def test_create_contract(self):
        """Contract created with title and two parties."""
        c = Contract("Service Agreement", ["alice", "bob"])
        assert c.title == "Service Agreement"
        assert c.status == ContractStatus.DRAFT
        assert len(c.terms) == 0

    def test_create_requires_two_parties(self):
        """Contract with fewer than 2 parties raises ContractError."""
        with pytest.raises(ContractError, match="at least 2"):
            Contract("Solo", ["alone"])

    def test_create_no_duplicate_parties(self):
        """Contract with duplicate parties raises ContractError."""
        with pytest.raises(ContractError, match="Duplicate"):
            Contract("Bad", ["alice", "alice"])

    def test_add_term(self):
        """add_term() appends term to DRAFT contract."""
        c = Contract("SLA", ["alice", "bob"])
        term = ContractTerm("Uptime 99.9%", "obligation", "alice")
        c.add_term(term)
        assert len(c.terms) == 1

    def test_add_term_wrong_party_raises(self):
        """add_term() raises ContractError for unknown party."""
        c = Contract("SLA", ["alice", "bob"])
        term = ContractTerm("Some obligation", "obligation", "charlie")
        with pytest.raises(ContractError, match="not a party"):
            c.add_term(term)

    def test_add_term_to_active_contract_raises(self):
        """add_term() raises ContractError when contract is not DRAFT."""
        c = Contract("SLA", ["alice", "bob"])
        c.sign("alice")
        c.sign("bob")  # Now ACTIVE
        term = ContractTerm("Late addition", "obligation", "alice")
        with pytest.raises(ContractError, match="DRAFT"):
            c.add_term(term)

    def test_sign_activates_when_all_signed(self):
        """Signing by all parties activates the contract."""
        c = Contract("Agreement", ["alice", "bob"])
        assert c.status == ContractStatus.DRAFT
        c.sign("alice")
        assert c.status == ContractStatus.DRAFT
        c.sign("bob")
        assert c.status == ContractStatus.ACTIVE

    def test_sign_wrong_party_raises(self):
        """Signing with unknown party raises ContractError."""
        c = Contract("Agreement", ["alice", "bob"])
        with pytest.raises(ContractError, match="not a party"):
            c.sign("charlie")

    def test_sign_twice_raises(self):
        """Signing the same party twice raises ContractError."""
        c = Contract("Agreement", ["alice", "bob"])
        c.sign("alice")
        with pytest.raises(ContractError, match="already signed"):
            c.sign("alice")

    def test_sign_non_draft_raises(self):
        """Signing a non-DRAFT contract raises ContractError."""
        c = Contract("Agreement", ["alice", "bob"])
        c.sign("alice")
        c.sign("bob")  # ACTIVE
        with pytest.raises(ContractError, match="DRAFT"):
            c.sign("alice")

    def test_expire_active_contract(self):
        """expire() transitions ACTIVE to EXPIRED."""
        c = Contract("SLA", ["alice", "bob"])
        c.sign("alice")
        c.sign("bob")
        c.expire()
        assert c.status == ContractStatus.EXPIRED
        assert c.expired_at is not None

    def test_expire_non_active_raises(self):
        """expire() on DRAFT contract raises ContractError."""
        c = Contract("SLA", ["alice", "bob"])
        with pytest.raises(ContractError, match="active"):
            c.expire()

    def test_terminate_any_status(self):
        """terminate() works on DRAFT and ACTIVE contracts."""
        c = Contract("SLA", ["alice", "bob"])
        c.terminate()
        assert c.status == ContractStatus.TERMINATED

    def test_terminate_already_terminated_raises(self):
        """terminate() on already-terminated contract raises ContractError."""
        c = Contract("SLA", ["alice", "bob"])
        c.terminate()
        with pytest.raises(ContractError, match="already terminated"):
            c.terminate()

    def test_dispute_active_contract(self):
        """dispute() transitions ACTIVE to DISPUTED."""
        c = Contract("SLA", ["alice", "bob"])
        c.sign("alice")
        c.sign("bob")
        c.dispute()
        assert c.status == ContractStatus.DISPUTED

    def test_dispute_non_active_raises(self):
        """dispute() on DRAFT contract raises ContractError."""
        c = Contract("SLA", ["alice", "bob"])
        with pytest.raises(ContractError, match="active"):
            c.dispute()

    def test_is_active_true(self):
        """is_active() returns True for ACTIVE contracts."""
        c = Contract("SLA", ["alice", "bob"])
        c.sign("alice")
        c.sign("bob")
        assert c.is_active() is True

    def test_is_active_false_for_draft(self):
        """is_active() returns False for DRAFT contracts."""
        c = Contract("SLA", ["alice", "bob"])
        assert c.is_active() is False

    def test_get_status(self):
        """get_status() returns lowercase string."""
        c = Contract("SLA", ["alice", "bob"])
        assert c.get_status() == "draft"

    def test_check_compliance_empty(self):
        """check_compliance() on contract with no terms returns 100% rate."""
        c = Contract("SLA", ["alice", "bob"])
        result = c.check_compliance()
        assert result["total_terms"] == 0
        assert result["compliance_rate"] == pytest.approx(1.0)

    def test_check_compliance_all_fulfilled(self):
        """check_compliance() with all fulfilled terms returns 100%."""
        c = Contract("SLA", ["alice", "bob"])
        term = ContractTerm("Deliver", "obligation", "alice")
        term.fulfill()
        c.add_term(term)
        result = c.check_compliance()
        assert result["fulfilled"] == 1
        assert result["compliance_rate"] == pytest.approx(1.0)

    def test_check_compliance_overdue(self):
        """check_compliance() flags overdue terms."""
        c = Contract("SLA", ["alice", "bob"])
        past = datetime.now() - timedelta(days=1)
        term = ContractTerm("Overdue task", "obligation", "alice", deadline=past)
        c.add_term(term)
        result = c.check_compliance()
        assert result["overdue"] == 1
        assert len(result["issues"]) == 1

    def test_repr(self):
        """repr includes title, status, parties."""
        c = Contract("My Contract", ["alice", "bob"])
        r = repr(c)
        assert "My Contract" in r
        assert "draft" in r


class TestDisputeResolution:
    """Tests for governance/dispute_resolution.py DisputeResolver."""

    def _make_dispute(self, dispute_id: str = "D001", contract_id: str = "C001") -> Dispute:
        return Dispute(
            id=dispute_id,
            contract_id=contract_id,
            filer_id="alice",
            description="breach of terms",
        )

    def test_create_resolver(self):
        """DisputeResolver can be instantiated."""
        resolver = DisputeResolver()
        assert resolver is not None

    def test_dispute_defaults(self):
        """Dispute dataclass sets status OPEN by default."""
        d = self._make_dispute()
        assert d.status == DisputeStatus.OPEN
        assert d.resolution is None

    def test_file_dispute(self):
        """file_dispute() records a dispute without error."""
        resolver = DisputeResolver()
        dispute = self._make_dispute()
        resolver.file_dispute(dispute)
        assert resolver.get_dispute("D001") is dispute

    def test_file_duplicate_raises(self):
        """file_dispute() with duplicate ID raises DisputeError."""
        resolver = DisputeResolver()
        d1 = self._make_dispute("D001")
        d2 = self._make_dispute("D001")  # Same ID
        resolver.file_dispute(d1)
        with pytest.raises(DisputeError, match="already exists"):
            resolver.file_dispute(d2)

    def test_resolve_dispute(self):
        """resolve_dispute() sets resolution text and RESOLVED status."""
        resolver = DisputeResolver()
        dispute = self._make_dispute()
        resolver.file_dispute(dispute)
        resolver.resolve_dispute("D001", "Parties agreed to new terms.")
        resolved = resolver.get_dispute("D001")
        assert resolved.status == DisputeStatus.RESOLVED
        assert resolved.resolution == "Parties agreed to new terms."

    def test_resolve_nonexistent_raises(self):
        """resolve_dispute() for unknown ID raises DisputeError."""
        resolver = DisputeResolver()
        with pytest.raises(DisputeError, match="not found"):
            resolver.resolve_dispute("ghost", "resolution")

    def test_get_dispute_returns_none_for_unknown(self):
        """get_dispute() returns None when dispute does not exist."""
        resolver = DisputeResolver()
        assert resolver.get_dispute("unknown") is None

    def test_dispute_status_enum(self):
        """DisputeStatus has OPEN, UNDER_REVIEW, RESOLVED, CLOSED."""
        statuses = {s.name for s in DisputeStatus}
        assert "OPEN" in statuses
        assert "UNDER_REVIEW" in statuses
        assert "RESOLVED" in statuses
        assert "CLOSED" in statuses
