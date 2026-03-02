#!/usr/bin/env python3
"""
MCP Tool Discovery CLI

Discovers and catalogs MCP tools across the codebase.

Usage:
    python mcp_discover.py                    # Discover all tools
    python mcp_discover.py --module llm       # Discover in specific module
    python mcp_discover.py --export tools.json # Export to JSON
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse

from codomyrmex.model_context_protocol.discovery import (
    SpecificationScanner,
    ToolCatalog,
)
from codomyrmex.utils.cli_helpers import setup_logging, print_info, print_success


def find_spec_files(base_path: Path) -> list:
    """Find all MCP_TOOL_SPECIFICATION.md files."""
    return list(base_path.rglob("MCP_TOOL_SPECIFICATION.md"))


def discover_all_tools(base_path: Path, module: str = None) -> ToolCatalog:
    """Discover all tools from specs and modules."""
    catalog = ToolCatalog()
    
    # Find and parse spec files
    spec_scanner = SpecificationScanner()
    
    if module:
        spec_path = base_path / "src" / "codomyrmex" / module / "MCP_TOOL_SPECIFICATION.md"
        if spec_path.exists():
            for tool in spec_scanner.scan_spec_file(spec_path):
                catalog.add(tool)
    else:
        for spec_file in find_spec_files(base_path / "src"):
            for tool in spec_scanner.scan_spec_file(spec_file):
                catalog.add(tool)
    
    return catalog


def print_catalog(catalog: ToolCatalog) -> None:
    """Print catalog in readable format."""
    tools = catalog.list_all()
    
    print_info(f"Discovered {len(tools)} MCP tools")
    
    # Group by source
    by_source = {}
    for tool in tools:
        if tool.source not in by_source:
            by_source[tool.source] = []
        by_source[tool.source].append(tool)
    
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
    
    parser.add_argument(
        "--module", "-m",
        help="Specific module to scan"
    )
    parser.add_argument(
        "--export", "-e",
        help="Export catalog to JSON file"
    )
    parser.add_argument(
        "--specs-only",
        action="store_true",
        help="Only scan specification files"
    )
    parser.add_argument(
        "--list-specs",
        action="store_true",
        help="List all MCP_TOOL_SPECIFICATION.md files"
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
    catalog = discover_all_tools(project_root, args.module)
    
    if args.export:
        output_path = Path(args.export)
        output_path.write_text(catalog.to_json())
        print_success(f"Exported {len(catalog.list_all())} tools to {args.export}")
    else:
        print_catalog(catalog)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
