"""Regression tests for the executable Colony Kernel invariant predicates."""

from collections.abc import Callable, Sequence
from dataclasses import fields
from pathlib import Path
from typing import overload

import pytest

from codomyrmex.agentic_memory.stigmergy.models import StigmergyConfig
from codomyrmex.colony_kernel.actuation_gate import GATE_SCORE_WEIGHTS
from codomyrmex.colony_kernel.invariants import (
    all_invariants_hold,
    check_budget_monotonic,
    check_consequence_trust_bounds,
    check_enum_values_no_conflict,
    check_gate_decision_space_closed,
    check_gate_thresholds_ordered,
    check_gate_weights_sum_to_one,
    check_pheromone_strength_bounds,
    check_role_ladder_monotonic,
    check_trust_score_in_range,
)
from codomyrmex.colony_kernel.models import (
    ActionProposal,
    AgentRole,
    AgentTrustProfile,
    ConsequenceRecord,
    GateDecision,
    GateResult,
    ResourceCost,
)

pytestmark = pytest.mark.unit


class UnavailableSequence(Sequence[object]):
    """A real sequence whose state acquisition fails, as a monitoring source may."""

    def __init__(self, failure: BaseException | None = None) -> None:
        self.failure = failure or RuntimeError("snapshot unavailable")

    def __len__(self) -> int:
        return 1

    @overload
    def __getitem__(self, index: int) -> object: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[object]: ...

    def __getitem__(self, index: int | slice) -> object:
        raise self.failure


def test_invariant_predicates_read_live_runtime_constants() -> None:
    """The formal checks must follow the policies that execute at runtime."""
    assert check_gate_weights_sum_to_one(list(GATE_SCORE_WEIGHTS.values()))
    assert check_pheromone_strength_bounds([0.0, StigmergyConfig().max_strength])
    assert check_role_ladder_monotonic()


def test_invariant_predicates_reject_boundary_violations() -> None:
    profile = AgentTrustProfile(agent_id="agent", trust_score=0.5)
    profile.trust_score = 1.01

    assert not check_trust_score_in_range([profile])
    assert not check_pheromone_strength_bounds([-0.001])
    assert not check_pheromone_strength_bounds([StigmergyConfig().max_strength + 1])
    assert not check_role_ladder_monotonic([0.2, 0.2])
    assert not check_gate_weights_sum_to_one([0.25, 0.25, 0.25])


def test_composite_invariant_report_is_true_for_live_defaults() -> None:
    report = all_invariants_hold(
        profiles=[AgentTrustProfile(agent_id="agent", trust_score=0.5)],
        strengths=[0.0, 1.0],
    )

    assert report == {
        "gate_weights_sum_to_one": True,
        "gate_thresholds_ordered": True,
        "trust_score_in_range": True,
        "pheromone_strength_bounds": True,
        "role_ladder_monotonic": True,
        "enum_values_no_conflict": True,
        "budget_monotonic": True,
        "gate_decision_space_closed": True,
        "consequence_trust_bounds": True,
    }
    assert check_enum_values_no_conflict()


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -0.1, 1.1, "bad"])
def test_invalid_role_thresholds_and_gate_thresholds_fail_closed(value: float) -> None:
    """A single invalid threshold cannot pass through vacuous comparisons."""
    assert not check_role_ladder_monotonic([value])
    assert not check_gate_thresholds_ordered(execute_thresh=value)
    assert not check_gate_thresholds_ordered(hold_thresh=value)


def test_negative_weights_cannot_cancel_into_valid_sum() -> None:
    assert not check_gate_weights_sum_to_one([-1.0, 2.0])


@pytest.mark.parametrize("value", [1, 0.5, object(), UnavailableSequence()])
def test_scalar_state_inputs_fail_closed(value: object) -> None:
    """Dynamic monitoring inputs can be malformed despite static annotations."""
    checks: list[Callable[..., bool]] = [
        check_gate_weights_sum_to_one,
        check_trust_score_in_range,
        check_pheromone_strength_bounds,
        check_role_ladder_monotonic,
        check_budget_monotonic,
        check_gate_decision_space_closed,
        check_consequence_trust_bounds,
    ]
    for check in checks:
        assert not check(value)
    report: Callable[..., dict[str, bool]] = all_invariants_hold
    result = report(
        profiles=value,
        strengths=value,
        budget_usage=value,
        gate_results=value,
        consequences=value,
    )
    assert not result["trust_score_in_range"]
    assert not result["pheromone_strength_bounds"]
    assert not result["budget_monotonic"]
    assert not result["gate_decision_space_closed"]
    assert not result["consequence_trust_bounds"]


def test_integer_budget_counts_keep_exact_precision() -> None:
    """One-unit decreases above floating-point integer precision are detected."""
    upper = ResourceCost(llm_calls=2**53 + 1)
    lower = ResourceCost(llm_calls=2**53)
    assert not check_budget_monotonic([upper, lower])
    assert check_budget_monotonic([lower, upper])
    assert check_budget_monotonic([ResourceCost(llm_calls=10**1000)])


def test_monitoring_does_not_swallow_process_interruptions() -> None:
    checks: list[Callable[..., bool]] = [
        check_gate_weights_sum_to_one,
        check_trust_score_in_range,
        check_pheromone_strength_bounds,
        check_role_ladder_monotonic,
        check_budget_monotonic,
        check_gate_decision_space_closed,
        check_consequence_trust_bounds,
    ]
    for check in checks:
        with pytest.raises(KeyboardInterrupt):
            check(UnavailableSequence(failure=KeyboardInterrupt()))


