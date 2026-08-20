"""Tests for the Active Inference research adapter (F5 / R6)."""

from __future__ import annotations

import pytest

from codomyrmex.colony_kernel.research.active_inference_adapter import (
    ActiveInferenceDecision,
    ColonyActiveInferenceAdapter,
    create_default_colony_generative_model,
)


def test_active_inference_adapter_low_pressure_favors_execute() -> None:
    adapter = ColonyActiveInferenceAdapter()
    decision = adapter.evaluate_step(risk_pressure=0.0, trust_score=0.8)

    assert isinstance(decision, ActiveInferenceDecision)
    assert (
        decision.posterior_beliefs["safe"] > decision.posterior_beliefs["compromised"]
    )
    assert decision.policy_action == "execute"
    assert decision.gate_decision == "execute"
    assert decision.aligned_with_gate is True


def test_active_inference_adapter_high_pressure_favors_refuse() -> None:
    adapter = ColonyActiveInferenceAdapter()
    decision = adapter.evaluate_step(risk_pressure=8.0, trust_score=0.8)

    assert (
        decision.posterior_beliefs["compromised"] > decision.posterior_beliefs["safe"]
    )
    assert decision.policy_action == "refuse"
    assert decision.gate_decision in ("hold", "refuse")


def test_custom_generative_model_specification() -> None:
    spec = create_default_colony_generative_model()
    adapter = ColonyActiveInferenceAdapter(spec=spec)
    assert len(adapter.spec.states) == 3
    assert len(adapter.spec.actions) == 2
    assert "safe" in adapter.spec.preferences
