"""Unit tests for colony_kernel/models.py.

Zero-mock policy: no MagicMock, no unittest.mock, no pytest-mock.
All tests use real model instantiations and real function calls.
"""

from __future__ import annotations

import pytest

from codomyrmex.colony_kernel.models import (
    ActionProposal,
    AgentRole,
    AgentTrustProfile,
    ColonySignal,
    ConsequenceRecord,
    DecayRate,
    ResourceCost,
    SignalSource,
    SignalType,
    compute_trust_delta,
    make_trace_key,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

CONFIG_TRUST_SANDBOX_SCORE: float = 0.1  # matches models.py default


def _minimal_proposal() -> ActionProposal:
    """Return the smallest valid ActionProposal for use in ConsequenceRecord tests."""
    return ActionProposal(
        agent_id="test-agent",
        agent_type="repair_ant",
        action_type="patch_file",
        target="codomyrmex.colony_kernel.models",
        rationale="Fix type error in models",
        expected_outcome="All tests pass",
    )


def _consequence(
    *,
    tests_passed: bool,
    repair_needed: bool = False,
    human_feedback: float = 0.0,
) -> ConsequenceRecord:
    """Build a ConsequenceRecord with the given outcome flags."""
    return ConsequenceRecord(
        proposal=_minimal_proposal(),
        action_taken="Applied patch",
        actual_outcome="Tests passed" if tests_passed else "Tests failed",
        tests_passed=tests_passed,
        repair_needed=repair_needed,
        human_feedback=human_feedback,
    )


# ---------------------------------------------------------------------------
# make_trace_key
# ---------------------------------------------------------------------------


class TestMakeTraceKey:
    def test_returns_string(self) -> None:
        key = make_trace_key("codomyrmex.colony_kernel", SignalType.SUCCESS)
        assert isinstance(key, str)

    def test_contains_location(self) -> None:
        location = "codomyrmex.git_operations.core"
        key = make_trace_key(location, SignalType.FAILURE)
        assert location in key

    def test_contains_signal_type_value(self) -> None:
        key = make_trace_key("some.module", SignalType.RISK)
        assert SignalType.RISK.value in key

    def test_deterministic_same_inputs_same_key(self) -> None:
        location = "codomyrmex.colony_kernel"
        signal = SignalType.SUCCESS
        assert make_trace_key(location, signal) == make_trace_key(location, signal)

    def test_format_is_location_colon_signal_value(self) -> None:
        location = "codomyrmex.events"
        signal = SignalType.DEPENDENCY
        expected = f"{location}:{signal.value}"
        assert make_trace_key(location, signal) == expected

    def test_empty_location_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="location"):
            make_trace_key("", SignalType.SUCCESS)

    def test_different_signal_types_produce_different_keys(self) -> None:
        location = "codomyrmex.module"
        key_fail = make_trace_key(location, SignalType.FAILURE)
        key_success = make_trace_key(location, SignalType.SUCCESS)
        assert key_fail != key_success


# ---------------------------------------------------------------------------
# compute_trust_delta
# ---------------------------------------------------------------------------


