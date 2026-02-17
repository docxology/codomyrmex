#!/usr/bin/env python3
"""
PAI Skill Manifest Inspector

Generate and deeply inspect the PAI skill manifest. Show algorithm-to-tool
mapping, knowledge scope breakdown, and validate manifest structure.

Usage:
    python scripts/agents/pai/skill_manifest.py                    # Full report
    python scripts/agents/pai/skill_manifest.py --section mapping  # Algorithm mapping
    python scripts/agents/pai/skill_manifest.py --json             # JSON output

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
    get_skill_manifest,
    get_tool_registry,
    PAIBridge,
    ALGORITHM_PHASES,
    TOOL_COUNT,
    RESOURCE_COUNT,
    PROMPT_COUNT,
)
from codomyrmex.utils.cli_helpers import (
    setup_logging, print_info, print_success, print_warning,
)

SECTIONS = ["overview", "tools", "mapping", "scope", "workflows"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="PAI Skill Manifest Inspector — generate and inspect the manifest",
    )
    parser.add_argument("--section", "-s", choices=SECTIONS, help="Show specific section")
    parser.add_argument("--json", "-j", action="store_true", dest="json_output", help="JSON output")
    return parser.parse_args()


def _header(title: str) -> None:
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print(f"{'─' * 60}")


def section_overview(manifest: dict) -> dict:
    """Manifest overview."""
    _header("Skill Manifest Overview")

    name = manifest.get("name", "N/A")
    version = manifest.get("version", "N/A")
    description = manifest.get("description", "N/A")
    upstream = manifest.get("upstream", "N/A")

    print(f"  Name        : {name}")
    print(f"  Version     : {version}")
    print(f"  Description : {description}")
    print(f"  Upstream    : {upstream}")

    tools = manifest.get("tools", [])
    resources = manifest.get("resources", [])
    prompts = manifest.get("prompts", [])

    print(f"\n  Manifest contents:")
    print(f"    Tools     : {len(tools)} (constant: {TOOL_COUNT})")
    print(f"    Resources : {len(resources)} (constant: {RESOURCE_COUNT})")
    print(f"    Prompts   : {len(prompts)} (constant: {PROMPT_COUNT})")

    return {
        "name": name,
        "version": version,
        "tool_count": len(tools),
        "resource_count": len(resources),
        "prompt_count": len(prompts),
    }


def section_tools(manifest: dict) -> dict:
    """Tool breakdown by category."""
    _header("Tool Inventory")

    tools = manifest.get("tools", [])
    if not tools:
        print_warning("  No tools in manifest.")
        return {"tools": []}

    categories: dict[str, list] = {}
    for tool in tools:
        name = tool.get("name", str(tool)) if isinstance(tool, dict) else str(tool)
        cat = tool.get("category", "uncategorized") if isinstance(tool, dict) else "uncategorized"
        categories.setdefault(cat, []).append(name)

    for cat, cat_tools in sorted(categories.items()):
        print(f"\n  {cat} ({len(cat_tools)}):")
        for t in cat_tools:
            print(f"    • {t}")

    return {"categories": {k: len(v) for k, v in categories.items()}, "total": len(tools)}


def section_mapping(manifest: dict) -> dict:
    """Algorithm-to-tool mapping."""
    _header("Algorithm → Tool Mapping")

    mapping = manifest.get("algorithm_mapping", {})
    if not mapping:
        # Build from ALGORITHM_PHASES constant
        print_info("  No algorithm_mapping in manifest. Showing phase reference:")
        for phase in ALGORITHM_PHASES:
            print(f"    {phase['phase']}  {phase['name']:10s}  {phase['description']}")
        return {"phases": len(ALGORITHM_PHASES), "from_manifest": False}

    for phase_name, phase_tools in mapping.items():
        tool_list = phase_tools if isinstance(phase_tools, list) else [phase_tools]
        print(f"\n  {phase_name} ({len(tool_list)} tools):")
        for t in tool_list:
            print(f"    • {t}")

    return {"phases": len(mapping), "from_manifest": True, "mapping": mapping}


def section_scope(manifest: dict) -> dict:
    """Knowledge scope breakdown."""
    _header("Knowledge Scope")

    scope = manifest.get("knowledge_scope", {})
    if not scope:
        # Show skills as proxy
        bridge = PAIBridge()
        skills = bridge.list_skills()
        print_info(f"  No knowledge_scope in manifest. Showing {len(skills)} skill packs:")
        for sk in skills:
            tools_icon = "🔧" if sk.has_tools else "  "
            print(f"    {tools_icon} {sk.name:30s}  {sk.file_count} files")
        return {"skill_count": len(skills), "from_manifest": False}

    total_modules = 0
    for domain, modules in scope.items():
        module_list = modules if isinstance(modules, list) else [modules]
        total_modules += len(module_list)
        print(f"\n  {domain} ({len(module_list)} modules):")
        for m in module_list[:8]:
            print(f"    • {m}")
        if len(module_list) > 8:
            print(f"    ... and {len(module_list) - 8} more")

    print(f"\n  Total: {total_modules} modules across {len(scope)} domains")
    return {"domains": len(scope), "total_modules": total_modules, "from_manifest": True}


def section_workflows(manifest: dict) -> dict:
    """Workflow definitions."""
    _header("Workflows")

    workflows = manifest.get("workflows", [])
    if not workflows:
        print_info("  No workflows in manifest. Expected:")
        expected = ["codomyrmexVerify", "codomyrmexTrust"]
        for w in expected:
            print(f"    • {w}")
        return {"workflows": expected, "from_manifest": False}

    for wf in workflows:
        if isinstance(wf, dict):
            name = wf.get("name", "unnamed")
            desc = wf.get("description", "")
            steps = wf.get("steps", [])
            print(f"\n  {name}: {desc}")
            for i, step in enumerate(steps, 1):
                print(f"    {i}. {step}")
        else:
            print(f"  • {wf}")

    return {"workflow_count": len(workflows), "from_manifest": True}


def main() -> int:
    args = parse_args()
    setup_logging()

    manifest = get_skill_manifest()
    print_success(f"Skill manifest generated ({len(manifest)} top-level keys)")

    results: dict = {}
    fns = {
        "overview": lambda: section_overview(manifest),
        "tools": lambda: section_tools(manifest),
        "mapping": lambda: section_mapping(manifest),
        "scope": lambda: section_scope(manifest),
        "workflows": lambda: section_workflows(manifest),
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
