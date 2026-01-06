"""Active inference implementation based on the free energy principle."""

import math
from dataclasses import dataclass, field
from typing import Any, Optional

import numpy as np

from codomyrmex.cerebrum.exceptions import ActiveInferenceError
from codomyrmex.cerebrum.utils import softmax
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class BeliefState:
    """Represents a belief state in active inference."""

    states: dict[str, float] = field(default_factory=dict)
    observations: dict[str, Any] = field(default_factory=dict)

    def normalize(self) -> None:
        """Normalize state probabilities."""
        total = sum(self.states.values())
        if total > 0:
            self.states = {s: p / total for s, p in self.states.items()}

    def entropy(self) -> float:
        """Compute entropy of belief distribution."""
        probs = [p for p in self.states.values() if p > 0]
        if not probs:
            return 0.0
        return -sum(p * math.log(p) for p in probs)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "states": self.states,
            "observations": self.observations,
        }


class VariationalFreeEnergy:
    """Computes variational free energy for active inference."""

    def __init__(self, precision: float = 1.0):
        """Initialize free energy calculator.

        Args:
            precision: Precision parameter (inverse variance)
        """
        self.precision = precision
        self.logger = get_logger(__name__)

    def compute(
        self,
        beliefs: BeliefState,
        observations: dict[str, Any],
        likelihood: dict[str, dict[str, float]],
    ) -> float:
        """Compute variational free energy.

        Args:
            beliefs: Current belief state
            observations: Observed data
            likelihood: Likelihood mapping states to observation probabilities

        Returns:
            Variational free energy value
        """
        # F = -log P(o|s) + KL[q(s) || p(s)]
        # Simplified version: complexity + accuracy

        # Accuracy term: -log P(o|s)
        accuracy = 0.0
        for state, prob in beliefs.states.items():
            if prob > 0 and state in likelihood:
                obs_probs = likelihood[state]
                # Compute expected log likelihood
                for obs_key, obs_value in observations.items():
                    if obs_key in obs_probs:
                        accuracy -= prob * math.log(obs_probs[obs_key] + 1e-10)

        # Complexity term: KL divergence (simplified)
        # Assuming uniform prior for simplicity
        complexity = beliefs.entropy()

        free_energy = accuracy + complexity / self.precision
        return free_energy

    def compute_expected_free_energy(
        self,
        beliefs: BeliefState,
        policy: str,
        transition_model: dict[str, dict[str, float]],
        observation_model: dict[str, dict[str, float]],
    ) -> float:
        """Compute expected free energy for a policy.

        Args:
            beliefs: Current belief state
            policy: Policy/action to evaluate
            transition_model: State transition probabilities
            observation_model: Observation probabilities given states

        Returns:
            Expected free energy
        """
        # EFE = E[log q(s) - log p(s|o)] - E[log p(o)]
        # Simplified: expected complexity + expected ambiguity

        # Expected complexity
        expected_complexity = 0.0
        for state, prob in beliefs.states.items():
            if prob > 0 and state in transition_model:
                next_states = transition_model[state]
                # Compute entropy of next state distribution
                next_probs = list(next_states.values())
                next_probs = [p for p in next_probs if p > 0]
                if next_probs:
                    entropy = -sum(p * math.log(p + 1e-10) for p in next_probs)
                    expected_complexity += prob * entropy

        # Expected ambiguity (uncertainty about observations)
        expected_ambiguity = 0.0
        for state, prob in beliefs.states.items():
            if prob > 0 and state in transition_model:
                next_states = transition_model[state]
                for next_state, trans_prob in next_states.items():
                    if next_state in observation_model:
                        obs_probs = list(observation_model[next_state].values())
                        obs_probs = [p for p in obs_probs if p > 0]
                        if obs_probs:
                            entropy = -sum(p * math.log(p + 1e-10) for p in obs_probs)
                            expected_ambiguity += prob * trans_prob * entropy

        efe = expected_complexity + expected_ambiguity
        return efe


class PolicySelector:
    """Selects actions/policies based on expected free energy."""

    def __init__(self, exploration_weight: float = 0.1):
        """Initialize policy selector.

        Args:
            exploration_weight: Weight for exploration vs exploitation
        """
        self.exploration_weight = exploration_weight
        self.logger = get_logger(__name__)

    def select_policy(
        self,
        policies: list[str],
        expected_free_energies: list[float],
        temperature: float = 1.0,
    ) -> str:
        """Select a policy based on expected free energy.

        Args:
            policies: List of available policies
            expected_free_energies: EFE values for each policy
            temperature: Temperature for softmax selection

        Returns:
            Selected policy
        """
        if not policies:
            raise ActiveInferenceError("No policies available")

        if len(policies) != len(expected_free_energies):
            raise ActiveInferenceError("Policies and EFE values must have same length")

        # Convert EFE to utilities (lower EFE = higher utility)
        utilities = [-efe for efe in expected_free_energies]

        # Apply softmax with temperature
        probabilities = softmax(utilities, temperature=temperature)

        # Select policy
        selected_idx = np.random.choice(len(policies), p=probabilities)
        return policies[selected_idx]

    def select_greedy(self, policies: list[str], expected_free_energies: list[float]) -> str:
        """Select policy with lowest expected free energy (greedy).

        Args:
            policies: List of available policies
            expected_free_energies: EFE values for each policy

        Returns:
            Policy with lowest EFE
        """
        if not policies:
            raise ActiveInferenceError("No policies available")

        min_idx = np.argmin(expected_free_energies)
        return policies[min_idx]