class TestComputeTrustDelta:
    def test_pass_outcome_returns_positive_delta(self) -> None:
        record = _consequence(tests_passed=True)
        delta = compute_trust_delta(record)
        assert delta == pytest.approx(+0.04)

    def test_fail_outcome_returns_negative_delta(self) -> None:
        record = _consequence(tests_passed=False)
        delta = compute_trust_delta(record)
        assert delta == pytest.approx(-0.08)

    def test_repair_outcome_adds_repair_penalty(self) -> None:
        # tests_passed=True but repair_needed=True → 0.04 + (-0.05) = -0.01
        record = _consequence(tests_passed=True, repair_needed=True)
        delta = compute_trust_delta(record)
        assert delta == pytest.approx(-0.01)

    def test_repair_with_fail_outcome(self) -> None:
        # tests_passed=False and repair_needed=True → -0.08 + (-0.05) = -0.13
        record = _consequence(tests_passed=False, repair_needed=True)
        delta = compute_trust_delta(record)
        assert delta == pytest.approx(-0.13)

    def test_human_feedback_positive_adds_to_delta(self) -> None:
        # tests_passed=True, human_feedback=+1.0 → 0.04 + 0.03 = 0.07
        record = _consequence(tests_passed=True, human_feedback=1.0)
        delta = compute_trust_delta(record)
        assert delta == pytest.approx(0.07)

    def test_human_feedback_negative_subtracts_from_delta(self) -> None:
        # tests_passed=True, human_feedback=-1.0 → 0.04 - 0.03 = 0.01
        record = _consequence(tests_passed=True, human_feedback=-1.0)
        delta = compute_trust_delta(record)
        assert delta == pytest.approx(0.01)

    def test_zero_human_feedback_has_no_effect(self) -> None:
        record_no_fb = _consequence(tests_passed=True, human_feedback=0.0)
        record_explicit = _consequence(tests_passed=True)
        assert compute_trust_delta(record_no_fb) == pytest.approx(
            compute_trust_delta(record_explicit)
        )


# ---------------------------------------------------------------------------
# ResourceCost.__add__
# ---------------------------------------------------------------------------


class TestResourceCostAdd:
    def test_llm_calls_summed(self) -> None:
        a = ResourceCost(llm_calls=3)
        b = ResourceCost(llm_calls=7)
        result = a + b
        assert result.llm_calls == 10

    def test_runtime_seconds_summed(self) -> None:
        a = ResourceCost(runtime_seconds=1.5)
        b = ResourceCost(runtime_seconds=2.5)
        result = a + b
        assert result.runtime_seconds == pytest.approx(4.0)

    def test_human_attention_minutes_summed(self) -> None:
        a = ResourceCost(human_attention_minutes=5.0)
        b = ResourceCost(human_attention_minutes=3.0)
        result = a + b
        assert result.human_attention_minutes == pytest.approx(8.0)

    def test_doc_debt_summed(self) -> None:
        a = ResourceCost(doc_debt=2.0)
        b = ResourceCost(doc_debt=3.5)
        result = a + b
        assert result.doc_debt == pytest.approx(5.5)

    def test_risk_level_summed_normally_when_under_one(self) -> None:
        a = ResourceCost(risk_level=0.2)
        b = ResourceCost(risk_level=0.3)
        result = a + b
        assert result.risk_level == pytest.approx(0.5)

    def test_risk_level_clamped_at_one_when_sum_exceeds_one(self) -> None:
        a = ResourceCost(risk_level=0.7)
        b = ResourceCost(risk_level=0.8)
        result = a + b
        assert result.risk_level == pytest.approx(1.0)

    def test_merge_risk_clamped_at_one(self) -> None:
        a = ResourceCost(merge_risk=0.6)
        b = ResourceCost(merge_risk=0.6)
        result = a + b
        assert result.merge_risk == pytest.approx(1.0)

    def test_security_exposure_clamped_at_one(self) -> None:
        a = ResourceCost(security_exposure=0.8)
        b = ResourceCost(security_exposure=0.5)
        result = a + b
        assert result.security_exposure == pytest.approx(1.0)

    def test_all_fields_summed_correctly(self) -> None:
        a = ResourceCost(
            llm_calls=2,
            runtime_seconds=10.0,
            risk_level=0.1,
            human_attention_minutes=3.0,
            merge_risk=0.2,
            doc_debt=1.0,
            security_exposure=0.1,
        )
        b = ResourceCost(
            llm_calls=3,
            runtime_seconds=5.0,
            risk_level=0.2,
            human_attention_minutes=2.0,
            merge_risk=0.1,
            doc_debt=0.5,
            security_exposure=0.2,
        )
        result = a + b
        assert result.llm_calls == 5
        assert result.runtime_seconds == pytest.approx(15.0)
        assert result.risk_level == pytest.approx(0.3)
        assert result.human_attention_minutes == pytest.approx(5.0)
        assert result.merge_risk == pytest.approx(0.3)
        assert result.doc_debt == pytest.approx(1.5)
        assert result.security_exposure == pytest.approx(0.3)


