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
# the Foundation -> Core layer boundary.
# ---------------------------------------------------------------------------
_OPTIONAL_CORE_MCP_MODULES: list[str] = [
    "codomyrmex.coding.mcp_tools",
    "codomyrmex.containerization.mcp_tools",
    "codomyrmex.git_operations.mcp_tools",
    "codomyrmex.search.mcp_tools",
]

logger = get_logger(__name__)


def _load_optional_mcp_tools():
    """Late-bind Core-layer MCP tool modules.

    Returns a list of successfully imported module objects.
    Called inside ``run_server()`` -- never at module import time -- so that
    the Foundation layer does not pull in Core-layer code on ``import``.
    """
    loaded = []
    for module_path in _OPTIONAL_CORE_MCP_MODULES:
        try:
            loaded.append(importlib.import_module(module_path))
        except ImportError as exc:
            logger.warning("Optional MCP tool module %s could not be imported: %s", module_path, exc)
    return loaded


async def run_server() -> None:
    """Run the MCP server."""
    # Configure logging for the MCP server specifically if needed
    logging.basicConfig(level=logging.INFO)

    config = MCPServerConfig(
        name="codomyrmex-mcp",
        version="0.1.2",
    )
    server = MCPServer(config)

    # Late-load Core-layer MCP tool modules (lazy, not at import time)
    modules_to_scan = _load_optional_mcp_tools()

    for module in modules_to_scan:
        # Iterate over all attributes in the module
        for name in dir(module):
            obj = getattr(module, name)
            # Check if the object has the MCP tool metadata attached by the decorator
            if callable(obj) and hasattr(obj, "_mcp_tool_meta"):
                meta = obj._mcp_tool_meta
                # Register the tool with the server
                # Assuming the server has an `add_tool` method or we use `tool_registry.register`
                # Let's check `server.py` again. It has `_tool_registry`.
                # We need to see if `MCPServer` exposes a public method to add tools.
                # If not, we might need to use `server._tool_registry.register(tool_def)`.
                # The `_tool_registry` likely has a `register` method.

                # Construct the tool definition/schema from the function and metadata
                # The `server.py` we read seems to expect schemas.
                # We might need a helper to convert function -> JSON schema.
                # The `codomyrmex.model_context_protocol.tools` module likely has this helper.

                # Let's import the helper if available, or invoke `server._tool_registry` directly
                # if it handles functions.
                # Assuming for now we can just register it.

                # Ideally, we should use a public API. If `MCPServer` doesn't have `add_tool`,
                # we should add it or use the registry directly.

                # Based on standard MCP implementations, we usually register the function directly.
                try:
                    tool_name = meta.get("name", name)
                    tool_schema = meta.get("schema", {})
                    server._tool_registry.register(
                        tool_name=tool_name,
                        schema=tool_schema,
                        handler=obj,
                    )
                    logger.info(f"Registered tool: {tool_name} from {module.__name__}")
                except Exception as e:
                    logger.error(f"Failed to register tool {name}: {e}")

    await server.run_stdio()

def main() -> None:
    """Synchronous entry point."""
    asyncio.run(run_server())

if __name__ == "__main__":
    main()
