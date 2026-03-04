import pytest
from codomyrmex.collaboration.mcp_tools import swarm_submit_task, pool_status, list_agents

@pytest.mark.unit
def test_swarm_submit_task():
    result = swarm_submit_task(
        mission="Build a web app and test it",
        agents=[{"name": "Alice", "role": "coder"}, {"name": "Bob", "role": "tester"}]
    )
    assert result["mission"] == "Build a web app and test it"
    assert "agent_count" in result
    assert result["agent_count"] == 2
    assert "results" in result
    assert "subtasks" in result

@pytest.mark.unit
def test_swarm_submit_task_no_agents():
    result = swarm_submit_task(mission="Do something")
    assert result["mission"] == "Do something"
    assert result["agent_count"] == 1

@pytest.mark.unit
def test_pool_status():
    status = pool_status()
    assert "pool" in status
    assert status["pool"]["status"] == "ready"
    assert "enums" in status
    assert "task_priorities" in status["enums"]
    assert "task_statuses" in status["enums"]

@pytest.mark.unit
def test_list_agents():
    agents = list_agents()
    assert "agent_classes" in agents
    assert "BaseAgent" in agents["agent_classes"]
    assert "protocols" in agents
    assert "round_robin" in agents["protocols"]
    assert "coordinator" in agents
    assert "decomposer" in agents
