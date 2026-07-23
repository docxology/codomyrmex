"""Explicit probabilistic bridge for future Colony Kernel experiments."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def _normalise(values: dict[str, float]) -> dict[str, float]:
    if not values or any(value < 0 for value in values.values()):
        raise ValueError("probability mappings must be non-empty and non-negative")
    total = sum(values.values())
    if total <= 0:
        raise ValueError("probability mappings must have positive mass")
    return {key: value / total for key, value in values.items()}


@dataclass(frozen=True)
class GenerativeModelSpec:
    states: tuple[str, ...]
    observations: tuple[str, ...]
    actions: tuple[str, ...]
    priors: dict[str, float]
    likelihood: dict[str, dict[str, float]]
    transitions: dict[str, dict[str, dict[str, float]]]
    preferences: dict[str, float]
    policy_horizon: int = 1
    seed: int = 0

    def __post_init__(self) -> None:
        if not self.states or not self.observations or not self.actions:
            raise ValueError("states, observations, and actions must be non-empty")
        if self.policy_horizon < 1 or self.seed < 0:
            raise ValueError("policy_horizon must be positive and seed non-negative")
        if set(self.priors) != set(self.states):
            raise ValueError("priors must cover all states")
        _normalise(self.priors)
        for state in self.states:
            if set(self.likelihood.get(state, {})) != set(self.observations):
                raise ValueError(f"likelihood for {state} must cover all observations")
            _normalise(self.likelihood[state])
            for action in self.actions:
                _normalise(self.transitions.get(action, {}).get(state, {}))


@dataclass(frozen=True)
class KernelObservation:
    """Observation extracted from an authenticated kernel trace."""

    target: str
    pressure: float
    gate_decision: str
    tests_passed: bool | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class KernelProbabilisticAdapter:
    """Small explicit Bayesian adapter; not a replacement for the gate."""

    def __init__(self, spec: GenerativeModelSpec) -> None:
        self.spec = spec

    def posterior(self, observation: str) -> dict[str, float]:
        if observation not in self.spec.observations:
            raise ValueError(f"unknown observation: {observation}")
        priors = _normalise(self.spec.priors)
        unnormalised = {
            state: priors[state] * self.spec.likelihood[state][observation]
            for state in self.spec.states
        }
        return _normalise(unnormalised)

    def expected_free_energy_proxy(
        self, belief: dict[str, float], action: str
    ) -> float:
        """Return declared risk/ambiguity cost for policy comparison.

        This is an explicitly named proxy used for research plumbing.  It is
        not asserted to be a complete variational free-energy implementation.
        """

        if action not in self.spec.actions:
            raise ValueError(f"unknown action: {action}")
        belief = _normalise(belief)
        if set(belief) != set(self.spec.states):
            raise ValueError("belief must cover exactly the declared model states")
        transitions = self.spec.transitions[action]
        cost = 0.0
        for state, state_probability in belief.items():
            next_distribution = transitions[state]
            for next_state, probability in next_distribution.items():
                preference = self.spec.preferences.get(next_state, 0.0)
                cost += state_probability * probability * (-preference)
        return cost

    def select_action(self, belief: dict[str, float]) -> str:
        values = {
            action: self.expected_free_energy_proxy(belief, action)
            for action in self.spec.actions
        }
        return min(values, key=lambda action: (values[action], action))

    def posterior_predictive(self, observation: str) -> dict[str, float]:
        """Return the predicted state distribution for a held-out observation."""
        return self.posterior(observation)

    def observation_from_kernel(self, observation: KernelObservation) -> dict[str, Any]:
        """Keep kernel evidence and probabilistic interpretation separate."""

        return {
            "target": observation.target,
            "pressure": observation.pressure,
            "gate_decision": observation.gate_decision,
            "tests_passed": observation.tests_passed,
            "probabilistic_observation": observation.gate_decision,
            "claim_boundary": "adapter observation; not a safety probability",
        }


__all__ = ["GenerativeModelSpec", "KernelObservation", "KernelProbabilisticAdapter"]
