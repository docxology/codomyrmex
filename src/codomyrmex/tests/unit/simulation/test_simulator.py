"""Unit tests for the simulation module."""

import pytest
from unittest.mock import MagicMock
from codomyrmex.simulation.agent import Agent, Action
from codomyrmex.simulation.simulator import Simulator, SimulationConfig


class MockAgent(Agent):
    """A simple mock agent for testing."""
    def act(self, observation):
        return Action(type="move", parameters={"x": 1, "y": 1})

    def learn(self, reward):
        pass


def test_agent_initialization():
    """Test standard agent initialization."""
    agent = MockAgent(agent_id="agent_1", name="Test Agent")
    assert agent.id == "agent_1"
    assert agent.name == "Test Agent"
    assert agent.step_count == 0
    assert len(agent._history) == 0


def test_simulator_initialization():
    """Test simulator initialization."""
    config = SimulationConfig(max_steps=10)
    agent = MockAgent("agent_1")
    sim = Simulator(config, agents=[agent])

    assert sim.config.max_steps == 10
    assert "agent_1" in sim.agents
    assert sim.step_count == 0


def test_simulator_add_remove_agent():
    """Test adding and removing agents."""
    sim = Simulator()
    agent = MockAgent("agent_1")

    sim.add_agent(agent)
    assert "agent_1" in sim.agents

    with pytest.raises(ValueError):
        sim.add_agent(agent)  # Duplicate ID

    sim.remove_agent("agent_1")
    assert "agent_1" not in sim.agents


def test_simulator_run():
    """Test running the simulation loop."""
    config = SimulationConfig(max_steps=5)
    agent = MockAgent("agent_1")
    sim = Simulator(config, agents=[agent])

    result = sim.run()

    assert result.steps_completed == 5
    assert result.status == "completed"
    assert result.agent_count == 1
    assert agent.step_count == 5
    assert len(agent._history) == 5
    assert agent._history[-1].type == "move"