@pytest.mark.parametrize("calls", [True, 0.5])
def test_budget_counts_reject_boolean_or_fractional_units(calls: object) -> None:
    usage = ResourceCost()
    usage.__dict__["llm_calls"] = calls
    assert not check_budget_monotonic([usage])


def test_explicit_ledger_reset_starts_a_new_snapshot_sequence() -> None:
    """Real period resets are valid only when snapshot sequences are split."""
    from codomyrmex.colony_kernel.resource_ledger import ResourceLedger

    ledger = ResourceLedger()
    first_period = [ledger.current_usage()]
    ledger.record_cost(ResourceCost(llm_calls=2), agent_id="agent")
    first_period.append(ledger.current_usage())
    ledger.reset_period()
    second_period = [ledger.current_usage()]
    ledger.record_cost(ResourceCost(llm_calls=1), agent_id="agent")
    second_period.append(ledger.current_usage())
    assert check_budget_monotonic(first_period)
    assert check_budget_monotonic(second_period)
    assert not check_budget_monotonic(first_period + second_period)


@pytest.mark.parametrize("dimension", [item.name for item in fields(ResourceCost)])
def test_each_budget_dimension_must_be_monotonic(dimension: str) -> None:
    before = ResourceCost()
    after = ResourceCost()
    setattr(before, dimension, 1)
    setattr(after, dimension, 0)
    assert not check_budget_monotonic([before, after])
    assert check_budget_monotonic([after, before])


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -0.1, "bad"])
def test_corrupted_budget_snapshot_fails_closed(value: float) -> None:
    usage = ResourceCost()
    usage.runtime_seconds = value
    assert not check_budget_monotonic([usage])


@pytest.mark.parametrize("decision", list(GateDecision))
def test_gate_decision_closure_accepts_runtime_enum(decision: GateDecision) -> None:
    assert check_gate_decision_space_closed(
        [GateResult(decision=decision, gate_score=0.5, reason="test")]
    )


@pytest.mark.parametrize("attribute", ["gate_score", "falsification_severity"])
@pytest.mark.parametrize("value", [float("nan"), float("inf"), -0.1, 1.1, "bad"])
def test_corrupted_gate_scores_fail_closed(attribute: str, value: float) -> None:
    result = GateResult(decision=GateDecision.HOLD, gate_score=0.5, reason="test")
    setattr(result, attribute, value)
    assert not check_gate_decision_space_closed([result])


def test_execution_requires_budget_and_noncritical_falsification() -> None:
    result = GateResult(
        decision=GateDecision.EXECUTE,
        gate_score=0.9,
        reason="test",
        budget_approved=False,
    )
    assert not check_gate_decision_space_closed([result])
    result.budget_approved = True
    result.falsification_severity = 1.0
    assert not check_gate_decision_space_closed([result])


def test_raw_gate_decision_string_is_not_a_runtime_verdict() -> None:
    result = GateResult(decision=GateDecision.HOLD, gate_score=0.5, reason="test")
    result.__dict__["decision"] = "execute"
    assert not check_gate_decision_space_closed([result])


def test_cross_subsystem_runtime_invariant_report(tmp_path: Path) -> None:
    """Real ledger, gate, SQLite records, and trust profiles share the crosswalk."""
    from codomyrmex.colony_kernel.actuation_gate import ActuationGate
    from codomyrmex.colony_kernel.consequence_memory import ConsequenceMemory
    from codomyrmex.colony_kernel.pheromone_store import PheromoneStore
    from codomyrmex.colony_kernel.resource_ledger import ResourceLedger

    ledger = ResourceLedger()
    usage = [ledger.current_usage()]
    for _ in range(3):
        ledger.record_cost(ResourceCost(llm_calls=1, risk_level=0.6), agent_id="agent")
        usage.append(ledger.current_usage())
    assert usage[-1].risk_level == 1.0  # Saturation stays nondecreasing.
    proposal = ActionProposal(
        agent_id="agent",
        agent_type="repair_ant",
        action_type="patch_file",
        target="codomyrmex.example",
        rationale="Repair a regression",
        expected_outcome="Tests pass",
        rollback_plan="Revert patch",
        evidence={"test_id": "regression"},
    )
    gate = ActuationGate(pheromone_store=PheromoneStore())
    verdict = gate.evaluate(
        proposal,
        AgentTrustProfile(agent_id="agent", role=AgentRole.REPAIR_ANT, trust_score=0.9),
        budget_approved=True,
    )
    records = []
    with ConsequenceMemory(db_path=str(tmp_path / "consequences.db")) as memory:
        for passed, feedback, repair in [(True, 1.0, False), (False, -1.0, True)]:
            record = ConsequenceRecord(
                proposal=proposal,
                action_taken="Applied patch",
                actual_outcome="Recorded tests",
                tests_passed=passed,
                human_feedback=feedback,
                repair_needed=repair,
            )
            records.append(memory.record(record))
        profile = memory.get_profile("agent")
    report = all_invariants_hold(
        profiles=[profile],
        strengths=[0.0, 1.0],
        budget_usage=usage,
        gate_results=[verdict],
        consequences=records,
    )
    assert all(report.values()), report
    records[-1].trust_delta = 0.9
    assert not check_consequence_trust_bounds(records)
    usage[-1].llm_calls = 0
    assert not all_invariants_hold(budget_usage=usage)["budget_monotonic"]
