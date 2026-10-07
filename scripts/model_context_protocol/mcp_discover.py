#!/usr/bin/env python3
"""
MCP Tool Discovery CLI

Discovers and catalogs MCP tools across the codebase by scanning each
``mcp_tools`` module for ``@mcp_tool`` definitions with ``MCPDiscovery``.

Usage:
    python mcp_discover.py                    # Discover all tools
    python mcp_discover.py --module llm       # Discover in specific module
    python mcp_discover.py --export tools.json # Export to JSON
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import json

from codomyrmex.model_context_protocol.discovery import MCPDiscovery
from codomyrmex.utils.cli_helpers import (
    print_info,
    print_success,
    print_warning,
    setup_logging,
)

_IGNORED_PARTS = {"__pycache__", "tests", "vendor"}


def find_spec_files(base_path: Path) -> list:
    """Find all MCP_TOOL_SPECIFICATION.md files."""
    return list(base_path.rglob("MCP_TOOL_SPECIFICATION.md"))


def find_mcp_tool_modules(base_path: Path, module: str | None = None) -> list[str]:
    """Return dotted names of ``mcp_tools`` modules under src/codomyrmex."""
    package_root = base_path / "src" / "codomyrmex"
    search_root = package_root / module if module else package_root
    modules = []
    for path in search_root.rglob("mcp_tools.py"):
        parts = path.relative_to(package_root).with_suffix("").parts
        if _IGNORED_PARTS.isdisjoint(parts):
            modules.append("codomyrmex." + ".".join(parts))
    return sorted(modules)


def discover_all_tools(base_path: Path, module: str | None = None) -> MCPDiscovery:
    """Discover all ``@mcp_tool`` tools (optionally within one module)."""
    discovery = MCPDiscovery()
    failed = []
    for module_name in find_mcp_tool_modules(base_path, module):
        failed.extend(discovery.scan_module(module_name).failed_modules)
    for failure in failed:
        print_warning(f"Could not scan {failure.module}: {failure.error}")
    return discovery


def _source(module_path: str) -> str:
    """Top-level codomyrmex module that defines a tool."""
    parts = module_path.split(".")
    return parts[1] if len(parts) > 1 else module_path


def print_catalog(discovery: MCPDiscovery) -> None:
    """Print discovered tools in readable format."""
    tools = discovery.list_tools()

    print_info(f"Discovered {len(tools)} MCP tools")

    # Group by source module
    by_source = {}
    for tool in tools:
        by_source.setdefault(_source(tool.module_path), []).append(tool)

    for source, source_tools in sorted(by_source.items()):
        print(f"📂 {source.upper()} ({len(source_tools)} tools)")
        for tool in sorted(source_tools, key=lambda t: t.name):
            print(f"   • {tool.name}")
            if tool.description:
                print(f"     {tool.description[:60]}...")
        print()


def main() -> int:
    setup_logging()
    parser = argparse.ArgumentParser(
        description="MCP Tool Discovery",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--module", "-m", help="Specific module to scan")
    parser.add_argument("--export", "-e", help="Export catalog to JSON file")
    parser.add_argument(
        "--list-specs",
        action="store_true",
        help="List all MCP_TOOL_SPECIFICATION.md files",
    )

    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent.parent

    if args.list_specs:
        print_info("MCP Tool Specification Files")
        for spec in find_spec_files(project_root / "src"):
            rel_path = spec.relative_to(project_root)
            print(f"   {rel_path}")
        return 0

    # Discover tools
    discovery = discover_all_tools(project_root, args.module)

    if args.export:
        output_path = Path(args.export)
        schemas = [tool.to_mcp_schema() for tool in discovery.list_tools()]
        output_path.write_text(json.dumps(schemas, indent=2, default=str))
        print_success(f"Exported {len(schemas)} tools to {args.export}")
    else:
        print_catalog(discovery)

    return 0


if __name__ == "__main__":
    sys.exit(main())
