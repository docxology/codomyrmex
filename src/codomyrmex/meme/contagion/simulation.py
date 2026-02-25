"""Simulation runner for contagion scenarios."""

from __future__ import annotations

from codomyrmex.meme.contagion.epidemic import SIRModel
from codomyrmex.meme.contagion.models import ContagionModel, PropagationTrace


def run_simulation(
    model_config: ContagionModel,
    steps: int = 100,
    seed_nodes: int = 1,
    topology: str = "random",  # random, scale_free, small_world
) -> PropagationTrace:
    """Run a full contagion simulation with specified topology.

    Currently wraps the mean-field SIRModel but accepts topology
    params for future expansion to network-based simulation.

    Args:
        model_config: Config object with beta/gamma parameters.
        steps: Simulation duration.
        seed_nodes: Initial infected count.
        topology: (Future use) Network structure type.

    Returns:
        PropagationTrace object.
    """
    # For this phase, we use the mean-field approximation
    # Future versions will build explicit NetworkX graphs here
    engine = SIRModel(
        population_size=model_config.network_size,
        beta=model_config.infection_rate,
        gamma=model_config.recovery_rate,
    )

    return engine.simulate(steps=steps, initial_infected=seed_nodes)
