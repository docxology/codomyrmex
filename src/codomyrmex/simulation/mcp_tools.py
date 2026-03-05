"""MCP tool definitions for the simulation module.

Exposes simulation configuration, execution, and agent management as MCP tools.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


def _get_simulator(
    name: str = "default", max_steps: int = 100, seed: int | None = None
):
    """Lazy import and create a Simulator with config."""
    from codomyrmex.simulation.simulator import SimulationConfig, Simulator

    config = SimulationConfig(name=name, max_steps=max_steps, seed=seed)
    return Simulator(config=config)


def _get_agent_classes():
    """Lazy import of agent classes."""
    from codomyrmex.simulation.agent import RandomAgent, RuleBasedAgent

    return RandomAgent, RuleBasedAgent


@mcp_tool(
    category="simulation",
    description="Run a simulation with random agents for a specified number of steps.",
)
def simulation_run(
    name: str = "default",
    max_steps: int = 100,
    agent_count: int = 3,
    agent_action_types: list[str] | None = None,
) -> dict[str, Any]:
    """Run a simulation with random agents.

    Args:
        name: Simulation name.
        max_steps: Maximum number of simulation steps.
        agent_count: Number of random agents to create.
        agent_action_types: Action types for agents (default: move, wait, observe).

    Returns:
        dict with keys: status, steps_completed, agent_count, config_name
    """
    try:
        sim = _get_simulator(name=name, max_steps=max_steps)
        RandomAgent, _ = _get_agent_classes()

        actions = agent_action_types or ["move", "wait", "observe"]
        for i in range(agent_count):
            agent = RandomAgent(agent_id=f"agent_{i}", action_types=actions)
            sim.add_agent(agent)

        result = sim.run()
        return {
            "status": "success",
            "steps_completed": result.steps_completed,
            "agent_count": result.agent_count,
            "config_name": result.config_name,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="simulation",
    description="Get the current status and configuration of a simulation.",
)
def simulation_status(
    name: str = "default",
    max_steps: int = 100,
) -> dict[str, Any]:
    """Get simulation configuration and readiness status.

    Args:
        name: Simulation name.
        max_steps: Configured max steps.

    Returns:
        dict with keys: status, config_name, max_steps, agent_count
    """
    try:
        sim = _get_simulator(name=name, max_steps=max_steps)
        return {
            "status": "success",
            "config_name": sim.config.name,
            "max_steps": sim.config.max_steps,
            "agent_count": len(sim.agents),
            "step_count": sim.step_count,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="simulation",
    description="List available agent types and their descriptions.",
)
def simulation_list_agents() -> dict[str, Any]:
    """List available simulation agent types.

    Returns:
        dict with keys: status, agent_types
    """
    try:
        return {
            "status": "success",
            "agent_types": [
                {
                    "name": "RandomAgent",
                    "description": "Acts randomly from a pool of action types.",
                },
                {
                    "name": "RuleBasedAgent",
                    "description": "Executes prioritized condition-to-action rules.",
                },
                {
                    "name": "QLearningAgent",
                    "description": "Tabular Q-learning with epsilon-greedy exploration.",
                },
            ],
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
