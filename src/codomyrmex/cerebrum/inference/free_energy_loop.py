"""Free-energy minimization closed-loop runner.

Wraps an ActiveInferenceAgent in a perception–action loop that iterates
until variational free energy converges below a threshold or a step limit
is reached.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from codomyrmex.cerebrum.core.exceptions import ActiveInferenceError
from codomyrmex.logging_monitoring import get_logger

if TYPE_CHECKING:
    from collections.abc import Callable

    from codomyrmex.cerebrum.inference.active_inference import ActiveInferenceAgent

logger = get_logger(__name__)


@dataclass
class StepResult:
    """Result of a single perception–action cycle.

    Attributes:
        step: Step index (0-based).
        action: Action selected by the agent.
        free_energy: Variational free energy after belief update.
        beliefs: Snapshot of belief-state probabilities.
    """

    step: int
    action: str
    free_energy: float
    beliefs: dict[str, float] = field(default_factory=dict)


@dataclass
class LoopResult:
    """Result of a complete free-energy minimization run.

    Attributes:
        steps: Total steps executed.
        converged: Whether the loop converged below the threshold.
        final_free_energy: Free energy at the final step.
        action_history: Ordered list of actions taken.
        belief_trajectory: Belief snapshots at each step.
        step_results: Full per-step results.
    """

    steps: int
    converged: bool
    final_free_energy: float
    action_history: list[str] = field(default_factory=list)
    belief_trajectory: list[dict[str, float]] = field(default_factory=list)
    step_results: list[StepResult] = field(default_factory=list)


class FreeEnergyLoop:
    """Closed-loop free-energy minimization runner.

    Orchestrates an ActiveInferenceAgent through repeated
    observe → infer → act cycles, tracking convergence.

    Example::

        loop = FreeEnergyLoop(agent, max_steps=50, fe_threshold=0.1)
        result = loop.run({"sensor": 0.5})
        print(f"Converged: {result.converged} in {result.steps} steps")
    """

    def __init__(
        self,
        agent: ActiveInferenceAgent,
        max_steps: int = 100,
        fe_threshold: float = 0.01,
        convergence_window: int = 3,
        observation_fn: Callable[[str, int], dict[str, Any]] | None = None,
    ) -> None:
        """Initialize the free-energy loop.

        Args:
            agent: Active inference agent to drive.
            max_steps: Maximum number of perception–action steps.
            fe_threshold: Free energy below which the loop is considered converged.
            convergence_window: Number of consecutive steps that must remain
                below threshold before declaring convergence.
            observation_fn: Optional callable (action, step) -> observation dict.
                If None, the initial observation is reused each step.
        """
        if max_steps < 1:
            raise ValueError("max_steps must be >= 1")
        if fe_threshold < 0:
            raise ValueError("fe_threshold must be >= 0")
        if convergence_window < 1:
            raise ValueError("convergence_window must be >= 1")

        self.agent = agent
        self.max_steps = max_steps
        self.fe_threshold = fe_threshold
        self.convergence_window = convergence_window
        self.observation_fn = observation_fn

    def step(self, observation: dict[str, Any], step_idx: int = 0) -> StepResult:
        """Execute a single perception–action cycle.

        1. Update beliefs given observation.
        2. Compute free energy.
        3. Select action.

        Args:
            observation: Current observation dict.
            step_idx: Step index for logging.

        Returns:
            StepResult with action, free energy, and beliefs.
        """
        # Perception: update beliefs
        self.agent.update_beliefs(observation)

        # Compute free energy
        fe = self.agent.compute_free_energy(
            beliefs=self.agent.beliefs,
            observations=observation,
        )

        # Action: select based on expected free energy
        action = self.agent.select_action()

        beliefs_snapshot = self.agent.beliefs.states.copy()

        logger.debug(
            "Step %d: action=%s, FE=%.4f",
            step_idx,
            action,
            fe,
        )

        return StepResult(
            step=step_idx,
            action=action,
            free_energy=fe,
            beliefs=beliefs_snapshot,
        )

    def run(self, initial_observation: dict[str, Any]) -> LoopResult:
        """Run the free-energy minimization loop.

        Args:
            initial_observation: Starting observation.

        Returns:
            LoopResult summarizing convergence, actions, and beliefs.

        Raises:
            ActiveInferenceError: If the agent raises during stepping.
        """
        action_history: list[str] = []
        belief_trajectory: list[dict[str, float]] = []
        step_results: list[StepResult] = []
        consecutive_below = 0
        final_fe = float("inf")
        converged = False

        observation = initial_observation

        for i in range(self.max_steps):
            try:
                result = self.step(observation, step_idx=i)
            except Exception as exc:
                raise ActiveInferenceError(f"Agent error at step {i}: {exc}") from exc

            step_results.append(result)
            action_history.append(result.action)
            belief_trajectory.append(result.beliefs)
            final_fe = result.free_energy

            # Check convergence
            if result.free_energy <= self.fe_threshold:
                consecutive_below += 1
            else:
                consecutive_below = 0

            if consecutive_below >= self.convergence_window:
                converged = True
                logger.info(
                    "Converged at step %d (FE=%.6f <= %.6f for %d steps)",
                    i,
                    result.free_energy,
                    self.fe_threshold,
                    self.convergence_window,
                )
                break

            # Generate next observation
            if self.observation_fn is not None:
                observation = self.observation_fn(result.action, i)
            # else: reuse the same observation

        total_steps = len(step_results)

        if not converged:
            logger.info(
                "Loop ended after %d steps without convergence (final FE=%.6f)",
                total_steps,
                final_fe,
            )

        return LoopResult(
            steps=total_steps,
            converged=converged,
            final_free_energy=final_fe,
            action_history=action_history,
            belief_trajectory=belief_trajectory,
            step_results=step_results,
        )


__all__ = [
    "FreeEnergyLoop",
    "LoopResult",
    "StepResult",
]
