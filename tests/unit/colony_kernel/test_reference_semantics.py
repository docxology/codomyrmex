from __future__ import annotations

import pytest

from codomyrmex.colony_kernel.actuation_gate import GATE_SCORE_WEIGHTS, ActuationGate
from codomyrmex.colony_kernel.models import (
    ActionProposal,
    AgentRole,
    AgentTrustProfile,
    ColonySignal,
    DecayRate,
    SignalSource,
    SignalType,
)
from codomyrmex.colony_kernel.pheromone_store import PheromoneStore
from codomyrmex.colony_kernel.reference import (
    ReferenceDecision,
    ReferenceGate,
    ReferenceInput,
    ReferencePolicy,
    ReferenceState,
)


def _proposal() -> ActionProposal:
    return ActionProposal(
        agent_id="agent",
        agent_type="test",
        action_type="patch_file",
        target="module.py",
        rationale="bounded change",
        expected_outcome="tests pass",
        rollback_plan="revert commit",
        evidence={"test": "fixture"},
    )


@pytest.mark.parametrize(
    ("role", "trust", "pressure", "expected"),
    [
        (AgentRole.REPAIR_ANT, 0.8, 0.0, ReferenceDecision.EXECUTE),
        (AgentRole.REPAIR_ANT, 0.8, 3.0, ReferenceDecision.EXECUTE),
        (AgentRole.SANDBOX, 0.8, 0.0, ReferenceDecision.REFUSE),
        (AgentRole.REPAIR_ANT, 0.1, 0.0, ReferenceDecision.REFUSE),
    ],
)
def test_reference_matches_live_gate_decision(role, trust, pressure, expected):
    store = PheromoneStore()
    if pressure:
        store.deposit_signal(
            ColonySignal(
                location="module.py",
                signal_type=SignalType.RISK,
                strength=pressure,
                decay_rate=DecayRate.FAST,
                source=SignalSource.TEST,
            )
        )
    profile = AgentTrustProfile(agent_id="agent", role=role, trust_score=trust)
    live = ActuationGate(store).evaluate(_proposal(), profile)
    reference = ReferenceGate(
        ReferencePolicy(weights=dict(GATE_SCORE_WEIGHTS))
    ).evaluate(
        ReferenceInput(
            budget_approved=True,
            role=role.value,
            trust_score=trust,
            risk_pressure=pressure,
            failure_pressure=0.0,
            missing_fields=0,
        )
    )

    assert live.decision.value == reference.decision.value == expected.value
    assert live.gate_score == pytest.approx(reference.score)


def test_reference_state_is_deterministic_and_local():
    first = ReferenceState()
    first.deposit("a.py", "failure", 2.0)
    first.deposit("b.py", "success", 1.0)
    first.evaporate({"failure": 0.5, "success": 0.1})

    second = ReferenceState()
    second.deposit("a.py", "failure", 2.0)
    second.deposit("b.py", "success", 1.0)
    second.evaporate({"failure": 0.5, "success": 0.1})

    assert first.digest() == second.digest()
    assert first.pressures["a.py"]["failure"] == pytest.approx(1.5)
    assert first.pressures["b.py"]["success"] == pytest.approx(0.9)


def test_reference_policy_rejects_non_normalized_weights():
    with pytest.raises(ValueError, match="sum to one"):
        ReferenceGate(ReferencePolicy(weights={"budget": 0.5}))
