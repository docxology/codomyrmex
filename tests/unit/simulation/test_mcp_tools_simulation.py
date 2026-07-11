"""Tests for simulation MCP tools."""

from __future__ import annotations


class TestSimulationRun:
    """Tests for simulation_run MCP tool."""

    def test_run_default(self):
        from codomyrmex.simulation.mcp_tools import simulation_run

        result = simulation_run(name="test_sim", max_steps=10, agent_count=2)
        assert result["status"] == "success"
        assert result["steps_completed"] == 10
        assert result["agent_count"] == 2
        assert result["config_name"] == "test_sim"

    def test_run_custom_actions(self):
        from codomyrmex.simulation.mcp_tools import simulation_run

        result = simulation_run(
            name="custom",
            max_steps=5,
            agent_count=1,
            agent_action_types=["attack", "defend", "heal"],
        )
        assert result["status"] == "success"
        assert result["steps_completed"] == 5

    def test_run_zero_agents(self):
        from codomyrmex.simulation.mcp_tools import simulation_run

        result = simulation_run(max_steps=3, agent_count=0)
        assert result["status"] == "success"
        assert result["agent_count"] == 0
        assert result["steps_completed"] == 3


class TestSimulationStatus:
    """Tests for simulation_status MCP tool."""

    def test_status_default(self):
        from codomyrmex.simulation.mcp_tools import simulation_status

        result = simulation_status(name="status_test", max_steps=50)
        assert result["status"] == "success"
        assert result["config_name"] == "status_test"
        assert result["max_steps"] == 50
        assert result["agent_count"] == 0
        assert result["step_count"] == 0


class TestSimulationListAgents:
    """Tests for simulation_list_agents MCP tool."""

    def test_list_agents(self):
        from codomyrmex.simulation.mcp_tools import simulation_list_agents

        result = simulation_list_agents()
        assert result["status"] == "success"
        agent_names = [a["name"] for a in result["agent_types"]]
        assert "RandomAgent" in agent_names
        assert "RuleBasedAgent" in agent_names
        assert "QLearningAgent" in agent_names
