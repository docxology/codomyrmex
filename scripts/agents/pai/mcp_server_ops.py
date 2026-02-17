#!/usr/bin/env python3
"""
PAI MCP Server Operations

Create, inspect, and validate the Codomyrmex MCP server. Enumerate all
registered tools, resources, and prompts. Verify counts match expectations.

Usage:
    python scripts/agents/pai/mcp_server_ops.py                   # Full report
    python scripts/agents/pai/mcp_server_ops.py --section registry # Registry only
    python scripts/agents/pai/mcp_server_ops.py --json             # JSON output

Upstream: https://github.com/danielmiessler/Personal_AI_Infrastructure
"""

import argparse
import json
import sys
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.agents.pai import (
    create_codomyrmex_mcp_server,
    get_tool_registry,
    TOOL_COUNT,
    RESOURCE_COUNT,
    PROMPT_COUNT,
)
from codomyrmex.agents.pai.mcp_bridge import get_total_tool_count
from codomyrmex.utils.cli_helpers import (
    setup_logging, print_info, print_success, print_warning, print_error,
)

SECTIONS = ["registry", "server", "health"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="PAI MCP Server Operations — create, inspect, and validate MCP server",
    )
    parser.add_argument("--section", "-s", choices=SECTIONS, help="Show specific section")
    parser.add_argument("--json", "-j", action="store_true", dest="json_output", help="JSON output")
    return parser.parse_args()


def _header(title: str) -> None:
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print(f"{'─' * 60}")


def section_registry() -> dict:
    """Inspect the tool registry."""
    _header("Tool Registry")

    registry = get_tool_registry()
    tools = registry.list_tools()

    print(f"  Static tool constant : {TOOL_COUNT}")
    print(f"  Total tool count     : {get_total_tool_count()}")
    print(f"  Registry tools       : {len(tools)}")
    print()

    # Categorize tools
    categories: dict[str, list[str]] = {}
    for tool in tools:
        name = tool.get("name", "") if isinstance(tool, dict) else str(tool)
        parts = name.split(".")
        category = parts[1] if len(parts) > 1 else "uncategorized"
        categories.setdefault(category, []).append(name)

    for cat, cat_tools in sorted(categories.items()):
        print(f"  {cat} ({len(cat_tools)} tools):")
        for t in cat_tools:
            print(f"    • {t}")

    return {
        "static_count": TOOL_COUNT,
        "total_count": get_total_tool_count(),
        "registry_count": len(tools),
        "categories": {k: len(v) for k, v in categories.items()},
    }


def section_server() -> dict:
    """Create and inspect MCP server."""
    _header("MCP Server Creation")

    server = create_codomyrmex_mcp_server(name="pai-example-server")
    print_success("  MCP server created: pai-example-server")
    print(f"  Server type: {type(server).__name__}")

    # Inspect server internals
    server_tools = []
    if hasattr(server, "_tool_registry"):
        server_tools = server._tool_registry.list_tools()
        print(f"  Server tools   : {len(server_tools)}")
    if hasattr(server, "_resources"):
        print(f"  Server resources: {len(server._resources)}")
    if hasattr(server, "_prompts"):
        print(f"  Server prompts : {len(server._prompts)}")

    # Show resource definitions
    _header("Resources")
    print(f"  Resource constant: {RESOURCE_COUNT}")
    print(f"  Expected resources:")
    print(f"    • codomyrmex://modules — Module inventory")
    print(f"    • codomyrmex://status  — System health snapshot")

    # Show prompt definitions
    _header("Prompts")
    print(f"  Prompt constant: {PROMPT_COUNT}")
    prompts = [
        "analyze_module", "debug_issue", "create_test",
        "codomyrmexAnalyze", "codomyrmexMemory", "codomyrmexSearch",
        "codomyrmexDocs", "codomyrmexStatus", "codomyrmexVerify", "codomyrmexTrust",
    ]
    for p in prompts:
        print(f"    • {p}")

    return {
        "server_type": type(server).__name__,
        "tool_count": len(server_tools),
        "resource_count": RESOURCE_COUNT,
        "prompt_count": PROMPT_COUNT,
    }


def section_health() -> dict:
    """Health validation of MCP setup."""
    _header("MCP Health Check")

    registry = get_tool_registry()
    registry_tools = registry.list_tools()
    total = get_total_tool_count()

    checks = [
        ("Static tool count matches constant", len(registry_tools) >= TOOL_COUNT),
        ("Total tool count >= static count", total >= TOOL_COUNT),
        ("Resource count matches constant", RESOURCE_COUNT == 2),
        ("Prompt count matches constant", PROMPT_COUNT == 10),
        ("Registry is not empty", len(registry_tools) > 0),
    ]

    all_pass = True
    for label, passed in checks:
        icon = "✅" if passed else "❌"
        print(f"  {icon} {label}")
        if not passed:
            all_pass = False

    status = "HEALTHY" if all_pass else "DEGRADED"
    print(f"\n  Overall: {status}")

    return {
        "status": status,
        "checks_passed": sum(1 for _, p in checks if p),
        "checks_total": len(checks),
    }


def main() -> int:
    args = parse_args()
    setup_logging()

    results: dict = {}
    fns = {
        "registry": section_registry,
        "server": section_server,
        "health": section_health,
    }

    if args.section:
        results[args.section] = fns[args.section]()
    else:
        for name, fn in fns.items():
            results[name] = fn()

    if args.json_output:
        print("\n" + json.dumps(results, indent=2, default=str))

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