class ActiveInferenceAgent:
    """Implements active inference agent based on free energy principle."""

    def __init__(
        self,
        states: list[str],
        observations: list[str],
        actions: list[str],
        precision: float = 1.0,
        policy_horizon: int = 5,
        exploration_weight: float = 0.1,
    ):
        """Initialize active inference agent.

        Args:
            states: List of possible states
            observations: List of possible observations
            actions: List of possible actions
            precision: Precision parameter for free energy
            policy_horizon: Planning horizon
            exploration_weight: Exploration vs exploitation weight
        """
        self.states = states
        self.observations = observations
        self.actions = actions
        self.precision = precision
        self.policy_horizon = policy_horizon
        self.exploration_weight = exploration_weight

        self.beliefs = BeliefState()
        self.transition_model: dict[str, dict[str, float]] = {}
        self.observation_model: dict[str, dict[str, float]] = {}
        self.likelihood: dict[str, dict[str, float]] = {}

        self.free_energy_calculator = VariationalFreeEnergy(precision=precision)
        self.policy_selector = PolicySelector(exploration_weight=exploration_weight)

        self.logger = get_logger(__name__)

        # Initialize uniform beliefs
        uniform_prob = 1.0 / len(states) if states else 1.0
        self.beliefs.states = {state: uniform_prob for state in states}

    def set_transition_model(
        self, model: dict[str, dict[str, float]]
    ) -> None:
        """Set state transition model.

        Args:
            model: Transition probabilities P(s'|s, a)
        """
        self.transition_model = model
        self.logger.debug("Set transition model")

    def set_observation_model(
        self, model: dict[str, dict[str, float]]
    ) -> None:
        """Set observation model.

        Args:
            model: Observation probabilities P(o|s)
        """
        self.observation_model = model
        self.likelihood = model  # Alias for compatibility
        self.logger.debug("Set observation model")

    def predict(self, observation: Optional[dict[str, Any]] = None) -> dict[str, float]:
        """Predict state distribution given observation.

        Args:
            observation: Optional observation to condition on

        Returns:
            Predicted state distribution
        """
        if observation is None:
            # Return current beliefs
            return self.beliefs.states.copy()

        # Update beliefs based on observation using Bayes' rule
        updated_beliefs = {}
        for state, prior_prob in self.beliefs.states.items():
            if state in self.observation_model:
                obs_probs = self.observation_model[state]
                likelihood = 1.0
                for obs_key, obs_value in observation.items():
                    if obs_key in obs_probs:
                        likelihood *= obs_probs[obs_key]
                updated_beliefs[state] = prior_prob * likelihood
            else:
                updated_beliefs[state] = prior_prob

        # Normalize
        total = sum(updated_beliefs.values())
        if total > 0:
            updated_beliefs = {s: p / total for s, p in updated_beliefs.items()}

        return updated_beliefs

    def select_action(self, state: Optional[dict[str, Any]] = None) -> str:
        """Select action based on expected free energy.

        Args:
            state: Optional current state (uses beliefs if None)

        Returns:
            Selected action
        """
        # Evaluate each action as a policy
        policies = self.actions
        expected_free_energies = []

        for action in policies:
            efe = self._compute_action_efe(action)
            expected_free_energies.append(efe)

        # Select action
        selected = self.policy_selector.select_policy(
            policies, expected_free_energies, temperature=1.0 / self.precision
        )

        self.logger.debug(f"Selected action: {selected}")
        return selected

    def _compute_action_efe(self, action: str) -> float:
        """Compute expected free energy for an action.

        Args:
            action: Action to evaluate

        Returns:
            Expected free energy
        """
        # Simplified: use transition and observation models
        if not self.transition_model or not self.observation_model:
            return 0.0  # No model, return neutral value

        # Compute expected next state distribution
        next_state_probs = {}
        for state, prob in self.beliefs.states.items():
            if prob > 0:
                # Get transition probabilities for this action
                key = f"{state}_{action}"
                if key in self.transition_model:
                    transitions = self.transition_model[key]
                    for next_state, trans_prob in transitions.items():
                        next_state_probs[next_state] = (
                            next_state_probs.get(next_state, 0.0) + prob * trans_prob
                        )

        # Compute expected ambiguity
        expected_ambiguity = 0.0
        for next_state, prob in next_state_probs.items():
            if prob > 0 and next_state in self.observation_model:
                obs_probs = list(self.observation_model[next_state].values())
                obs_probs = [p for p in obs_probs if p > 0]
                if obs_probs:
                    entropy = -sum(p * math.log(p + 1e-10) for p in obs_probs)
                    expected_ambiguity += prob * entropy

        return expected_ambiguity

    def update_beliefs(self, observation: dict[str, Any]) -> None:
        """Update beliefs based on new observation.

        Args:
            observation: New observation
        """
        updated = self.predict(observation)
        self.beliefs.states = updated
        self.beliefs.observations.update(observation)
        self.beliefs.normalize()
        self.logger.debug("Updated beliefs")

    def compute_free_energy(
        self, beliefs: Optional[BeliefState] = None, observations: Optional[dict[str, Any]] = None
    ) -> float:
        """Compute variational free energy.

        Args:
            beliefs: Belief state (uses current if None)
            observations: Observations (uses current if None)

        Returns:
            Free energy value
        """
        beliefs = beliefs or self.beliefs
        observations = observations or self.beliefs.observations

        return self.free_energy_calculator.compute(beliefs, observations, self.likelihood)

    def get_beliefs(self) -> BeliefState:
        """Get current belief state."""
        return self.beliefs

    def reset(self) -> None:
        """Reset agent to initial state."""
        uniform_prob = 1.0 / len(self.states) if self.states else 1.0
        self.beliefs = BeliefState()
        self.beliefs.states = {state: uniform_prob for state in self.states}
        self.beliefs.observations = {}
        self.logger.debug("Reset agent")