# ---------------------------------------------------------------------------
# ResourceCost risk_level clamping behaviour
# ---------------------------------------------------------------------------


class TestResourceCostRiskLevelClamping:
    def test_risk_level_above_one_raises_value_error(self) -> None:
        """Assigning risk_level > 1.0 at construction raises ValueError — no silent clamping."""
        with pytest.raises(ValueError, match="risk_level"):
            ResourceCost(risk_level=1.5)

    def test_risk_level_at_exactly_one_is_valid(self) -> None:
        cost = ResourceCost(risk_level=1.0)
        assert cost.risk_level == 1.0

    def test_risk_level_at_zero_is_valid(self) -> None:
        cost = ResourceCost(risk_level=0.0)
        assert cost.risk_level == 0.0

    def test_risk_level_negative_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="risk_level"):
            ResourceCost(risk_level=-0.1)

    def test_add_clamps_but_direct_construction_does_not_allow_over_one(self) -> None:
        """__add__ internally uses min(1.0, ...) so result is valid; direct construction is not."""
        a = ResourceCost(risk_level=0.7)
        b = ResourceCost(risk_level=0.8)
        summed = a + b
        # Result from __add__ is clamped to 1.0, so it's a valid ResourceCost
        assert summed.risk_level == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# ColonySignal construction
# ---------------------------------------------------------------------------


class TestColonySignalConstruction:
    def test_minimal_construction_no_error(self) -> None:
        signal = ColonySignal(
            location="codomyrmex.colony_kernel",
            signal_type=SignalType.SUCCESS,
            strength=0.5,
        )
        assert signal.location == "codomyrmex.colony_kernel"
        assert signal.signal_type == SignalType.SUCCESS
        assert signal.strength == pytest.approx(0.5)

    def test_defaults_are_applied(self) -> None:
        signal = ColonySignal(
            location="some.module",
            signal_type=SignalType.FAILURE,
            strength=1.0,
        )
        assert signal.decay_rate == DecayRate.NORMAL
        assert signal.source == SignalSource.AGENT
        assert signal.evidence == {}

    def test_all_fields_explicit(self) -> None:
        signal = ColonySignal(
            location="codomyrmex.git_operations",
            signal_type=SignalType.RISK,
            strength=0.8,
            decay_rate=DecayRate.FAST,
            source=SignalSource.HUMAN,
            evidence={"pr": "42"},
        )
        assert signal.decay_rate == DecayRate.FAST
        assert signal.source == SignalSource.HUMAN
        assert signal.evidence == {"pr": "42"}

    def test_empty_location_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="location"):
            ColonySignal(location="", signal_type=SignalType.SUCCESS, strength=0.5)

    def test_negative_strength_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="strength"):
            ColonySignal(
                location="codomyrmex.module",
                signal_type=SignalType.SUCCESS,
                strength=-0.1,
            )


# ---------------------------------------------------------------------------
# ActionProposal construction
# ---------------------------------------------------------------------------


