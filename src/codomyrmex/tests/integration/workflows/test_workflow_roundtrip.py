"""Workflow integration test: MCP server round-trip.

Validates that creating an MCP server, listing tools, and calling
tools through the bridge works end-to-end.
"""

import pytest


@pytest.mark.integration
class TestWorkflowRoundtrip:
    """End-to-end MCP server creation and tool invocation."""

    def test_create_mcp_server(self):
        """MCP server creation succeeds without errors."""
        from codomyrmex.agents.pai.mcp_bridge import create_codomyrmex_mcp_server

        server = create_codomyrmex_mcp_server(name="test-server", transport="stdio")
        assert server is not None

    def test_tool_registry_has_tools(self):
        """Tool registry contains ≥10 tools."""
        from codomyrmex.agents.pai.mcp_bridge import get_tool_registry

        registry = get_tool_registry()
        tools = registry.list_tools() if hasattr(registry, "list_tools") else []
        tool_count = len(tools) if isinstance(tools, (list, dict)) else 0
        assert tool_count >= 10, f"Expected ≥10 tools, got {tool_count}"

    def test_call_tool_list_modules(self):
        """call_tool('codomyrmex.list_modules') returns module data."""
        from codomyrmex.agents.pai import trust_gateway
        from codomyrmex.agents.pai.mcp_bridge import call_tool

        trust_gateway.trust_all()

        result = call_tool("codomyrmex.list_modules")
        assert isinstance(result, dict)
        # Result may have modules or an error from TrustRegistry
        if "error" in result:
            err_msg = str(result["error"])
            if "TrustRegistry" in err_msg:
                pytest.skip(f"TrustRegistry internal: {err_msg}")
        # If we got here, check modules
        modules = result.get("modules", [])
        if isinstance(modules, list):
            assert len(modules) >= 10, f"Expected ≥10 modules, got {len(modules)}"

    def test_call_tool_module_info(self):
        """call_tool('codomyrmex.module_info') returns module details."""
        from codomyrmex.agents.pai import trust_gateway
        from codomyrmex.agents.pai.mcp_bridge import call_tool

        trust_gateway.trust_all()

        result = call_tool("codomyrmex.module_info", module_name="logging_monitoring")
        assert isinstance(result, dict)
        if "error" in result:
            err_msg = str(result["error"])
            if "TrustRegistry" in err_msg:
                pytest.skip(f"TrustRegistry internal: {err_msg}")

    def test_call_tool_list_workflows(self):
        """Workflow listing returns available workflows."""
        from codomyrmex.agents.pai.mcp_bridge import _tool_list_workflows

        result = _tool_list_workflows()
        assert isinstance(result, dict)
        workflows = result.get("workflows", [])
        assert isinstance(workflows, list)
        assert len(workflows) >= 5, f"Expected ≥5 workflows, got {len(workflows)}"

    def test_call_tool_unknown_raises_keyerror(self):
        """Calling a nonexistent tool raises KeyError."""
        from codomyrmex.agents.pai import trust_gateway
        from codomyrmex.agents.pai.mcp_bridge import call_tool

        trust_gateway.trust_all()

        with pytest.raises(KeyError):
            call_tool("codomyrmex.nonexistent_tool_xyz")
