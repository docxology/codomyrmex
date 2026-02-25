"""Integration tests for MCP tool exposure in new modules."""


from codomyrmex.networks.graph import NetworkGraph
from codomyrmex.simulation.simulator import Simulator


def test_simulator_run_is_mcp_tool():
    """Verify Simulator.run is decorated as an MCP tool."""
    assert hasattr(Simulator.run, "_mcp_tool")
    meta = Simulator.run._mcp_tool
    assert meta["name"] == "codomyrmex.Simulator.run"
    assert "simulation" in meta["description"].lower()

def test_network_graph_shortest_path_is_mcp_tool():
    """Verify NetworkGraph.shortest_path is decorated as an MCP tool."""
    assert hasattr(NetworkGraph.shortest_path, "_mcp_tool")
    meta = NetworkGraph.shortest_path._mcp_tool
    assert meta["name"] == "codomyrmex.NetworkGraph.shortest_path"
    assert "shortest path" in meta["description"].lower()

def test_call_tool_delegates_to_trust_gateway():
    """Verify call_tool returns a result dict (delegates to trust gateway end-to-end)."""
    from codomyrmex.agents.pai.mcp_bridge import call_tool
    from codomyrmex.agents.pai.trust_gateway import trust_all
    trust_all()
    result = call_tool("codomyrmex.list_modules")
    assert isinstance(result, dict)
    assert "modules" in result

def test_dynamic_discovery_finds_new_tools():
    """Verify that dynamic discovery finds the new tools."""
    from codomyrmex.agents.pai.mcp_bridge import invalidate_tool_cache
    from codomyrmex.model_context_protocol.discovery import MCPDiscovery

    # Ensure cache is clear
    invalidate_tool_cache()

    discovery = MCPDiscovery()
    # Manually trigger scan of relevant modules
    discovery.scan_module("codomyrmex.simulation.simulator")
    discovery.scan_module("codomyrmex.networks.graph")

    tools = {t.name for t in discovery.list_tools()}

    assert "codomyrmex.Simulator.run" in tools
    assert "codomyrmex.NetworkGraph.shortest_path" in tools