class TestActionProposalConstruction:
    def test_minimal_construction_no_error(self) -> None:
        proposal = _minimal_proposal()
        assert proposal.agent_id == "test-agent"
        assert proposal.agent_type == "repair_ant"
        assert proposal.action_type == "patch_file"
        assert proposal.target == "codomyrmex.colony_kernel.models"
        assert proposal.rationale == "Fix type error in models"
        assert proposal.expected_outcome == "All tests pass"

    def test_auto_assigned_proposal_id(self) -> None:
        proposal = _minimal_proposal()
        assert proposal.proposal_id
        assert len(proposal.proposal_id) > 0

    def test_proposal_id_is_unique_per_instance(self) -> None:
        p1 = _minimal_proposal()
        p2 = _minimal_proposal()
        assert p1.proposal_id != p2.proposal_id

    def test_budget_estimate_defaults_to_zero_cost(self) -> None:
        proposal = _minimal_proposal()
        assert proposal.budget_estimate.llm_calls == 0
        assert proposal.budget_estimate.runtime_seconds == pytest.approx(0.0)

    def test_rollback_plan_defaults_to_empty_string(self) -> None:
        proposal = _minimal_proposal()
        assert proposal.rollback_plan == ""

    def test_evidence_defaults_to_empty_dict(self) -> None:
        proposal = _minimal_proposal()
        assert proposal.evidence == {}

    def test_empty_agent_id_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="agent_id"):
            ActionProposal(
                agent_id="",
                agent_type="repair_ant",
                action_type="patch_file",
                target="codomyrmex.module",
                rationale="reason",
                expected_outcome="outcome",
            )


# ---------------------------------------------------------------------------
# AgentTrustProfile default score
# ---------------------------------------------------------------------------


class TestAgentTrustProfileDefaultScore:
    def test_default_trust_score_matches_sandbox_constant(self) -> None:
        profile = AgentTrustProfile(agent_id="agent-001")
        assert profile.trust_score == pytest.approx(CONFIG_TRUST_SANDBOX_SCORE)

    def test_default_trust_score_is_point_one(self) -> None:
        profile = AgentTrustProfile(agent_id="agent-002")
        assert profile.trust_score == pytest.approx(0.1)

    def test_default_role_is_sandbox(self) -> None:
        profile = AgentTrustProfile(agent_id="agent-003")
        assert profile.role == AgentRole.SANDBOX

    def test_default_total_proposals_is_zero(self) -> None:
        profile = AgentTrustProfile(agent_id="agent-004")
        assert profile.total_proposals == 0

    def test_custom_trust_score_accepted(self) -> None:
        profile = AgentTrustProfile(agent_id="agent-005", trust_score=0.5)
        assert profile.trust_score == pytest.approx(0.5)

    def test_trust_score_above_one_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="trust_score"):
            AgentTrustProfile(agent_id="agent-006", trust_score=1.1)

    def test_apply_delta_clamps_upward(self) -> None:
        profile = AgentTrustProfile(agent_id="agent-007", trust_score=0.95)
        profile.apply_delta(0.10)
        assert profile.trust_score == pytest.approx(1.0)

    def test_apply_delta_clamps_downward(self) -> None:
        profile = AgentTrustProfile(agent_id="agent-008", trust_score=0.05)
        profile.apply_delta(-0.10)
        assert profile.trust_score == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# AgentRole enum — all 5 canonical values
# ---------------------------------------------------------------------------


class TestAgentRoleEnum:
    def test_sandbox_exists(self) -> None:
        assert AgentRole.SANDBOX.value == "sandbox"

    def test_repair_ant_exists(self) -> None:
        assert AgentRole.REPAIR_ANT.value == "repair_ant"

    def test_memory_ant_exists(self) -> None:
        assert AgentRole.MEMORY_ANT.value == "memory_ant"

    def test_dispatcher_exists(self) -> None:
        assert AgentRole.DISPATCHER.value == "dispatcher"

    def test_guard_ant_exists(self) -> None:
        assert AgentRole.GUARD_ANT.value == "guard_ant"

    def test_exactly_five_canonical_values(self) -> None:
        values = list(AgentRole)
        assert len(values) == 5

    def test_all_five_canonical_values_present(self) -> None:
        role_values = {r.value for r in AgentRole}
        assert role_values == {"sandbox", "repair_ant", "memory_ant", "dispatcher", "guard_ant"}
