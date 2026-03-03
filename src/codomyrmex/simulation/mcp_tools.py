"""MCP tools for the simulation module."""

from typing import Any

from codomyrmex.logging_monitoring.core.logger_config import get_logger
from codomyrmex.model_context_protocol.decorators import mcp_tool
from codomyrmex.simulation.simulator import SimulationConfig, Simulator

logger = get_logger(__name__)

# Registry for simulation instances
_simulators: dict[str, Simulator] = {}


@mcp_tool(name="simulation_run", description="Executes a full simulation run with the given configuration parameters.")
def simulation_run(
    name: str = "default_simulation",
    max_steps: int = 1000,
    seed: int | None = None,
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run a simulation with the given configuration.

    Args:
        name: Simulation name identifier.
        max_steps: Maximum steps to execute.
        seed: Random seed for reproducibility.
        params: Arbitrary model-specific parameters.

    Returns:
        A dictionary containing status, steps_completed, config name, and simulation_status.
    """
    if not isinstance(max_steps, int) or max_steps <= 0:
        return {"error": "max_steps must be a positive integer"}
    if not isinstance(name, str) or not name:
        return {"error": "name must be a non-empty string"}

    config = SimulationConfig(
        name=name,
        max_steps=max_steps,
        seed=seed,
        params=params or {},
    )

    simulator = Simulator(config=config)
    _simulators[name] = simulator

    try:
        result = simulator.run()
        return {
            "status": "success",
            "steps_completed": result.steps_completed,
            "config": result.config_name,
            "simulation_status": result.status,
        }
    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        return {"error": str(e)}


@mcp_tool(name="simulation_get_results", description="Retrieves the current results from a simulation instance.")
def simulation_get_results(name: str) -> dict[str, Any]:
    """Get the results of a specific simulation.

    Args:
        name: Name of the simulation to retrieve results for.

    Returns:
        A dictionary containing status, steps_completed, config name, and simulation_status.
    """
    if not isinstance(name, str) or not name:
        return {"error": "name must be a non-empty string"}

    if name not in _simulators:
        return {"error": f"Simulation not found: {name}"}

    simulator = _simulators[name]
    result = simulator.get_results()

    return {
        "status": "success",
        "steps_completed": result.steps_completed,
        "config": result.config_name,
        "simulation_status": result.status,
    }
