"""Causal contracts for every named ActuationGate mechanism.

Each test compares a real-component control with exactly one changed input.
If the corresponding gate branch is removed or disabled, the assertion fails;
the tests therefore protect the mechanism rather than merely its final range.
"""

from __future__ import annotations

import pytest

from codomyrmex.agentic_memory.stigmergy.field import TraceField
from codomyrmex.agentic_memory.stigmergy.models import StigmergyConfig
from codomyrmex.colony_kernel.actuation_gate import ActuationGate
from codomyrmex.colony_kernel.consequence_memory import ConsequenceMemory
from codomyrmex.colony_kernel.models import (
    ActionProposal,
    AgentRole,
    AgentTrustProfile,
    ConsequenceRecord,
    FalsificationFinding,
    FalsificationSeverity,
    GateDecision,
    ResourceCost,
    SignalType,
)
from codomyrmex.colony_kernel.resource_ledger import ResourceBudget, ResourceLedger


def _proposal(**overrides: object) -> ActionProposal:
    values: dict[str, object] = {
        "agent_id": "mechanism-agent",
        "agent_type": "contract-test",
        "action_type": "patch_file",
        "target": "src/mechanism_target.py",
        "rationale": "isolate one gate mechanism",
        "expected_outcome": "the declared test passes",
        "budget_estimate": ResourceCost(llm_calls=1),
        "rollback_plan": "restore the prior file",
        "evidence": {"test": "mechanism-contract"},
    }
    values.update(overrides)
    return ActionProposal(**values)


def _profile(
    *,
    trust_score: float = 0.9,
    role: AgentRole = AgentRole.REPAIR_ANT,
) -> AgentTrustProfile:
    return AgentTrustProfile(
        agent_id="mechanism-agent",
        role=role,
        trust_score=trust_score,
        total_proposals=20,
        accepted_proposals=10,
    )


def _gate(
    *,
    budget: ResourceBudget | None = None,
    memory: ConsequenceMemory | None = None,
    field: TraceField | None = None,
) -> ActuationGate:
    return ActuationGate(
        pheromone_store=field if field is not None else TraceField(StigmergyConfig()),
        resource_ledger=ResourceLedger(budget or ResourceBudget(max_llm_calls=10)),
        consequence_memory_ref=memory,
    )


def test_budget_override_is_causal() -> None:
    proposal = _proposal()
    control = _gate().evaluate(proposal, _profile())
    rejected = _gate(budget=ResourceBudget(max_llm_calls=0)).evaluate(
        proposal, _profile()
    )

    assert control.decision is GateDecision.EXECUTE
    assert rejected.decision is GateDecision.REFUSE
    assert rejected.gate_score == 0.0
    assert "Budget ceiling exceeded" in rejected.reason


def test_sandbox_override_is_causal() -> None:
    proposal = _proposal()
    control = _gate().evaluate(proposal, _profile())
    rejected = _gate().evaluate(proposal, _profile(role=AgentRole.SANDBOX))

    assert control.decision is GateDecision.EXECUTE
    assert rejected.decision is GateDecision.REFUSE
    assert rejected.gate_score == 0.0
    assert "SANDBOX" in rejected.reason


def test_trust_floor_and_tier_are_causal() -> None:
    proposal = _proposal()
    high = _gate().evaluate(proposal, _profile(trust_score=0.9))
    medium = _gate().evaluate(proposal, _profile(trust_score=0.5))
    floor = _gate().evaluate(proposal, _profile(trust_score=0.29))

    assert high.gate_score == 1.0
    assert medium.gate_score == 0.875
    assert medium.gate_score < high.gate_score
    assert floor.decision is GateDecision.REFUSE
    assert floor.gate_score == 0.0


def test_risk_pressure_changes_score_and_reason() -> None:
    proposal = _proposal()
    field = TraceField(StigmergyConfig())
    field.deposit(f"{proposal.target}:{SignalType.RISK.value}", initial=6.0)
    clear = _gate().evaluate(proposal, _profile())
    hazardous = _gate(field=field).evaluate(proposal, _profile())

    assert clear.decision is GateDecision.EXECUTE
    assert hazardous.decision is GateDecision.HOLD
    assert hazardous.gate_score == pytest.approx(0.7)
    assert "elevated local pheromone hazard pressure" in hazardous.reason


def test_completeness_changes_score_and_diagnostic_reason() -> None:
    complete = _proposal()
    incomplete = _proposal(rollback_plan="", evidence={})
    control = _gate().evaluate(complete, _profile())
    degraded = _gate().evaluate(incomplete, _profile())

    assert control.gate_score == 1.0
    assert degraded.gate_score == 0.895
    assert degraded.gate_score < control.gate_score
    assert "missing: rollback_plan" in degraded.reason
    assert "missing: evidence" in degraded.reason


def test_recent_failure_memory_changes_trust_component() -> None:
    memory = ConsequenceMemory()
    for index in range(3):
        memory.record(
            ConsequenceRecord(
                proposal=_proposal(proposal_id=f"failure-{index}"),
                action_taken="patch_file",
                actual_outcome="the test failed",
                tests_passed=False,
            )
        )

    proposal = _proposal()
    control = _gate().evaluate(proposal, _profile())
    penalized = _gate(memory=memory).evaluate(proposal, _profile())

    assert control.gate_score == 1.0
    assert penalized.gate_score == 0.9375
    assert penalized.gate_score < control.gate_score
    assert "recent_failures=3" in penalized.reason


def test_critical_falsification_override_is_causal() -> None:
    proposal = _proposal()
    control = _gate().evaluate(proposal, _profile())
    critical = _gate().evaluate(
        proposal,
        _profile(),
        [
            FalsificationFinding(
                claim="the declared target is unsafe",
                attack_vector="scope",
                severity=FalsificationSeverity.CRITICAL,
                remediation="resolve the finding",
            )
        ],
        True,
    )

    assert control.decision is GateDecision.EXECUTE
    assert critical.decision is GateDecision.REFUSE
    assert critical.gate_score == 0.0
    assert "CRITICAL falsification finding" in critical.reason
