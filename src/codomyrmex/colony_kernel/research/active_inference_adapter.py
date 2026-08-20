"""Active Inference Research Adapter and Formalism Bridge (F5 / R6).

Provides an explicit active-inference decision loop bridging Cerebrum variational
models and Colony Kernel actuation gates under declared generative model assumptions.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from codomyrmex.colony_kernel.reference import (
    ReferenceDecision,
    ReferenceGate,
    ReferenceInput,
)
from codomyrmex.colony_kernel.research.probabilistic import (
    GenerativeModelSpec,
    KernelProbabilisticAdapter,
)


@dataclass(frozen=True)
class ActiveInferenceDecision:
    """Decision produced by the Active Inference research agent."""

    policy_action: str
    posterior_beliefs: dict[str, float]
    expected_free_energy: float
    gate_decision: str
    gate_score: float
    aligned_with_gate: bool
    free_energy_distribution: dict[str, float]


def create_default_colony_generative_model() -> GenerativeModelSpec:
    """Create a canonical 3-state, 3-observation, 2-action generative model."""
    states = ("safe", "risky", "compromised")
    observations = ("low_pressure", "med_pressure", "high_pressure")
    actions = ("execute", "refuse")

    priors = {"safe": 0.50, "risky": 0.30, "compromised": 0.20}

    likelihood = {
        "safe": {"low_pressure": 0.85, "med_pressure": 0.10, "high_pressure": 0.05},
        "risky": {"low_pressure": 0.15, "med_pressure": 0.70, "high_pressure": 0.15},
        "compromised": {
            "low_pressure": 0.05,
            "med_pressure": 0.15,
            "high_pressure": 0.80,
        },
    }

    transitions = {
        "execute": {
            "safe": {"safe": 0.90, "risky": 0.08, "compromised": 0.02},
            "risky": {"safe": 0.20, "risky": 0.40, "compromised": 0.40},
            "compromised": {"safe": 0.01, "risky": 0.09, "compromised": 0.90},
        },
        "refuse": {
            "safe": {"safe": 0.60, "risky": 0.30, "compromised": 0.10},
            "risky": {"safe": 0.50, "risky": 0.40, "compromised": 0.10},
            "compromised": {"safe": 0.30, "risky": 0.50, "compromised": 0.20},
        },
    }

    preferences = {
        "safe": 2.0,
        "risky": -1.0,
        "compromised": -5.0,
    }

    return GenerativeModelSpec(
        states=states,
        observations=observations,
        actions=actions,
        priors=priors,
        likelihood=likelihood,
        transitions=transitions,
        preferences=preferences,
        policy_horizon=1,
    )


class ColonyActiveInferenceAdapter:
    """Evaluates agent policy via Expected Free Energy and compares against ActuationGate."""

    def __init__(
        self,
        spec: GenerativeModelSpec | None = None,
        gate: ReferenceGate | None = None,
    ) -> None:
        self.spec = spec or create_default_colony_generative_model()
        self.probabilistic = KernelProbabilisticAdapter(self.spec)
        self.gate = gate or ReferenceGate()

    def map_pressure_to_observation(self, risk_pressure: float) -> str:
        """Discretize continuous risk pressure into categorical observation."""
        if risk_pressure < 1.0:
            return "low_pressure"
        if risk_pressure < 4.0:
            return "med_pressure"
        return "high_pressure"

    def evaluate_step(
        self,
        risk_pressure: float,
        trust_score: float,
        *,
        failure_pressure: float = 0.0,
        missing_fields: int = 0,
    ) -> ActiveInferenceDecision:
        """Run one active inference update step and gate comparison."""
        obs = self.map_pressure_to_observation(risk_pressure)
        posterior = self.probabilistic.posterior(obs)

        fe_dist: dict[str, float] = {}
        for action in self.spec.actions:
            fe_dist[action] = self.probabilistic.expected_free_energy_proxy(
                posterior, action
            )

        best_action = min(fe_dist, key=fe_dist.get)  # type: ignore

        gate_res = self.gate.evaluate(
            ReferenceInput(
                budget_approved=True,
                role="repair_ant",
                trust_score=trust_score,
                risk_pressure=risk_pressure,
                failure_pressure=failure_pressure,
                missing_fields=missing_fields,
            )
        )

        gate_act = (
            "execute" if gate_res.decision == ReferenceDecision.EXECUTE else "refuse"
        )
        aligned = best_action == gate_act

        return ActiveInferenceDecision(
            policy_action=best_action,
            posterior_beliefs=posterior,
            expected_free_energy=fe_dist[best_action],
            gate_decision=gate_res.decision.value,
            gate_score=gate_res.score,
            aligned_with_gate=aligned,
            free_energy_distribution=fe_dist,
        )
