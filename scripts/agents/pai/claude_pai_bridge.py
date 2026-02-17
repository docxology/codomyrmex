#!/usr/bin/env python3
"""
Claude + PAI Bridge Integration Demo

Demonstrate the integration between ClaudeClient/ClaudeIntegrationAdapter
and the PAI bridge: tool registration from MCP definitions, code review
with PAI context, and adapter methods.

Requires: Anthropic API key (graceful degradation without it)

Usage:
    python scripts/agents/pai/claude_pai_bridge.py                  # Full demo
    python scripts/agents/pai/claude_pai_bridge.py --demo register  # Tool registration
    python scripts/agents/pai/claude_pai_bridge.py --json           # JSON output

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
    PAIBridge,
    call_tool,
    get_tool_registry,
    get_skill_manifest,
)
from codomyrmex.utils.cli_helpers import (
    setup_logging, print_info, print_success, print_warning, print_error,
)

DEMOS = ["discover", "register", "manifest", "review"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Claude + PAI Bridge Integration — combined workflow demo",
    )
    parser.add_argument("--demo", "-d", choices=DEMOS, help="Run specific demo")
    parser.add_argument("--json", "-j", action="store_true", dest="json_output", help="JSON output")
    return parser.parse_args()


def _header(title: str) -> None:
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print(f"{'─' * 60}")


def _get_claude_client():
    """Try to create a ClaudeClient, return None if unavailable."""
    try:
        from codomyrmex.agents.claude.claude_client import ClaudeClient
        client = ClaudeClient()
        if client.test_connection():
            return client
        print_warning("  Claude API connection test failed.")
        return None
    except Exception as e:
        print_warning(f"  Claude client unavailable: {e}")
        return None


def demo_discover() -> dict:
    """Show PAI bridge discovery in context of Claude integration."""
    _header("Demo 1: PAI Discovery for Claude Context")

    bridge = PAIBridge()
    installed = bridge.is_installed()
    print(f"  PAI installed: {installed}")

    if installed:
        version = bridge.get_algorithm_version()
        skills = bridge.list_skills()
        tools = bridge.list_tools()
        agents = bridge.list_agents()

        print(f"  Algorithm version: {version}")
        print(f"  Skills: {len(skills)} packs")
        print(f"  Tools: {len(tools)} TypeScript tools")
        print(f"  Agents: {len(agents)} personalities")

        # Show how this context informs Claude
        print(f"\n  Claude integration context:")
        print(f"    Agent personalities available for delegation: {len(agents)}")
        print(f"    Skill packs for capability assessment: {len(skills)}")
        print(f"    Tools for Algorithm phase execution: {len(tools)}")

    return {
        "installed": installed,
        "skills": len(bridge.list_skills()),
        "tools": len(bridge.list_tools()),
        "agents": len(bridge.list_agents()),
    }


def demo_register() -> dict:
    """Demonstrate tool registration from MCP definitions."""
    _header("Demo 2: Tool Registration from MCP")

    # Get tool registry
    registry = get_tool_registry()
    tools = registry.list_tools()
    print(f"  MCP registry has {len(tools)} tools")

    # Show how tools would be registered with Claude
    client = _get_claude_client()
    registered = 0

    sample_tools = tools[:5] if tools else []
    print(f"\n  Registering first {len(sample_tools)} tools with Claude:")

    for tool in sample_tools:
        if isinstance(tool, dict):
            name = tool.get("name", "unknown")
            desc = tool.get("description", "")[:60]
            schema = tool.get("input_schema", {})
        else:
            name = str(tool)
            desc = ""
            schema = {}

        if client:
            try:
                client.register_tool(name=name, description=desc, input_schema=schema)
                print(f"    ✅ {name}")
                registered += 1
            except Exception as e:
                print(f"    ⚠️ {name}: {e}")
        else:
            print(f"    📋 {name}: {desc}")
            registered += 1  # Count as "would register"

    api_available = client is not None
    if not api_available:
        print_info("\n  (Dry run — no API key. Tools listed but not actually registered)")

    return {"tools_available": len(tools), "registered": registered, "api_available": api_available}


def demo_manifest() -> dict:
    """Show skill manifest as Claude system context."""
    _header("Demo 3: Skill Manifest as System Context")

    manifest = get_skill_manifest()

    print(f"  Manifest keys: {list(manifest.keys())}")
    print(f"  Name: {manifest.get('name', 'N/A')}")
    print(f"  Version: {manifest.get('version', 'N/A')}")

    # Show how manifest provides system prompt context
    tools = manifest.get("tools", [])
    resources = manifest.get("resources", [])
    prompts = manifest.get("prompts", [])

    print(f"\n  System context for Claude:")
    print(f"    Available tools: {len(tools)}")
    print(f"    Available resources: {len(resources)}")
    print(f"    Available prompts: {len(prompts)}")

    # Show a sample system prompt fragment
    print(f"\n  Sample system prompt fragment:")
    print(f"    'You have access to {len(tools)} Codomyrmex tools via MCP.'")
    print(f"    'Use codomyrmex.list_modules to discover available modules.'")
    print(f"    'Use codomyrmex.pai_status to check PAI integration status.'")

    return {
        "manifest_keys": list(manifest.keys()),
        "tool_count": len(tools),
        "resource_count": len(resources),
        "prompt_count": len(prompts),
    }


def demo_review() -> dict:
    """Demonstrate code review with PAI context."""
    _header("Demo 4: Code Review with PAI Context")

    # Read PAI bridge source via call_tool
    print_info("  Reading PAI bridge source via call_tool:")
    try:
        result = call_tool("codomyrmex.read_file", path="src/codomyrmex/agents/pai/__init__.py")
        content = result.get("content", "") if isinstance(result, dict) else ""
        lines = content.count("\n") + 1 if content else 0
        print(f"    Read {lines} lines from agents/pai/__init__.py")
    except Exception as e:
        print_warning(f"    Could not read file: {e}")
        content = ""

    # Attempt code review with Claude
    client = _get_claude_client()
    if client and content:
        try:
            review = client.review_code(
                code=content[:2000],
                language="python",
                analysis_type="general",
            )
            print_success("  Claude code review completed:")
            if isinstance(review, dict):
                for key, val in list(review.items())[:5]:
                    print(f"    {key}: {str(val)[:80]}")
            else:
                print(f"    {str(review)[:200]}")
            return {"review": "completed", "lines_reviewed": lines}
        except Exception as e:
            print_warning(f"  Review failed: {e}")
    else:
        print_info("  (Claude API not available — showing what would be reviewed)")
        print(f"    File: agents/pai/__init__.py ({lines} lines)")
        print(f"    Analysis: general code quality review")
        print(f"    Context: PAI bridge public API exports")

    return {"review": "skipped", "lines_available": lines, "api_available": client is not None}


def main() -> int:
    args = parse_args()
    setup_logging()

    print(f"🔗 Claude + PAI Bridge Integration Demo")

    results: dict = {}
    fns = {
        "discover": demo_discover,
        "register": demo_register,
        "manifest": demo_manifest,
        "review": demo_review,
    }

    if args.demo:
        results[args.demo] = fns[args.demo]()
    else:
        for name, fn in fns.items():
            results[name] = fn()

    if args.json_output:
        print("\n" + json.dumps(results, indent=2, default=str))

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
