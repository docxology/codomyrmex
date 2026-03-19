#!/usr/bin/env python3
"""Run the full Codomyrmex PAI MCP bridge over stdio.

Use this as the MCP server command for Cursor (global ``~/.cursor/mcp.json``) or
Claude Desktop. It registers static tools, auto-discovered ``@mcp_tool`` modules,
resources, and prompts — same surface as ``codomyrmex.agents.pai`` bridge docs.

Usage::

    uv run python scripts/model_context_protocol/run_pai_mcp_stdio.py

Run from the **repository root** (or set ``cwd`` in the MCP config to the repo root)
so ``uv`` resolves ``pyproject.toml`` correctly.
"""

from __future__ import annotations

from codomyrmex.agents.pai.mcp.server import create_codomyrmex_mcp_server


def main() -> None:
    server = create_codomyrmex_mcp_server(transport="stdio")
    server.run()


if __name__ == "__main__":
    main()
