"""Simulation module for Codomyrmex.

This module provides the core simulation capabilities, allowing for
agent-based modeling and system dynamics simulations.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from codomyrmex.logging_monitoring.core.logger_config import get_logger
from codomyrmex.simulation.agent import Agent, Action
from codomyrmex.model_context_protocol.decorators import mcp_tool

logger = get_logger(__name__)


@dataclass
class SimulationConfig:
    """Configuration for a simulation run."""
    name: str = "default_simulation"
    max_steps: int = 1000
    seed: int | None = None
    params: dict[str, Any] = field(default_factory=dict)


@dataclass
class SimulationResult:
    """Results from a simulation run."""
    steps_completed: int
    config_name: str
    status: str
    agent_count: int
    history: List[Dict[str, Any]] = field(default_factory=list)


class Simulator:
    """Core simulator engine."""

    def __init__(self, config: SimulationConfig | None = None, agents: List[Agent] | None = None):
        """Initialize the simulator.

        Args:
            config: Configuration for the simulation.
            agents: Initial list of agents.
        """
        self.config = config or SimulationConfig()
        self.agents: Dict[str, Agent] = {a.id: a for a in agents or []}
        self.step_count = 0
        self._running = False
        self._environment_state: Dict[str, Any] = {}
        logger.info(f"Simulator initialized: {self.config.name} with {len(self.agents)} agents")

    def add_agent(self, agent: Agent) -> None:
        """Add an agent to the simulation."""
        if agent.id in self.agents:
            raise ValueError(f"Agent with ID {agent.id} already exists")
        self.agents[agent.id] = agent
        logger.debug(f"Added agent {agent.id}")

    def remove_agent(self, agent_id: str) -> None:
        """Remove an agent from the simulation."""
        if agent_id in self.agents:
            del self.agents[agent_id]
            logger.debug(f"Removed agent {agent_id}")

    @mcp_tool(name="Simulator.run", description="Run the simulation loop")
    def run(self) -> SimulationResult:
        """Run the simulation until completion or max steps."""
        self._running = True
        self.step_count = 0
        logger.info("Starting simulation run")

        try:
            while self._running and self.step_count < self.config.max_steps:
                self.step()
                self.step_count += 1
        except Exception as e:
            logger.error(f"Simulation failed at step {self.step_count}: {e}")
            raise
        finally:
            self._running = False

        logger.info(f"Simulation completed after {self.step_count} steps")
        return self.get_results()

    def step(self) -> None:
        """Execute a single simulation step."""
        # 1. Agents act
        actions = []
        for agent in self.agents.values():
            try:
                # Provide strict observation of environment
                observation = self._get_observation(agent)
                action = agent.act(observation)
                agent.record_action(action)
                actions.append((agent.id, action))
            except Exception as e:
                logger.error(f"Agent {agent.id} failed to act: {e}")

        # 2. Environment updates based on actions
        self._update_environment(actions)

        # 3. Agents learn (optional)
        for agent in self.agents.values():
            try:
                reward = self._calculate_reward(agent)
                agent.learn(reward)
            except Exception as e:
                logger.error(f"Agent {agent.id} failed to learn: {e}")

    def _get_observation(self, agent: Agent) -> Dict[str, Any]:
        """Get observation for a specific agent."""
        return self._environment_state.copy()

    def _update_environment(self, actions: List[tuple[str, Action]]) -> None:
        """Update environment state based on agent actions."""
        for agent_id, action in actions:
            # Simple default logic: record action in environment state
            self._environment_state[f"last_action_{agent_id}"] = action.type

    def _calculate_reward(self, agent: Agent) -> float:
        """Calculate reward for an agent."""
        return 0.0

    def get_results(self) -> SimulationResult:
        """Return results from the simulation."""
        return SimulationResult(
            steps_completed=self.step_count,
            config_name=self.config.name,
            status="completed" if not self._running else "running",
            agent_count=len(self.agents),
            history=[{"step": self.step_count, "env": self._environment_state.copy()}]
        )
