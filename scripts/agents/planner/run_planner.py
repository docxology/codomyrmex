#!/usr/bin/env python3
"""Planner — Thin Script Orchestrator.

Introspects the agent planner submodule.

Usage:
    python scripts/agents/planner/run_planner.py
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
    print_info("Planner — introspecting module...")

    try:
        import codomyrmex.agents.planner as planner_mod
    except ImportError as e:
        print_error(f"Import failed: {e}")
        return 1

    exports = [n for n in dir(planner_mod) if not n.startswith("_")]
    print_success(f"Planner module: {len(exports)} exports")
    for name in exports[:10]:
        obj = getattr(planner_mod, name)
        print_info(f"  {name}: {type(obj).__name__}")
    print_success("Planner probe complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
