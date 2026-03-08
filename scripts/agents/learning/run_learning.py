#!/usr/bin/env python3
"""Learning — Thin Script Orchestrator.

Exercises the agent learning module's Skill class.

Usage:
    python scripts/agents/learning/run_learning.py
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
    print_info("Learning — exercising Skill class...")

    try:
        from codomyrmex.agents.learning import Skill
    except ImportError as e:
        print_error(f"Import failed: {e}")
        return 1

    print_success(f"Skill class imported: {Skill.__name__}")
    print_info(f"  Fields: {[f for f in dir(Skill) if not f.startswith('_')][:10]}")
    print_success("Learning probe complete.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
