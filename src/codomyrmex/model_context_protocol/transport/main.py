"""Main entry point for the Codomyrmex MCP server.

This module initializes the MCP server and registers all available tools
from the various sub-modules.

Note: Core-layer MCP tool modules (coding, containerization, git_operations,
search) are loaded lazily via importlib to respect the Foundation -> Core
layer boundary.  They are imported at server start-up inside run_server(),
NOT at module import time.
"""

import asyncio
import logging

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


async def run_server() -> None:
    """Run the authorization-aware Codomyrmex MCP server over stdio.

    There is one production registration path.  Delegating to the PAI bridge
    keeps dynamic discovery, trust enforcement, audit logging, and static vs.
    dynamic collision policy identical for the CLI and Python entrypoints.
    """
    # Configure logging for the MCP server specifically if needed
    logging.basicConfig(level=logging.INFO)

    import importlib

    pai_mcp_bridge = importlib.import_module("codomyrmex.agents.pai.mcp_bridge")
    create_codomyrmex_mcp_server = pai_mcp_bridge.create_codomyrmex_mcp_server

    server = create_codomyrmex_mcp_server(
        name="codomyrmex-mcp",
        transport="stdio",
    )
    logger.info("Authorization-aware MCP server ready with %d tools", server.tool_count)

    await server.run_stdio()


def main() -> None:
    """Synchronous entry point."""
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
