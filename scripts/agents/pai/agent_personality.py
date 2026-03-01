#!/usr/bin/env python3
"""
PAI Agent Personality Explorer

Deep dive into the PAI agent personality system: enumerate all agents,
cross-reference with skill packs, and inspect personality file metadata.

Usage:
    python scripts/agents/pai/agent_personality.py              # Full report
    python scripts/agents/pai/agent_personality.py --agent Remy  # Single agent
    python scripts/agents/pai/agent_personality.py --json        # JSON output

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

from codomyrmex.agents.pai import PAIBridge, PAIConfig
from codomyrmex.utils.cli_helpers import (
    setup_logging, print_info, print_warning,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="PAI Agent Personality Explorer — enumerate and inspect agent definitions",
    )
    parser.add_argument("--agent", "-a", help="Inspect a specific agent by name")
    parser.add_argument("--json", "-j", action="store_true", dest="json_output", help="JSON output")
    return parser.parse_args()


def _header(title: str) -> None:
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print(f"{'─' * 60}")


def enumerate_agents(bridge: PAIBridge) -> dict:
    """List all agent personalities with metadata."""
    agents = bridge.list_agents()
    _header(f"Agent Personalities ({len(agents)} total)")

    if not agents:
        print_warning("  No agent personalities found.")
        return {"agents": [], "count": 0}

    agents_sorted = sorted(agents, key=lambda a: a.size_bytes, reverse=True)
    total_bytes = sum(a.size_bytes for a in agents_sorted)

    for a in agents_sorted:
        pct = (a.size_bytes / total_bytes * 100) if total_bytes > 0 else 0
        print(f"  {a.name:30s}  {a.size_bytes:>8,} bytes  ({pct:4.1f}%)")

    print(f"\n  Total: {len(agents)} agents, {total_bytes:,} bytes")
    return {"agents": [a.__dict__ for a in agents_sorted], "count": len(agents), "total_bytes": total_bytes}


def inspect_agent(bridge: PAIBridge, name: str) -> dict:
    """Inspect a single agent personality in detail."""
    info = bridge.get_agent_info(name)
    _header(f"Agent Detail: {name}")

    if info is None:
        print_warning(f"  Agent '{name}' not found.")
        available = [a.name for a in bridge.list_agents()]
        if available:
            print_info(f"  Available agents: {', '.join(available[:10])}")
        return {"found": False, "name": name}

    print(f"  Name      : {info.name}")
    print(f"  Path      : {info.path}")
    print(f"  Size      : {info.size_bytes:,} bytes")

    # Read first 15 lines for personality preview
    agent_path = Path(info.path)
    if agent_path.exists():
        lines = agent_path.read_text().splitlines()[:15]
        print(f"\n  Preview ({min(15, len(lines))} lines):")
        for line in lines:
            print(f"    {line}")

    return {"found": True, **info.__dict__}


def cross_reference(bridge: PAIBridge) -> dict:
    """Cross-reference agents with skill packs."""
    _header("Agent-Skill Cross Reference")

    agents = bridge.list_agents()
    skills = bridge.list_skills()

    agent_skill = bridge.get_skill_info("Agents")
    if agent_skill:
        print(f"  Agents skill pack: {agent_skill.name}")
        print(f"    Has tools    : {agent_skill.has_tools}")
        print(f"    Has workflows: {agent_skill.has_workflows}")
        print(f"    File count   : {agent_skill.file_count}")
    else:
        print_info("  No 'Agents' skill pack found.")

    # Check PAIAGENTSYSTEM.md
    config = PAIConfig()
    agents_md = config.agents_md
    has_system_doc = agents_md.exists()
    print(f"\n  PAIAGENTSYSTEM.md exists: {'✅' if has_system_doc else '❌'}")
    print(f"  Agent count        : {len(agents)}")
    print(f"  Skill pack count   : {len(skills)}")

    return {
        "agent_count": len(agents),
        "skill_count": len(skills),
        "has_agents_skill": agent_skill is not None,
        "has_system_doc": has_system_doc,
    }


def main() -> int:
    args = parse_args()
    setup_logging()

    bridge = PAIBridge()
    if not bridge.is_installed():
        print_warning("PAI is not installed. Showing empty results.")

    results: dict = {}

    if args.agent:
        results["detail"] = inspect_agent(bridge, args.agent)
    else:
        results["agents"] = enumerate_agents(bridge)
        results["cross_reference"] = cross_reference(bridge)

    if args.json_output:
        print("\n" + json.dumps(results, indent=2, default=str))

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
