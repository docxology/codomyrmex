#!/usr/bin/env python3
"""Infrastructure Agent — Thin Script Orchestrator.

Instantiates the InfrastructureAgent and CloudToolFactory, lists available tools.

Usage:
    python scripts/agents/infrastructure/run_infrastructure.py
"""

import sys
from pathlib import Path

try:
    import codomyrmex
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "src"))

from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_success,
    setup_logging,
)


def main() -> int:
    setup_logging()
    print_info("Infrastructure Agent — probing capabilities...")

    try:
        from codomyrmex.agents.infrastructure import (
            CloudToolFactory,
            InfrastructureAgent,
        )
    except ImportError as e:
        print_error(f"Import failed: {e}")
        return 1

    print_success("InfrastructureAgent and CloudToolFactory imported.")
    print_info(f"  InfrastructureAgent bases: {[b.__name__ for b in InfrastructureAgent.__mro__[1:]]}")

    factory = CloudToolFactory()
    _tools = factory.list_tools() if hasattr(factory, "list_tools") else dir(factory)
    print_info(f"  CloudToolFactory methods: {[m for m in dir(factory) if not m.startswith('_')][:10]}")

    agent = InfrastructureAgent()
    print_success(f"  Agent name: {getattr(agent, 'name', type(agent).__name__)}")
    print_success("Infrastructure agent probe complete.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
