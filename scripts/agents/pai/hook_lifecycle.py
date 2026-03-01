#!/usr/bin/env python3
"""
PAI Hook Lifecycle Explorer

Deep exploration of the PAI hook system: enumerate all hooks, separate active
from archived, analyze hook naming patterns, and cross-reference with
Algorithm phases.

Usage:
    python scripts/agents/pai/hook_lifecycle.py                    # Full report
    python scripts/agents/pai/hook_lifecycle.py --hook SessionStart # Single hook
    python scripts/agents/pai/hook_lifecycle.py --active-only       # Active only
    python scripts/agents/pai/hook_lifecycle.py --json              # JSON output

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

from codomyrmex.agents.pai import PAIBridge
from codomyrmex.utils.cli_helpers import (
    setup_logging, print_info, print_warning,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="PAI Hook Lifecycle Explorer — enumerate and analyze lifecycle hooks",
    )
    parser.add_argument("--hook", help="Inspect a specific hook by name")
    parser.add_argument("--active-only", action="store_true", help="Show only active hooks")
    parser.add_argument("--json", "-j", action="store_true", dest="json_output", help="JSON output")
    return parser.parse_args()


def _header(title: str) -> None:
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print(f"{'─' * 60}")


def overview(bridge: PAIBridge, active_only: bool = False) -> dict:
    """List all hooks with active/archived status."""
    all_hooks = bridge.list_hooks()
    active_hooks = bridge.list_active_hooks()
    archived = [h for h in all_hooks if h.is_archived]

    display = active_hooks if active_only else all_hooks
    label = "Active Hooks" if active_only else "All Hooks"
    _header(f"{label} ({len(display)} total)")

    if not display:
        print_warning("  No hooks found.")
        return {"hooks": [], "active": 0, "archived": 0}

    for h in sorted(display, key=lambda x: x.name):
        status = "📦 archived" if h.is_archived else "✅ active  "
        print(f"  {status}  {h.name:35s}  {h.size_bytes:>6,} bytes")

    print(f"\n  Active: {len(active_hooks)} | Archived: {len(archived)} | Total: {len(all_hooks)}")
    ratio = len(active_hooks) / len(all_hooks) * 100 if all_hooks else 0
    print(f"  Active ratio: {ratio:.0f}%")

    return {
        "hooks": [h.__dict__ for h in display],
        "active_count": len(active_hooks),
        "archived_count": len(archived),
        "total": len(all_hooks),
    }


def inspect_hook(bridge: PAIBridge, name: str) -> dict:
    """Inspect a single hook in detail."""
    info = bridge.get_hook_info(name)
    _header(f"Hook Detail: {name}")

    if info is None:
        print_warning(f"  Hook '{name}' not found.")
        available = [h.name for h in bridge.list_hooks()[:10]]
        if available:
            print_info(f"  Available hooks: {', '.join(available)}")
        return {"found": False, "name": name}

    print(f"  Name     : {info.name}")
    print(f"  Path     : {info.path}")
    print(f"  Size     : {info.size_bytes:,} bytes")
    print(f"  Archived : {info.is_archived}")

    # Read first 10 lines for event pattern preview
    hook_path = Path(info.path)
    if hook_path.exists():
        lines = hook_path.read_text().splitlines()[:10]
        print(f"\n  Preview ({len(lines)} lines):")
        for line in lines:
            print(f"    {line}")

    return {"found": True, **info.__dict__}


def lifecycle_analysis(bridge: PAIBridge) -> dict:
    """Classify hooks by lifecycle event type."""
    _header("Lifecycle Event Analysis")

    active = bridge.list_active_hooks()
    categories: dict[str, list[str]] = {
        "session": [],
        "tool": [],
        "task": [],
        "prompt": [],
        "other": [],
    }

    for h in active:
        name_lower = h.name.lower()
        if "session" in name_lower:
            categories["session"].append(h.name)
        elif "tool" in name_lower or "pretool" in name_lower or "posttool" in name_lower:
            categories["tool"].append(h.name)
        elif "task" in name_lower:
            categories["task"].append(h.name)
        elif "prompt" in name_lower or "submit" in name_lower:
            categories["prompt"].append(h.name)
        else:
            categories["other"].append(h.name)

    for cat, hooks in categories.items():
        print(f"\n  {cat.upper()} hooks ({len(hooks)}):")
        if hooks:
            for h in hooks:
                print(f"    • {h}")
        else:
            print(f"    (none)")

    # Map to Algorithm phases
    phase_mapping = {
        "session": "OBSERVE (1/7) — session initialization",
        "tool": "EXECUTE (5/7) — tool invocation events",
        "task": "VERIFY (6/7) — task completion events",
        "prompt": "OBSERVE (1/7) — user prompt processing",
    }

    print(f"\n  Hook → Algorithm Phase Mapping:")
    for cat, phase in phase_mapping.items():
        has = "✅" if categories[cat] else "❌"
        print(f"    {has} {cat:10s} → {phase}")

    return {"categories": {k: len(v) for k, v in categories.items()}}


def main() -> int:
    args = parse_args()
    setup_logging()

    bridge = PAIBridge()
    if not bridge.is_installed():
        print_warning("PAI is not installed. Showing empty results.")

    results: dict = {}

    if args.hook:
        results["detail"] = inspect_hook(bridge, args.hook)
    else:
        results["overview"] = overview(bridge, active_only=args.active_only)
        results["lifecycle"] = lifecycle_analysis(bridge)

    if args.json_output:
        print("\n" + json.dumps(results, indent=2, default=str))

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
