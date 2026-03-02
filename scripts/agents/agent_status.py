#!/usr/bin/env python3
"""
Agent system status and management utilities.

Usage:
    python agent_status.py [--list] [--health]
"""

import sys
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import os


def find_agents_configs() -> list:
    """Find agent configuration files."""
    patterns = ["AGENTS.md", "agents.yaml", "agents.json", ".agent/*"]
    found = []
    
    for pattern in patterns:
        found.extend(Path(".").glob(f"**/{pattern}"))
    
    return [f for f in found if "node_modules" not in str(f)][:20]


def parse_agents_md(path: Path) -> dict:
    """Extract info from AGENTS.md file."""
    with open(path) as f:
        content = f.read()
    
    info = {
        "path": str(path),
        "size": len(content),
        "sections": [],
    }
    
    for line in content.split("\n"):
        if line.startswith("## "):
            info["sections"].append(line[3:].strip())
    
    return info


def check_agent_health() -> dict:
    """Check agent-related system health."""
    health = {
        "python_version": sys.version.split()[0],
        "codomyrmex_available": False,
        "env_vars": [],
    }
    
    try:
        import codomyrmex  # noqa: F401
        health["codomyrmex_available"] = True
    except ImportError:
        pass
    
    agent_vars = ["AGENT_", "OPENAI_", "ANTHROPIC_", "LLM_", "MODEL_"]
    for key in os.environ:
        if any(key.startswith(v) for v in agent_vars):
            health["env_vars"].append(key)
    
    return health


def main():
    parser = argparse.ArgumentParser(description="Agent system status")
    parser.add_argument("--list", "-l", action="store_true", help="List agent configurations")
    parser.add_argument("--health", "-H", action="store_true", help="Check system health")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()
    
    print("🤖 Agent System Status\n")
    
    # Health check
    health = check_agent_health()
    print(f"🔧 System:")
    print(f"   Python: {health['python_version']}")
    print(f"   Codomyrmex: {'✅ Available' if health['codomyrmex_available'] else '❌ Not installed'}")
    if health["env_vars"]:
        print(f"   Agent env vars: {len(health['env_vars'])}")
        if args.verbose:
            for v in health["env_vars"][:5]:
                print(f"      - {v}")
    print()
    
    if args.health:
        return 0
    
    # List configurations
    configs = find_agents_configs()
    
    if not configs:
        print("📋 No agent configurations found")
        return 0
    
    print(f"📋 Agent Configurations ({len(configs)}):\n")
    
    for config in configs[:10]:
        if config.name == "AGENTS.md":
            info = parse_agents_md(config)
            print(f"   📄 {config}")
            if args.verbose and info["sections"]:
                print(f"      Sections: {', '.join(info['sections'][:5])}")
        else:
            print(f"   📄 {config}")
    
    if len(configs) > 10:
        print(f"\n   ... and {len(configs) - 10} more")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
