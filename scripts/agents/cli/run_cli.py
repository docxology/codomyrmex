#!/usr/bin/env python3
"""CLI — Thin Script Orchestrator.

Exercises the agents CLI handler module.

Usage:
    python scripts/agents/cli/run_cli.py
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
    print_info("CLI — introspecting agent CLI handlers...")

    try:
        from codomyrmex.agents.cli import handle_agent_setup, handle_agent_test
    except ImportError as e:
        print_error(f"Import failed: {e}")
        return 1

    print_success("CLI handlers imported:")
    print_info(f"  handle_agent_setup: {handle_agent_setup.__doc__ or 'available'}")
    print_info(f"  handle_agent_test: {handle_agent_test.__doc__ or 'available'}")
    print_success("CLI probe complete.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
