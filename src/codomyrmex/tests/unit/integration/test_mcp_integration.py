"""Integration tests for MCP tool exposure in new modules."""

import pytest
from unittest.mock import MagicMock, patch

from codomyrmex.simulation.simulator import Simulator
from codomyrmex.networks.graph import NetworkGraph
from codomyrmex.model_context_protocol.decorators import mcp_tool

def test_simulator_run_is_mcp_tool():
    """Verify Simulator.run is decorated as an MCP tool."""
    assert hasattr(Simulator.run, "_mcp_tool")
    meta = getattr(Simulator.run, "_mcp_tool")
    assert meta["name"] == "codomyrmex.Simulator.run"
    assert "simulation" in meta["description"].lower()

def test_network_graph_shortest_path_is_mcp_tool():
    """Verify NetworkGraph.shortest_path is decorated as an MCP tool."""
    assert hasattr(NetworkGraph.shortest_path, "_mcp_tool")
    meta = getattr(NetworkGraph.shortest_path, "_mcp_tool")
    assert meta["name"] == "codomyrmex.NetworkGraph.shortest_path"
    assert "shortest path" in meta["description"].lower()

@patch("codomyrmex.agents.pai.trust_gateway.trusted_call_tool")
def test_call_tool_delegates_to_trust_gateway(mock_trusted_call):
    """Verify call_tool delegates to trusted_call_tool."""
    from codomyrmex.agents.pai.mcp_bridge import call_tool
    
    mock_trusted_call.return_value = {"result": "success"}
    
    result = call_tool("some.tool", arg=1)
    
    mock_trusted_call.assert_called_once_with("some.tool", arg=1)
    assert result == {"result": "success"}

def test_dynamic_discovery_finds_new_tools():
    """Verify that dynamic discovery finds the new tools."""
    from codomyrmex.model_context_protocol.discovery import MCPDiscovery
    from codomyrmex.agents.pai.mcp_bridge import invalidate_tool_cache
    
    # Ensure cache is clear
    invalidate_tool_cache()
    
    discovery = MCPDiscovery()
    # Manually trigger scan of relevant modules
    discovery.scan_module("codomyrmex.simulation.simulator")
    discovery.scan_module("codomyrmex.networks.graph")
    
    tools = {t.name for t in discovery.list_tools()}
    
    assert "codomyrmex.Simulator.run" in tools
    assert "codomyrmex.NetworkGraph.shortest_path" in tools
