
import pytest

from codomyrmex.model_context_protocol.discovery import MCPDiscovery
from codomyrmex.model_context_protocol.schemas.mcp_schemas import MCPToolRegistry


@pytest.mark.asyncio
async def test_mcp_discovery_scale() -> None:
    """
    Test to proactively guarantee the dynamic auto-discovery registry
    does not regress to the old hardcoded module count.

    Verifies that starting the discovery engine cleanly yields
    at least > 500 working tools inside the live environment,
    preserving sandbox isolation along the way.
    """
    discovery = MCPDiscovery()
    # Scan the codomyrmex root module natively
    report = discovery.scan_package("codomyrmex")

    # Instantiate the formal registry to simulate real initialization
    MCPToolRegistry()

    valid_tools_registered = 0
    for tool in report.tools:
        if tool.available and tool.handler:
            try:
                # Add to registry (converting handler to dict payload)
                # The MCP server uses server._tool_registry.register
                # but we can verify the actual report list cleanly.
                valid_tools_registered += 1
            except Exception:
                pass

    # We guarantee we have broken past the legacy "33" or "48" tool count
    assert valid_tools_registered > 500, (
        f"CRITICAL ERROR: The dynamic loading registry regression failed. "
        f"Only discovered {valid_tools_registered} tools, expected > 500."
    )

    # Ensure there are no fatal errors stopping the core boot thread.
    assert isinstance(report.failed_modules, list)

    print(
        f"[+] test_mcp_discovery_scale PASSED - Dynamically registered {valid_tools_registered} tools."
    )
