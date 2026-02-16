#!/usr/bin/env python3
"""
PAI Bridge — Example Script

Demonstrates all Personal AI Infrastructure operations available
through the codomyrmex PAI bridge.

Usage:
    python scripts/agents/pai_example.py                    # Full report
    python scripts/agents/pai_example.py --subsystem skills  # Single subsystem
    python scripts/agents/pai_example.py --json              # JSON output
    python scripts/agents/pai_example.py --help

Upstream: https://github.com/danielmiessler/Personal_AI_Infrastructure
"""

import argparse
import json
import sys
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.agents.pai import (
    PAIBridge,
    ALGORITHM_PHASES,
    PAI_PRINCIPLES,
    RESPONSE_DEPTH_LEVELS,
    PAI_UPSTREAM_URL,
)

SUBSYSTEMS = [
    "discovery", "algorithm", "skills", "tools", "hooks",
    "agents", "memory", "security", "telos", "settings", "mcp",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="PAI Bridge example — demonstrate all PAI operations",
    )
    parser.add_argument(
        "--subsystem", "-s",
        choices=SUBSYSTEMS,
        help="Show only a specific subsystem (default: all)",
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        dest="json_output",
        help="Output as JSON instead of human-readable text",
    )
    return parser.parse_args()


# ── Printers ──────────────────────────────────────────────────────────

def _header(title: str) -> None:
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print(f"{'─' * 60}")


def show_discovery(bridge: PAIBridge) -> dict:
    """Discovery & status."""
    status = bridge.get_status()
    _header("Discovery & Status")
    print(f"  PAI installed : {status.get('pai_installed', False)}")
    print(f"  PAI root      : {status.get('pai_root', 'N/A')}")
    for comp, present in status.get("components", {}).items():
        icon = "✅" if present else "❌"
        print(f"    {icon} {comp}")
    return status


def show_algorithm(bridge: PAIBridge) -> dict:
    """Algorithm phases, principles, depth levels."""
    _header("Algorithm (The Algorithm™)")
    version = bridge.get_algorithm_version()
    print(f"  Version: {version or 'N/A'}")
    print()
    print("  Phases:")
    for phase in ALGORITHM_PHASES:
        print(f"    {phase['phase']}  {phase['name']:10s}  {phase['description']}")
    print()
    print("  Principles:")
    for p in PAI_PRINCIPLES[:5]:
        print(f"    #{p['num']:>2s}  {p['name']}")
    if len(PAI_PRINCIPLES) > 5:
        print(f"    ... and {len(PAI_PRINCIPLES) - 5} more")
    print()
    print("  Response Depth Levels:")
    for lvl in RESPONSE_DEPTH_LEVELS:
        print(f"    {lvl['depth']:12s}  {lvl['when']}")
    return {
        "version": version,
        "phases": ALGORITHM_PHASES,
        "principles_count": len(PAI_PRINCIPLES),
        "depth_levels": RESPONSE_DEPTH_LEVELS,
    }


def show_skills(bridge: PAIBridge) -> dict:
    """Skill packs."""
    skills = bridge.list_skills()
    _header(f"Skills ({len(skills)} packs)")
    for sk in skills:
        tools_icon = "🔧" if sk.has_tools else "  "
        wf_icon = "⚙️" if sk.has_workflows else "  "
        print(f"  {sk.name:30s}  {tools_icon} {wf_icon}  {sk.file_count} files")
    return {"skills": [s.__dict__ for s in skills]}


def show_tools(bridge: PAIBridge) -> dict:
    """TypeScript tools."""
    tools = bridge.list_tools()
    _header(f"Tools ({len(tools)} TypeScript)")
    for t in tools:
        print(f"  {t.name:35s}  {t.size_bytes:>8,} bytes")
    return {"tools": [t.__dict__ for t in tools]}


def show_hooks(bridge: PAIBridge) -> dict:
    """Lifecycle hooks."""
    hooks = bridge.list_hooks()
    active = bridge.list_active_hooks()
    _header(f"Hooks ({len(hooks)} total, {len(active)} active)")
    for h in hooks:
        status = "📦 archived" if h.is_archived else "✅ active"
        print(f"  {h.name:35s}  {status}  {h.size_bytes:>6,} bytes")
    return {"hooks": [h.__dict__ for h in hooks], "active_count": len(active)}


def show_agents(bridge: PAIBridge) -> dict:
    """Agent personalities."""
    agents = bridge.list_agents()
    _header(f"Agents ({len(agents)} personalities)")
    for a in agents:
        print(f"  {a.name:35s}  {a.size_bytes:>8,} bytes")
    return {"agents": [a.__dict__ for a in agents]}


def show_memory(bridge: PAIBridge) -> dict:
    """Memory stores."""
    stores = bridge.list_memory_stores()
    _header(f"Memory ({len(stores)} stores)")
    for m in stores:
        print(f"  {m.name:25s}  {m.item_count:>5} items")
    return {"memory_stores": [m.__dict__ for m in stores]}


def show_security(bridge: PAIBridge) -> dict:
    """Security system."""
    config = bridge.get_security_config()
    _header("Security System")
    for key, val in config.items():
        print(f"  {key:25s}  {val}")
    return {"security": config}


def show_telos(bridge: PAIBridge) -> dict:
    """TELOS identity files."""
    files = bridge.get_telos_files()
    _header(f"TELOS ({len(files)} files)")
    for f in files:
        print(f"  {f}")
    return {"telos_files": files}


def show_settings(bridge: PAIBridge) -> dict:
    """Settings & env."""
    settings = bridge.get_settings()
    env = bridge.get_pai_env()
    _header("Settings")
    if settings:
        print(f"  settings.json keys: {list(settings.keys())}")
    else:
        print("  settings.json: not found")
    print(f"  PAI env vars: {len(env)}")
    for k, v in list(env.items())[:5]:
        display_v = v if len(v) < 40 else v[:37] + "..."
        print(f"    {k} = {display_v}")
    if len(env) > 5:
        print(f"    ... and {len(env) - 5} more")
    return {"settings_keys": list((settings or {}).keys()), "env_count": len(env)}


def show_mcp(bridge: PAIBridge) -> dict:
    """MCP registration."""
    reg = bridge.get_mcp_registration()
    has_codom = bridge.has_codomyrmex_mcp()
    _header("MCP Registration")
    if reg:
        servers = list(reg.get("mcpServers", {}).keys())
        print(f"  Registered servers: {servers}")
    else:
        print("  MCP config not found")
    icon = "✅" if has_codom else "❌"
    print(f"  {icon} codomyrmex MCP registered: {has_codom}")
    return {"has_mcp_config": reg is not None, "has_codomyrmex_mcp": has_codom}


# ── Dispatcher ────────────────────────────────────────────────────────

SUBSYSTEM_FNS = {
    "discovery": show_discovery,
    "algorithm": show_algorithm,
    "skills": show_skills,
    "tools": show_tools,
    "hooks": show_hooks,
    "agents": show_agents,
    "memory": show_memory,
    "security": show_security,
    "telos": show_telos,
    "settings": show_settings,
    "mcp": show_mcp,
}


def main() -> int:
    args = parse_args()
    bridge = PAIBridge()

    print(f"🧬 PAI Bridge Example — upstream: {PAI_UPSTREAM_URL}")

    results: dict = {}

    if args.subsystem:
        fn = SUBSYSTEM_FNS[args.subsystem]
        results[args.subsystem] = fn(bridge)
    else:
        for name, fn in SUBSYSTEM_FNS.items():
            results[name] = fn(bridge)

    if args.json_output:
        print("\n" + json.dumps(results, indent=2, default=str))

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
