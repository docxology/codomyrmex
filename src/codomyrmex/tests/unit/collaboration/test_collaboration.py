"""Unit tests for collaboration module."""
import pytest

from codomyrmex.collaboration import AgentProxy, SwarmManager, TaskDecomposer


@pytest.mark.unit
def test_swarm_execution():
    """Test mission distribution across a swarm of agents."""
    manager = SwarmManager()
    agent1 = AgentProxy("A1", "Builder")
    agent2 = AgentProxy("A2", "Reviewer")

    manager.add_agent(agent1)
    manager.add_agent(agent2)

    results = manager.execute("Build a feature")

    assert len(results) == 2
    assert "A1" in results
    assert "A2" in results
    assert results["A1"] == "Result from A1"
    assert results["A2"] == "Result from A2"

@pytest.mark.unit
def test_task_decomposition():
    """Test mission splitting."""
    tasks = TaskDecomposer.decompose("Design and Build")
    assert len(tasks) == 2
    assert "Design" in tasks
    assert "Build" in tasks

@pytest.mark.unit
def test_consensus():
    """Test voting logic."""
    manager = SwarmManager()
    manager.add_agent(AgentProxy("A1", "Voter"))
    manager.add_agent(AgentProxy("A2", "Voter"))
    manager.add_agent(AgentProxy("A3", "Voter"))

    # Majority vote
    assert manager.consensus_vote("Upgrade") is True
