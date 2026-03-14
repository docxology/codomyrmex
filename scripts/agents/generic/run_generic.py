#!/usr/bin/env python3
"""Generic Agents — Thin Script Orchestrator.

Demonstrates the base agent classes: APIAgentBase, CLIAgentBase, AgentOrchestrator.

Usage:
    python scripts/agents/generic/run_generic.py
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
    print_info("Generic Agents — listing base classes...")

    try:
        from codomyrmex.agents.generic import (
            AgentOrchestrator,
            APIAgentBase,
            CLIAgentBase,
            TaskPlanner,
            TaskStatus,
        )
    except ImportError as e:
        print_error(f"Import failed: {e}")
        return 1

    print_success("Base classes imported:")
    for cls in [APIAgentBase, CLIAgentBase, AgentOrchestrator, TaskPlanner]:
        print_info(f"  {cls.__name__}: {[b.__name__ for b in cls.__mro__[1:3]]}")

    print_info(f"  TaskStatus values: {[s.name for s in TaskStatus]}")
    print_success("Generic agents probe complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
