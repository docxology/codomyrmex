#!/usr/bin/env python3
"""Agent Setup — Thin Script Orchestrator.

Lists registered agents via AgentRegistry and probes health status.

Usage:
    python scripts/agents/agent_setup/run_agent_setup.py
"""

import sys
from pathlib import Path

try:
    import codomyrmex
except ImportError:
    sys.path.insert(
        0, str(Path(__file__).resolve().parent.parent.parent.parent / "src")
    )

from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_success,
    setup_logging,
)


def main() -> int:
    setup_logging()
    print_info("Agent Setup — listing registered agents...")

    try:
        from codomyrmex.agents.agent_setup import (
            AgentRegistry,
            generate_env_template,
            load_config,
        )
    except ImportError as e:
        print_error(f"Import failed: {e}")
        return 1

    registry = AgentRegistry()
    agents = registry.list_agents() if hasattr(registry, "list_agents") else []
    print_success(f"AgentRegistry: {len(agents)} agents registered")
    for a in agents[:10]:
        name = getattr(a, "name", str(a))
        print_info(f"  • {name}")

    # Show env template
    template = generate_env_template()
    print_info(f"  .env template: {len(template)} chars")
    print_success("Agent setup probe complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
