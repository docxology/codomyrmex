"""Main entry point for the Codomyrmex MCP server.

This module initializes the MCP server and registers all available tools
from the various sub-modules.

Note: Core-layer MCP tool modules (coding, containerization, git_operations,
search) are loaded lazily via importlib to respect the Foundation -> Core
layer boundary.  They are imported at server start-up inside run_server(),
NOT at module import time.
"""

import asyncio
import importlib
import logging

from codomyrmex.logging_monitoring import get_logger

from .server import MCPServer, MCPServerConfig

# ---------------------------------------------------------------------------
# Core-layer modules whose mcp_tools we want to register.
# These are NOT imported at module level -- doing so would violate
# the Foundation -> Core layer boundary. Instead, we use the MCPDiscovery
# engine at runtime to dynamically scan the entire Codomyrmex package.
# ---------------------------------------------------------------------------

logger = get_logger(__name__)


async def run_server() -> None:
    """Run the MCP server."""
    # Configure logging for the MCP server specifically if needed
    logging.basicConfig(level=logging.INFO)

    config = MCPServerConfig(
        name="codomyrmex-mcp",
        version="0.1.2",
    )
    server = MCPServer(config)

    # Lazily scan and load ALL MCP tools across the entire project
    from codomyrmex.model_context_protocol.discovery import MCPDiscovery

    logger.info("Scanning for Codomyrmex MCP Tools...")
    discovery = MCPDiscovery()
    report = discovery.scan_package("codomyrmex")

    for tool in report.tools:
        if tool.available and tool.handler:
            try:
                server._tool_registry.register(
                    tool_name=tool.name,
                    schema=tool.parameters,
                    handler=tool.handler,
                )
                logger.info("Registered tool: %s from %s", tool.name, tool.module_path)
            except Exception as e:
                logger.error("Failed to register tool %s: %s", tool.name, e)

    tool_count = (
        len(server._tool_registry.list_tools())
        if hasattr(server._tool_registry, "list_tools")
        else len(report.tools)
    )
    logger.info(
        "Successfully loaded %d MCP tools (encountered %d isolated module import failures)",
        tool_count,
        len(report.failed_modules),
    )

    await server.run_stdio()


def main() -> None:
    """Synchronous entry point."""
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
